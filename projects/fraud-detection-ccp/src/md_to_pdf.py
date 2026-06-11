"""
Convert report/report.md to report/report.pdf using ReportLab.

Adapted from projects/kalman-filter-assignment/md_to_pdf.py with added support
for embedding images ( ![alt](path) ) so result figures appear inline.

Handles: H1/H2/H3 headings, paragraphs, bullet/numbered lists, inline code,
code blocks, tables, bold/italic, horizontal rules, and images.
"""

import re
import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    Table, TableStyle, HRFlowable, ListFlowable, ListItem, Image,
)
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.utils import ImageReader

# ----------------------------------------------------------------
# Paths
# ----------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))          # src/
PROJECT_ROOT = os.path.dirname(BASE)
INPUT = os.path.join(PROJECT_ROOT, "report", "report.md")
OUTPUT = os.path.join(PROJECT_ROOT, "report", "report.pdf")

with open(INPUT, encoding="utf-8") as f:
    raw = f.read()

# ----------------------------------------------------------------
# Styles
# ----------------------------------------------------------------
PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm
AVAIL_W = PAGE_W - 2 * MARGIN

styles = getSampleStyleSheet()


def make_style(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=styles[parent], **kw)
    if name not in styles:
        styles.add(s)
    return s


H1 = make_style("H1", fontSize=19, spaceAfter=8, spaceBefore=16, leading=24,
                textColor=colors.HexColor("#1a237e"), fontName="Helvetica-Bold",
                alignment=TA_CENTER)
H2 = make_style("H2", fontSize=14, spaceAfter=6, spaceBefore=14, leading=19,
                textColor=colors.HexColor("#283593"), fontName="Helvetica-Bold")
H3 = make_style("H3", fontSize=11.5, spaceAfter=4, spaceBefore=10, leading=15,
                textColor=colors.HexColor("#3949ab"), fontName="Helvetica-BoldOblique")
BODY = make_style("Body", fontSize=10, spaceAfter=5, spaceBefore=2, leading=15,
                  alignment=TA_JUSTIFY)
CAPTION = make_style("Caption", fontSize=8.5, spaceAfter=8, spaceBefore=2, leading=11,
                     textColor=colors.HexColor("#616161"), alignment=TA_CENTER,
                     fontName="Helvetica-Oblique")
CODE_BLOCK = ParagraphStyle("CodeBlock", fontName="Courier", fontSize=8.5, leading=12,
                            leftIndent=10, rightIndent=10, spaceAfter=6, spaceBefore=6,
                            backColor=colors.HexColor("#f5f5f5"),
                            textColor=colors.HexColor("#212121"))
BULLET = make_style("Bullet", parent="Body", leftIndent=18, spaceAfter=3)
NUM = make_style("Num", parent="Body", leftIndent=18, spaceAfter=3)
TABLE_HEADER = ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, leading=11,
                              textColor=colors.white)
TABLE_CELL = ParagraphStyle("TD", fontName="Helvetica", fontSize=8.5, leading=11)


# ----------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------
def inline(text):
    text = re.sub(r"`([^`]+)`", r'<font name="Courier" color="#c0392b">\1</font>', text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text


def make_image(path, alt=""):
    """Return [Image, Caption] flowables scaled to page width."""
    abs_path = path
    if not os.path.isabs(abs_path):
        abs_path = os.path.join(PROJECT_ROOT, path)
        if not os.path.exists(abs_path):
            abs_path = os.path.join(PROJECT_ROOT, "report", path)
    if not os.path.exists(abs_path):
        return [Paragraph(f"[missing image: {path}]", CAPTION)]
    iw, ih = ImageReader(abs_path).getSize()
    max_w = AVAIL_W
    max_h = 11 * cm
    ratio = min(max_w / iw, max_h / ih)
    w, h = iw * ratio, ih * ratio
    flow = [Spacer(1, 4), Image(abs_path, width=w, height=h, hAlign="CENTER")]
    if alt:
        flow.append(Paragraph(inline(alt), CAPTION))
    else:
        flow.append(Spacer(1, 6))
    return flow


def parse_table(block_lines):
    rows = []
    for line in block_lines:
        line = line.strip()
        if re.match(r"^[|\s\-:]+$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    if not rows:
        return None
    col_count = max(len(r) for r in rows)
    rows = [r + [""] * (col_count - len(r)) for r in rows]
    col_w = AVAIL_W / col_count
    tdata = []
    for i, row in enumerate(rows):
        style = TABLE_HEADER if i == 0 else TABLE_CELL
        tdata.append([Paragraph(inline(c), style) for c in row])
    ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3949ab")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f7ff"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c5cae9")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])
    return Table(tdata, colWidths=[col_w] * col_count, style=ts, hAlign="LEFT", repeatRows=1)


# ----------------------------------------------------------------
# Main parser
# ----------------------------------------------------------------
def parse_md(text):
    story = []
    lines = text.splitlines()
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]

        if line.startswith("# ") and not line.startswith("## "):
            story.append(Paragraph(inline(line[2:].strip()), H1))
            story.append(HRFlowable(width="100%", thickness=1.5,
                                    color=colors.HexColor("#3949ab"), spaceAfter=8))
            i += 1
            continue
        if line.startswith("## ") and not line.startswith("### "):
            story.append(Spacer(1, 4))
            story.append(Paragraph(inline(line[3:].strip()), H2))
            story.append(HRFlowable(width="100%", thickness=0.8,
                                    color=colors.HexColor("#c5cae9"), spaceAfter=4))
            i += 1
            continue
        if line.startswith("### "):
            story.append(Paragraph(inline(line[4:].strip()), H3))
            i += 1
            continue
        if re.match(r"^-{3,}$", line.strip()) or re.match(r"^_{3,}$", line.strip()):
            story.append(HRFlowable(width="100%", thickness=0.6,
                                    color=colors.HexColor("#9e9e9e"),
                                    spaceAfter=6, spaceBefore=6))
            i += 1
            continue
        # standalone image line:  ![alt](path)
        m_img = re.match(r"^\s*!\[(.*?)\]\((.*?)\)\s*$", line)
        if m_img:
            alt, path = m_img.group(1), m_img.group(2)
            for fl in make_image(path, alt):
                story.append(fl)
            i += 1
            continue
        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1
            story.append(Preformatted("\n".join(code_lines), CODE_BLOCK, maxLineLength=90))
            story.append(Spacer(1, 4))
            continue
        if line.startswith("|"):
            table_lines = []
            while i < n and lines[i].startswith("|"):
                table_lines.append(lines[i])
                i += 1
            tbl = parse_table(table_lines)
            if tbl:
                story.append(tbl)
                story.append(Spacer(1, 6))
            continue
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                txt = re.sub(r"^\s*[-*]\s+", "", lines[i])
                items.append(ListItem(Paragraph(inline(txt), BULLET), leftIndent=22,
                                      bulletColor=colors.HexColor("#3949ab")))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", bulletFontSize=8,
                                      start="-", leftIndent=10))
            story.append(Spacer(1, 3))
            continue
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                txt = re.sub(r"^\s*\d+\.\s+", "", lines[i])
                items.append(ListItem(Paragraph(inline(txt), NUM), leftIndent=22))
                i += 1
            story.append(ListFlowable(items, bulletType="1", leftIndent=10))
            story.append(Spacer(1, 3))
            continue
        if line.strip() == "":
            story.append(Spacer(1, 4))
            i += 1
            continue
        # paragraph (collect continuation lines)
        para_lines = [line]
        i += 1
        while i < n and lines[i].strip() != "" \
                and not lines[i].startswith("#") and not lines[i].startswith("|") \
                and not lines[i].strip().startswith("```") \
                and not re.match(r"^\s*[-*]\s+", lines[i]) \
                and not re.match(r"^\s*\d+\.\s+", lines[i]) \
                and not re.match(r"^\s*!\[", lines[i]) \
                and not re.match(r"^[-_]{3,}$", lines[i].strip()):
            para_lines.append(lines[i])
            i += 1
        story.append(Paragraph(inline(" ".join(para_lines)), BODY))
    return story


# ----------------------------------------------------------------
# Build PDF
# ----------------------------------------------------------------
def build():
    doc = SimpleDocTemplate(
        OUTPUT, pagesize=A4,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN,
        title="AI-Driven Financial Fraud Detection - CCP Report",
        author="Aleem Ul Hassan",
    )
    doc.build(parse_md(raw))
    print(f"PDF saved to: {OUTPUT}")


if __name__ == "__main__":
    build()
