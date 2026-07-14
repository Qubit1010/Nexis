"""Extraction modes (orthogonal to the engine): raw | links | css | llm.

- raw   : the page markdown as-is (already on the engine result).
- links : the page's links (already on the engine result, or via firecrawl /map).
- css   : deterministic CSS-schema -> rows. Fast, stable, free. Best when the DOM is regular.
- llm   : schema-driven LLM extraction -> clean rows. For messy/varied pages where CSS breaks.
          This is the "well-formatted data" answer. OpenAI structured output, mirrors research/synthesize.py.

CSS schema (compatible with crawl4ai's JsonCssExtractionStrategy shape):
    {"container": ".card", "fields": [
        {"name": "title", "selector": "h2", "type": "text"},
        {"name": "url",   "selector": "a",  "type": "attr", "attr": "href"}]}
LLM schema:
    {"fields": [{"name": "company", "description": "business name"}, ...], "many": true}
"""
from __future__ import annotations

import json
import re
import sys
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, __import__("os").path.dirname(__file__))
from _env import get_key  # noqa: E402

LLM_MODEL = "gpt-5.2"          # latest small-capable; falls back to gpt-4.1-mini on model error
LLM_FALLBACK = "gpt-4.1-mini"
MAX_INPUT_CHARS = 48_000       # keep the LLM call inside token budget


# ---- CSS extraction ---------------------------------------------------------
def _cell(el, field: dict) -> str:
    if el is None:
        return ""
    typ = field.get("type", "text")
    if typ == "attr":
        return (el.get(field.get("attr", "href")) or "").strip()
    if typ == "html":
        return str(el)
    return el.get_text(strip=True)


def extract_css(html: str, schema: dict, *, base_url: str = "") -> list[dict]:
    """Deterministic rows from a repeated container + per-field selectors."""
    soup = BeautifulSoup(html or "", "html.parser")
    container = schema.get("container")
    fields = schema.get("fields") or []
    scopes = soup.select(container) if container else [soup]
    rows = []
    for scope in scopes:
        row = {}
        for f in fields:
            el = scope.select_one(f["selector"]) if f.get("selector") else scope
            val = _cell(el, f)
            if f.get("type") == "attr" and base_url and val:
                val = urljoin(base_url, val)
            row[f["name"]] = val
        if any(row.values()):
            rows.append(row)
    return rows


# ---- LLM extraction ---------------------------------------------------------
def _strip_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return text.strip()


def _responses_json(client, model: str, system: str, user: str) -> str:
    try:
        return client.responses.create(model=model, instructions=system, input=user).output_text
    except Exception as e:  # noqa: BLE001 - fall back off the newest model on a model error
        if model != LLM_FALLBACK and "model" in str(e).lower():
            print(f"[extract] {model} unavailable ({e}); falling back to {LLM_FALLBACK}", file=sys.stderr)
            return client.responses.create(model=LLM_FALLBACK, instructions=system, input=user).output_text
        raise


def extract_llm(content: str, schema: dict, *, instructions: str = "") -> list[dict]:
    """Schema-driven extraction from page text/markdown. Returns validated rows (list of dicts).

    Validation at the trust boundary: the model can return anything, so we coerce to a list of
    dicts and keep only the requested field names — never trust the shape blindly.
    """
    from openai import OpenAI

    fields = schema.get("fields") or []
    if not fields:
        raise ValueError("llm schema needs a non-empty 'fields' list")
    many = schema.get("many", True)
    names = [f["name"] for f in fields]
    field_lines = "\n".join(f"- {f['name']}: {f.get('description', '')}" for f in fields)
    shape = "a JSON array of objects" if many else "a single JSON object"
    system = (
        "You extract structured data from web page content. Return ONLY valid JSON, no prose, no code "
        "fence. Use exactly the given field names. If a field is missing on the page, use an empty string. "
        "Never invent values that are not present in the content."
    )
    user = (
        f"{instructions or 'Extract every matching record from the content below.'}\n\n"
        f"Fields to extract:\n{field_lines}\n\n"
        f"Return {shape} with those exact keys.\n\n"
        f"--- CONTENT ---\n{(content or '')[:MAX_INPUT_CHARS]}"
    )
    client = OpenAI(api_key=get_key("OPENAI_API_KEY"))
    raw = _strip_fence(_responses_json(client, LLM_MODEL, system, user))
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        m = re.search(r"(\[.*\]|\{.*\})", raw, re.S)  # salvage a JSON blob from stray prose
        if not m:
            raise ValueError(f"llm extraction returned non-JSON: {raw[:200]}")
        data = json.loads(m.group(1))
    records = data if isinstance(data, list) else [data]
    return [{n: (rec.get(n, "") if isinstance(rec, dict) else "") for n in names} for rec in records]


# ---- dispatcher -------------------------------------------------------------
def extract(res: dict, mode: str, *, schema: dict | None = None, instructions: str = "") -> dict:
    """Apply an extraction mode to an engine result. Returns the result with 'rows' populated (css/llm)."""
    if mode == "raw":
        return res
    if mode == "links":
        return res
    if mode == "css":
        if not schema:
            raise ValueError("css mode needs --schema")
        res = dict(res)
        res["rows"] = extract_css(res.get("html") or "", schema, base_url=res.get("url", ""))
        return res
    if mode == "llm":
        if not schema:
            raise ValueError("llm mode needs --schema")
        res = dict(res)
        content = res.get("markdown") or res.get("html") or ""
        res["rows"] = extract_llm(content, schema, instructions=instructions)
        return res
    raise ValueError(f"unknown extract mode: {mode}")


if __name__ == "__main__":
    html = """<ul>
      <li class="card"><h2>Acme Plumbing</h2><a href="/acme">site</a><span class="price">$99</span></li>
      <li class="card"><h2>Bob HVAC</h2><a href="/bob">site</a><span class="price">$120</span></li>
    </ul>"""
    schema = {"container": ".card", "fields": [
        {"name": "title", "selector": "h2", "type": "text"},
        {"name": "url", "selector": "a", "type": "attr", "attr": "href"},
        {"name": "price", "selector": ".price", "type": "text"}]}
    rows = extract_css(html, schema, base_url="https://x.com")
    assert len(rows) == 2, rows
    assert rows[0] == {"title": "Acme Plumbing", "url": "https://x.com/acme", "price": "$99"}, rows[0]
    assert rows[1]["title"] == "Bob HVAC", rows[1]
    print("extract_css self-check OK:", rows)
