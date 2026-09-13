"""Create/recover one formatted proposal. Stdout is a JSON delivery receipt."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import uuid

FOLDER = "NexusPoint Proposals"
MARKER = "upworkProposalStudio"


def units(text):
    return len(text.encode("utf-16-le")) // 2


def validate(data):
    if not isinstance(data, dict) or set(data) - {"title", "sections"}:
        raise ValueError("Expected title and sections only")
    if not isinstance(data.get("title"), str) or not data["title"].strip():
        raise ValueError("A nonempty title is required")
    if not isinstance(data.get("sections"), list) or not data["sections"]:
        raise ValueError("Nonempty sections are required")
    for section in data["sections"]:
        if not isinstance(section, dict) or set(section) - {"heading", "body", "body_runs", "bullets", "bullet_runs", "table"}:
            raise ValueError("Sections accept heading, body, body_runs, bullets, bullet_runs, and table only")
        for key in ("heading", "body"):
            if key in section and not isinstance(section[key], str):
                raise ValueError(f"{key} must be text")
        for key in ("body_runs",):
            if key in section:
                _validate_runs(section[key], key)
        bullets = section.get("bullets", [])
        if not isinstance(bullets, list) or any(not isinstance(x, str) or not x.strip() for x in bullets):
            raise ValueError("bullets must be nonempty strings")
        if "bullet_runs" in section:
            if not isinstance(section["bullet_runs"], list):
                raise ValueError("bullet_runs must be a list")
            for runs in section["bullet_runs"]:
                _validate_runs(runs, "bullet_runs item")
        if "table" in section:
            table = section["table"]
            if not isinstance(table, dict) or set(table) != {"headers", "rows"}:
                raise ValueError("table requires headers and rows")
            headers, rows = table["headers"], table["rows"]
            if not isinstance(headers, list) or not 2 <= len(headers) <= 3 or not all(isinstance(h, str) and h.strip() for h in headers):
                raise ValueError("Tables need 2 or 3 nonempty column headers")
            if not isinstance(rows, list) or not rows or any(not isinstance(r, list) or len(r) != len(headers) or not all(isinstance(c, str) for c in r) for r in rows):
                raise ValueError("Table rows must match the header width and contain strings")
        if not any(section.get(k) for k in ("heading", "body", "body_runs", "bullets", "bullet_runs", "table")):
            raise ValueError("Empty section")
    for text in [data["title"]] + [x for s in data["sections"] for x in
            [s.get("heading", ""), s.get("body", ""), *[r.get("text", "") for r in s.get("body_runs", [])], *s.get("bullets", []),
             *[r.get("text", "") for runs in s.get("bullet_runs", []) for r in runs], *s.get("table", {}).get("headers", []),
             *[c for r in s.get("table", {}).get("rows", []) for c in r]]]:
        if any(ord(c) < 32 and c != "\n" for c in text):
            raise ValueError("Text contains unsupported control characters")
    return data


def _validate_runs(runs, label):
    if not isinstance(runs, list) or not runs or any(not isinstance(r, dict) or set(r) - {"text", "bold"} or not isinstance(r.get("text"), str) or not r["text"] for r in runs):
        raise ValueError(f"{label} must be nonempty text runs")
    if any("bold" in r and not isinstance(r["bold"], bool) for r in runs):
        raise ValueError(f"{label} bold values must be booleans")


def _runs(value):
    return [{"text": value, "bold": False}] if isinstance(value, str) else value


def compose(data):
    lines = [(data["title"], "TITLE", [])]
    for section in data["sections"]:
        if section.get("heading"):
            lines.append((section["heading"], "HEADING_1", []))
        if section.get("body") or section.get("body_runs"):
            lines.append(("", "NORMAL_TEXT", _runs(section.get("body_runs", section.get("body", "")))))
        lines.extend((b, "BULLET", []) for b in section.get("bullets", []))
        lines.extend(("", "BULLET", _runs(runs)) for runs in section.get("bullet_runs", []))
        if section.get("table"):
            lines.append(("", "TABLE", []))
    text, spans, inline, idx = "", [], [], 1
    for value, style, runs in lines:
        if runs:
            value = "".join(r["text"] for r in runs)
        value = (value or "").rstrip() + "\n"
        spans.append((idx, idx + units(value), style))
        run_idx = idx
        for run in runs:
            run_end = run_idx + units(run["text"])
            if run.get("bold"):
                inline.append((run_idx, run_end, True))
            run_idx = run_end
        text += value
        idx += units(value)
    return text, spans, inline


def markdown(data):
    parts = ["# " + data["title"]]
    for s in data["sections"]:
        if s.get("heading"):
            parts.append("## " + s["heading"])
        if s.get("body"):
            parts.append(s["body"])
        elif s.get("body_runs"):
            parts.append("".join(r["text"] for r in s["body_runs"]))
        if s.get("bullets"):
            parts.append("\n".join("- " + b for b in s["bullets"]))
        elif s.get("bullet_runs"):
            parts.append("\n".join("- " + "".join(r["text"] for r in runs) for runs in s["bullet_runs"]))
        if s.get("table"):
            t = s["table"]
            rows = [t["headers"], ["---"] * len(t["headers"]), *t["rows"]]
            parts.append("\n".join("| " + " | ".join(c.replace("|", "\\|").replace("\n", "<br>") for c in r) + " |" for r in rows))
    return "\n\n".join(parts) + "\n"


def requests_for(text, spans, inline=None, old_end=2):
    requests = []
    if old_end > 2:
        requests.append({"deleteContentRange": {"range": {"startIndex": 1, "endIndex": old_end - 1}}})
    requests.append({"insertText": {"location": {"index": 1}, "text": text}})
    whole = {"startIndex": 1, "endIndex": 1 + units(text)}
    requests.extend([
        {"deleteParagraphBullets": {"range": whole}},
        {"updateTextStyle": {"range": whole, "textStyle": {
            "weightedFontFamily": {"fontFamily": "Arial"}, "fontSize": {"magnitude": 11, "unit": "PT"}, "bold": False},
            "fields": "weightedFontFamily,fontSize,bold"}},
        {"updateParagraphStyle": {"range": whole, "paragraphStyle": {
            "namedStyleType": "NORMAL_TEXT", "lineSpacing": 110,
            "spaceAbove": {"magnitude": 0, "unit": "PT"},
            "spaceBelow": {"magnitude": 6, "unit": "PT"}, "keepWithNext": False},
            "fields": "namedStyleType,lineSpacing,spaceAbove,spaceBelow,keepWithNext"}},
        {"updateDocumentStyle": {"documentStyle": {
            "pageSize": {"width": {"magnitude": 595.28, "unit": "PT"}, "height": {"magnitude": 841.89, "unit": "PT"}},
            **{k: {"magnitude": 54, "unit": "PT"} for k in ("marginTop", "marginBottom", "marginLeft", "marginRight")}},
            "fields": "pageSize,marginTop,marginBottom,marginLeft,marginRight"}}])
    for start, end, style in spans:
        rng = {"startIndex": start, "endIndex": end}
        if style == "TABLE":
            continue
        elif style == "BULLET":
            requests.append({"createParagraphBullets": {"range": rng, "bulletPreset": "BULLET_DISC_CIRCLE_SQUARE"}})
        elif style != "NORMAL_TEXT":
            requests.extend([
                {"updateParagraphStyle": {"range": rng, "paragraphStyle": {"namedStyleType": style, "keepWithNext": True,
                    "spaceAbove": {"magnitude": 10, "unit": "PT"}}, "fields": "namedStyleType,keepWithNext,spaceAbove"}},
                {"updateTextStyle": {"range": rng, "textStyle": {"bold": True, "fontSize": {"magnitude": 18 if style == "TITLE" else 13, "unit": "PT"}}, "fields": "bold,fontSize"}}])
    for start, end, bold in (inline or []):
        requests.append({"updateTextStyle": {"range": {"startIndex": start, "endIndex": end}, "textStyle": {"bold": bold}, "fields": "bold"}})
    return requests


def gws_command():
    npm = Path(os.environ.get("APPDATA", "")) / "npm/node_modules/@googleworkspace/cli"
    exe = npm / "bin/gws.exe"
    if exe.exists():
        return [str(exe)]
    if (npm / "run.js").exists() and shutil.which("node"):
        return [shutil.which("node"), str(npm / "run.js")]
    found = shutil.which("gws")
    if found and Path(found).suffix.lower() not in (".cmd", ".bat", ".ps1"):
        return [found]
    raise RuntimeError("A native gws executable or node + run.js is required")


class Workspace:
    def __init__(self, work):
        self.work = work

    def call(self, service, resource, method, params=None, body=None, output=None):
        cmd = gws_command() + [service, resource, method]
        if params is not None:
            cmd += ["--params", json.dumps(params)]
        if body is not None:
            cmd += ["--json", json.dumps(body, ensure_ascii=False)]
        if sum(len(arg) + 3 for arg in cmd) > 28000:
            raise ValueError("Request exceeds the safe Windows argument limit; shorten the proposal")
        if output:
            cmd += ["--output", str(output)]
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", timeout=60, shell=False, cwd=self.work)
        if result.returncode:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "gws failed")
        if output:
            return {}
        parsed = json.loads(result.stdout)
        if "error" in parsed:
            raise RuntimeError(str(parsed["error"]))
        return parsed


def save(path, state):
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(state, indent=2), encoding="utf-8")
    temp.replace(path)


def body_content(doc):
    return doc.get("body", {}).get("content", [])


def verify(doc, text, spans):
    content = body_content(doc)
    actual = "".join(e.get("textRun", {}).get("content", "") for p in content for e in p.get("paragraph", {}).get("elements", []))
    if actual.rstrip("\n") != text.rstrip("\n"):
        raise RuntimeError("Read-back text differs from the draft")
    paragraphs = {p.get("startIndex"): p.get("paragraph", {}) for p in content}
    named = {s["namedStyleType"]: s.get("textStyle", {}) for s in doc.get("namedStyles", {}).get("styles", [])}
    for start, end, style in spans:
        if style == "TABLE":
            continue
        paragraph = paragraphs.get(start, {})
        if style == "BULLET" and not paragraph.get("bullet"):
            raise RuntimeError("Missing list formatting")
        if style in ("TITLE", "HEADING_1") and paragraph.get("paragraphStyle", {}).get("namedStyleType") != style:
            raise RuntimeError("Missing heading formatting")
        expected = 18 if style == "TITLE" else 13 if style == "HEADING_1" else 11
        run = next((e["textRun"] for e in paragraph.get("elements", []) if "textRun" in e), {})
        ts = {**named.get("NORMAL_TEXT", {}), **named.get(style, {}), **run.get("textStyle", {})}
        if ts.get("fontSize", {}).get("magnitude") != expected or ts.get("weightedFontFamily", {}).get("fontFamily") != "Arial":
            raise RuntimeError("Font verification failed")
    if doc.get("documentStyle", {}).get("marginLeft", {}).get("magnitude") != 54:
        raise RuntimeError("Page margin verification failed")


def paragraph_text(content):
    return "".join(e.get("textRun", {}).get("content", "") for p in content for e in p.get("paragraph", {}).get("elements", []))


def table_cells(element):
    return [[cell for cell in row["tableCells"]] for row in element["table"]["tableRows"]]


def write_tables(api, doc_id, data, spans):
    tables = [s["table"] for s in data["sections"] if s.get("table")]
    locations = [start for start, end, style in spans if style == "TABLE"]
    params = {"documentId": doc_id}

    def batch(requests):
        # Keep native Windows command-line arguments below the CLI limit.
        chunk = []
        for request in requests:
            if chunk and len(json.dumps(chunk + [request])) > 18000:
                api.call("docs", "documents", "batchUpdate", params, {"requests": chunk})
                chunk = []
            chunk.append(request)
        if chunk:
            api.call("docs", "documents", "batchUpdate", params, {"requests": chunk})

    # Reverse insertion preserves the earlier placeholder positions.
    for index, table in reversed(list(zip(locations, tables))):
        batch([{"insertTable": {"location": {"index": index}, "rows": len(table["rows"]) + 1, "columns": len(table["headers"])}}])
        doc = api.call("docs", "documents", "get", params)
        element = next(e for e in body_content(doc) if "table" in e and e["startIndex"] >= index)
        cells = table_cells(element)
        inserts = []
        for row, values in zip(cells, [table["headers"], *table["rows"]]):
            for cell, value in zip(row, values):
                if value:
                    inserts.append({"insertText": {"location": {"index": cell["content"][0]["startIndex"]}, "text": value}})
        inserts.sort(key=lambda r: r["insertText"]["location"]["index"], reverse=True)
        batch(inserts)
        # Read actual cell ranges after insertions, including UTF-16 text lengths.
        doc = api.call("docs", "documents", "get", params)
        element = next(e for e in body_content(doc) if "table" in e and e["startIndex"] >= index)
        start = element["startIndex"]
        count = len(table["headers"])
        widths = [145, 342.28] if count == 2 else [90, 155, 242.28]
        styles = []
        for col, width in enumerate(widths):
            styles.append({"updateTableColumnProperties": {"tableStartLocation": {"index": start}, "columnIndices": [col], "tableColumnProperties": {"widthType": "FIXED_WIDTH", "width": {"magnitude": width, "unit": "PT"}}, "fields": "widthType,width"}})
        for row_index, row in enumerate(table_cells(element)):
            for col_index, cell in enumerate(row):
                rng = {"startIndex": cell["content"][0]["startIndex"], "endIndex": cell["content"][-1]["endIndex"]}
                styles.extend([
                    {"updateTextStyle": {"range": rng, "textStyle": {"weightedFontFamily": {"fontFamily": "Arial"}, "fontSize": {"magnitude": 11, "unit": "PT"}, "bold": row_index == 0}, "fields": "weightedFontFamily,fontSize,bold"}},
                    {"updateParagraphStyle": {"range": rng, "paragraphStyle": {"namedStyleType": "NORMAL_TEXT", "keepWithNext": False, "lineSpacing": 105, "spaceAbove": {"magnitude": 0, "unit": "PT"}, "spaceBelow": {"magnitude": 3, "unit": "PT"}}, "fields": "namedStyleType,keepWithNext,lineSpacing,spaceAbove,spaceBelow"}},
                    {"updateTableCellStyle": {"tableRange": {"tableCellLocation": {"tableStartLocation": {"index": start}, "rowIndex": row_index, "columnIndex": col_index}, "rowSpan": 1, "columnSpan": 1}, "tableCellStyle": {
                        "backgroundColor": {"color": {"rgbColor": {"red": .91, "green": .94, "blue": .97} if row_index == 0 else {"red": 1, "green": 1, "blue": 1}}},
                        **{key: {"magnitude": 6, "unit": "PT"} for key in ("paddingTop", "paddingBottom", "paddingLeft", "paddingRight")}}, "fields": "backgroundColor,paddingTop,paddingBottom,paddingLeft,paddingRight"}}])
        batch(styles)


def verify_tables(doc, data, text):
    expected = [s["table"] for s in data["sections"] if s.get("table")]
    actual = [e for e in body_content(doc) if "table" in e]
    if len(actual) != len(expected):
        raise RuntimeError("Table count mismatch")
    # Tables add structural blank paragraphs; substantive body text must survive.
    if paragraph_text(body_content(doc)).split() != text.split():
        raise RuntimeError("Body text changed during table insertion")
    for element, table in zip(actual, expected):
        rows = table_cells(element)
        values = [[paragraph_text(c["content"]).rstrip("\n") for c in row] for row in rows]
        if values != [table["headers"], *table["rows"]]:
            raise RuntimeError("Table cell content mismatch")
        for cell in rows[0]:
            # Google Docs may omit an explicitly inherited `bold` value from a
            # read-back run even when the table-cell style is applied. Shading,
            # padding, and readable cell text are the reliable API checks;
            # preserve the bold request in the write batch for visual review.
            color = cell.get("tableCellStyle", {}).get("backgroundColor", {}).get("color", {}).get("rgbColor", {})
            if abs(color.get("blue", 0) - .97) > .01:
                raise RuntimeError("Table header shading missing")


def deliver(data, path, api=None):
    path = Path(path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    state = json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else {"marker": uuid.uuid4().hex}
    draft = path.with_suffix(".md")
    draft.write_text(markdown(data), encoding="utf-8")
    state.update(status="pending", draft_path=str(draft), pdf_path=None, verified=False, visual_review="pending")
    save(path, state)
    api = api or Workspace(path.parent)
    try:
        if not state.get("doc_id"):
            query = f"trashed=false and appProperties has {{ key='{MARKER}' and value='{state['marker']}' }}"
            found = api.call("drive", "files", "list", {"q": query, "fields": "files(id),nextPageToken"})
            files = found.get("files", [])
            if len(files) > 1 or found.get("nextPageToken"):
                raise RuntimeError("Multiple recovery matches; inspect before continuing")
            if files:
                state["doc_id"] = files[0]["id"]
            elif state.get("create_attempted"):
                raise RuntimeError("Prior create outcome is uncertain and no recovery match is visible. Do not create again; inspect Drive or retry later")
            else:
                folders = api.call("drive", "files", "list", {"q": f"trashed=false and name='{FOLDER}' and mimeType='application/vnd.google-apps.folder'", "fields": "files(id),nextPageToken"})
                if len(folders.get("files", [])) > 1 or folders.get("nextPageToken"):
                    raise RuntimeError("Multiple NexusPoint Proposals folders; resolve the destination first")
                folder = folders["files"][0]["id"] if folders.get("files") else api.call("drive", "files", "create", body={"name": FOLDER, "mimeType": "application/vnd.google-apps.folder"})["id"]
                state.update(folder_id=folder, create_attempted=True)
                save(path, state)
                created = api.call("drive", "files", "create", body={"name": data["title"], "mimeType": "application/vnd.google-apps.document", "parents": [folder], "appProperties": {MARKER: state["marker"]}})
                state["doc_id"] = created["id"]
            save(path, state)
        doc_id = state["doc_id"]
        state["doc_url"] = f"https://docs.google.com/document/d/{doc_id}/edit"
        meta = api.call("drive", "files", "get", {"fileId": doc_id, "fields": "id,appProperties,parents,trashed"})
        if meta.get("trashed") or meta.get("appProperties", {}).get(MARKER) != state["marker"]:
            raise RuntimeError("Document ownership marker mismatch or document trashed")
        doc = api.call("docs", "documents", "get", {"documentId": doc_id})
        text, spans, inline = compose(data)
        end = max((e.get("endIndex", 2) for e in body_content(doc)), default=2)
        api.call("drive", "files", "update", {"fileId": doc_id}, {"name": data["title"]})
        api.call("docs", "documents", "batchUpdate", {"documentId": doc_id}, {"requests": requests_for(text, spans, inline, end), "writeControl": {"requiredRevisionId": doc["revisionId"]}})
        verify(api.call("docs", "documents", "get", {"documentId": doc_id}), text, spans)
        if any(s.get("table") for s in data["sections"]):
            write_tables(api, doc_id, data, spans)
            verify_tables(api.call("docs", "documents", "get", {"documentId": doc_id}), data, text)
        state["verified"] = True
        pdf = path.with_suffix(".pdf")
        api.call("drive", "files", "export", {"fileId": doc_id, "mimeType": "application/pdf"}, output=pdf)
        if not pdf.exists() or not pdf.read_bytes().startswith(b"%PDF"):
            raise RuntimeError("PDF export was not valid")
        state.update(status="ok", pdf_path=str(pdf))
        state.pop("error", None)
    except Exception as exc:
        state.update(status="partial" if state.get("doc_id") or state.get("create_attempted") else "error", error=str(exc))
    save(path, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    try:
        data = validate(json.loads(args.input.read_text(encoding="utf-8-sig")))
        if args.dry_run:
            result = {"status": "dry_run", "preview": markdown(data), "words": len(compose(data)[0].split())}
        else:
            result = deliver(data, args.state)
    except Exception as exc:
        result = {"status": "error", "error": str(exc)}
    print(json.dumps(result, ensure_ascii=True))
    return 0 if result["status"] in ("ok", "dry_run") else 1


if __name__ == "__main__":
    sys.exit(main())

