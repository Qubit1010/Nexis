"""Convert nexis-catalog.md to nexis-catalog.pdf using ReportLab."""
import re, os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    Table, TableStyle, HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_JUSTIFY, TA_CENTER

BASE = os.path.dirname(os.path.abspath(__file__))
INPUT = os.path.join(BASE, "nexis-catalog.md")
OUTPUT = os.path.join(BASE, "nexis-catalog.pdf")

with open(INPUT, encoding="utf-8") as f:
    raw = f.read()

PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm
styles = getSampleStyleSheet()

def make_style(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=styles[parent], **kw)
    if name not in styles:
        styles.add(s)
    return s

H1 = make_style("H1", fontSize=20, spaceAfter=8, spaceBefore=14, leading=25,
                textColor=colors.HexColor("#1a237e"), fontName="Helvetica-Bold", alignment=TA_CENTER)
H2 = make_style("H2", fontSize=15, spaceAfter=6, spaceBefore=16, leading=20,
                textColor=colors.HexColor("#283593"), fontName="Helvetica-Bold")
H3 = make_style("H3", fontSize=11.5, spaceAfter=3, spaceBefore=10, leading=15,
                textColor=colors.HexColor("#3949ab"), fontName="Helvetica-Bold")
BODY = make_style("Body", fontSize=9.5, spaceAfter=4, spaceBefore=1, leading=14, alignment=TA_JUSTIFY)
CODE_BLOCK = ParagraphStyle("CodeBlock", fontName="Courier", fontSize=8, leading=11,
                            leftIndent=8, rightIndent=8, spaceAfter=6, spaceBefore=6,
                            backColor=colors.HexColor("#f5f5f5"), textColor=colors.HexColor("#212121"))
BULLET = make_style("Bullet", parent="Body", leftIndent=16, spaceAfter=2)
NUM = make_style("Num", parent="Body", leftIndent=16, spaceAfter=2)
TABLE_HEADER = ParagraphStyle("TH", fontName="Helvetica-Bold", fontSize=8.5, leading=11, textColor=colors.white)
TABLE_CELL = ParagraphStyle("TD", fontName="Helvetica", fontSize=8.5, leading=11)

def inline(text):
    text = text.replace("&", "&amp;")
    text = re.sub(r"`([^`]+)`", lambda m: '<font name="Courier" color="#c0392b">%s</font>' % m.group(1), text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<i>\1</i>", text)
    return text

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
    avail_w = PAGE_W - 2 * MARGIN
    col_w = avail_w / col_count
    tdata = []
    for i, row in enumerate(rows):
        style = TABLE_HEADER if i == 0 else TABLE_CELL
        tdata.append([Paragraph(inline(c), style) for c in row])
    ts = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3949ab")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f5f7ff"), colors.white]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#c5cae9")),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ])
    return Table(tdata, colWidths=[col_w] * col_count, style=ts, hAlign="LEFT", repeatRows=1)

def parse_md(text):
    story = []
    lines = text.splitlines()
    i, n = 0, len(text.splitlines())
    while i < n:
        line = lines[i]
        if line.startswith("# ") and not line.startswith("## "):
            story.append(Paragraph(inline(line[2:].strip()), H1))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#3949ab"), spaceAfter=8))
            i += 1; continue
        if line.startswith("## ") and not line.startswith("### "):
            story.append(Spacer(1, 4))
            story.append(Paragraph(inline(line[3:].strip()), H2))
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor("#c5cae9"), spaceAfter=4))
            i += 1; continue
        if line.startswith("### "):
            story.append(Paragraph(inline(line[4:].strip()), H3))
            i += 1; continue
        if re.match(r"^-{3,}$", line.strip()) or re.match(r"^_{3,}$", line.strip()):
            story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#9e9e9e"), spaceAfter=6, spaceBefore=6))
            i += 1; continue
        if line.strip().startswith("```"):
            code_lines = []; i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code_lines.append(lines[i]); i += 1
            i += 1
            story.append(Preformatted("\n".join(code_lines), CODE_BLOCK, maxLineLength=95))
            story.append(Spacer(1, 4)); continue
        if line.startswith("|"):
            table_lines = []
            while i < n and lines[i].startswith("|"):
                table_lines.append(lines[i]); i += 1
            tbl = parse_table(table_lines)
            if tbl:
                story.append(tbl); story.append(Spacer(1, 6))
            continue
        if re.match(r"^\s*[-*]\s+", line):
            items = []
            while i < n and re.match(r"^\s*[-*]\s+", lines[i]):
                txt = re.sub(r"^\s*[-*]\s+", "", lines[i])
                items.append(ListItem(Paragraph(inline(txt), BULLET), leftIndent=20, bulletColor=colors.HexColor("#3949ab")))
                i += 1
            story.append(ListFlowable(items, bulletType="bullet", bulletFontSize=7, start="-", leftIndent=8))
            story.append(Spacer(1, 3)); continue
        if re.match(r"^\s*\d+\.\s+", line):
            items = []
            while i < n and re.match(r"^\s*\d+\.\s+", lines[i]):
                txt = re.sub(r"^\s*\d+\.\s+", "", lines[i])
                items.append(ListItem(Paragraph(inline(txt), NUM), leftIndent=20))
                i += 1
            story.append(ListFlowable(items, bulletType="1", leftIndent=8))
            story.append(Spacer(1, 3)); continue
        if line.strip() == "":
            story.append(Spacer(1, 4)); i += 1; continue
        para_lines = [line]; i += 1
        while i < n and lines[i].strip() != "" \
              and not lines[i].startswith("#") and not lines[i].startswith("|") \
              and not lines[i].strip().startswith("```") \
              and not re.match(r"^\s*[-*]\s+", lines[i]) \
              and not re.match(r"^\s*\d+\.\s+", lines[i]) \
              and not re.match(r"^[-_]{3,}$", lines[i].strip()):
            para_lines.append(lines[i]); i += 1
        para = " ".join(para_lines)
        if re.match(r"^\s*!\[", para):
            continue
        story.append(Paragraph(inline(para), BODY))
    return story

doc = SimpleDocTemplate(OUTPUT, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                        topMargin=MARGIN, bottomMargin=MARGIN,
                        title="NexusPoint Skills & Projects Catalog", author="Aleem Ul Hassan")
doc.build(parse_md(raw))
print("PDF saved to:", OUTPUT)
