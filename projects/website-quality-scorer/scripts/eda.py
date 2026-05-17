"""Exploratory Data Analysis on data/labeled/dataset.csv.

Generates a deck of PNG visualizations plus CSV/Markdown reports under
data/eda/. Re-runnable end-to-end:

    cd projects/website-quality-scorer
    python scripts/eda.py

Outputs:
    data/eda/figures/*.png
    data/eda/summary_stats.csv
    data/eda/missing_value_report.csv
    data/eda/feature_target_correlation.csv
    data/eda/eda_report.md
"""

from __future__ import annotations

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.patches import Patch
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Allow imports from backend/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from features.extractor import FEATURE_NAMES, FEATURE_SCHEMA  # noqa: E402
from ml.preprocessing import coerce_numeric  # noqa: E402

DATA_PATH = ROOT / "data" / "labeled" / "dataset.csv"
OUT_DIR = ROOT / "data" / "eda"
FIG_DIR = OUT_DIR / "figures"

DIM_COLORS = {
    "ux":        "#3B82F6",
    "content":   "#10B981",
    "technical": "#F59E0B",
    "trust":     "#8B5CF6",
}
SUBSCORE_COLS = ["score_ux", "score_content", "score_technical", "score_trust"]
TIER_EDGES = [0, 25, 50, 75, 100]
TIER_LABELS = ["Poor (0-25)", "Average (26-50)", "Good (51-75)", "Excellent (76-100)"]
TIER_PALETTE = ["#EF4444", "#F59E0B", "#3B82F6", "#10B981"]


def setup() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_style("whitegrid")
    plt.rcParams["figure.dpi"] = 100
    plt.rcParams["savefig.dpi"] = 150
    plt.rcParams["savefig.bbox"] = "tight"
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["font.size"] = 9


def save(fig: plt.Figure, name: str) -> None:
    path = FIG_DIR / name
    fig.savefig(path)
    plt.close(fig)
    print(f"  saved {path.relative_to(ROOT)}")


def load_dataset() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Returns (raw_df, X) where X is the coerced 41-feature matrix."""
    raw = pd.read_csv(DATA_PATH)
    raw = raw.rename(columns={f"feature_{n}": n for n in FEATURE_NAMES})
    X = coerce_numeric(raw[FEATURE_NAMES])
    return raw, X


# ============================================================
# Visualizations
# ============================================================

def fig01_target_distribution(raw: pd.DataFrame) -> None:
    y = raw["score_total"].dropna()
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.histplot(y, bins=25, kde=True, color="#1E40AF", ax=ax, alpha=0.7)
    ax.axvline(y.mean(), color="red", lw=2, ls="--", label=f"Mean = {y.mean():.1f}")
    ax.axvline(y.median(), color="green", lw=2, ls="--", label=f"Median = {y.median():.1f}")
    ax.axvspan(y.mean() - y.std(), y.mean() + y.std(), color="red", alpha=0.07, label=f"±1 std ({y.std():.1f})")
    ax.set_title("Distribution of score_total (n=%d)" % len(y))
    ax.set_xlabel("score_total (0-100)")
    ax.set_ylabel("Count")
    ax.legend()
    save(fig, "01_target_total_distribution.png")


def fig02_subscore_distributions(raw: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    for ax, col in zip(axes.flat, SUBSCORE_COLS):
        dim = col.replace("score_", "")
        s = raw[col].dropna()
        sns.histplot(s, bins=20, kde=True, color=DIM_COLORS[dim], ax=ax, alpha=0.75)
        ax.axvline(s.mean(), color="red", lw=1.5, ls="--", label=f"μ={s.mean():.1f}")
        ax.set_title(f"{col} (0-25)")
        ax.set_xlim(0, 25)
        ax.legend()
    fig.suptitle("Sub-score distributions across 4 dimensions", fontweight="bold")
    fig.tight_layout()
    save(fig, "02_subscore_distributions.png")


def fig03_tier_pie(raw: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    """Returns (tier_series, counts) for downstream reuse."""
    tier = pd.cut(raw["score_total"], bins=TIER_EDGES, labels=TIER_LABELS, include_lowest=True)
    counts = tier.value_counts().reindex(TIER_LABELS, fill_value=0)
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        counts.values,
        labels=counts.index,
        autopct=lambda p: f"{p:.1f}%\n(n={int(round(p * counts.sum() / 100))})",
        colors=TIER_PALETTE,
        startangle=90,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
        textprops={"fontsize": 11},
    )
    for t in autotexts:
        t.set_color("white")
        t.set_fontweight("bold")
    ax.set_title(f"Tier breakdown by score_total (n={counts.sum()})", fontweight="bold", pad=20)
    save(fig, "03_tier_pie.png")
    return tier, counts


def fig04_missing_values(raw: pd.DataFrame, X: pd.DataFrame) -> pd.Series:
    pct = (X.isna().mean() * 100).sort_values(ascending=True)
    colors = [DIM_COLORS[FEATURE_SCHEMA[name]["dim"]] for name in pct.index]
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.barh(pct.index, pct.values, color=colors)
    ax.set_xlabel("% missing")
    ax.set_title(f"Missing values per feature (n={len(raw)} rows)")
    ax.set_xlim(0, max(100, pct.max() * 1.1))
    for i, v in enumerate(pct.values):
        if v > 0:
            ax.text(v + 0.5, i, f"{v:.1f}%", va="center", fontsize=8)
    legend_handles = [Patch(facecolor=c, label=d.title()) for d, c in DIM_COLORS.items()]
    ax.legend(handles=legend_handles, loc="lower right", title="Dimension")
    save(fig, "04_missing_values.png")
    return pct.sort_values(ascending=False)


def _feature_grid(X: pd.DataFrame, dim: str, filename: str) -> None:
    feats = [n for n, info in FEATURE_SCHEMA.items() if info["dim"] == dim]
    ncols = 4
    nrows = int(np.ceil(len(feats) / ncols))
    fig, axes = plt.subplots(nrows, ncols, figsize=(4.2 * ncols, 3.2 * nrows))
    axes_flat = axes.flat if hasattr(axes, "flat") else [axes]
    color = DIM_COLORS[dim]
    for ax, name in zip(axes_flat, feats):
        s = X[name].dropna()
        is_bool = FEATURE_SCHEMA[name]["type"] == "bool"
        if is_bool:
            counts = s.value_counts().reindex([0, 1], fill_value=0)
            ax.bar(["False", "True"], counts.values, color=[color, "#1F2937"], alpha=0.85)
            for i, v in enumerate(counts.values):
                ax.text(i, v + 0.3, str(int(v)), ha="center", fontsize=8)
        else:
            sns.histplot(s, bins=20, color=color, ax=ax, alpha=0.8, kde=False)
        ax.set_title(name.replace(f"{dim}_", ""), fontsize=9)
        ax.set_xlabel("")
        ax.set_ylabel("")
    # Hide extra axes
    for ax in list(axes_flat)[len(feats):]:
        ax.axis("off")
    fig.suptitle(f"{dim.title()} feature distributions (n={len(X)})", fontweight="bold")
    fig.tight_layout()
    save(fig, filename)


def fig05_feature_distributions(X: pd.DataFrame) -> None:
    _feature_grid(X, "ux",        "05a_ux_feature_distributions.png")
    _feature_grid(X, "content",   "05b_content_feature_distributions.png")
    _feature_grid(X, "technical", "05c_technical_feature_distributions.png")
    _feature_grid(X, "trust",     "05d_trust_feature_distributions.png")


def fig06_boolean_counts(X: pd.DataFrame) -> None:
    bool_feats = [n for n, info in FEATURE_SCHEMA.items() if info["type"] == "bool"]
    rows = []
    for name in bool_feats:
        s = X[name]
        rows.append({
            "feature": name,
            "True":  int((s == 1).sum()),
            "False": int((s == 0).sum()),
            "NaN":   int(s.isna().sum()),
            "dim":   FEATURE_SCHEMA[name]["dim"],
        })
    df = pd.DataFrame(rows).sort_values("dim")
    fig, ax = plt.subplots(figsize=(12, max(6, 0.4 * len(df))))
    y = np.arange(len(df))
    ax.barh(y - 0.25, df["True"],  height=0.25, label="True",  color="#10B981")
    ax.barh(y,        df["False"], height=0.25, label="False", color="#EF4444")
    ax.barh(y + 0.25, df["NaN"],   height=0.25, label="NaN",   color="#6B7280")
    ax.set_yticks(y)
    ax.set_yticklabels(df["feature"])
    ax.set_xlabel("Count")
    ax.set_title("Boolean feature counts (True / False / NaN)")
    ax.legend()
    save(fig, "06_boolean_feature_counts.png")


def fig07_correlation_heatmap(X: pd.DataFrame) -> pd.DataFrame:
    corr = X.corr(method="pearson")
    fig, ax = plt.subplots(figsize=(16, 14))
    sns.heatmap(corr, cmap="RdBu_r", center=0, vmin=-1, vmax=1, ax=ax,
                cbar_kws={"shrink": 0.7, "label": "Pearson r"},
                xticklabels=True, yticklabels=True, linewidths=0.3, linecolor="white")
    ax.set_title("Feature × Feature correlation heatmap (Pearson)", fontweight="bold")
    plt.setp(ax.get_xticklabels(), rotation=90, fontsize=7)
    plt.setp(ax.get_yticklabels(), rotation=0, fontsize=7)
    save(fig, "07_correlation_heatmap.png")
    return corr


def fig08_feature_target_correlation(X: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
    """Compute Pearson + Spearman correlation between each feature and score_total. Returns sorted table."""
    y = raw["score_total"]
    rows = []
    for name in FEATURE_NAMES:
        s = X[name]
        mask = s.notna() & y.notna()
        if mask.sum() < 5 or s[mask].nunique() < 2:
            pearson = np.nan
            spearman = np.nan
        else:
            pearson = s[mask].corr(y[mask], method="pearson")
            spearman = s[mask].corr(y[mask], method="spearman")
        rows.append({
            "feature": name,
            "dim": FEATURE_SCHEMA[name]["dim"],
            "pearson_r": pearson,
            "spearman_r": spearman,
        })
    df = pd.DataFrame(rows).sort_values("pearson_r", key=lambda s: s.abs(), ascending=True)
    colors = [DIM_COLORS[d] for d in df["dim"]]
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.barh(df["feature"], df["pearson_r"], color=colors)
    ax.axvline(0, color="black", lw=0.7)
    ax.set_xlabel("Pearson r with score_total")
    ax.set_title("Feature → target correlation (sorted by |r|)")
    legend_handles = [Patch(facecolor=c, label=d.title()) for d, c in DIM_COLORS.items()]
    ax.legend(handles=legend_handles, loc="lower right", title="Dimension")
    save(fig, "08_feature_target_correlation.png")
    return df.sort_values("pearson_r", key=lambda s: s.abs(), ascending=False)


def fig09_top_features_scatter(X: pd.DataFrame, raw: pd.DataFrame, corr_df: pd.DataFrame) -> None:
    top = corr_df.dropna(subset=["pearson_r"]).head(6)
    y = raw["score_total"]
    fig, axes = plt.subplots(2, 3, figsize=(15, 8))
    for ax, (_, row) in zip(axes.flat, top.iterrows()):
        name = row["feature"]
        color = DIM_COLORS[row["dim"]]
        x = X[name]
        mask = x.notna() & y.notna()
        sns.regplot(x=x[mask], y=y[mask], ax=ax, color=color,
                    scatter_kws={"alpha": 0.5, "s": 25}, line_kws={"color": "black", "lw": 1.5})
        ax.set_title(f"{name}\nr = {row['pearson_r']:.2f}", fontsize=10)
        ax.set_xlabel(name, fontsize=8)
        ax.set_ylabel("score_total", fontsize=8)
    fig.suptitle("Top 6 features by |Pearson r| vs score_total", fontweight="bold")
    fig.tight_layout()
    save(fig, "09_top_features_scatter.png")


def fig10_boxplots_continuous(X: pd.DataFrame) -> None:
    continuous = [n for n, info in FEATURE_SCHEMA.items() if info["type"] == "num"]
    # Standardize so we can compare scales on one figure
    X_num = X[continuous].copy()
    means = X_num.mean()
    stds = X_num.std(ddof=0).replace(0, 1)
    X_z = (X_num - means) / stds
    long_df = X_z.melt(var_name="feature", value_name="z_value").dropna()
    long_df["dim"] = long_df["feature"].map(lambda n: FEATURE_SCHEMA[n]["dim"])
    order = sorted(continuous, key=lambda n: (FEATURE_SCHEMA[n]["dim"], n))
    palette = {d: DIM_COLORS[d] for d in DIM_COLORS}
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.boxplot(data=long_df, x="feature", y="z_value", hue="dim", order=order,
                palette=palette, ax=ax, dodge=False, linewidth=0.8, fliersize=3)
    ax.axhline(0, color="black", lw=0.6, ls=":")
    ax.set_title("Continuous feature boxplots (z-scored for comparison) — outliers visible")
    ax.set_ylabel("z-score")
    ax.set_xlabel("")
    plt.setp(ax.get_xticklabels(), rotation=90, fontsize=8)
    ax.legend(title="Dimension", loc="upper right")
    save(fig, "10_boxplots_continuous.png")


def fig11_subscore_pairplot(raw: pd.DataFrame) -> None:
    df = raw[SUBSCORE_COLS].copy()
    g = sns.pairplot(df, kind="reg", diag_kind="kde", height=2.4,
                     plot_kws={"scatter_kws": {"alpha": 0.45, "s": 18},
                               "line_kws": {"color": "red", "lw": 1.2}},
                     diag_kws={"fill": True, "color": "#3B82F6"})
    g.figure.suptitle("Sub-score pairwise relationships", fontweight="bold", y=1.01)
    fig = g.figure
    save(fig, "11_subscore_pairplot.png")


def fig12_skewness(X: pd.DataFrame) -> pd.Series:
    continuous = [n for n, info in FEATURE_SCHEMA.items() if info["type"] == "num"]
    skew = X[continuous].skew(numeric_only=True).sort_values()
    colors = ["#EF4444" if abs(s) > 1 else "#10B981" for s in skew.values]
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.barh(skew.index, skew.values, color=colors)
    ax.axvline(1, color="red", lw=1, ls="--", label="|skew|=1 threshold")
    ax.axvline(-1, color="red", lw=1, ls="--")
    ax.axvline(0, color="black", lw=0.7)
    ax.set_xlabel("Skewness")
    ax.set_title("Skewness per continuous feature (red = transform candidate)")
    ax.legend(loc="lower right")
    save(fig, "12_skewness_bars.png")
    return skew


def fig13_pca_scatter(X: pd.DataFrame, raw: pd.DataFrame) -> None:
    # Fill NaN with column median; scale; PCA(2)
    X_filled = X.fillna(X.median(numeric_only=True))
    X_scaled = StandardScaler().fit_transform(X_filled)
    coords = PCA(n_components=2, random_state=42).fit_transform(X_scaled)
    y = raw["score_total"].values
    fig, ax = plt.subplots(figsize=(10, 7))
    sc = ax.scatter(coords[:, 0], coords[:, 1], c=y, cmap="viridis", s=50,
                    edgecolor="white", linewidth=0.5, alpha=0.85)
    fig.colorbar(sc, ax=ax, label="score_total")
    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.set_title("PCA(2) of features — colored by score_total")
    save(fig, "13_pca_scatter.png")


def fig14_score_by_boolean(X: pd.DataFrame, raw: pd.DataFrame) -> None:
    bool_feats = [n for n, info in FEATURE_SCHEMA.items() if info["type"] == "bool"]
    nrows = int(np.ceil(len(bool_feats) / 4))
    fig, axes = plt.subplots(nrows, 4, figsize=(16, 3 * nrows))
    y = raw["score_total"]
    for ax, name in zip(axes.flat, bool_feats):
        mask = X[name].notna()
        df = pd.DataFrame({"value": X.loc[mask, name].astype(int), "score_total": y[mask]})
        sns.boxplot(data=df, x="value", y="score_total", ax=ax,
                    palette={0: "#EF4444", 1: "#10B981"}, hue="value", legend=False)
        ax.set_title(name, fontsize=9)
        ax.set_xlabel("")
        ax.set_ylabel("")
    for ax in list(axes.flat)[len(bool_feats):]:
        ax.axis("off")
    fig.suptitle("score_total stratified by each boolean feature", fontweight="bold")
    fig.tight_layout()
    save(fig, "14_score_total_by_boolean.png")


# ============================================================
# Pattern extraction + report writing
# ============================================================

def find_high_corr_pairs(corr: pd.DataFrame, threshold: float = 0.85) -> pd.DataFrame:
    """Returns DataFrame of feature pairs with |r| > threshold (excludes self-pairs)."""
    pairs = []
    feats = corr.columns.tolist()
    for i, a in enumerate(feats):
        for b in feats[i + 1:]:
            r = corr.loc[a, b]
            if pd.notna(r) and abs(r) >= threshold:
                pairs.append({
                    "feature_a": a,
                    "feature_b": b,
                    "dim_a": FEATURE_SCHEMA[a]["dim"],
                    "dim_b": FEATURE_SCHEMA[b]["dim"],
                    "pearson_r": r,
                })
    return pd.DataFrame(pairs).sort_values("pearson_r", key=lambda s: s.abs(), ascending=False)


def iqr_outlier_counts(X: pd.DataFrame) -> pd.Series:
    continuous = [n for n, info in FEATURE_SCHEMA.items() if info["type"] == "num"]
    counts = {}
    for name in continuous:
        s = X[name].dropna()
        if len(s) < 5:
            counts[name] = 0
            continue
        q1, q3 = s.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr == 0:
            counts[name] = 0
            continue
        lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        counts[name] = int(((s < lo) | (s > hi)).sum())
    return pd.Series(counts).sort_values(ascending=False)


def near_constant(X: pd.DataFrame) -> list[str]:
    flags = []
    for name in X.columns:
        s = X[name].dropna()
        if len(s) == 0:
            flags.append(name)
            continue
        top_share = s.value_counts(normalize=True).iloc[0]
        if top_share >= 0.95 or s.std(ddof=0) < 0.01:
            flags.append(name)
    return flags


def write_report(
    raw: pd.DataFrame,
    X: pd.DataFrame,
    tier_counts: pd.Series,
    missing_pct: pd.Series,
    corr_target: pd.DataFrame,
    corr: pd.DataFrame,
    skew: pd.Series,
) -> None:
    y = raw["score_total"].dropna()
    high_pairs = find_high_corr_pairs(corr, threshold=0.85)
    outliers = iqr_outlier_counts(X)
    constants = near_constant(X)
    subscore_corr = raw[SUBSCORE_COLS].corr()

    # --- Conditional preprocessing recommendations ---
    recs: list[str] = []
    pagespeed_cols = [n for n in FEATURE_NAMES if n.startswith("tech_pagespeed") or n in (
        "tech_lcp_seconds", "tech_cls", "tech_tbt_seconds")]
    ps_missing = missing_pct.reindex(pagespeed_cols).dropna()
    if (ps_missing > 30).any():
        recs.append(
            f"**Missing values:** PageSpeed columns are >30% missing "
            f"({', '.join(f'{c} ({ps_missing[c]:.0f}%)' for c in ps_missing[ps_missing > 30].index)}). "
            f"Recommendation: keep as NaN — XGBoost handles missing natively (see [backend/ml/preprocessing.py](../../backend/ml/preprocessing.py)). "
            f"If switching to a non-tree model, apply median imputation per column."
        )
    else:
        recs.append("**Missing values:** No column exceeds 30% missing — light imputation acceptable.")

    high_skew = skew[skew.abs() > 1].sort_values(key=lambda s: s.abs(), ascending=False)
    if len(high_skew):
        recs.append(
            f"**Skew correction:** {len(high_skew)} continuous features have |skew| > 1 — apply `np.log1p` before training:\n"
            + "\n".join(f"  - `{name}` (skew={val:.2f})" for name, val in high_skew.items())
        )
    else:
        recs.append("**Skew correction:** No feature has |skew| > 1 — log transform unnecessary.")

    cross_dim_pairs = high_pairs[high_pairs["dim_a"] != high_pairs["dim_b"]] if not high_pairs.empty else high_pairs
    if not cross_dim_pairs.empty:
        recs.append(
            f"**Multicollinearity:** {len(cross_dim_pairs)} cross-dimension feature pairs have |r| > 0.85 — consider dropping one of each pair if interpretability matters:\n"
            + "\n".join(f"  - `{r.feature_a}` ↔ `{r.feature_b}` (r={r.pearson_r:.2f})"
                        for r in cross_dim_pairs.itertuples())
        )
    else:
        recs.append("**Multicollinearity:** No cross-dimension feature pair exceeds |r| > 0.85 — keep all features.")

    if constants:
        recs.append(f"**Constant/near-constant features:** {', '.join(f'`{c}`' for c in constants)} — drop before training.")
    else:
        recs.append("**Constant/near-constant features:** None detected.")

    tier_share = tier_counts / tier_counts.sum()
    imbalanced = tier_share[tier_share < 0.10]
    if not imbalanced.empty:
        recs.append(
            f"**Class imbalance:** {', '.join(imbalanced.index)} tiers each hold <10% of samples. "
            f"Recommendation: stratify train/test split on tier label and use stratified k-fold during CV "
            f"(see [backend/ml/train.py:78](../../backend/ml/train.py#L78))."
        )
    else:
        recs.append("**Class imbalance:** Tier shares are reasonably balanced — random split acceptable.")

    recs.append(
        "**Scaling:** Continuous features → StandardScaler; booleans → passthrough. "
        "XGBoost is scale-invariant so this is optional for the deployed model, but required if benchmarking against "
        "linear models or k-NN."
    )

    # --- Write the report ---
    md = []
    md.append("# EDA Report — `data/labeled/dataset.csv`\n")
    md.append(f"_Generated automatically by `scripts/eda.py` — re-run to refresh._\n")
    md.append("## 1. Dataset shape\n")
    md.append(f"- Rows: **{len(raw)}**")
    md.append(f"- Features: **{len(FEATURE_NAMES)}** ("
              f"UX={sum(1 for n in FEATURE_NAMES if FEATURE_SCHEMA[n]['dim']=='ux')}, "
              f"Content={sum(1 for n in FEATURE_NAMES if FEATURE_SCHEMA[n]['dim']=='content')}, "
              f"Technical={sum(1 for n in FEATURE_NAMES if FEATURE_SCHEMA[n]['dim']=='technical')}, "
              f"Trust={sum(1 for n in FEATURE_NAMES if FEATURE_SCHEMA[n]['dim']=='trust')})")
    bool_count = sum(1 for n in FEATURE_NAMES if FEATURE_SCHEMA[n]['type'] == 'bool')
    md.append(f"- Numeric features: **{len(FEATURE_NAMES) - bool_count}**, boolean features: **{bool_count}**\n")

    md.append("## 2. Target statistics (`score_total`)\n")
    md.append(f"- Mean: **{y.mean():.2f}** | Median: **{y.median():.2f}** | Std: **{y.std():.2f}**")
    md.append(f"- Min: **{y.min():.2f}** | Max: **{y.max():.2f}** | Range: **{y.max() - y.min():.2f}**")
    md.append(f"- Skewness: **{y.skew():.3f}** | Kurtosis: **{y.kurt():.3f}**\n")

    md.append("**Tier counts:**\n")
    for label, count in tier_counts.items():
        pct = count / tier_counts.sum() * 100
        md.append(f"- {label}: **{count}** ({pct:.1f}%)")
    md.append("")

    md.append("## 3. Missing-value summary\n")
    nz_missing = missing_pct[missing_pct > 0]
    if nz_missing.empty:
        md.append("No missing values in any feature.\n")
    else:
        md.append(f"Total NaN cells in feature matrix: **{int(X.isna().sum().sum())}** "
                  f"/ {len(X) * len(FEATURE_NAMES)} possible ({X.isna().sum().sum() / (len(X) * len(FEATURE_NAMES)) * 100:.2f}%).\n")
        md.append("Top 10 columns by missing %:\n")
        for name, pct in nz_missing.head(10).items():
            md.append(f"- `{name}` — **{pct:.1f}%** missing")
        md.append("")

    md.append("## 4. Constant / near-constant features\n")
    if constants:
        for name in constants:
            md.append(f"- `{name}`")
    else:
        md.append("None detected (every feature has >5% variation in non-NaN values).")
    md.append("")

    md.append("## 5. Top-15 features by |Pearson r| with `score_total`\n")
    md.append("| Rank | Feature | Dim | Pearson r | Spearman r |")
    md.append("|------|---------|-----|-----------|------------|")
    for i, row in enumerate(corr_target.head(15).itertuples(), 1):
        md.append(f"| {i} | `{row.feature}` | {row.dim} | {row.pearson_r:+.3f} | {row.spearman_r:+.3f} |")
    md.append("")

    md.append("## 6. High-correlation feature pairs (|r| > 0.85)\n")
    if high_pairs.empty:
        md.append("No feature pair exceeds |r| > 0.85.\n")
    else:
        md.append("| Feature A | Feature B | Dim A | Dim B | Pearson r |")
        md.append("|-----------|-----------|-------|-------|-----------|")
        for row in high_pairs.head(20).itertuples():
            md.append(f"| `{row.feature_a}` | `{row.feature_b}` | {row.dim_a} | {row.dim_b} | {row.pearson_r:+.3f} |")
        md.append("")

    md.append("## 7. Skewness flags (|skew| > 1)\n")
    if high_skew.empty:
        md.append("No continuous feature has |skew| > 1.\n")
    else:
        md.append("| Feature | Skew |")
        md.append("|---------|------|")
        for name, val in high_skew.items():
            md.append(f"| `{name}` | {val:+.2f} |")
        md.append("")

    md.append("## 8. Outliers (IQR method, 1.5×IQR rule)\n")
    md.append("Top 15 continuous features by outlier count:\n")
    md.append("| Feature | Outlier count | Outlier % |")
    md.append("|---------|---------------|-----------|")
    for name, count in outliers.head(15).items():
        denom = X[name].notna().sum()
        pct = count / denom * 100 if denom else 0
        md.append(f"| `{name}` | {count} | {pct:.1f}% |")
    md.append("")

    md.append("## 9. Sub-score inter-correlation\n")
    md.append("| | " + " | ".join(SUBSCORE_COLS) + " |")
    md.append("|" + "|".join(["---"] * (len(SUBSCORE_COLS) + 1)) + "|")
    for col in SUBSCORE_COLS:
        row = " | ".join(f"{subscore_corr.loc[col, c]:+.2f}" for c in SUBSCORE_COLS)
        md.append(f"| **{col}** | {row} |")
    md.append("")

    md.append("## 10. Preprocessing recommendations\n")
    for rec in recs:
        md.append(f"- {rec}\n")

    md.append("## Figures\n")
    md.append("All saved under [`figures/`](figures/):\n")
    figure_files = sorted(FIG_DIR.glob("*.png"))
    for f in figure_files:
        md.append(f"- ![{f.stem}](figures/{f.name})")
    md.append("")

    (OUT_DIR / "eda_report.md").write_text("\n".join(md), encoding="utf-8")
    print(f"  wrote {(OUT_DIR / 'eda_report.md').relative_to(ROOT)}")


# ============================================================
# Main
# ============================================================

def main() -> None:
    setup()
    print(f"Loading {DATA_PATH.relative_to(ROOT)} ...")
    raw, X = load_dataset()
    print(f"  shape: {raw.shape}, features: {X.shape[1]}")

    print("\nWriting summary tables ...")
    X.describe(include="all").to_csv(OUT_DIR / "summary_stats.csv")
    print(f"  wrote {(OUT_DIR / 'summary_stats.csv').relative_to(ROOT)}")

    print("\nGenerating figures ...")
    fig01_target_distribution(raw)
    fig02_subscore_distributions(raw)
    _, tier_counts = fig03_tier_pie(raw)
    missing_pct = fig04_missing_values(raw, X)
    missing_pct.rename("pct_missing").to_csv(OUT_DIR / "missing_value_report.csv", header=True)
    print(f"  wrote {(OUT_DIR / 'missing_value_report.csv').relative_to(ROOT)}")

    fig05_feature_distributions(X)
    fig06_boolean_counts(X)
    corr = fig07_correlation_heatmap(X)
    corr_target = fig08_feature_target_correlation(X, raw)
    corr_target.to_csv(OUT_DIR / "feature_target_correlation.csv", index=False)
    print(f"  wrote {(OUT_DIR / 'feature_target_correlation.csv').relative_to(ROOT)}")

    fig09_top_features_scatter(X, raw, corr_target)
    fig10_boxplots_continuous(X)
    fig11_subscore_pairplot(raw)
    skew = fig12_skewness(X)
    fig13_pca_scatter(X, raw)
    fig14_score_by_boolean(X, raw)

    print("\nWriting EDA report ...")
    write_report(raw, X, tier_counts, missing_pct, corr_target, corr, skew)

    print(f"\nDone. All outputs in {OUT_DIR.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
