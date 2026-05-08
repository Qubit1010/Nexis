"""
PDF generator for client content packages.
Uses reportlab to produce a clean, professional PDF from the markdown content file.

Usage:
    python generate_pdf.py --input content.md --output content.pdf
"""

import argparse
import re
import sys
from pathlib import Path

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib.colors import HexColor, black, white
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
        PageBreak, Table, TableStyle
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
except ImportError:
    print("ERROR: reportlab not installed. Run: pip install reportlab", file=sys.stderr)
    sys.exit(1)


# --- Style constants ---
ACCENT = HexColor("#2C2C2C")
SUBTEXT = HexColor("#555555")
RULE_COLOR = HexColor("#CCCCCC")
PAGE_MARGIN = 2.2 * cm


def build_styles():
    base = getSampleStyleSheet()

    styles = {
        "title": ParagraphStyle(
            "title",
            fontName="Helvetica-Bold",
            fontSize=20,
            leading=26,
            textColor=ACCENT,
            spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "subtitle",
            fontName="Helvetica",
            fontSize=11,
            leading=15,
            textColor=SUBTEXT,
            spaceAfter=14,
        ),
        "h1": ParagraphStyle(
            "h1",
            fontName="Helvetica-Bold",
            fontSize=15,
            leading=20,
            textColor=ACCENT,
            spaceBefore=18,
            spaceAfter=6,
        ),
        "h2": ParagraphStyle(
            "h2",
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=16,
            textColor=ACCENT,
            spaceBefore=12,
            spaceAfter=4,
        ),
        "h3": ParagraphStyle(
            "h3",
            fontName="Helvetica-BoldOblique",
            fontSize=11,
            leading=15,
            textColor=SUBTEXT,
            spaceBefore=8,
            spaceAfter=3,
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=10,
            leading=15,
            textColor=black,
            spaceAfter=6,
        ),
        "bold_body": ParagraphStyle(
            "bold_body",
            fontName="Helvetica-Bold",
            fontSize=10,
            leading=15,
            textColor=black,
            spaceAfter=3,
        ),
        "blockquote": ParagraphStyle(
            "blockquote",
            fontName="Helvetica-Oblique",
            fontSize=10,
            leading=15,
            textColor=SUBTEXT,
            leftIndent=20,
            spaceAfter=6,
        ),
        "code": ParagraphStyle(
            "code",
            fontName="Courier",
            fontSize=9,
            leading=13,
            textColor=ACCENT,
            backColor=HexColor("#F5F5F5"),
            leftIndent=10,
            rightIndent=10,
            spaceAfter=6,
        ),
        "hashtag": ParagraphStyle(
            "hashtag",
            fontName="Courier",
            fontSize=9,
            leading=13,
            textColor=SUBTEXT,
            spaceAfter=6,
        ),
    }
    return styles


def sanitize(text):
    """Escape XML special chars for reportlab Paragraph."""
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    return text


def inline_format(text, styles):
    """Apply basic inline markdown: **bold**, *italic*, `code`."""
    text = sanitize(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`(.+?)`", r"<font name='Courier'>\1</font>", text)
    return text


def parse_markdown(md_text, styles):
    """Convert markdown text to a list of reportlab flowables."""
    flowables = []
    lines = md_text.split("\n")
    i = 0

    in_table = False
    table_rows = []
    in_code_block = False
    code_lines = []

    while i < len(lines):
        line = lines[i]

        # Code block fence
        if line.strip().startswith("```"):
            if in_code_block:
                # Close code block
                if code_lines:
                    code_text = "\n".join(code_lines)
                    flowables.append(Paragraph(sanitize(code_text).replace("\n", "<br/>"), styles["code"]))
                    flowables.append(Spacer(1, 4))
                code_lines = []
                in_code_block = False
            else:
                in_code_block = True
            i += 1
            continue

        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Table row detection
        if line.strip().startswith("|") and line.strip().endswith("|"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            # Skip separator rows (---|--- etc.)
            if all(re.match(r"^[-:]+$", c) for c in cells if c):
                i += 1
                continue
            table_rows.append(cells)
            i += 1
            continue
        else:
            # Flush table if we just finished one
            if table_rows:
                flowables.append(_build_table(table_rows, styles))
                flowables.append(Spacer(1, 6))
                table_rows = []

        stripped = line.strip()

        # Blank line
        if not stripped:
            flowables.append(Spacer(1, 5))
            i += 1
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            flowables.append(Spacer(1, 4))
            flowables.append(HRFlowable(width="100%", thickness=0.5, color=RULE_COLOR))
            flowables.append(Spacer(1, 4))
            i += 1
            continue

        # H1 (document title treated specially)
        if stripped.startswith("# ") and not stripped.startswith("## "):
            text = stripped[2:].strip()
            if not flowables:  # Very first heading = document title
                flowables.append(Paragraph(inline_format(text, styles), styles["title"]))
            else:
                flowables.append(Paragraph(inline_format(text, styles), styles["h1"]))
                flowables.append(HRFlowable(width="100%", thickness=0.5, color=RULE_COLOR))
                flowables.append(Spacer(1, 4))
            i += 1
            continue

        # H2
        if stripped.startswith("## "):
            text = stripped[3:].strip()
            flowables.append(Paragraph(inline_format(text, styles), styles["h2"]))
            i += 1
            continue

        # H3
        if stripped.startswith("### "):
            text = stripped[4:].strip()
            flowables.append(Paragraph(inline_format(text, styles), styles["h3"]))
            i += 1
            continue

        # Blockquote
        if stripped.startswith("> "):
            text = stripped[2:].strip()
            flowables.append(Paragraph(inline_format(text, styles), styles["blockquote"]))
            i += 1
            continue

        # Bullet list
        if stripped.startswith(("- ", "* ", "+ ")):
            text = stripped[2:].strip()
            flowables.append(Paragraph("• " + inline_format(text, styles), styles["body"]))
            i += 1
            continue

        # Numbered list
        if re.match(r"^\d+\.\s", stripped):
            text = re.sub(r"^\d+\.\s", "", stripped)
            flowables.append(Paragraph(inline_format(text, styles), styles["body"]))
            i += 1
            continue

        # Hashtag line
        if stripped.startswith("#") and " " not in stripped.split("#")[1][:1]:
            flowables.append(Paragraph(sanitize(stripped), styles["hashtag"]))
            i += 1
            continue

        # Bold-only line (slide heading style: **Heading:** text)
        if stripped.startswith("**") and "**" in stripped[2:]:
            flowables.append(Paragraph(inline_format(stripped, styles), styles["body"]))
            i += 1
            continue

        # Metadata lines (key: value at doc top)
        if re.match(r"^\*\*[^*]+:\*\*", stripped):
            flowables.append(Paragraph(inline_format(stripped, styles), styles["subtitle"]))
            i += 1
            continue

        # Regular paragraph
        flowables.append(Paragraph(inline_format(stripped, styles), styles["body"]))
        i += 1

    # Flush any remaining table
    if table_rows:
        flowables.append(_build_table(table_rows, styles))

    return flowables


def _build_table(rows, styles):
    if not rows:
        return Spacer(1, 1)

    data = []
    is_first = True
    for row in rows:
        formatted = [Paragraph(inline_format(cell, styles),
                               styles["bold_body"] if is_first else styles["body"])
                     for cell in row]
        data.append(formatted)
        is_first = False

    col_count = max(len(r) for r in data)
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HexColor("#F0F0F0")),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("GRID", (0, 0), (-1, -1), 0.4, RULE_COLOR),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [white, HexColor("#FAFAFA")]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def add_footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SUBTEXT)
    canvas.drawString(
        PAGE_MARGIN,
        1.2 * cm,
        f"Page {doc.page}  •  Prepared by NexusPoint"
    )
    canvas.restoreState()


def generate_pdf(input_path: str, output_path: str):
    md_text = Path(input_path).read_text(encoding="utf-8")
    styles = build_styles()
    flowables = parse_markdown(md_text, styles)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=PAGE_MARGIN,
        rightMargin=PAGE_MARGIN,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=Path(input_path).stem,
    )
    doc.build(flowables, onFirstPage=add_footer, onLaterPages=add_footer)
    print(f"PDF saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert markdown content package to PDF")
    parser.add_argument("--input", required=True, help="Path to input markdown file")
    parser.add_argument("--output", help="Path to output PDF (default: same name as input with .pdf)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    output_path = args.output or str(input_path.with_suffix(".pdf"))
    generate_pdf(str(input_path), output_path)


if __name__ == "__main__":
    main()
