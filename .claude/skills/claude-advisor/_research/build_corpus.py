#!/usr/bin/env python3
"""Build (and refresh) the Claude Advisor research corpus in NotebookLM.

This mirrors the marketing-advisor / content-engine research pipeline so the
claude-advisor skill is grounded in cited 2026 sources, per
`.claude/rules/research-backed-skills.md`.

Phases:
  research    - run deep web-research passes into the notebook (default).
                Blocking + sequential (one pass at a time) with --import-all
                --cited-only so each pass fully imports before the next starts.
  synthesize  - ask the Q1-Q8 questions (--json), write q*.json, then build
                a deduped sources.json (uuid_to_index + sources[]).

Usage (PowerShell):
  python build_corpus.py research
  python build_corpus.py synthesize

NotebookLM CLI outputs UTF-8 with a BOM, so we parse with utf-8-sig.
"""
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

NOTEBOOK_ID = "63a3705e-e871-4830-83a5-966f584a3142"
NOTEBOOK_TITLE = "Claude - Complete Guide 2026 (NexusPoint)"
RESEARCH_DIR = Path(__file__).resolve().parent


def find_exe():
    candidates = [
        Path(r"C:\Users\qubit\AppData\Local\Programs\Python\Python312\Scripts\notebooklm.exe"),
        Path(r"C:\Users\Aleem\AppData\Local\Programs\Python\Python312\Scripts\notebooklm.exe"),
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    w = shutil.which("notebooklm")
    if w:
        return w
    raise SystemExit("notebooklm.exe not found")


EXE = find_exe()

# Deep web-research seed queries (one pass each). Phrased to pull current 2026
# sources, including post-cutoff products like Claude Cowork.
QUERIES = {
    "q1_models": (
        "Anthropic Claude model family in 2026: Claude Opus 4.x, Sonnet 4.x, and "
        "Haiku 4.x. Capabilities, context window sizes, pricing per million tokens, "
        "benchmark performance, and how the models differ. What a large language "
        "model is, explained for business owners."
    ),
    "q2_surfaces": (
        "The different ways to use Claude in 2026: Claude.ai web chat (Projects, "
        "Artifacts), Claude Code, Claude Cowork, the Claude Desktop app, the mobile "
        "app, and the Anthropic API. What each product is, what it is for, and when "
        "to use which one."
    ),
    "q3_claude_code": (
        "Claude Code in 2026: what it is, capabilities and limitations, hooks, MCP "
        "servers, subagents, agent skills, plugins, slash commands, headless mode, "
        "the Claude Agent SDK, IDE and terminal integrations, and best practices for "
        "developer productivity."
    ),
    "q4_cowork": (
        "Claude Cowork by Anthropic in 2026: what it is, how the agentic product "
        "works, autonomous multi-step task execution, use cases, limitations, "
        "pricing and availability, and how it differs from Claude Code and Claude.ai."
    ),
    "q5_business": (
        "How businesses and individuals use Claude AI in 2026: real use cases across "
        "operations, marketing, sales, customer support, software development, "
        "research, finance, and legal. Creative and unconventional uses, productivity "
        "gains and ROI, and case studies."
    ),
    "q6_ecosystem": (
        "Best Claude tools and ecosystem in 2026: most useful Claude Code plugins, "
        "MCP servers, GitHub repositories and open-source tools for Claude, plugin "
        "marketplaces, awesome-claude lists, and community resources for power users."
    ),
    "q7_building": (
        "Building applications with the Anthropic Claude API in 2026: tool use and "
        "function calling, Model Context Protocol (MCP), the Claude Agent SDK, prompt "
        "caching, batch processing, cost optimization, and when to build custom "
        "versus use Claude's products."
    ),
    "q8_plans": (
        "Claude pricing and plans in 2026: Free, Pro, Max, Team, and Enterprise "
        "subscription tiers, usage limits, and features per tier. How Claude compares "
        "to ChatGPT and Google Gemini for business use, and a decision framework for "
        "choosing the right Claude product and model for a task."
    ),
}

# One synthesis question per topic. Suffix pulls specifics + citations.
SUFFIX = " Give specific 2026 numbers, product names, and concrete tactics, and cite sources."
ASKS = {
    "q1_models": "Summarize the Claude model lineup in 2026 (Opus, Sonnet, Haiku versions), their capabilities, context windows, and per-token pricing, and explain in plain terms which model to use when." + SUFFIX,
    "q2_surfaces": "Compare every way to use Claude in 2026 - Claude.ai chat (Projects, Artifacts), Claude Code, Claude Cowork, Desktop, mobile, and API. For each: what it is, who it's for, and the tasks it's best at." + SUFFIX,
    "q3_claude_code": "Explain Claude Code in depth for 2026: its capabilities and limits, and how hooks, MCP, subagents, skills, plugins, slash commands, headless mode, and the Agent SDK work. What are the highest-leverage productivity practices?" + SUFFIX,
    "q4_cowork": "Explain Claude Cowork in 2026: what the agentic product is, how it works, its best use cases and limits, and exactly how it differs from Claude Code and Claude.ai chat." + SUFFIX,
    "q5_business": "How are businesses and individuals actually using Claude in 2026 across functions (ops, marketing, sales, support, dev, research, finance, legal)? Include creative uses, ROI/productivity numbers, and case studies." + SUFFIX,
    "q6_ecosystem": "What are the most useful Claude Code plugins, MCP servers, and GitHub/open-source tools in 2026, and where do power users find them (marketplaces, awesome-lists)? Name specific tools and what each does." + SUFFIX,
    "q7_building": "How do you build with the Claude API in 2026 - tool use, MCP, the Agent SDK, prompt caching, batch, and cost optimization? When should someone build custom on the API versus just use Claude's products?" + SUFFIX,
    "q8_plans": "Lay out Claude's 2026 plans (Free, Pro, Max, Team, Enterprise) with limits and features, how Claude compares to ChatGPT and Gemini for business, and a clear decision framework for picking the right Claude product + model for a given task." + SUFFIX,
}


def run(args, timeout=4000):
    return subprocess.run(
        [EXE] + args,
        capture_output=True, text=True,
        encoding="utf-8-sig", errors="replace",
        timeout=timeout,
    )


def log(msg, logfile="research-run.log"):
    line = f"[{datetime.now().isoformat(timespec='seconds')}] {msg}"
    print(line, flush=True)
    with open(RESEARCH_DIR / logfile, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def research():
    log(f"=== RESEARCH START notebook={NOTEBOOK_ID} passes={len(QUERIES)} ===")
    for key, q in QUERIES.items():
        log(f"START pass {key}")
        try:
            r = run(["source", "add-research", q, "--from", "web", "--mode", "deep",
                     "--import-all", "--cited-only", "-n", NOTEBOOK_ID,
                     "--timeout", "1800", "--json"], timeout=4200)
            out = (r.stdout or "").strip().replace("\n", " ")[:300]
            err = (r.stderr or "").strip().replace("\n", " ")[:300]
            log(f"DONE pass {key} rc={r.returncode} out={out} err={err}")
        except Exception as e:  # noqa: BLE001
            log(f"ERROR pass {key}: {e}")
    # Snapshot the imported source list for sources.json building.
    try:
        r = run(["source", "list", "-n", NOTEBOOK_ID, "--json"], timeout=300)
        (RESEARCH_DIR / "sources-raw.json").write_text(r.stdout or "", encoding="utf-8")
        log("Wrote sources-raw.json")
    except Exception as e:  # noqa: BLE001
        log(f"ERROR source list: {e}")
    log("=== RESEARCH DONE ===")


def _load_json(text):
    try:
        return json.loads(text)
    except Exception:  # noqa: BLE001
        return None


def synthesize():
    log("=== SYNTHESIZE START ===", "ask-run.log")
    for key, question in ASKS.items():
        log(f"ASK {key}", "ask-run.log")
        try:
            # --new -y starts a fresh conversation so topics don't bleed.
            r = run(["ask", question, "--json", "-n", NOTEBOOK_ID, "--new", "-y"], timeout=600)
            (RESEARCH_DIR / f"{key}.json").write_text(r.stdout or "", encoding="utf-8")
            data = _load_json(r.stdout or "")
            nrefs = len(data.get("references", [])) if isinstance(data, dict) else 0
            log(f"WROTE {key}.json refs={nrefs} rc={r.returncode}", "ask-run.log")
        except Exception as e:  # noqa: BLE001
            log(f"ERROR ask {key}: {e}", "ask-run.log")
    build_sources_index()
    log("=== SYNTHESIZE DONE ===", "ask-run.log")


def build_sources_index():
    """Build sources.json (uuid_to_index + sources[]) from the source list."""
    raw_path = RESEARCH_DIR / "sources-raw.json"
    raw = _load_json(raw_path.read_text(encoding="utf-8-sig")) if raw_path.exists() else None
    src_list = []
    if isinstance(raw, dict):
        src_list = raw.get("sources") or raw.get("results") or []
    elif isinstance(raw, list):
        src_list = raw

    uuid_to_index = {}
    sources = []
    for i, s in enumerate(src_list, start=1):
        sid = s.get("id") or s.get("source_id") or ""
        sources.append({
            "index": i,
            "id": sid,
            "title": s.get("title", ""),
            "type": str(s.get("type", "")),
            "url": s.get("url", ""),
        })
        if sid:
            uuid_to_index[sid] = i

    out = {
        "notebook_id": NOTEBOOK_ID,
        "notebook_title": NOTEBOOK_TITLE,
        "generated_at": datetime.now().date().isoformat(),
        "method": "NotebookLM deep web-research (8 passes), cited-source import, then per-question ask --json synthesis",
        "source_count": len(sources),
        "uuid_to_index": uuid_to_index,
        "sources": sources,
    }
    (RESEARCH_DIR / "sources.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"Wrote sources.json ({len(sources)} sources)", "ask-run.log")


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "research"
    if phase == "research":
        research()
    elif phase == "synthesize":
        synthesize()
    elif phase == "sources":
        build_sources_index()
    else:
        raise SystemExit(f"Unknown phase: {phase} (use research | synthesize | sources)")
