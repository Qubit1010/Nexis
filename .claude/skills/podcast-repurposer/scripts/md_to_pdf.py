"""
Styled PDF renderer for podcast-repurposer outputs.
Matches the Braden Hall visual format:
  - Dark navy page-header strip with slug label
  - H1 title in navy + underline rule
  - Inline bold labels rendered in accent blue (metadata + body)
  - Blockquote with left blue border, italic gray text
  - H2 segment headers as filled navy box / white text
  - H3 in accent blue
  - Clean HR separators

Usage:
  python md_to_pdf.py path/to/05-hybrid.md
  python md_to_pdf.py output/brenda-thompson/bt-hss-pod-ep35/
  python md_to_pdf.py output/brenda-thompson/
  python md_to_pdf.py output/

Requires: pip install fpdf2
"""
import re
import sys
from pathlib import Path

# Color palette
NAV_BLUE  = (27, 58, 92)     # dark navy — page header bar + segment fill
ACC_BLUE  = (27, 90, 138)    # accent blue — bold labels, H3, blockquote border
GRAY_TEXT = (90, 90, 90)     # blockquote italic text
DARK      = (20, 20, 20)     # body text
RULE_CLR  = (210, 210, 210)  # HR line

LEFT_M  = 20
RIGHT_M = 20
TOP_M   = 24   # top margin to clear the header bar

# Type scale (pt) — generous, readable hierarchy
H1_SZ   = 22
H2_SZ   = 13
H3_SZ   = 11.5
BODY_SZ = 10.5
META_SZ = 9.5

# Leading (mm) — line height for body-weight text
BODY_LH = 5.8


def sanitize(text: str) -> str:
    """Replace non-latin-1 characters, preserving whitespace."""
    return (
        text
        .replace("‘", "'").replace("’", "'")
        .replace("“", '"').replace("”", '"')
        .replace("—", "-").replace("–", "-")
        .replace("→", "->").replace("←", "<-")
        .replace("•", "-")
        .replace("…", "...")
    )


def clean(text: str) -> str:
    """Strip markdown formatting, sanitize, strip whitespace."""
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"\*(.+?)\*", r"\1", text)
    text = re.sub(r"`(.+?)`", r"\1", text)
    return sanitize(text).strip()


def render_inline(pdf, raw_line: str, line_h: float = BODY_LH, font_size: float = BODY_SZ) -> None:
    """Render a line with **bold** spans: bold portions in accent blue, rest in dark normal."""
    parts = re.split(r"(\*\*[^*]+\*\*)", raw_line)
    for part in parts:
        m = re.match(r"\*\*([^*]+)\*\*", part)
        if m:
            pdf.set_font("Helvetica", "B", font_size)
            pdf.set_text_color(*ACC_BLUE)
            pdf.write(line_h, sanitize(m.group(1)))
        else:
            s = sanitize(part)
            if s:
                pdf.set_font("Helvetica", "", font_size)
                pdf.set_text_color(*DARK)
                pdf.write(line_h, s)
    pdf.ln(line_h)
    # Always reset to body defaults so nothing bleeds into the next element
    pdf.set_font("Helvetica", "", font_size)
    pdf.set_text_color(*DARK)


def wrap_text(pdf, text: str, max_w: float) -> list:
    """Greedy word-wrap to a max width, measured in the current font."""
    words = text.split(" ")
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if not cur or pdf.get_string_width(trial) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def render_metadata_card(pdf, fields: list, cw: float) -> None:
    """Render a segment's metadata as a light card: accent left bar, subtle fill,
    bold accent-blue labels with dark values. Pre-measures height so the fill sits
    behind the text."""
    pad = 4.0
    line_h = 5.6
    inner_w = cw - 2  # text runs LEFT_M -> right margin, kept inside the card
    pdf.set_font("Helvetica", "", META_SZ)

    wrapped_fields = []
    total_lines = 0
    for k, v in fields:
        full = f"{k}: {v}" if v else f"{k}:"
        wrapped = wrap_text(pdf, full, inner_w)
        wrapped_fields.append((k, wrapped))
        total_lines += len(wrapped)

    box_h = total_lines * line_h + 2 * pad
    if pdf.get_y() + box_h > pdf.page_break_trigger:
        pdf.add_page()

    y0 = pdf.get_y()
    x0 = LEFT_M - 4
    pdf.set_fill_color(244, 247, 251)        # very light blue-gray panel
    pdf.rect(x0, y0, cw + 8, box_h, "F")
    pdf.set_fill_color(*ACC_BLUE)            # accent left bar
    pdf.rect(x0, y0, 1.6, box_h, "F")

    y = y0 + pad
    for k, wrapped in wrapped_fields:
        for idx, ln in enumerate(wrapped):
            pdf.set_xy(LEFT_M, y)
            if idx == 0:
                key_str = f"{k}:"
                pdf.set_font("Helvetica", "B", META_SZ)
                pdf.set_text_color(*ACC_BLUE)
                pdf.cell(pdf.get_string_width(key_str + " "), line_h, key_str)
                rest = ln[len(key_str):].lstrip()
                if rest:
                    pdf.set_font("Helvetica", "", META_SZ)
                    pdf.set_text_color(*DARK)
                    pdf.cell(0, line_h, rest)
            else:
                pdf.set_font("Helvetica", "", META_SZ)
                pdf.set_text_color(*DARK)
                pdf.cell(0, line_h, ln)
            y += line_h

    pdf.set_xy(LEFT_M, y0 + box_h + 4)
    pdf.set_font("Helvetica", "", BODY_SZ)
    pdf.set_text_color(*DARK)


def render_list_item(pdf, text: str, cw: float, marker: str = None) -> None:
    """Hanging-indent list item: the marker sits in the gutter and every wrapped
    line of the text aligns to the same left edge (not under the marker).
    marker=None draws a bullet dot; otherwise it's a numbered marker like '1.'."""
    pdf.set_font("Helvetica", "", BODY_SZ)
    pdf.set_text_color(*DARK)
    x0 = LEFT_M + 4
    y = pdf.get_y()
    if y + BODY_LH > pdf.page_break_trigger:
        pdf.add_page()
        y = pdf.get_y()

    if marker is None:
        r = 0.7
        pdf.set_fill_color(*DARK)
        pdf.ellipse(x0 + 0.8, y + BODY_LH / 2 - r, r * 2, r * 2, style="F")
        text_x = x0 + 4.5
    else:
        pdf.set_xy(x0, y)
        mw = pdf.get_string_width(marker) + 2.0
        pdf.cell(mw, BODY_LH, marker)
        text_x = x0 + mw

    pdf.set_xy(text_x, y)
    old_lm = pdf.l_margin
    pdf.set_left_margin(text_x)              # makes wrapped lines hang under the text
    pdf.multi_cell(pdf.w - RIGHT_M - text_x, BODY_LH, text)
    pdf.set_left_margin(old_lm)
    pdf.set_x(LEFT_M)


def reorder_segment_metadata(lines: list) -> list:
    """Move **Segment metadata:** blocks to the top of each H2 section."""
    result = []
    i = 0
    while i < len(lines):
        if re.match(r"^## ", lines[i]):
            h2_line = lines[i]
            i += 1
            section = []
            while i < len(lines) and not re.match(r"^## ", lines[i]):
                section.append(lines[i])
                i += 1
            meta_start = next(
                (j for j, ln in enumerate(section) if re.match(r"^\*\*Segment metadata", ln)),
                None,
            )
            if meta_start is not None:
                meta_block = section[meta_start:]
                body = section[:meta_start]
                # Drop the body's standalone Pillar line — the metadata card now owns it
                for j, ln in enumerate(body):
                    if re.match(r"^\*\*Pillar:\*\*", ln):
                        del body[j]
                        break
                result.append(h2_line)
                result.append("")
                result.extend(meta_block)
                result.append("")
                result.extend(body)
            else:
                result.append(h2_line)
                result.extend(section)
        else:
            result.append(lines[i])
            i += 1
    return result


def md_to_pdf(md_path: Path) -> None:
    from fpdf import FPDF

    slug = md_path.stem  # e.g. "05-hybrid"

    class _PDF(FPDF):
        def header(self_):
            # Dark navy strip across full top
            self_.set_fill_color(*NAV_BLUE)
            self_.rect(0, 0, self_.w, 9, "F")
            # Slug label right-aligned in white
            self_.set_font("Helvetica", "", 7)
            self_.set_text_color(255, 255, 255)
            self_.set_xy(0, 2)
            self_.cell(self_.w - 5, 5, slug, align="R")
            # Reset cursor below the header bar so page-break content doesn't overlap
            self_.set_xy(self_.l_margin, self_.t_margin)

        def footer(self_):
            self_.set_y(-12)
            self_.set_font("Helvetica", "I", 8)
            self_.set_text_color(150, 150, 150)
            self_.cell(0, 10, f"Page {self_.page_no()}", align="C")

    pdf = _PDF()
    pdf.set_margins(LEFT_M, TOP_M, RIGHT_M)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    cw = pdf.w - LEFT_M - RIGHT_M  # usable content width

    lines = reorder_segment_metadata(md_path.read_text(encoding="utf-8").splitlines())
    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1

        # Skip code fences
        if raw.startswith("```"):
            while i < len(lines) and not lines[i].startswith("```"):
                i += 1
            i += 1
            continue

        # H1 — large navy title + underline
        h1 = re.match(r"^# (.+)", raw)
        if h1:
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", H1_SZ)
            pdf.set_text_color(*NAV_BLUE)
            pdf.set_x(LEFT_M)
            pdf.multi_cell(0, 10, clean(h1.group(1)))
            pdf.ln(2)
            pdf.set_draw_color(*NAV_BLUE)
            pdf.set_line_width(0.7)
            pdf.line(LEFT_M, pdf.get_y(), pdf.w - RIGHT_M, pdf.get_y())
            pdf.ln(5)
            continue

        # H2 — filled navy box, white text (segment headers)
        h2 = re.match(r"^## (.+)", raw)
        if h2:
            pdf.ln(7)
            text = clean(h2.group(1))
            box_h = 13
            y0 = pdf.get_y()
            # Keep-with-next: a section heading must have room for itself plus a few
            # lines of content, otherwise it orphans at the bottom — push to next page.
            if y0 + box_h + 24 > pdf.page_break_trigger:
                pdf.add_page()
                y0 = pdf.get_y()
            pdf.set_fill_color(*NAV_BLUE)
            pdf.rect(LEFT_M - 4, y0, cw + 8, box_h, "F")
            pdf.set_font("Helvetica", "B", H2_SZ)
            pdf.set_text_color(255, 255, 255)
            pdf.set_xy(LEFT_M, y0)
            pdf.cell(cw, box_h, text, align="L")  # vertically centered in the box
            pdf.set_y(y0 + box_h + 4)
            pdf.set_text_color(*DARK)
            continue

        # H3 — accent blue subheading
        h3 = re.match(r"^### (.+)", raw)
        if h3:
            pdf.ln(5)
            # Keep-with-next: don't leave a subheading stranded at the page bottom
            if pdf.get_y() + 7 + 16 > pdf.page_break_trigger:
                pdf.add_page()
            pdf.set_font("Helvetica", "B", H3_SZ)
            pdf.set_text_color(*ACC_BLUE)
            pdf.set_x(LEFT_M)
            pdf.multi_cell(0, 7, clean(h3.group(1)))
            pdf.ln(1)
            pdf.set_text_color(*DARK)
            continue

        # HR
        if re.match(r"^---+$", raw.strip()):
            pdf.ln(3)
            pdf.set_draw_color(*RULE_CLR)
            pdf.set_line_width(0.3)
            pdf.line(LEFT_M, pdf.get_y(), pdf.w - RIGHT_M, pdf.get_y())
            pdf.ln(4)
            continue

        # Blank line
        if raw.strip() == "":
            pdf.ln(2.4)
            continue

        # Blockquote — collect consecutive > lines, draw left border after
        if raw.startswith(">"):
            bq_parts = [re.match(r"^>\s*(.*)", raw).group(1)]
            while i < len(lines) and lines[i].startswith(">"):
                bq_parts.append(re.match(r"^>\s*(.*)", lines[i]).group(1))
                i += 1
            bq_text = " ".join(p for p in bq_parts)
            pdf.ln(1)
            y0 = pdf.get_y()
            pdf.set_font("Helvetica", "I", BODY_SZ)
            pdf.set_text_color(*GRAY_TEXT)
            pdf.set_x(LEFT_M + 6)
            pdf.multi_cell(cw - 6, BODY_LH, sanitize(bq_text))
            y1 = pdf.get_y()
            # Left blue border
            pdf.set_draw_color(*ACC_BLUE)
            pdf.set_line_width(1.5)
            pdf.line(LEFT_M + 1.5, y0, LEFT_M + 1.5, y1)
            pdf.set_line_width(0.2)
            pdf.ln(1)
            pdf.set_text_color(*DARK)
            continue

        # Checkbox list
        cb = re.match(r"^- \[[ x]\] (.+)", raw)
        if cb:
            render_list_item(pdf, clean(cb.group(1)), cw)
            continue

        # Bullet list
        bullet = re.match(r"^[-*] (.+)", raw)
        if bullet:
            render_list_item(pdf, clean(bullet.group(1)), cw)
            continue

        # Numbered list
        num = re.match(r"^(\d+)\. (.+)", raw)
        if num:
            render_list_item(pdf, clean(num.group(2)), cw, marker=f"{num.group(1)}.")
            continue

        # Segment metadata block — collect the **key:** value lines into a card
        if re.match(r"^\*\*Segment metadata", raw):
            fields = []
            while i < len(lines):
                fm = re.match(r"^\*\*(.+?):\*\*\s*(.*)", lines[i])
                if fm:
                    fields.append((clean(fm.group(1)), clean(fm.group(2))))
                    i += 1
                elif lines[i].strip() == "":
                    i += 1
                    break
                else:
                    break
            pdf.ln(1)
            render_metadata_card(pdf, fields, cw)
            continue

        # Lines with inline bold (metadata + body labels) — render with colored labels
        if "**" in raw:
            pdf.set_x(LEFT_M)
            render_inline(pdf, raw, line_h=BODY_LH, font_size=BODY_SZ)
            continue

        # Regular paragraph
        pdf.set_font("Helvetica", "", BODY_SZ)
        pdf.set_text_color(*DARK)
        pdf.set_x(LEFT_M)
        pdf.multi_cell(0, BODY_LH, clean(raw))

    out = md_path.with_suffix(".pdf")
    pdf.output(str(out))
    print(f"  -> {out}")


def resolve_targets(path: Path) -> list:
    if path.is_file() and path.suffix == ".md":
        return [path]
    if path.is_dir():
        return sorted(path.rglob("*.md"))
    return []


def main():
    if len(sys.argv) < 2:
        print("Usage: python md_to_pdf.py <file.md | folder/>")
        sys.exit(1)

    target = Path(sys.argv[1])
    files = resolve_targets(target)

    if not files:
        print(f"No .md files found at: {target}")
        sys.exit(1)

    for f in files:
        label = "/".join(f.parts[-3:]) if len(f.parts) >= 3 else str(f)
        print(f"Converting {label} ...")
        try:
            md_to_pdf(f)
        except Exception as e:
            print(f"  ERROR: {e}")

    print(f"\nDone. {len(files)} file(s) processed.")


if __name__ == "__main__":
    main()
