"""QA helper: tile a PDF's pages into one PNG, or render chosen pages at readable resolution.

    python scripts/contact_sheet.py deliverables/X.pdf            -> build/qa/X-sheet.png
    python scripts/contact_sheet.py deliverables/X.pdf 3 7 --dpi 110 -> build/qa/X-p03.png, X-p07.png
"""
import sys
from pathlib import Path

import fitz

PROJECT = Path(__file__).resolve().parents[1]
QA = PROJECT / "build" / "qa"


def sheet(pdf: Path, cols: int = 6, width: int = 300) -> Path:
    doc = fitz.open(pdf)
    first = doc[0].rect
    scale = width / first.width
    h = int(first.height * scale)
    rows = (len(doc) + cols - 1) // cols
    out = fitz.open()
    page = out.new_page(width=cols * (width + 10) + 10, height=rows * (h + 10) + 10)
    page.draw_rect(page.rect, color=None, fill=(0.8, 0.82, 0.85))
    for i, pg in enumerate(doc):
        x, y = 10 + (i % cols) * (width + 10), 10 + (i // cols) * (h + 10)
        page.show_pdf_page(fitz.Rect(x, y, x + width, y + h), doc, i)
    QA.mkdir(parents=True, exist_ok=True)
    path = QA / f"{pdf.stem}-sheet.png"
    page.get_pixmap(dpi=72).save(str(path))
    return path


def pages(pdf: Path, nums: list[int], dpi: int) -> list[Path]:
    doc = fitz.open(pdf)
    QA.mkdir(parents=True, exist_ok=True)
    made = []
    for n in nums:
        p = QA / f"{pdf.stem}-p{n:02d}.png"
        doc[n - 1].get_pixmap(dpi=dpi).save(str(p))
        made.append(p)
    return made


if __name__ == "__main__":
    pdf = Path(sys.argv[1])
    if not pdf.is_absolute():
        pdf = PROJECT / pdf
    dpi = 100
    args = sys.argv[2:]
    if "--dpi" in args:
        i = args.index("--dpi")
        dpi = int(args[i + 1])
        args = args[:i] + args[i + 2:]
    nums = [int(a) for a in args]
    print(*(pages(pdf, nums, dpi) if nums else [sheet(pdf)]), sep="\n")
