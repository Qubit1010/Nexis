"""
Convert report.md to report.pdf using ReportLab.
Handles: H1/H2/H3 headings, paragraphs, bullet lists, numbered lists,
         inline code, code blocks, tables, bold/italic text, horizontal rules.
"""

import re
import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    Table, TableStyle, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

# ----------------------------------------------------------------
# Source / output paths
# ----------------------------------------------------------------
BASE = os.path.dirname(os.path.abspath(__file__))
# Optional CLI args: python md_to_pdf.py [input.md] [output.pdf]
INPUT  = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "report.md")
if len(sys.argv) > 2:
    OUTPUT = sys.argv[2]
else:
    OUTPUT = os.path.splitext(INPUT)[0] + ".pdf"

# ----------------------------------------------------------------
# Read markdown
# ----------------------------------------------------------------
with open(INPUT, encoding="utf-8") as f:
    raw = f.read()

# ----------------------------------------------------------------
# Styles
# ----------------------------------------------------------------
PAGE_W, PAGE_H = A4
MARGIN = 2.2 * cm

styles = getSampleStyleSheet()

def make_style(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=styles[parent], **kw)
    if name not in styles:
        styles.add(s)
    return s

H1 = make_style("H1", fontSize=20, spaceAfter=8, spaceBefore=16,
                leading=26, textColor=colors.HexColor("#1a237e"),
                fontName="Helvetica-Bold", alignment=TA_CENTER)

H2 = make_style("H2", fontSize=15, spaceAfter=6, spaceBefore=14,
                leading=20, textColor=colors.HexColor("#283593"),
                fontName="Helvetica-Bold",
                borderPad=2, borderColor=colors.HexColor("#7986cb"),
                borderWidth=0, leftIndent=0)

H3 = make_style("H3", fontSize=12, spaceAfter=4, spaceBefore=10,
                leading=16, textColor=colors.HexColor("#3949ab"),
                fontName="Helvetica-BoldOblique")

BODY = make_style("Body", fontSize=10, spaceAfter=5, spaceBefore=2,
                  leading=15, alignment=TA_JUSTIFY)

CODE_BLOCK = ParagraphStyle("CodeBlock", fontName="Courier", fontSize=8.5,
                             leading=12, leftIndent=10, rightIndent=10,
                             spaceAfter=6, spaceBefore=6,
                             backColor=colors.HexColor("#f5f5f5"),
                             textColor=colors.HexColor("#212121"))

BULLET = make_style("Bullet", parent="Body", leftIndent=18, spaceAfter=3)
NUM    = make_style("Num",    parent="Body", leftIndent=18, spaceAfter=3)

TABLE_HEADER = ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=9,
                               leading=12, textColor=colors.white)
TABLE_CELL   = ParagraphStyle("TD", fontName="Helvetica", fontSize=9,
                               leading=12)

# ----------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------
def inline(text):
    """Convert inline markdown (bold, italic, inline code) to RL markup."""
    # inline code  `...`
    text = re.sub(r"`([^`]+)`",
                  r'<font name="Courier" color="#c0392b">\1</font>', text)
    # bold **...**
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    # italic *...*  (not inside **)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    # escape lone &, <, > that aren't our tags
    # (do a minimal pass — angle brackets inside our tags are already gone)
    return text


def parse_table(block_lines):
    """Parse a markdown table block into a ReportLab Table flowable."""
    rows = []
    for line in block_lines:
        line = line.strip()
        if re.match(r"^[|\s\-:]+$", line):   # separator row
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)

    if not rows:
        return None

    col_count = max(len(r) for r in rows)
    # normalise row widths
    rows = [r + [""] * (col_count - len(r)) for r in rows]

    avail_w = PAGE_W - 2 * MARGIN
    col_w = avail_w / col_count

    tdata = []
    for i, row in enumerate(rows):
        style = TABLE_HEADER if i == 0 else TABLE_CELL
        tdata.append([Paragraph(inline(c), style) for c in row])

    ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3949ab")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1),
         [colors.HexColor("#f5f7ff"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c5cae9")),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 6),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])

    return Table(tdata, colWidths=[col_w] * col_count, style=ts,
                 hAlign="LEFT", repeatRows=1)


# ----------------------------------------------------------------
# Main parser  ->  list of Flowables
# ----------------------------------------------------------------
def parse_md(text):
    story = []
    lines = text.splitlines()
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]

        # --- H1
        if line.startswith("# ") and not line.startswith("## "):
            story.append(Paragraph(inline(line[2:].strip()), H1))
            story.append(HRFlowable(width="100%", thickness=1.5,
                                    color=colors.HexColor("#3949ab"),
                                    spaceAfter=8))
            i += 1
            continue

        # --- H2
        if line.startswith("## ") and not line.startswith("### "):
            story.append(Spacer(1, 4))
            story.append(Paragraph(inline(line[3:].strip()), H2))
            story.append(HRFlowable(width="100%", thickness=0.8,
                                    color=colors.HexColor("#c5cae9"),
                                    spaceAfter=4))
            i += 1
            continue

        # --- H3
        if line.startswith("### "):
            story.append(Paragraph(inline(line[4:].strip()), H3))
            i += 1
            continue

        # --- HR  ---
        if re.match(r"^-{3,}$", line.strip()) or re.match(r"^_{3,}$", line.strip()):
            story.append(HRFlowable(width="100%", thickness=0.6,
                                    color=colors.HexColor("#9e9e9e"),
                                    spaceAfter=6, spaceBefore=6))
            i += 1
            continue

        # --- Code block  ```
        if line.strip().startswith("```"):
            code_lines = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i])
                i += 1
            i += 1   # skip closing ```
            code_text = "\n".join(code_lines)
            story.append(Preformatted(code_text, CODE_BLOCK,
                                      maxLineLength=90))
            story.append(Spacer(1, 4))
            continue

        # --- Table block
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

        # --- Bullet list  -  or *
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                txt = re.sub(r"^\s*[-*]\s+", "", lines[i])
                items.append(ListItem(Paragraph(inline(txt), BULLET),
                                      leftIndent=22, bulletColor=colors.HexColor("#3949ab")))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet",
                                      bulletFontSize=8, start="-",
                                      leftIndent=10))
            story.append(Spacer(1, 3))
            continue

        # --- Numbered list  1.
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            idx = 1
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                txt = re.sub(r"^\s*\d+\.\s+", "", lines[i])
                items.append(ListItem(Paragraph(inline(txt), NUM),
                                      leftIndent=22))
                i += 1
                idx += 1
            story.append(ListFlowable(items, bulletType="1",
                                      leftIndent=10))
            story.append(Spacer(1, 3))
            continue

        # --- Blank line -> small spacer
        if line.strip() == "":
            story.append(Spacer(1, 4))
            i += 1
            continue

        # --- Normal paragraph (collect continuation lines)
        para_lines = [line]
        i += 1
        while i < n and lines[i].strip() != "" \
              and not lines[i].startswith("#") \
              and not lines[i].startswith("|") \
              and not lines[i].strip().startswith("```") \
              and not re.match(r"^\s*[-*]\s+", lines[i]) \
              and not re.match(r"^\s*\d+\.\s+", lines[i]) \
              and not re.match(r"^[-_]{3,}$", lines[i].strip()):
            para_lines.append(lines[i])
            i += 1
        para = " ".join(para_lines)
        # skip image references  ![...](...)
        if re.match(r"^\s*!\[", para):
            continue
        story.append(Paragraph(inline(para), BODY))

    return story


# ----------------------------------------------------------------
# Build PDF
# ----------------------------------------------------------------
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    leftMargin=MARGIN,
    rightMargin=MARGIN,
    topMargin=MARGIN,
    bottomMargin=MARGIN,
    title="Kalman Filter - Assignment 3",
    author="Aleem Ul Hassan",
)

story = parse_md(raw)
doc.build(story)
print(f"PDF saved to: {OUTPUT}")
