"""Assemble the EDA outputs into a single PDF.

Reads the labeled dataset, recomputes summary statistics (fast — no figures),
and embeds the 14 PNGs from data/eda/figures/. Produces:

    data/eda/EDA_Report.pdf

Run:
    cd projects/website-quality-scorer
    python scripts/build_eda_pdf.py

Requires `scripts/eda.py` to have been run first (so the PNGs exist).
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from features.extractor import FEATURE_NAMES, FEATURE_SCHEMA  # noqa: E402
from ml.preprocessing import coerce_numeric  # noqa: E402

DATA_PATH = ROOT / "data" / "labeled" / "dataset.csv"
EDA_DIR = ROOT / "data" / "eda"
FIG_DIR = EDA_DIR / "figures"
PDF_PATH = EDA_DIR / "EDA_Report.pdf"

SUBSCORE_COLS = ["score_ux", "score_content", "score_technical", "score_trust"]
TIER_EDGES = [0, 25, 50, 75, 100]
TIER_LABELS = ["Poor (0-25)", "Average (26-50)", "Good (51-75)", "Excellent (76-100)"]

DIM_HEX = {
    "ux":        "#3B82F6",
    "content":   "#10B981",
    "technical": "#F59E0B",
    "trust":     "#8B5CF6",
}

# ----------------------------------------------------------------------------
# Analytical helpers (recomputed — fast, no figures)
# ----------------------------------------------------------------------------

def load_dataset() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = pd.read_csv(DATA_PATH)
    raw = raw.rename(columns={f"feature_{n}": n for n in FEATURE_NAMES})
    X = coerce_numeric(raw[FEATURE_NAMES])
    return raw, X


def tier_breakdown(raw: pd.DataFrame) -> pd.Series:
    tier = pd.cut(raw["score_total"], bins=TIER_EDGES, labels=TIER_LABELS, include_lowest=True)
    return tier.value_counts().reindex(TIER_LABELS, fill_value=0)


def missing_pct(X: pd.DataFrame) -> pd.Series:
    return (X.isna().mean() * 100).sort_values(ascending=False)


def feature_target_corr(X: pd.DataFrame, raw: pd.DataFrame) -> pd.DataFrame:
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
    return pd.DataFrame(rows).sort_values("pearson_r", key=lambda s: s.abs(), ascending=False)


def high_corr_pairs(X: pd.DataFrame, threshold: float = 0.85) -> pd.DataFrame:
    corr = X.corr(method="pearson")
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


def skewness_table(X: pd.DataFrame) -> pd.Series:
    continuous = [n for n, info in FEATURE_SCHEMA.items() if info["type"] == "num"]
    return X[continuous].skew(numeric_only=True).sort_values(key=lambda s: s.abs(), ascending=False)


def outlier_counts(X: pd.DataFrame) -> pd.Series:
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


# ----------------------------------------------------------------------------
# PDF building
# ----------------------------------------------------------------------------

def make_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", parent=base["Title"], fontSize=24, leading=28,
                                spaceAfter=12, alignment=TA_CENTER, textColor=colors.HexColor("#1E40AF")),
        "subtitle": ParagraphStyle("subtitle", parent=base["Normal"], fontSize=13, leading=16,
                                   alignment=TA_CENTER, textColor=colors.HexColor("#374151"),
                                   spaceAfter=24),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontSize=16, leading=20,
                             spaceBefore=14, spaceAfter=10, textColor=colors.HexColor("#1E3A8A")),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontSize=12, leading=16,
                             spaceBefore=8, spaceAfter=6, textColor=colors.HexColor("#1F2937")),
        "body": ParagraphStyle("body", parent=base["Normal"], fontSize=10, leading=14,
                               alignment=TA_LEFT),
        "bullet": ParagraphStyle("bullet", parent=base["Normal"], fontSize=10, leading=13,
                                 leftIndent=14, bulletIndent=2),
        "small": ParagraphStyle("small", parent=base["Normal"], fontSize=8.5, leading=11,
                                textColor=colors.HexColor("#6B7280")),
        "caption": ParagraphStyle("caption", parent=base["Italic"], fontSize=9, leading=12,
                                  alignment=TA_CENTER, textColor=colors.HexColor("#4B5563"),
                                  spaceBefore=6),
        "code": ParagraphStyle("code", parent=base["Code"], fontSize=9, leading=12),
    }


def kv_table(rows: list[tuple[str, str]], col_widths=(5 * cm, 9 * cm)) -> Table:
    t = Table(rows, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (-1, -1), "Helvetica", 10),
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 10),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#1F2937")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1),
            [colors.HexColor("#F9FAFB"), colors.HexColor("#FFFFFF")]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def data_table(headers: list[str], rows: list[list[str]], col_widths=None,
               dim_col: int | None = None) -> Table:
    """Build a styled data table. If dim_col is given, color rows by dimension."""
    data = [headers] + rows
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E3A8A")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
        ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LINEBELOW", (0, 0), (-1, -1), 0.25, colors.HexColor("#E5E7EB")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if dim_col is None:
        style.append(("ROWBACKGROUNDS", (0, 1), (-1, -1),
                      [colors.HexColor("#F9FAFB"), colors.HexColor("#FFFFFF")]))
    else:
        for ridx, row in enumerate(rows, start=1):
            dim = row[dim_col]
            style.append(("BACKGROUND", (0, ridx), (-1, ridx),
                          colors.HexColor(DIM_HEX.get(dim, "#FFFFFF") + "22")))
    t.setStyle(TableStyle(style))
    return t


def fit_image(path: Path, max_w: float, max_h: float) -> Image:
    """Scale an image to fit within (max_w, max_h) preserving aspect ratio."""
    reader = ImageReader(str(path))
    iw, ih = reader.getSize()
    ratio = min(max_w / iw, max_h / ih)
    return Image(str(path), width=iw * ratio, height=ih * ratio)


# ----------------------------------------------------------------------------
# Page builders
# ----------------------------------------------------------------------------

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#6B7280"))
    # Header
    canvas.drawString(2 * cm, A4[1] - 1.2 * cm, "Website Quality & Conversion Gap Scorer — EDA Report")
    canvas.drawRightString(A4[0] - 2 * cm, A4[1] - 1.2 * cm, datetime.now().strftime("%Y-%m-%d"))
    canvas.setStrokeColor(colors.HexColor("#E5E7EB"))
    canvas.line(2 * cm, A4[1] - 1.35 * cm, A4[0] - 2 * cm, A4[1] - 1.35 * cm)
    # Footer
    canvas.line(2 * cm, 1.3 * cm, A4[0] - 2 * cm, 1.3 * cm)
    canvas.drawCentredString(A4[0] / 2, 1 * cm, f"Page {doc.page}")
    canvas.restoreState()


def build_cover(story: list, styles: dict, raw: pd.DataFrame) -> None:
    story.append(Spacer(1, 3 * cm))
    story.append(Paragraph("Exploratory Data Analysis", styles["title"]))
    story.append(Paragraph("Website Quality &amp; Conversion Gap Scorer", styles["subtitle"]))
    story.append(Spacer(1, 1.5 * cm))

    y = raw["score_total"].dropna()
    info = [
        ("Course", "Machine Learning AIN-373 — Spring 2026"),
        ("Institution", "Iqra University, Islamabad"),
        ("Team", "Aleem Ul Hassan (42490), Abdul Hadi Minhas (37520)"),
        ("Dataset", str(DATA_PATH.relative_to(ROOT))),
        ("Samples", f"{len(raw)} websites"),
        ("Features", f"{len(FEATURE_NAMES)} across 4 dimensions (UX, Content, Technical, Trust)"),
        ("Target", f"score_total ∈ [0, 100], μ={y.mean():.2f}, σ={y.std():.2f}"),
        ("Generated", datetime.now().strftime("%Y-%m-%d %H:%M")),
    ]
    story.append(kv_table([(k, v) for k, v in info]))

    story.append(Spacer(1, 1.5 * cm))
    story.append(Paragraph(
        "<b>Contents</b><br/>"
        "1. Dataset overview<br/>"
        "2. Target distribution &amp; tier breakdown<br/>"
        "3. Missing-value analysis<br/>"
        "4. Feature distributions (per dimension)<br/>"
        "5. Correlation &amp; multicollinearity<br/>"
        "6. Top predictive features<br/>"
        "7. Outliers, skewness, sub-scores, PCA<br/>"
        "8. Preprocessing recommendations<br/>"
        "9. Figure appendix (14 visualizations)",
        styles["body"]
    ))
    story.append(PageBreak())


def build_overview(story: list, styles: dict, raw: pd.DataFrame, X: pd.DataFrame) -> None:
    story.append(Paragraph("1. Dataset Overview", styles["h1"]))

    bool_count = sum(1 for n in FEATURE_NAMES if FEATURE_SCHEMA[n]['type'] == 'bool')
    cont_count = len(FEATURE_NAMES) - bool_count

    info = [
        ("Total rows", str(len(raw))),
        ("Features", f"{len(FEATURE_NAMES)} (continuous: {cont_count}, boolean: {bool_count})"),
        ("UX dimension",        f"{sum(1 for n in FEATURE_NAMES if FEATURE_SCHEMA[n]['dim']=='ux')} features"),
        ("Content dimension",   f"{sum(1 for n in FEATURE_NAMES if FEATURE_SCHEMA[n]['dim']=='content')} features"),
        ("Technical dimension", f"{sum(1 for n in FEATURE_NAMES if FEATURE_SCHEMA[n]['dim']=='technical')} features"),
        ("Trust dimension",     f"{sum(1 for n in FEATURE_NAMES if FEATURE_SCHEMA[n]['dim']=='trust')} features"),
        ("Labels", "score_ux, score_content, score_technical, score_trust (0-25 each) + score_total (0-100)"),
        ("NaN cells in feature matrix", f"{int(X.isna().sum().sum())} / {len(X) * len(FEATURE_NAMES)} ({X.isna().sum().sum() / (len(X) * len(FEATURE_NAMES)) * 100:.2f}%)"),
    ]
    story.append(kv_table([(k, v) for k, v in info]))


def build_target(story: list, styles: dict, raw: pd.DataFrame) -> None:
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("2. Target Distribution &amp; Tier Breakdown", styles["h1"]))

    y = raw["score_total"].dropna()
    stats = [
        ("Mean", f"{y.mean():.2f}"),
        ("Median", f"{y.median():.2f}"),
        ("Std", f"{y.std():.2f}"),
        ("Min / Max", f"{y.min():.2f} / {y.max():.2f}"),
        ("Skewness", f"{y.skew():.3f}"),
        ("Kurtosis", f"{y.kurt():.3f}"),
    ]
    story.append(kv_table([(k, v) for k, v in stats]))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Tier counts", styles["h2"]))
    tier_counts = tier_breakdown(raw)
    total = int(tier_counts.sum())
    tier_rows = [[label, str(int(count)), f"{count / total * 100:.1f}%"] for label, count in tier_counts.items()]
    story.append(data_table(["Tier", "Count", "Share"], tier_rows,
                            col_widths=[8 * cm, 3 * cm, 3 * cm]))

    sub = raw[SUBSCORE_COLS].describe().T[["mean", "std", "min", "max"]]
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Sub-score statistics", styles["h2"]))
    sub_rows = [[idx, f"{r['mean']:.2f}", f"{r['std']:.2f}", f"{r['min']:.2f}", f"{r['max']:.2f}"]
                for idx, r in sub.iterrows()]
    story.append(data_table(["Sub-score", "Mean", "Std", "Min", "Max"], sub_rows,
                            col_widths=[5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm, 2.5 * cm]))


def build_missing(story: list, styles: dict, missing: pd.Series) -> None:
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("3. Missing-Value Analysis", styles["h1"]))
    nz = missing[missing > 0]
    if nz.empty:
        story.append(Paragraph("No missing values in any feature.", styles["body"]))
        return
    story.append(Paragraph(
        f"{len(nz)} of {len(missing)} columns have missing values. "
        "PageSpeed columns dominate (crawled without API key).",
        styles["body"]
    ))
    rows = [[name, FEATURE_SCHEMA[name]["dim"], f"{pct:.1f}%"] for name, pct in nz.items()]
    story.append(data_table(["Feature", "Dimension", "% Missing"], rows,
                            col_widths=[8 * cm, 4 * cm, 3 * cm], dim_col=1))


def build_predictors(story: list, styles: dict, corr_target: pd.DataFrame) -> None:
    story.append(PageBreak())
    story.append(Paragraph("4. Top Predictive Features", styles["h1"]))
    story.append(Paragraph(
        "Features sorted by absolute Pearson correlation with <b>score_total</b>. "
        "These are the strongest linear signals; tree models like XGBoost can also "
        "exploit nonlinear interactions invisible here.",
        styles["body"]
    ))
    top = corr_target.head(20)
    rows = [
        [f"{i + 1}", row["feature"], row["dim"],
         f"{row['pearson_r']:+.3f}", f"{row['spearman_r']:+.3f}"]
        for i, (_, row) in enumerate(top.iterrows())
    ]
    story.append(data_table(
        ["#", "Feature", "Dim", "Pearson r", "Spearman r"], rows,
        col_widths=[1 * cm, 7 * cm, 2.5 * cm, 3 * cm, 3 * cm], dim_col=2,
    ))


def build_collinearity_constants(story: list, styles: dict, pairs: pd.DataFrame, constants: list[str]) -> None:
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("5. Multicollinearity &amp; Constant Features", styles["h1"]))

    story.append(Paragraph("Feature pairs with |r| ≥ 0.85", styles["h2"]))
    if pairs.empty:
        story.append(Paragraph("None detected.", styles["body"]))
    else:
        rows = [[r.feature_a, r.feature_b, r.dim_a, r.dim_b, f"{r.pearson_r:+.3f}"]
                for r in pairs.itertuples()]
        story.append(data_table(
            ["Feature A", "Feature B", "Dim A", "Dim B", "Pearson r"], rows,
            col_widths=[5 * cm, 5 * cm, 2 * cm, 2 * cm, 2.5 * cm],
        ))

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("Constant / near-constant features", styles["h2"]))
    if not constants:
        story.append(Paragraph("None detected.", styles["body"]))
    else:
        story.append(Paragraph(
            "These features have ≥95% of values concentrated in a single bucket "
            "(or near-zero variance). Drop before training.",
            styles["body"]
        ))
        rows = [[name, FEATURE_SCHEMA[name]["dim"]] for name in constants]
        story.append(data_table(["Feature", "Dimension"], rows,
                                col_widths=[8 * cm, 6 * cm], dim_col=1))


def build_skew_outliers(story: list, styles: dict, skew: pd.Series, outliers: pd.Series) -> None:
    story.append(PageBreak())
    story.append(Paragraph("6. Skewness &amp; Outliers", styles["h1"]))

    story.append(Paragraph("Features with |skew| > 1 (log1p transform candidates)", styles["h2"]))
    high_skew = skew[skew.abs() > 1]
    if high_skew.empty:
        story.append(Paragraph("No feature has |skew| > 1.", styles["body"]))
    else:
        rows = [[name, FEATURE_SCHEMA[name]["dim"], f"{val:+.2f}"] for name, val in high_skew.items()]
        story.append(data_table(["Feature", "Dim", "Skew"], rows,
                                col_widths=[8 * cm, 3 * cm, 3 * cm], dim_col=1))

    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("Top 15 features by IQR outlier count", styles["h2"]))
    rows = [[name, FEATURE_SCHEMA[name]["dim"], str(int(count))]
            for name, count in outliers.head(15).items()]
    story.append(data_table(["Feature", "Dim", "Outlier count"], rows,
                            col_widths=[8 * cm, 3 * cm, 3 * cm], dim_col=1))


def build_subscore_corr(story: list, styles: dict, raw: pd.DataFrame) -> None:
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph("7. Sub-Score Inter-Correlation", styles["h1"]))
    story.append(Paragraph(
        "Off-diagonal Pearson r between the four dimension labels. Low values "
        "indicate the four sub-scores carry independent information — desirable for "
        "decomposing the composite score.",
        styles["body"]
    ))
    sc = raw[SUBSCORE_COLS].corr()
    header = [""] + SUBSCORE_COLS
    rows = [[col] + [f"{sc.loc[col, c]:+.2f}" for c in SUBSCORE_COLS] for col in SUBSCORE_COLS]
    story.append(data_table(header, rows,
                            col_widths=[4 * cm] + [3 * cm] * 4))


def build_recommendations(
    story: list, styles: dict,
    missing: pd.Series, skew: pd.Series, pairs: pd.DataFrame,
    constants: list[str], tier_counts: pd.Series,
) -> None:
    story.append(PageBreak())
    story.append(Paragraph("8. Preprocessing Recommendations", styles["h1"]))

    items: list[str] = []
    # Missing values
    pagespeed_cols = [n for n in FEATURE_NAMES if n.startswith("tech_pagespeed") or n in (
        "tech_lcp_seconds", "tech_cls", "tech_tbt_seconds")]
    ps_missing = missing.reindex(pagespeed_cols).dropna()
    if (ps_missing > 30).any():
        bad = ps_missing[ps_missing > 30]
        items.append(
            f"<b>Missing values.</b> PageSpeed columns are &gt;30% missing "
            f"({', '.join(f'{c} ({ps_missing[c]:.0f}%)' for c in bad.index)}). "
            f"<b>Action:</b> keep as NaN — XGBoost handles missing natively. If switching "
            f"to a non-tree model, apply median imputation per column."
        )
    else:
        items.append("<b>Missing values.</b> No column exceeds 30% missing — light imputation acceptable.")

    high_skew = skew[skew.abs() > 1]
    if len(high_skew):
        items.append(
            f"<b>Skew correction.</b> {len(high_skew)} continuous features have |skew| &gt; 1. "
            f"<b>Action:</b> apply <font face='Courier'>np.log1p</font> before training "
            f"(particularly: {', '.join(f'<font face=Courier>{n}</font>' for n in list(high_skew.index[:5]))}…)."
        )
    else:
        items.append("<b>Skew correction.</b> No feature has |skew| &gt; 1.")

    cross = pairs[pairs["dim_a"] != pairs["dim_b"]] if not pairs.empty else pairs
    if pairs.empty:
        items.append("<b>Multicollinearity.</b> No pair exceeds |r| &gt; 0.85 — keep all features.")
    else:
        same_dim = pairs[pairs["dim_a"] == pairs["dim_b"]]
        msg_parts = []
        if not same_dim.empty:
            ex = same_dim.iloc[0]
            msg_parts.append(
                f"within-dimension: <font face='Courier'>{ex['feature_a']}</font> ↔ "
                f"<font face='Courier'>{ex['feature_b']}</font> (r={ex['pearson_r']:+.2f}) → drop one"
            )
        if not cross.empty:
            msg_parts.append(f"{len(cross)} cross-dimension pair(s) flagged")
        items.append("<b>Multicollinearity.</b> " + "; ".join(msg_parts) + ".")

    if constants:
        items.append(
            "<b>Constant / near-constant features.</b> Drop before training: "
            + ", ".join(f"<font face='Courier'>{c}</font>" for c in constants) + "."
        )
    else:
        items.append("<b>Constant / near-constant features.</b> None detected.")

    tier_share = tier_counts / tier_counts.sum()
    imbalanced = tier_share[tier_share < 0.10]
    if not imbalanced.empty:
        items.append(
            f"<b>Class imbalance.</b> {', '.join(imbalanced.index)} tiers hold &lt;10% of samples. "
            f"<b>Action:</b> stratify train/test split on tier label and use stratified k-fold CV."
        )
    else:
        items.append("<b>Class imbalance.</b> Tier shares are balanced — random split acceptable.")

    items.append(
        "<b>Scaling.</b> Continuous features → StandardScaler; booleans → passthrough. "
        "XGBoost is scale-invariant, so this is optional for the deployed model but required "
        "if benchmarking against linear models or k-NN."
    )

    items.append(
        "<b>Train/test protocol.</b> 80/20 split with <font face='Courier'>stratify=tier</font>; "
        "5-fold stratified CV for hyperparameter tuning. Hold out final 20% only for end-of-project metrics."
    )

    for item in items:
        story.append(Paragraph(f"• {item}", styles["bullet"]))
        story.append(Spacer(1, 0.15 * cm))


def build_figure_appendix(story: list, styles: dict) -> None:
    story.append(PageBreak())
    story.append(Paragraph("9. Figure Appendix", styles["h1"]))
    story.append(Paragraph(
        "All 14 figures generated by <font face='Courier'>scripts/eda.py</font>. "
        "Source PNGs live in <font face='Courier'>data/eda/figures/</font>.",
        styles["body"]
    ))

    captions: dict[str, str] = {
        "01_target_total_distribution.png":     "Figure 1 — Distribution of score_total. The narrow [16.6, 71.0] range and slight left-skew (skew=−0.20) indicate no website in the dataset reached the Excellent tier.",
        "02_subscore_distributions.png":        "Figure 2 — Sub-score distributions per dimension. Technical and Trust sub-scores cluster lower (median ≈ 10–14) while UX and Content span more of the 0–25 range.",
        "03_tier_pie.png":                      "Figure 3 — Tier breakdown. Average (62.4%) dominates, Good (32.6%) is solid, but Poor (5.0%) is sparse and Excellent (0%) is absent — class imbalance to address via stratified splitting.",
        "04_missing_values.png":                "Figure 4 — % missing per feature. Five PageSpeed columns dominate (~55% each) due to crawling without a Google API key; all other features are complete.",
        "05a_ux_feature_distributions.png":    "Figure 5a — UX feature distributions. Most CTA/link counts are zero-heavy; viewport_meta and responsive_breakpoints are degenerate.",
        "05b_content_feature_distributions.png":"Figure 5b — Content features. Word counts and readability are roughly bell-shaped; h1_count and h1_unique skew toward zero.",
        "05c_technical_feature_distributions.png":"Figure 5c — Technical features. PageSpeed and Core Web Vitals are sparse (NaN-heavy). HTTPS and external_js_count are near-constant.",
        "05d_trust_feature_distributions.png": "Figure 5d — Trust features. Most booleans skew False; address_visible is near-constant (almost always missing/false).",
        "06_boolean_feature_counts.png":       "Figure 6 — True / False / NaN counts for every boolean feature. Reveals which boolean signals carry usable variance vs. degenerate.",
        "07_correlation_heatmap.png":          "Figure 7 — Full feature × feature correlation matrix. Block structure within each dimension is visible; one perfect anti-correlation (flesch_reading_ease vs. flesch_kincaid_grade).",
        "08_feature_target_correlation.png":   "Figure 8 — Each feature's Pearson r with score_total, sorted by magnitude, colored by dimension. content_heading_hierarchy_score and content_h1_unique lead.",
        "09_top_features_scatter.png":         "Figure 9 — Scatter plots of the top-6 most-correlated features against score_total with regression lines.",
        "10_boxplots_continuous.png":          "Figure 10 — Z-scored boxplots of all continuous features. Outliers are visible as points beyond whiskers; high-skew features (e.g., page_size_kb, word_count) dominate.",
        "11_subscore_pairplot.png":            "Figure 11 — Pairwise relationships among the four sub-scores. Content↔Trust is the strongest (r=0.45); Technical is largely independent.",
        "12_skewness_bars.png":                "Figure 12 — Skewness per continuous feature. Red bars (|skew| > 1) are log-transform candidates; 22 features qualify.",
        "13_pca_scatter.png":                  "Figure 13 — 2D PCA projection of features, colored by score_total. Gradient along PC1 confirms the feature space carries a meaningful score signal.",
        "14_score_total_by_boolean.png":       "Figure 14 — score_total stratified by each boolean feature (True vs. False). Boolean features where the green box sits clearly above the red one contribute strong positive signal.",
    }

    figures = sorted(FIG_DIR.glob("*.png"))
    if not figures:
        story.append(Paragraph("<i>No figures found — run scripts/eda.py first.</i>", styles["body"]))
        return

    # Page geometry: A4 minus header (1.4cm), footer (1.6cm), and side margins (2cm each)
    page_w, page_h = A4
    usable_w = page_w - 4 * cm
    usable_h = page_h - 1.4 * cm - 1.6 * cm - 2.5 * cm  # leave room for caption

    for path in figures:
        title = path.stem.replace("_", " ")
        caption = captions.get(path.name, "")
        block = [
            Paragraph(f"<b>{title}</b>", styles["h2"]),
            fit_image(path, usable_w, usable_h),
        ]
        if caption:
            block.append(Paragraph(caption, styles["caption"]))
        story.append(KeepTogether(block))
        story.append(PageBreak())


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main() -> None:
    if not FIG_DIR.exists() or not any(FIG_DIR.glob("*.png")):
        sys.exit("ERROR: no figures found in data/eda/figures/. Run `python scripts/eda.py` first.")

    print(f"Loading {DATA_PATH.relative_to(ROOT)} ...")
    raw, X = load_dataset()

    print("Computing analysis tables ...")
    tier_counts = tier_breakdown(raw)
    missing = missing_pct(X)
    corr_target = feature_target_corr(X, raw)
    pairs = high_corr_pairs(X)
    skew = skewness_table(X)
    outliers = outlier_counts(X)
    constants = near_constant(X)

    print(f"Building PDF -> {PDF_PATH.relative_to(ROOT)} ...")
    doc = SimpleDocTemplate(
        str(PDF_PATH),
        pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=1.8 * cm, bottomMargin=1.8 * cm,
        title="Website Quality Scorer — EDA Report",
        author="Aleem Ul Hassan / NexusPoint",
    )
    styles = make_styles()
    story: list = []

    build_cover(story, styles, raw)
    build_overview(story, styles, raw, X)
    build_target(story, styles, raw)
    build_missing(story, styles, missing)
    build_predictors(story, styles, corr_target)
    build_collinearity_constants(story, styles, pairs, constants)
    build_skew_outliers(story, styles, skew, outliers)
    build_subscore_corr(story, styles, raw)
    build_recommendations(story, styles, missing, skew, pairs, constants, tier_counts)
    build_figure_appendix(story, styles)

    doc.build(story, onFirstPage=header_footer, onLaterPages=header_footer)
    size_kb = PDF_PATH.stat().st_size / 1024
    print(f"Done. {PDF_PATH.relative_to(ROOT)} ({size_kb:.1f} KB)")


if __name__ == "__main__":
    main()
