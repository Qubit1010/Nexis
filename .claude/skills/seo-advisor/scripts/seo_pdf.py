# -*- coding: utf-8 -*-
"""Reusable PDF engine for The 2026 SEO Playbook.

Ported from the Practical Claude Playbook engine (which lived in C:\\tmp and so was
not reproducible from the repo). Same proven typographic system, teal accent so the
two playbooks are visually distinct.

Usage:
    from seo_pdf import build
    build(meta={"title": ..., "footer": ...}, blocks=[...], outpath="...pdf")

Block types:
    {"type":"kicker","text":...}      small label above the title
    {"type":"title","text":...}
    {"type":"deck","text":...}        one-line subtitle under the title
    {"type":"rule"}
    {"type":"h2","text":...}
    {"type":"h3","text":...}
    {"type":"body","text":...}        supports <b>..</b> / <i>..</i>
    {"type":"lead","text":...}        accent emphasis line
    {"type":"bullets","items":[...]}
    {"type":"numbers","items":[...]}
    {"type":"callout","title":...,"text":...}   shaded box w/ accent bar
    {"type":"table","headers":[...],"rows":[[...]],"widths":[...]}
    {"type":"spacer","h":N}

Set the module global `_START_PAGE` before building a section so footer page numbers
run continuously across the merged master (see build_course_pdf.py). Pass
`meta["no_footer"]=True` to suppress the rule and page number entirely.

`cover(spec, outpath)` renders the standalone dark cover page on the canvas directly,
since a cover is not flowing body copy.
"""
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

# Palette - teal accent distinguishes this from the Claude Playbook's blue.
INK = colors.HexColor("#111827")
ACCENT = colors.HexColor("#0F766E")
MUTED = colors.HexColor("#475569")
LIGHT = colors.HexColor("#ECFDF5")
CALLOUT_BG = colors.HexColor("#F8FAFC")
RULE = colors.HexColor("#E2E8F0")

CONTENT_W = letter[0] - 1.8 * inch  # 0.9in margins both sides

_START_PAGE = 1

_ss = getSampleStyleSheet()


def _S(name, **kw):
    base = kw.pop("parent", _ss["Normal"])
    return ParagraphStyle(name, parent=base, **kw)


ST = {
    "kicker": _S("kicker", fontName="Helvetica-Bold", fontSize=9.5, leading=12,
                 textColor=ACCENT, spaceAfter=4),
    "title": _S("title", fontName="Helvetica-Bold", fontSize=23, leading=27,
                textColor=INK, spaceAfter=4),
    "deck": _S("deck", fontName="Helvetica-Oblique", fontSize=12, leading=16,
               textColor=MUTED, spaceAfter=6),
    "h2": _S("h2", fontName="Helvetica-Bold", fontSize=14, leading=18,
             textColor=INK, spaceBefore=15, spaceAfter=5),
    "h3": _S("h3", fontName="Helvetica-Bold", fontSize=11.5, leading=15,
             textColor=ACCENT, spaceBefore=9, spaceAfter=3),
    "body": _S("body", fontName="Helvetica", fontSize=10.5, leading=15.5,
               textColor=INK, spaceAfter=8, alignment=TA_LEFT),
    "lead": _S("lead", fontName="Helvetica-Bold", fontSize=12.5, leading=17,
               textColor=ACCENT, spaceAfter=8),
    "bullet": _S("bullet", fontName="Helvetica", fontSize=10.5, leading=15,
                 textColor=INK, spaceAfter=4),
    "co_title": _S("co_title", fontName="Helvetica-Bold", fontSize=10, leading=13,
                   textColor=ACCENT, spaceAfter=3),
    "co_body": _S("co_body", fontName="Helvetica", fontSize=10.5, leading=15,
                  textColor=INK),
    "cellh": _S("cellh", fontName="Helvetica-Bold", fontSize=9.5, leading=13,
                textColor=colors.white),
    "cell": _S("cell", fontName="Helvetica", fontSize=9.5, leading=13, textColor=INK),
}


def _callout(title, text):
    inner = []
    if title:
        inner.append(Paragraph(title, ST["co_title"]))
    inner.append(Paragraph(text, ST["co_body"]))
    t = Table([[inner]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CALLOUT_BG),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return t


def _table(headers, rows, widths=None):
    n = len(headers)
    data = [[Paragraph(h, ST["cellh"]) for h in headers]]
    for r in rows:
        data.append([Paragraph(str(c), ST["cell"]) for c in r])
    cw = widths if widths else [CONTENT_W / n] * n
    t = Table(data, colWidths=cw, hAlign="LEFT", repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), INK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("GRID", (0, 1), (-1, -1), 0.4, RULE),
    ]))
    return t


def _bullets(items, numbered=False):
    lis = [ListItem(Paragraph(it, ST["bullet"]), leftIndent=12) for it in items]
    if numbered:
        return ListFlowable(lis, bulletType="1", leftIndent=18,
                            bulletFontName="Helvetica-Bold", bulletColor=ACCENT)
    return ListFlowable(lis, bulletType="bullet", start=u"\u2022", leftIndent=16,
                        bulletFontSize=10, bulletOffsetY=1, bulletColor=ACCENT)


def cover(spec, outpath):
    """Full-bleed dark cover page, drawn on the canvas directly.

    The block system is built for flowing body copy, which a cover is not. Keys:
    kicker, title_lines (list), deck, stats (list), blurb (list of lines),
    provenance, date.
    """
    from reportlab.pdfgen import canvas as _canvas

    W, H = letter
    M = 0.9 * inch
    c = _canvas.Canvas(outpath, pagesize=letter)
    c.setTitle(spec.get("doc_title", "The 2026 SEO Playbook"))
    c.setAuthor("NexusPoint")

    c.setFillColor(INK)
    c.rect(0, 0, W, H, stroke=0, fill=1)

    # Accent bar anchoring the title block.
    c.setFillColor(ACCENT)
    c.rect(M, H - 1.35 * inch, 2.15 * inch, 0.1 * inch, stroke=0, fill=1)

    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(M, H - 1.78 * inch, spec.get("kicker", "").upper())

    y = H - 2.75 * inch
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 44)
    for ln in spec.get("title_lines", []):
        c.drawString(M, y, ln)
        y -= 0.66 * inch

    y -= 0.05 * inch
    c.setFillColor(colors.HexColor("#94A3B8"))
    c.setFont("Helvetica-Oblique", 13.5)
    c.drawString(M, y, spec.get("deck", ""))

    # Hairline + stat row.
    y -= 0.55 * inch
    c.setStrokeColor(colors.HexColor("#334155"))
    c.setLineWidth(0.6)
    c.line(M, y, W - M, y)

    y -= 0.34 * inch
    c.setFillColor(ACCENT)
    c.setFont("Helvetica-Bold", 10.5)
    c.drawString(M, y, "     ".join(spec.get("stats", [])))

    # Three deliberate bands: title block, blurb, foot. Keep the gaps between them
    # comparable or the middle of the page reads as a hole rather than as air.
    y = 4.55 * inch
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.setFont("Helvetica", 10.5)
    for ln in spec.get("blurb", []):
        c.drawString(M, y, ln)
        y -= 0.235 * inch

    c.setStrokeColor(colors.HexColor("#334155"))
    c.line(M, 2.55 * inch, W - M, 2.55 * inch)

    c.setFillColor(colors.HexColor("#64748B"))
    c.setFont("Helvetica", 9)
    c.drawString(M, 2.25 * inch, spec.get("provenance", ""))
    c.drawString(M, 2.01 * inch, spec.get("date", ""))

    c.setFillColor(ACCENT)
    c.rect(M, 1.55 * inch, 0.7 * inch, 0.07 * inch, stroke=0, fill=1)

    c.showPage()
    c.save()
    return outpath


def build(meta, blocks, outpath):
    story = []
    for b in blocks:
        t = b["type"]
        if t == "kicker":
            story.append(Paragraph(b["text"].upper(), ST["kicker"]))
        elif t == "title":
            story.append(Paragraph(b["text"], ST["title"]))
        elif t == "deck":
            story.append(Paragraph(b["text"], ST["deck"]))
        elif t == "rule":
            story.append(Spacer(1, 3))
            story.append(HRFlowable(width="100%", thickness=2, color=ACCENT))
            story.append(Spacer(1, 10))
        elif t == "h2":
            story.append(Paragraph(b["text"], ST["h2"]))
        elif t == "h3":
            story.append(Paragraph(b["text"], ST["h3"]))
        elif t == "body":
            story.append(Paragraph(b["text"], ST["body"]))
        elif t == "lead":
            story.append(Paragraph(b["text"], ST["lead"]))
        elif t == "bullets":
            story.append(_bullets(b["items"]))
            story.append(Spacer(1, 8))
        elif t == "numbers":
            story.append(_bullets(b["items"], numbered=True))
            story.append(Spacer(1, 8))
        elif t == "callout":
            story.append(Spacer(1, 2))
            story.append(_callout(b.get("title"), b["text"]))
            story.append(Spacer(1, 10))
        elif t == "table":
            story.append(_table(b["headers"], b["rows"], b.get("widths")))
            story.append(Spacer(1, 10))
        elif t == "spacer":
            story.append(Spacer(1, b.get("h", 8)))

    footer_left = meta.get("footer", "NexusPoint  |  The 2026 SEO Playbook")
    no_footer = meta.get("no_footer", False)

    def on_page(canvas, doc):
        if no_footer:
            return
        canvas.saveState()
        canvas.setStrokeColor(RULE)
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, 0.7 * inch,
                    doc.pagesize[0] - doc.rightMargin, 0.7 * inch)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(MUTED)
        canvas.drawString(doc.leftMargin, 0.52 * inch, footer_left)
        canvas.drawRightString(doc.pagesize[0] - doc.rightMargin, 0.52 * inch,
                               "Page %d" % (doc.page + _START_PAGE - 1))
        canvas.restoreState()

    doc = BaseDocTemplate(
        outpath, pagesize=letter,
        leftMargin=0.9 * inch, rightMargin=0.9 * inch,
        topMargin=0.85 * inch, bottomMargin=0.95 * inch,
        title=meta.get("title", "The 2026 SEO Playbook"),
        author="NexusPoint",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=on_page)])
    doc.build(story)
    return outpath
