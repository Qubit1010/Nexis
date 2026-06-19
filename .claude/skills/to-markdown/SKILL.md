---
name: to-markdown
description: Convert a PDF, document, or any text into a clean markdown (.md) file. Handles PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, plain text files, and raw pasted text, extracting the content and saving it as a well-structured .md next to the source. Make sure to use this skill whenever the user wants something turned into markdown or a .md file - phrases like "convert this to markdown", "pdf to md", "turn this PDF into markdown", "extract this PDF as markdown", "convert [file] to .md", "make a markdown file from this", "save this as markdown", or when they paste raw text/a document and ask for a .md version. Trigger even if they don't say the word "skill".
---

# to-markdown

Converts a file (PDF, DOCX, PPTX, XLSX, HTML, CSV, JSON, TXT) or raw pasted text into a clean markdown `.md` file, saved alongside the source.

Uses Microsoft's `markitdown` for file conversion. Output is written next to the source file as `<basename>.md`.

## When to trigger

- "convert this to markdown" / "save this as markdown" / "make a .md from this"
- "pdf to md", "turn this PDF into markdown", "extract this PDF as markdown"
- "convert `<file>` to .md", "give me the markdown for `<file>`"
- The user pastes raw text or a document and asks for a `.md` version
- The user drops one or more file paths and wants markdown out

## Workflow

1. **Detect the input type:**
   - **One or more file paths** → use the script (step 2).
   - **Raw pasted text** (no file on disk) → skip the script. Lightly structure the text into clean markdown (headings, lists, code blocks where obvious) and write it with the Write tool to a `.md` the user names, or a sensible default like `C:/tmp/<slug>.md`. Confirm the path.

2. **For files, run the converter:**
   ```bash
   python .claude/skills/to-markdown/scripts/convert.py "<input-path>" ["<input-path>" ...]
   ```
   - Accepts one or many paths (and globs the shell expands).
   - Writes `<source_dir>/<basename>.md` next to each source.
   - Prints a JSON result per input: `{"input": ..., "output": ..., "ok": true}` or an error entry.

3. **Report** the output path(s) back to the user. If anything failed (missing dependency, bad path, empty extraction), surface the script's error message plainly.

## Script usage notes

- The script converts via `markitdown`. For plain-text inputs (`.txt`, `.md`, `.markdown`) it short-circuits to a direct read/write — no conversion needed.
- If the `.md` output path already exists, the script overwrites it. Mention this if the user might not expect it.
- Multiple files are processed independently; one failure doesn't stop the rest.

## Dependencies

Requires the `markitdown` package (PDF/Office support included):

```bash
pip install "markitdown[all]"
```

If it's not installed, the script exits non-zero and prints this exact install hint. Install it, then re-run.

## Edge cases

- **Missing file** → error entry for that path; other paths still processed.
- **Unsupported / unknown extension** → markitdown attempts it; if it fails, the error is reported. Plain-text extensions bypass markitdown entirely.
- **Empty extraction** (e.g. a scanned image-only PDF with no text layer) → the `.md` is still written but flagged as empty in the result so the user knows OCR may be needed.
- **Output already markdown** (`.md` input) → copied through to a `<basename>.md` only if the target differs; otherwise reported as already-markdown.
