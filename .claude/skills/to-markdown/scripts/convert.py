#!/usr/bin/env python3
"""Convert files (PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, TXT) to markdown.

Writes <basename>.md next to each source file. Plain-text inputs are passed
through directly; everything else goes through Microsoft's markitdown.

Usage:
    python convert.py <input-path> [<input-path> ...]

Prints one JSON object per line for each input:
    {"input": "...", "output": "...", "ok": true, "empty": false}
    {"input": "...", "ok": false, "error": "..."}

Exits non-zero if any conversion failed or markitdown is missing.
"""
import json
import os
import sys

PLAINTEXT_EXTS = {".txt", ".md", ".markdown", ".text"}
INSTALL_HINT = (
    'markitdown is not installed. Run: pip install "markitdown[all]"'
)


def emit(obj):
    print(json.dumps(obj, ensure_ascii=False))


def output_path_for(input_path):
    base, _ = os.path.splitext(input_path)
    return base + ".md"


def convert_one(input_path, converter):
    """Return (result_dict, ok_bool). converter may be None (loaded lazily)."""
    if not os.path.isfile(input_path):
        return {"input": input_path, "ok": False,
                "error": "File not found"}, False

    ext = os.path.splitext(input_path)[1].lower()
    out_path = output_path_for(input_path)

    # Plain text passthrough — no conversion library needed.
    if ext in PLAINTEXT_EXTS:
        try:
            with open(input_path, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception as e:  # noqa: BLE001
            return {"input": input_path, "ok": False, "error": str(e)}, False
        if os.path.abspath(out_path) == os.path.abspath(input_path):
            return {"input": input_path, "output": input_path, "ok": True,
                    "empty": not text.strip(),
                    "note": "input is already markdown"}, True
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
        except Exception as e:  # noqa: BLE001
            return {"input": input_path, "ok": False, "error": str(e)}, False
        return {"input": input_path, "output": out_path, "ok": True,
                "empty": not text.strip()}, True

    # Everything else → markitdown.
    try:
        result = converter.convert(input_path)
        text = result.text_content or ""
    except Exception as e:  # noqa: BLE001
        return {"input": input_path, "ok": False, "error": str(e)}, False

    try:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
    except Exception as e:  # noqa: BLE001
        return {"input": input_path, "ok": False, "error": str(e)}, False

    return {"input": input_path, "output": out_path, "ok": True,
            "empty": not text.strip()}, True


def main(argv):
    inputs = argv[1:]
    if not inputs:
        emit({"ok": False, "error": "No input paths given. "
              "Usage: python convert.py <path> [<path> ...]"})
        return 2

    # Only load markitdown if at least one non-plaintext file is present.
    needs_converter = any(
        os.path.splitext(p)[1].lower() not in PLAINTEXT_EXTS for p in inputs
    )
    converter = None
    if needs_converter:
        try:
            from markitdown import MarkItDown
        except ImportError:
            emit({"ok": False, "error": INSTALL_HINT})
            return 1
        converter = MarkItDown()

    all_ok = True
    for path in inputs:
        result, ok = convert_one(path, converter)
        emit(result)
        all_ok = all_ok and ok

    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
