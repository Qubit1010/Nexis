#!/usr/bin/env python3
"""Canonical Exa.ai client for Nexis — web search, contents, cited answers, and agentic research.

Why this exists: it gives every Nexis skill/script one well-behaved entry point to Exa, with
high-quality source curation (neural search, category + domain filters, date windows) instead of
generic web scraping. Auth is read from EXA_API_KEY in the repo .env (gitignored) or the environment,
so nothing needs to be exported by hand.

Use as a CLI:
    python tools/exa/exa_client.py search "best way to learn reinforcement learning" \
        --num 8 --type deep --highlights
    python tools/exa/exa_client.py search "transformer tutorial" --category "research paper" --text
    python tools/exa/exa_client.py answer "what is retrieval practice and how big is its effect?"
    python tools/exa/exa_client.py contents https://example.com/post --text
    python tools/exa/exa_client.py research "Summarize the 2026 evidence on spaced repetition with sources" \
        --model exa-research

Use as a library:
    from tools.exa.exa_client import get_client, search, answer, research
    res = search("spaced repetition meta-analysis", num_results=10, category="research paper")

Exa SDK reference (exa-py >= 2.x):
    client.search(query, *, contents={text,highlights,summary}, num_results, type, category,
                  include_domains, exclude_domains, start_published_date, end_published_date, ...)
    client.answer(query, *, text=False, model="exa"|"exa-pro")  -> .answer, .citations
    client.get_contents(urls, ...)
    client.research.create(instructions=..., model="exa-research-fast"|"exa-research")
    client.research.poll_until_finished(research_id, timeout_ms=...)
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
from pathlib import Path
from typing import Any

try:
    from exa_py import Exa
except ImportError:  # pragma: no cover
    print("exa-py not installed. Run: python -m pip install exa-py", file=sys.stderr)
    sys.exit(2)

# Attribute API usage so Exa dashboards can see it's coming from Nexis tooling.
EXA_INTEGRATION_HEADER = "nexis"


# --------------------------------------------------------------------------- #
# Key loading
# --------------------------------------------------------------------------- #
def _find_repo_env() -> Path | None:
    """Walk up from this file to locate the repo-root .env (the standard Nexis location)."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        candidate = parent / ".env"
        if candidate.exists():
            return candidate
    return None


def load_api_key() -> str:
    """Return the Exa API key from the environment, falling back to the repo .env."""
    key = os.environ.get("EXA_API_KEY")
    if key:
        return key.strip()
    env_path = _find_repo_env()
    if env_path:
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("EXA_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(
        "EXA_API_KEY not found in environment or repo .env. "
        "Add EXA_API_KEY=... to the Nexis .env."
    )


def get_client() -> Exa:
    """Build an authenticated Exa client with the Nexis integration header set."""
    client = Exa(api_key=load_api_key())
    try:
        client.headers["x-exa-integration"] = EXA_INTEGRATION_HEADER
    except Exception:  # noqa: BLE001 - header dict may differ across SDK versions
        pass
    return client


# --------------------------------------------------------------------------- #
# Core operations (importable)
# --------------------------------------------------------------------------- #
def _build_contents(text: bool, highlights: bool, summary: bool) -> dict[str, Any] | None:
    contents: dict[str, Any] = {}
    if text:
        contents["text"] = True
    if highlights:
        contents["highlights"] = True
    if summary:
        contents["summary"] = True
    return contents or None


def _result_to_dict(item: Any) -> dict[str, Any]:
    return {
        "title": getattr(item, "title", None),
        "url": getattr(item, "url", ""),
        "id": getattr(item, "id", None),
        "author": getattr(item, "author", None),
        "published_date": getattr(item, "published_date", None),
        "score": getattr(item, "score", None),
        "text": getattr(item, "text", None),
        "summary": getattr(item, "summary", None),
        "highlights": list(getattr(item, "highlights", None) or []),
    }


def search(
    query: str,
    *,
    num_results: int = 10,
    type: str | None = "auto",
    category: str | None = None,
    include_domains: list[str] | None = None,
    exclude_domains: list[str] | None = None,
    start_published_date: str | None = None,
    end_published_date: str | None = None,
    text: bool = True,
    highlights: bool = False,
    summary: bool = False,
    client: Exa | None = None,
) -> dict[str, Any]:
    """Neural/keyword web search with optional page contents. Returns a JSON-able dict."""
    client = client or get_client()
    kwargs: dict[str, Any] = {"query": query, "num_results": num_results}
    if type:
        kwargs["type"] = type
    if category:
        kwargs["category"] = category
    if include_domains:
        kwargs["include_domains"] = include_domains
    if exclude_domains:
        kwargs["exclude_domains"] = exclude_domains
    if start_published_date:
        kwargs["start_published_date"] = start_published_date
    if end_published_date:
        kwargs["end_published_date"] = end_published_date
    contents = _build_contents(text, highlights, summary)
    if contents is not None:
        kwargs["contents"] = contents

    response = client.search(**kwargs)
    results = [_result_to_dict(r) for r in getattr(response, "results", []) or []]
    return {
        "query": query,
        "type": type,
        "num_results": len(results),
        "results": results,
    }


def answer(
    query: str,
    *,
    text: bool = False,
    model: str = "exa",
    client: Exa | None = None,
) -> dict[str, Any]:
    """Ask Exa for a cited answer (LLM over live search). Returns answer text + citations."""
    client = client or get_client()
    response = client.answer(query, text=text, model=model)
    citations = []
    for c in getattr(response, "citations", []) or []:
        citations.append({
            "title": getattr(c, "title", None),
            "url": getattr(c, "url", ""),
            "id": getattr(c, "id", None),
            "published_date": getattr(c, "published_date", None),
            "author": getattr(c, "author", None),
            "text": getattr(c, "text", None),
        })
    return {
        "query": query,
        "answer": getattr(response, "answer", None),
        "citations": citations,
    }


def get_contents(urls: list[str], *, text: bool = True, highlights: bool = False,
                 summary: bool = False, client: Exa | None = None) -> dict[str, Any]:
    """Fetch cleaned page contents for one or more URLs."""
    client = client or get_client()
    contents = _build_contents(text, highlights, summary) or {"text": True}
    response = client.get_contents(urls, **contents)
    results = [_result_to_dict(r) for r in getattr(response, "results", []) or []]
    return {"urls": urls, "num_results": len(results), "results": results}


def research(
    instructions: str,
    *,
    model: str = "exa-research-fast",
    timeout_ms: int = 600_000,
    client: Exa | None = None,
) -> dict[str, Any]:
    """Run an agentic Exa research task (multi-step search + synthesis) and wait for the report.

    model: 'exa-research-fast' (default, quicker) or 'exa-research' (deeper).
    """
    client = client or get_client()
    task = client.research.create(instructions=instructions, model=model)
    task_id = getattr(task, "research_id", None) or getattr(task, "id", None)
    finished = client.research.poll_until_finished(task_id, timeout_ms=timeout_ms)

    # Normalize the report + citations across SDK shapes.
    report = (
        getattr(finished, "report", None)
        or getattr(finished, "output", None)
        or getattr(finished, "data", None)
    )
    citations = []
    raw_cites = getattr(finished, "citations", None) or []
    if isinstance(raw_cites, dict):
        # citations keyed by field -> list
        flat = []
        for v in raw_cites.values():
            if isinstance(v, list):
                flat.extend(v)
        raw_cites = flat
    for c in raw_cites:
        citations.append({
            "title": getattr(c, "title", None) if not isinstance(c, dict) else c.get("title"),
            "url": getattr(c, "url", None) if not isinstance(c, dict) else c.get("url"),
        })
    return {
        "instructions": instructions,
        "model": model,
        "research_id": task_id,
        "status": getattr(finished, "status", None),
        "report": report if isinstance(report, str) else _stringify(report),
        "citations": citations,
        "raw": _stringify(finished),
    }


def _stringify(obj: Any) -> Any:
    """Best-effort convert SDK objects to JSON-able structures for the --raw dump."""
    if obj is None or isinstance(obj, (str, int, float, bool, list, dict)):
        return obj
    for attr in ("model_dump", "dict", "to_dict"):
        fn = getattr(obj, attr, None)
        if callable(fn):
            try:
                return fn()
            except Exception:  # noqa: BLE001
                pass
    return str(obj)


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _emit(payload: dict[str, Any], output: str | None) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if output:
        Path(output).write_text(text, encoding="utf-8")
        n = payload.get("num_results", "")
        print(f"Wrote {n} result(s) to {output}")
    else:
        print(text)


def _split_csv(value: str | None) -> list[str] | None:
    if not value:
        return None
    items = [x.strip() for x in value.split(",") if x.strip()]
    return items or None


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Exa.ai client for Nexis (search, contents, answer, research).")
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("search", help="Web search with optional contents.")
    s.add_argument("query")
    s.add_argument("--num", "--num-results", type=int, default=10, dest="num_results")
    s.add_argument("--type", default="auto", choices=["auto", "fast", "deep", "keyword", "neural"])
    s.add_argument("--category", default=None,
                   choices=["company", "research paper", "news", "github", "personal site",
                            "financial report", "people", "tweet", "pdf"])
    s.add_argument("--include-domains", default=None, help="Comma-separated allowlist.")
    s.add_argument("--exclude-domains", default=None, help="Comma-separated blocklist.")
    s.add_argument("--start-date", default=None, dest="start_published_date", help="ISO published-after.")
    s.add_argument("--end-date", default=None, dest="end_published_date", help="ISO published-before.")
    s.add_argument("--text", action="store_true", help="Include full text per result.")
    s.add_argument("--highlights", action="store_true", help="Include highlight snippets.")
    s.add_argument("--summary", action="store_true", help="Include an AI summary per result.")
    s.add_argument("-o", "--output", default=None)

    a = sub.add_parser("answer", help="Cited LLM answer over live search.")
    a.add_argument("query")
    a.add_argument("--text", action="store_true", help="Include source text in citations.")
    a.add_argument("--model", default="exa", choices=["exa", "exa-pro"])
    a.add_argument("-o", "--output", default=None)

    c = sub.add_parser("contents", help="Fetch cleaned contents for URLs.")
    c.add_argument("urls", nargs="+")
    c.add_argument("--text", action="store_true")
    c.add_argument("--highlights", action="store_true")
    c.add_argument("--summary", action="store_true")
    c.add_argument("-o", "--output", default=None)

    r = sub.add_parser("research", help="Agentic multi-step research task with a synthesized report.")
    r.add_argument("instructions")
    r.add_argument("--model", default="exa-research-fast", choices=["exa-research-fast", "exa-research"])
    r.add_argument("--timeout-ms", type=int, default=600_000)
    r.add_argument("-o", "--output", default=None)
    return p


def main(argv: list[str] | None = None) -> int:
    # Force UTF-8 stdout so result titles with emoji/unicode don't crash on Windows cp1252.
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass

    args = build_parser().parse_args(argv)
    client = get_client()

    if args.cmd == "search":
        payload = search(
            args.query, num_results=args.num_results, type=args.type, category=args.category,
            include_domains=_split_csv(args.include_domains),
            exclude_domains=_split_csv(args.exclude_domains),
            start_published_date=args.start_published_date,
            end_published_date=args.end_published_date,
            text=args.text or not (args.highlights or args.summary),
            highlights=args.highlights, summary=args.summary, client=client,
        )
    elif args.cmd == "answer":
        payload = answer(args.query, text=args.text, model=args.model, client=client)
    elif args.cmd == "contents":
        payload = get_contents(args.urls, text=args.text or not (args.highlights or args.summary),
                               highlights=args.highlights, summary=args.summary, client=client)
    elif args.cmd == "research":
        payload = research(args.instructions, model=args.model, timeout_ms=args.timeout_ms, client=client)
    else:  # pragma: no cover
        build_parser().print_help()
        return 2

    _emit(payload, getattr(args, "output", None))
    return 0


if __name__ == "__main__":
    sys.exit(main())
