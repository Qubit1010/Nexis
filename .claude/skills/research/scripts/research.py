#!/usr/bin/env python3
"""Meta-research orchestrator — combine Exa / Tavily / Serper / Jina across depth + mode.

Depth  : light (1 fast service + answer) | medium (2-3 services, fused) | deep (all + extract + synthesize)
Mode   : auto | general | entity (person/company) | scientific
Fusion : default; dedupe by URL + rank by cross-source agreement. --single runs one backend deep.

Examples:
    python research.py --query "best open source vector databases 2026" --depth medium
    python research.py --query "founder of Perplexity AI" --mode entity --depth deep --save
    python research.py --query "spaced repetition effect size" --mode scientific --depth deep
    python research.py --query "..." --single --services exa --depth deep      # Exa agentic research
    python research.py --query "..." --single --services openai --depth deep    # OpenAI web research
"""
from __future__ import annotations

import argparse
import concurrent.futures as cf
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import exa_adapter
import jina_client
import serper_client
import synthesize as synth
import tavily_client
from _env import repo_root
from fuse import fuse

# depth -> per-mode default service set
_SERVICES = {
    "general":    {"light": ["tavily"], "medium": ["exa", "tavily", "serper"], "deep": ["exa", "tavily", "serper", "jina"]},
    "entity":     {"light": ["serper"], "medium": ["serper", "exa"], "deep": ["serper", "exa", "jina"]},
    "scientific": {"light": ["exa"], "medium": ["exa", "tavily"], "deep": ["exa", "tavily"]},
}
_PERSON_HINT = re.compile(r"\b(founder|co-?founder|ceo|cto|owner|president|who is|email|contact)\b", re.I)
_SCI_HINT = re.compile(r"\b(study|studies|meta-?analysis|clinical|peer-?reviewed|journal|paper|trial|efficacy|effect size)\b", re.I)


def detect_mode(query: str) -> str:
    if _PERSON_HINT.search(query):
        return "entity"
    if _SCI_HINT.search(query):
        return "scientific"
    return "general"


def _entity_queries(query: str) -> list[str]:
    """A couple of Google-dork variants for people/company lookups."""
    qs = [query]
    if "site:linkedin" not in query.lower():
        qs.append(f"{query} site:linkedin.com/in")
    return qs


def _run_service(name: str, query: str, mode: str, depth: str, num: int) -> dict:
    """Call one backend, return {results:[...], answer?:str}. Raises on failure (caller catches)."""
    if name == "exa":
        cat = {"scientific": "research paper",
               "entity": "people" if _PERSON_HINT.search(query) else "company"}.get(mode)
        return exa_adapter.search(query, num=num, category=cat, text=(depth == "deep"))
    if name == "tavily":
        return tavily_client.search(query, depth="advanced" if depth == "deep" else "basic",
                                    max_results=num, include_answer=True)
    if name == "serper":
        if mode == "entity":
            merged: list[dict] = []
            box = kg = None
            for q in _entity_queries(query):
                d = serper_client.search(q, num=num)
                merged.extend(d["results"])
                box = box or d.get("answer_box")
                kg = kg or d.get("knowledge_graph")
            return {"results": merged, "answer_box": box, "knowledge_graph": kg}
        return serper_client.search(query, num=num)
    if name == "jina":
        return jina_client.search(query, num=num)
    raise ValueError(f"unknown service: {name}")


def run(query: str, *, depth: str, mode: str, services: list[str], single: bool,
        do_synth: bool, num: int, context: str) -> dict:
    if mode == "auto":
        mode = detect_mode(query)

    # Single-service deep backends that aren't plain search.
    if single and depth == "deep" and services[:1] == ["exa"]:
        r = exa_adapter.deep_research(query)
        return {"mode": mode, "depth": depth, "query": query, "report": r.get("report"),
                "results": [{"title": c["title"], "url": c["url"], "sources": ["exa"], "snippet": ""}
                            for c in r.get("citations", [])], "answer": None}
    if single and services[:1] == ["openai"]:
        return {"mode": mode, "depth": depth, "query": query,
                "report": synth.openai_web_research(query, depth=depth, context=context),
                "results": [], "answer": None}

    if not services:
        services = _SERVICES[mode][depth]

    # Fan out across services in parallel.
    per_service: list[list[dict]] = []
    answer = None
    with cf.ThreadPoolExecutor(max_workers=max(1, len(services))) as ex:
        futs = {ex.submit(_run_service, s, query, mode, depth, num): s for s in services}
        for fut in cf.as_completed(futs):
            s = futs[fut]
            try:
                data = fut.result()
            except Exception as e:  # noqa: BLE001 - one dead service must not sink the run
                print(f"[warn] {s} failed: {e}", file=sys.stderr)
                continue
            per_service.append(data.get("results", []))
            if answer is None and data.get("answer"):
                answer = data["answer"]

    ranked = fuse(*per_service)

    # Light mode: the fast answer + a few sources, no LLM synthesis.
    if depth == "light":
        return {"mode": mode, "depth": depth, "query": query, "answer": answer,
                "results": ranked[:num], "report": None}

    report = None
    if do_synth:
        top = ranked[:8]
        if depth == "deep":  # enrich with clean page text before writing
            urls = [r["url"] for r in top if r.get("url")][:6]
            try:
                extracted = {c["url"]: c.get("text") for c in exa_adapter.contents(urls)["results"]}
                for r in top:
                    if extracted.get(r["url"]):
                        r["text"] = extracted[r["url"]]
            except Exception as e:  # noqa: BLE001
                print(f"[warn] content extraction failed: {e}", file=sys.stderr)
        report = synth.synthesize(query, top, mode=mode, depth=depth, context=context)

    return {"mode": mode, "depth": depth, "query": query, "answer": answer,
            "results": ranked, "report": report}


# --------------------------------------------------------------------------- #
def _slugify(text: str) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower().strip())
    return re.sub(r"[\s_]+", "-", text)[:60].rstrip("-")


def _save(payload: dict) -> Path:
    out_dir = repo_root() / "research"
    out_dir.mkdir(exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    fp = out_dir / f"{date}-{_slugify(payload['query'])}.md"
    fp.write_text(_render(payload, date), encoding="utf-8")
    return fp


def _render(payload: dict, date: str | None = None) -> str:
    date = date or datetime.now().strftime("%Y-%m-%d")
    lines = [f"# {payload['query']}", "",
             f"*mode: {payload['mode']} | depth: {payload['depth']} | {date}*", "", "---", ""]
    if payload.get("answer"):
        lines += ["## Answer", "", payload["answer"], ""]
    if payload.get("report"):
        lines += [payload["report"], ""]
    lines += ["## Ranked Sources", ""]
    for i, r in enumerate(payload.get("results", []), 1):
        srcs = "+".join(r.get("sources", [])) or r.get("source", "")
        lines.append(f"{i}. [{r.get('title') or '(untitled)'}]({r.get('url','')}) — `{srcs}`")
        if r.get("snippet"):
            lines.append(f"   > {r['snippet'][:200]}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:  # noqa: BLE001
        pass
    p = argparse.ArgumentParser(description="Meta-research orchestrator (Exa/Tavily/Serper/Jina).")
    p.add_argument("--query", required=True)
    p.add_argument("--depth", choices=["light", "medium", "deep"], default="medium")
    p.add_argument("--mode", choices=["auto", "general", "entity", "scientific"], default="auto")
    p.add_argument("--services", default="", help="Comma list to override auto (exa,tavily,serper,jina,openai).")
    p.add_argument("--single", action="store_true", help="Run only the given service(s) as a single-backend deep pass.")
    p.add_argument("--no-synth", action="store_true", help="Skip LLM synthesis (medium/deep).")
    p.add_argument("--num", type=int, default=10, help="Results per service.")
    p.add_argument("--save", action="store_true", help="Save the report to research/.")
    p.add_argument("--json", action="store_true", help="Emit raw JSON.")
    args = p.parse_args(argv)

    services = [s.strip() for s in args.services.split(",") if s.strip()]
    do_synth = not args.no_synth
    payload = run(args.query, depth=args.depth, mode=args.mode, services=services,
                  single=args.single, do_synth=do_synth, num=args.num, context="")

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(_render(payload))

    if args.save or (args.depth == "deep" and payload.get("report")):
        fp = _save(payload)
        print(f"\n[saved] {fp.relative_to(repo_root())}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
