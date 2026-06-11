"""
PaySim dataset loader for the Fraud Detection CCP.

Fetch strategy (first that works wins):
  1. Local cache  -> data/raw/paysim.csv (if already present)
  2. Public mirror download (HuggingFace / direct CSV)
  3. Synthetic PaySim-schema generator (fully reproducible fallback)

The synthetic fallback reproduces the PaySim schema and its key fraud signal
(fraud occurs only in TRANSFER / CASH_OUT, and fraudulent transfers tend to
drain the origin balance, producing a balance-error signal) so the rest of the
pipeline behaves identically whether real or synthetic data is used.

Columns (PaySim schema):
    step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig,
    nameDest, oldbalanceDest, newbalanceDest, isFraud, isFlaggedFraud
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent          # project root
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_CSV = RAW_DIR / "paysim.csv"

# Public mirrors of the Kaggle PaySim1 dataset (no auth). Tried in order.
MIRRORS = [
    "https://huggingface.co/datasets/Nooha/cc_fraud_detection_dataset/resolve/main/PS_20174392719_1491204439457_log.csv",
    "https://media.githubusercontent.com/media/MihaiNicolaeIonut/PaySim/main/PS_20174392719_1491204439457_log.csv",
]

TXN_TYPES = ["PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT"]


# --------------------------------------------------------------------------
# Download
# --------------------------------------------------------------------------
def _try_download(timeout: int = 60) -> bool:
    """Attempt to download a real PaySim mirror into RAW_CSV. Returns success."""
    import urllib.request

    for url in MIRRORS:
        try:
            print(f"[data_loader] Trying mirror: {url[:70]}...")
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
            if len(data) < 100_000:  # too small to be the real file
                print("[data_loader]   response too small, skipping")
                continue
            RAW_DIR.mkdir(parents=True, exist_ok=True)
            RAW_CSV.write_bytes(data)
            # sanity check the header
            head = pd.read_csv(RAW_CSV, nrows=5)
            if "isFraud" in head.columns and "type" in head.columns:
                print(f"[data_loader]   downloaded OK ({len(data)/1e6:.1f} MB)")
                return True
            print("[data_loader]   schema mismatch, skipping")
        except Exception as e:  # noqa: BLE001
            print(f"[data_loader]   mirror failed: {type(e).__name__}: {e}")
    return False


# --------------------------------------------------------------------------
# Synthetic PaySim-schema generator (reproducible fallback)
# --------------------------------------------------------------------------
def generate_synthetic_paysim(n_rows: int = 1_000_000,
                              fraud_rate: float = 0.0020,
                              seed: int = 42) -> pd.DataFrame:
    """
    Generate a PaySim-schema synthetic dataset.

    Reproduces the dataset's defining properties:
      * 5 transaction types with realistic mix (PAYMENT/CASH_OUT dominate)
      * fraud only in TRANSFER and CASH_OUT
      * fraudulent transactions tend to move the *entire* origin balance,
        creating the balance-error signal the pipeline relies on
      * merchant destinations (nameDest starting with 'M') never receive
        TRANSFER/CASH_OUT (mirrors PaySim)
    """
    rng = np.random.default_rng(seed)
    n = n_rows

    # --- transaction type mix (approx PaySim proportions) ---
    type_p = np.array([0.34, 0.084, 0.35, 0.22, 0.006])  # PAYMENT,TRANSFER,CASH_OUT,CASH_IN,DEBIT
    type_p = type_p / type_p.sum()
    ttype = rng.choice(TXN_TYPES, size=n, p=type_p)

    # --- step: hour over ~30 days (744 hours), diurnal-ish ---
    step = rng.integers(1, 744, size=n)

    # --- amount: heavy-tailed (log-normal), type-dependent scale ---
    base = rng.lognormal(mean=8.0, sigma=1.4, size=n)
    scale = np.where(np.isin(ttype, ["TRANSFER", "CASH_OUT"]), 2.2, 1.0)
    amount = np.round(base * scale, 2)
    amount = np.clip(amount, 1.0, 1.0e7)

    # --- origin balances ---
    oldbalanceOrg = np.round(rng.lognormal(mean=9.0, sigma=1.3, size=n), 2)
    # default "normal" behaviour: balance decreases by amount (clipped at 0)
    newbalanceOrig = np.clip(oldbalanceOrg - amount, 0.0, None)
    # small bookkeeping noise (fees / rounding) so balance-error terms are not a
    # perfectly clean signal for legitimate transactions
    newbalanceOrig += rng.normal(0, 30, size=n)
    newbalanceOrig = np.clip(np.round(newbalanceOrig, 2), 0.0, None)

    # a fraction of legitimate transfers / cash-outs also fully drain the account
    # (legitimate large withdrawals) -> creates realistic false-positive pressure
    eligible = np.isin(ttype, ["TRANSFER", "CASH_OUT"])
    legit_drain = eligible & (rng.random(n) < 0.05)
    newbalanceOrig[legit_drain] = 0.0

    # --- destination identity: merchants for PAYMENT, customers otherwise ---
    is_merchant = (ttype == "PAYMENT")
    nameDest = np.where(
        is_merchant,
        np.array(["M"] * n),
        np.array(["C"] * n),
    )
    dest_id = rng.integers(1_000_000, 9_999_999, size=n).astype(str)
    nameDest = np.char.add(nameDest, dest_id)
    nameOrig = np.char.add("C", rng.integers(1_000_000, 9_999_999, size=n).astype(str))

    # --- destination balances (merchants reported as 0 in PaySim) ---
    oldbalanceDest = np.where(is_merchant, 0.0,
                              np.round(rng.lognormal(mean=8.5, sigma=1.4, size=n), 2))
    newbalanceDest = np.where(is_merchant, 0.0,
                              np.round(oldbalanceDest + amount, 2))
    # bookkeeping noise on the destination side as well
    cust = ~is_merchant
    newbalanceDest[cust] += rng.normal(0, 30, size=int(cust.sum()))
    newbalanceDest = np.clip(np.round(newbalanceDest, 2), 0.0, None)

    # --- fraud injection: only TRANSFER / CASH_OUT, probabilistic (realistic overlap) ---
    isFraud = np.zeros(n, dtype=int)
    n_fraud = int(n * fraud_rate)
    elig_idx = np.where(eligible)[0]
    if len(elig_idx) > 0 and n_fraud > 0:
        fraud_idx = rng.choice(elig_idx, size=min(n_fraud, len(elig_idx)), replace=False)
        isFraud[fraud_idx] = 1
        # ~72% of fraud aggressively drains the account; the rest take a partial
        # amount to look more like a normal transaction (harder to detect)
        drain_mask = rng.random(len(fraud_idx)) < 0.72
        full = fraud_idx[drain_mask]
        partial = fraud_idx[~drain_mask]
        # full-drain fraud: take most of the balance; most (not all) report new == 0
        amount[full] = np.round(oldbalanceOrg[full] * rng.uniform(0.85, 1.0, len(full)), 2)
        nb_full = np.clip(oldbalanceOrg[full] - amount[full] + rng.normal(0, 20, len(full)), 0, None)
        newbalanceOrig[full] = np.where(rng.random(len(full)) < 0.7, 0.0, np.round(nb_full, 2))
        # partial fraud: smaller amount, balance behaves almost normally
        amount[partial] = np.round(oldbalanceOrg[partial] * rng.uniform(0.3, 0.7, len(partial)), 2)
        newbalanceOrig[partial] = np.clip(np.round(oldbalanceOrg[partial] - amount[partial], 2), 0, None)
        # ~60% of fraudulent destinations don't credit the balance (mule cash-out)
        no_credit = fraud_idx[rng.random(len(fraud_idx)) < 0.6]
        oldbalanceDest[no_credit] = 0.0
        newbalanceDest[no_credit] = 0.0

        # --- camouflaged fraud: ~15% behaves like a perfectly normal transaction
        #     (modest amount, clean bookkeeping, credited destination). These carry
        #     no anomaly signal, so they cap achievable recall (irreducible false
        #     negatives) - reflecting how sophisticated fraud evades detection.
        camo = fraud_idx[rng.random(len(fraud_idx)) < 0.15]
        amount[camo] = np.round(oldbalanceOrg[camo] * rng.uniform(0.05, 0.35, len(camo)), 2)
        newbalanceOrig[camo] = np.clip(np.round(oldbalanceOrg[camo] - amount[camo], 2), 0, None)
        oldbalanceDest[camo] = np.round(rng.lognormal(8.5, 1.4, len(camo)), 2)
        newbalanceDest[camo] = np.round(oldbalanceDest[camo] + amount[camo], 2)

    # --- fraud-mimicking legitimate transactions: a few genuine transactions look
    #     exactly like full-drain fraud (large legitimate withdrawal to an empty
    #     account). They cap achievable precision (irreducible false positives). ---
    legit_elig = np.where(eligible & (isFraud == 0))[0]
    n_mimic = int(0.0006 * len(legit_elig))
    if n_mimic > 0:
        mimic = rng.choice(legit_elig, size=n_mimic, replace=False)
        amount[mimic] = np.round(oldbalanceOrg[mimic] * rng.uniform(0.85, 1.0, len(mimic)), 2)
        newbalanceOrig[mimic] = 0.0
        oldbalanceDest[mimic] = 0.0
        newbalanceDest[mimic] = 0.0

    # --- isFlaggedFraud: legacy rule = TRANSFER and amount > 200,000 ---
    isFlaggedFraud = ((ttype == "TRANSFER") & (amount > 200_000)).astype(int)

    df = pd.DataFrame({
        "step": step,
        "type": ttype,
        "amount": amount,
        "nameOrig": nameOrig,
        "oldbalanceOrg": oldbalanceOrg,
        "newbalanceOrig": newbalanceOrig,
        "nameDest": nameDest,
        "oldbalanceDest": oldbalanceDest,
        "newbalanceDest": newbalanceDest,
        "isFraud": isFraud,
        "isFlaggedFraud": isFlaggedFraud,
    })
    # shuffle so fraud isn't clustered at the end
    df = df.sample(frac=1.0, random_state=seed).reset_index(drop=True)
    return df


# --------------------------------------------------------------------------
# Public API
# --------------------------------------------------------------------------
def load_paysim(nrows: int | None = None,
                allow_download: bool = True,
                synthetic_rows: int = 1_000_000,
                force_synthetic: bool = False) -> tuple[pd.DataFrame, str]:
    """
    Load PaySim data. Returns (dataframe, source_label).

    source_label is one of: "cache", "mirror", "synthetic".
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # 1. cache
    if RAW_CSV.exists() and not force_synthetic:
        print(f"[data_loader] Loading cached file: {RAW_CSV}")
        df = pd.read_csv(RAW_CSV, nrows=nrows)
        # detect whether cache is the synthetic one
        label = "synthetic" if (RAW_DIR / ".synthetic").exists() else "cache"
        return df, label

    # 2. mirror download
    if allow_download and not force_synthetic:
        if _try_download():
            df = pd.read_csv(RAW_CSV, nrows=nrows)
            return df, "mirror"

    # 3. synthetic fallback
    print(f"[data_loader] Falling back to synthetic PaySim ({synthetic_rows:,} rows)")
    df = generate_synthetic_paysim(n_rows=synthetic_rows)
    df.to_csv(RAW_CSV, index=False)
    (RAW_DIR / ".synthetic").write_text("synthetic fallback dataset\n")
    if nrows:
        df = df.head(nrows)
    return df, "synthetic"


if __name__ == "__main__":
    t0 = time.time()
    force = "--synthetic" in sys.argv
    df, src = load_paysim(force_synthetic=force)
    print("\n================ PaySim load summary ================")
    print(f"Source        : {src}")
    print(f"Shape         : {df.shape}")
    print(f"Columns       : {list(df.columns)}")
    print(f"Fraud count   : {int(df['isFraud'].sum()):,}")
    print(f"Fraud rate    : {df['isFraud'].mean()*100:.4f}%")
    print(f"Type mix      :\n{df['type'].value_counts()}")
    print(f"Fraud by type :\n{df[df['isFraud']==1]['type'].value_counts()}")
    print(f"Load time     : {time.time()-t0:.1f}s")
    print("====================================================")
