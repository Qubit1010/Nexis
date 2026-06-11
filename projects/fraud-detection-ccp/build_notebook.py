"""
Assemble notebooks/fraud_detection_ccp.ipynb from src/pipeline.py and execute it.

src/pipeline.py is written in the "percent" cell format:
    # %% [markdown]      -> markdown cell (following '# ' comment lines = content)
    # %%                 -> code cell

We parse those markers into nbformat cells, then run the notebook end-to-end with
nbconvert's ExecutePreprocessor so all outputs and figures are baked in.

Usage:
    python build_notebook.py            # build + execute
    python build_notebook.py --no-exec  # build only (fast)
"""

import sys
import asyncio
from pathlib import Path

# Avoid the noisy Proactor-loop shutdown error from ipykernel/pyzmq on Windows.
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

import nbformat
from nbformat.v4 import new_notebook, new_code_cell, new_markdown_cell

ROOT = Path(__file__).resolve().parent
PIPELINE = ROOT / "src" / "pipeline.py"
NB_PATH = ROOT / "notebooks" / "fraud_detection_ccp.ipynb"


def parse_cells(text: str):
    """Split percent-format source into (kind, source) cells."""
    lines = text.splitlines()
    cells = []
    kind = None          # "code" | "markdown"
    buf = []

    def flush():
        if kind is None:
            return
        src = "\n".join(buf).strip("\n")
        if kind == "markdown":
            # strip leading '# ' / '#' from each comment line
            md_lines = []
            for ln in src.splitlines():
                if ln.startswith("# "):
                    md_lines.append(ln[2:])
                elif ln.strip() == "#":
                    md_lines.append("")
                else:
                    md_lines.append(ln)
            cells.append(("markdown", "\n".join(md_lines).strip()))
        else:
            if src.strip():
                cells.append(("code", src))

    for ln in lines:
        if ln.strip() == "# %% [markdown]":
            flush(); kind, buf = "markdown", []
        elif ln.strip() == "# %%":
            flush(); kind, buf = "code", []
        else:
            buf.append(ln)
    flush()
    return cells


def build():
    text = PIPELINE.read_text(encoding="utf-8")
    cells = parse_cells(text)
    nb = new_notebook()
    nb.cells = [
        new_markdown_cell(src) if kind == "markdown" else new_code_cell(src)
        for kind, src in cells
    ]
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    NB_PATH.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, NB_PATH)
    n_code = sum(1 for k, _ in cells if k == "code")
    n_md = sum(1 for k, _ in cells if k == "markdown")
    print(f"Built {NB_PATH.name}: {n_md} markdown + {n_code} code cells")
    return nb


def execute(nb):
    from nbconvert.preprocessors import ExecutePreprocessor
    print("Executing notebook (this runs the full pipeline)...")
    ep = ExecutePreprocessor(timeout=1800, kernel_name="python3")
    ep.preprocess(nb, {"metadata": {"path": str(ROOT / "notebooks")}})
    nbformat.write(nb, NB_PATH)
    print(f"Executed and saved -> {NB_PATH}")


if __name__ == "__main__":
    nb = build()
    if "--no-exec" not in sys.argv:
        execute(nb)
