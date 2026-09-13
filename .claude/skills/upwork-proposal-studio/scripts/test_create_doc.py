import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import create_doc as m

DATA = {"title": "Test", "sections": [{"heading": "Plan", "body": "Read café and 𐐀 correctly.", "bullets": ["Verify the result."]}]}


def rendered(data):
    text, spans, _ = m.compose(data)
    content = []
    raw = text.encode("utf-16-le")
    for start, end, style in spans:
        para = {"paragraphStyle": {"namedStyleType": style}, "elements": [{"textRun": {
            "content": raw[(start-1)*2:(end-1)*2].decode("utf-16-le"),
            "textStyle": {"fontSize": {"magnitude": 18 if style == "TITLE" else 13 if style == "HEADING_1" else 11}, "weightedFontFamily": {"fontFamily": "Arial"}}}}]}
        if style == "BULLET":
            para["bullet"] = {"listId": "list"}
        content.append({"startIndex": start, "endIndex": end, "paragraph": para})
    return {"revisionId": "rev", "body": {"content": content}, "documentStyle": {"marginLeft": {"magnitude": 54}}}


class Fake:
    def __init__(self, data=DATA):
        self.data = data
        self.marker = None
        self.created = 0
        self.written = False
        self.fail_export = False
        self.lose_create = False

    def call(self, service, resource, method, params=None, body=None, output=None):
        if method == "list":
            if "appProperties" in params["q"]:
                return {"files": [{"id": "doc"}] if self.created else []}
            return {"files": [{"id": "folder"}]}
        if method == "create":
            self.created += 1
            self.marker = body["appProperties"]
            if self.lose_create:
                self.lose_create = False
                raise TimeoutError("lost response")
            return {"id": "doc"}
        if service == "drive" and method == "get":
            return {"appProperties": self.marker, "parents": ["folder"]}
        if service == "docs" and method == "get":
            return rendered(self.data) if self.written else {"revisionId": "rev", "body": {"content": [{"endIndex": 2}]}}
        if method == "batchUpdate":
            self.written = True
        if method == "export":
            if self.fail_export:
                raise RuntimeError("export unavailable")
            output.write_bytes(b"%PDF-fake")
        return {}


class Tests(unittest.TestCase):
    def test_inline_bold_runs(self):
        data = {"title": "T", "sections": [{"body_runs": [{"text": "Fee: "}, {"text": "$1,500/month", "bold": True}], "bullet_runs": [[{"text": "Deliver "}, {"text": "12 posts", "bold": True}]]}]}
        m.validate(data)
        text, spans, inline = m.compose(data)
        self.assertEqual(text, "T\nFee: $1,500/month\nDeliver 12 posts\n")
        self.assertEqual(len(inline), 2)
        requests = m.requests_for(text, spans, inline)
        self.assertEqual(sum(1 for r in requests if "updateTextStyle" in r and r["updateTextStyle"]["fields"] == "bold"), 2)

    def test_table_validation_and_markdown(self):
        data = {"title": "T", "sections": [{"table": {"headers": ["Fee", "Scope"], "rows": [["$1", "Café 𐐀"]]}}]}
        m.validate(data)
        self.assertIn("| $1 | Café 𐐀 |", m.markdown(data))
        self.assertEqual(m.compose(data)[1][-1][2], "TABLE")
        data["sections"][0]["table"]["rows"][0].append("extra")
        with self.assertRaises(ValueError):
            m.validate(data)

    def test_table_readback_checks_cells_and_header(self):
        data = {"title": "T", "sections": [{"table": {"headers": ["A", "B"], "rows": [["𐐀", "value"]]}}]}
        def cell(value, bold=False):
            return {"content": [{"paragraph": {"elements": [{"textRun": {"content": value + "\n", "textStyle": {"bold": bold}}}]}}], "tableCellStyle": {"backgroundColor": {"color": {"rgbColor": {"blue": .97}}}}}
        doc = {"body": {"content": [{"paragraph": {"elements": [{"textRun": {"content": "T\n\n"}}]}}, {"table": {"tableRows": [{"tableCells": [cell("A", True), cell("B", True)]}, {"tableCells": [cell("𐐀"), cell("value")]}]}}]}}
        m.verify_tables(doc, data, m.compose(data)[0])
        doc["body"]["content"][1]["table"]["tableRows"][1]["tableCells"][0] = cell("wrong")
        with self.assertRaises(RuntimeError):
            m.verify_tables(doc, data, m.compose(data)[0])

    def test_invalid_input(self):
        for data in ({}, {"title": "x", "sections": []}, {"title":"x", "sections":[{"bullets":"bad"}]}):
            with self.assertRaises(ValueError):
                m.validate(data)

    def test_unicode_ranges_and_verification(self):
        text, spans, _ = m.compose(DATA)
        self.assertEqual(spans[-1][1], 1 + m.units(text))
        self.assertGreater(m.units(text), len(text))
        m.verify(rendered(DATA), text, spans)
        broken = rendered(DATA)
        broken["body"]["content"][-1]["paragraph"].pop("bullet")
        with self.assertRaises(RuntimeError):
            m.verify(broken, text, spans)

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "input.json"
            source.write_text(json.dumps(DATA), encoding="utf-8")
            result = subprocess.run([sys.executable, str(Path(m.__file__)), "--input", str(source), "--state", str(root / "state.json"), "--dry-run"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(list(root.iterdir()), [source])

    def test_inherited_font_is_resolved(self):
        doc = rendered(DATA)
        doc["namedStyles"] = {"styles": [{"namedStyleType": "NORMAL_TEXT", "textStyle": {"weightedFontFamily": {"fontFamily": "Arial"}, "fontSize": {"magnitude": 11}}}]}
        for p in doc["body"]["content"]:
            p["paragraph"]["elements"][0]["textRun"]["textStyle"].pop("weightedFontFamily")
        text, spans, _ = m.compose(DATA)
        m.verify(doc, text, spans)

    def test_retry_replaces_body(self):
        text, spans, inline = m.compose(DATA)
        requests = m.requests_for(text, spans, inline, 100)
        self.assertEqual(requests[0]["deleteContentRange"]["range"], {"startIndex": 1, "endIndex": 99})
        self.assertEqual(requests[1]["insertText"]["text"], text)

    def test_export_failure_recovers_same_doc(self):
        with tempfile.TemporaryDirectory() as directory:
            api = Fake()
            api.fail_export = True
            path = Path(directory) / "state.json"
            first = m.deliver(DATA, path, api)
            self.assertEqual(first["status"], "partial")
            self.assertTrue(Path(first["draft_path"]).exists())
            api.fail_export = False
            self.assertEqual(m.deliver(DATA, path, api)["status"], "ok")
            self.assertEqual(api.created, 1)

    def test_lost_create_response_recovers_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            api = Fake()
            api.lose_create = True
            path = Path(directory) / "state.json"
            self.assertEqual(m.deliver(DATA, path, api)["status"], "partial")
            self.assertEqual(m.deliver(DATA, path, api)["status"], "ok")
            self.assertEqual(api.created, 1)

    def test_uncertain_create_without_match_stops(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps({"marker":"abc", "create_attempted":True}))
            api = Fake()
            self.assertEqual(m.deliver(DATA, path, api)["status"], "partial")
            self.assertEqual(api.created, 0)

    def test_wrong_marker_stops(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "state.json"
            path.write_text(json.dumps({"marker":"abc", "doc_id":"other"}))
            api = Fake()
            result = m.deliver(DATA, path, api)
            self.assertEqual(result["status"], "partial")
            self.assertFalse(api.written)


if __name__ == "__main__":
    unittest.main()
