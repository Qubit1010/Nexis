#!/usr/bin/env python3
"""Build (and refresh) the Developer Advisor research corpus in NotebookLM.

Mirrors the student-advisor / marketing-advisor research pipeline so the skill's
ADVISOR half is grounded in cited sources, per `.claude/rules/research-backed-skills.md`.
The Project Architect (intake -> blueprint) half is generative and uses the corpus for
stack/architecture recommendations rather than being fully corpus-authored.

Sources are Exa-gathered + hand-vetted (see gather_sources.py / boost_sources.py /
import_to_notebooklm.py), NOT NotebookLM auto-research. The research() phase below is
retained only as a fallback.

Phases:
  research    - deep web-research passes into the notebook (fallback only).
  synthesize  - ask the Q1-Q9 questions (--json), write q*.json, then build a deduped
                sources.json (uuid_to_index + sources[]).

Usage (PowerShell):
  python build_corpus.py synthesize

NotebookLM CLI outputs UTF-8 with a BOM, so we parse with utf-8-sig.
"""
import json
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

NOTEBOOK_ID = "5c8257d3-cdb3-469e-8d8c-da500a99ea14"
NOTEBOOK_TITLE = "Developer Advisor - Curated Sources 2026"
RESEARCH_DIR = Path(__file__).resolve().parent


def find_exe():
    candidates = [
        Path(r"C:\Users\Aleem\AppData\Local\Programs\Python\Python313\Scripts\notebooklm.exe"),
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

# Deep web-research seed queries (fallback path only; live pipeline uses Exa-curated import).
QUERIES = {
    "q1_architecture": (
        "Software architecture patterns and system design in 2026: modular monolith vs "
        "microservices vs serverless vs event-driven, clean architecture, domain-driven design, "
        "and how to choose an architecture for web and AI applications by scale and team size."
    ),
    "q2_frontend": (
        "Modern frontend and web frameworks in 2026: Next.js and React server components, Astro, "
        "SvelteKit, rendering strategies (SSR, SSG, streaming, islands), performance, accessibility, "
        "and how to choose a frontend stack."
    ),
    "q3_backend": (
        "Backend frameworks and API design in 2026: Node.js, Bun, FastAPI, Django, Go; REST vs "
        "GraphQL vs tRPC; API design best practices (versioning, pagination, idempotency, auth), "
        "and when to choose each."
    ),
    "q4_database": (
        "Databases and the data layer in 2026: Postgres, serverless Postgres (Neon, Supabase), "
        "SQLite/Turso, MongoDB, vector databases and pgvector; ORMs (Drizzle, Prisma); caching; "
        "schema design and scaling; how to choose a database."
    ),
    "q5_ai_engineering": (
        "Building LLM and AI applications in production in 2026: RAG vs agents, agent architectures, "
        "evals, structured outputs, retrieval pipeline design, frameworks (LangChain, LangGraph) vs "
        "direct SDK, cost and latency, and reliability best practices."
    ),
    "q6_agentic_coding": (
        "Agentic coding and AI-assisted software engineering in 2026: best practices for coding "
        "agents and Claude Code, context engineering, CLAUDE.md, spec-driven and plan-first "
        "development, subagents, review loops, and how to get the highest-quality code from AI tools."
    ),
    "q7_mobile": (
        "Mobile development in 2026: React Native and Expo vs Flutter vs native, PWAs, cross-platform "
        "tradeoffs, and when a business actually needs a native mobile app versus a responsive web app."
    ),
    "q8_practices": (
        "Software engineering best practices in 2026: testing strategy (unit/integration/e2e, the test "
        "pyramid), CI/CD, DORA metrics, trunk-based development, code review, security (OWASP), and "
        "code quality for small teams and agencies."
    ),
    "q9_hosting": (
        "Hosting, deployment, and infrastructure in 2026: Vercel, Cloudflare, Railway, Fly.io, AWS; "
        "serverless vs containers vs edge; cost and scaling tradeoffs; and how to choose a deployment "
        "platform for web and AI apps."
    ),
}

SUFFIX = " Give specific tools, frameworks, version-era details, concrete tradeoffs, decision criteria, and actionable recommendations, and cite sources."
ASKS = {
    "q1_architecture": "What are the main software architecture patterns to choose between in 2026 (modular monolith, microservices, serverless, event-driven), the tradeoffs of each, and a decision framework for picking one by scale, team size, and project type?" + SUFFIX,
    "q2_frontend": "What is the best way to choose a frontend/web stack in 2026 among Next.js/React, Astro, and SvelteKit, including rendering strategies (SSR/SSG/streaming/islands) and when each is the right call, plus core performance and accessibility practices?" + SUFFIX,
    "q3_backend": "How should you choose a backend framework and API style in 2026 (Node/Bun, FastAPI, Django, Go; REST vs GraphQL vs tRPC), and what are the API design best practices (versioning, pagination, idempotency, auth, error handling)?" + SUFFIX,
    "q4_database": "How do you choose a database and data layer in 2026 (Postgres, serverless Postgres like Neon/Supabase, SQLite/Turso, MongoDB, vector DBs/pgvector), which ORM (Drizzle vs Prisma), and what are the schema, indexing, and caching best practices?" + SUFFIX,
    "q5_ai_engineering": "What is the best way to architect an LLM/AI application in 2026: RAG vs agents, when to use agent frameworks (LangChain/LangGraph) vs the direct SDK, evals, structured outputs, retrieval design, and reliability/cost/latency best practices for production?" + SUFFIX,
    "q6_agentic_coding": "What are the best practices for agentic coding and getting the highest-quality output from AI coding tools like Claude Code in 2026: context engineering, CLAUDE.md, spec/plan-first development, subagents, review loops, and workflow design?" + SUFFIX,
    "q7_mobile": "How should you decide on a mobile approach in 2026 (React Native/Expo vs Flutter vs native vs PWA), the tradeoffs, and when a business actually needs a native app versus a responsive web app?" + SUFFIX,
    "q8_practices": "What are the essential software engineering best practices in 2026 for a small team/agency: testing strategy and the test pyramid, CI/CD, DORA metrics, trunk-based development, code review, and security (OWASP)?" + SUFFIX,
    "q9_hosting": "How should you choose a hosting/deployment platform in 2026 (Vercel, Cloudflare, Railway, Fly.io, AWS), serverless vs containers vs edge, and what are the cost and scaling tradeoffs for web and AI apps?" + SUFFIX,
}


def run(args, timeout=4200):
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


def research(only=None):
    items = [(k, v) for k, v in QUERIES.items() if not only or k in only]
    log(f"=== RESEARCH START notebook={NOTEBOOK_ID} passes={len(items)} ===")
    for key, q in items:
        log(f"START pass {key}")
        try:
            r = run(["source", "add-research", q, "--from", "web", "--mode", "deep",
                     "--import-all", "-n", NOTEBOOK_ID], timeout=4200)
            out = (r.stdout or "").strip().replace("\n", " ")[:300]
            err = (r.stderr or "").strip().replace("\n", " ")[:300]
            log(f"DONE pass {key} rc={r.returncode} out={out} err={err}")
        except Exception as e:  # noqa: BLE001
            log(f"ERROR pass {key}: {e}")
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
    try:
        r = run(["source", "list", "-n", NOTEBOOK_ID, "--json"], timeout=300)
        (RESEARCH_DIR / "sources-raw.json").write_text(r.stdout or "", encoding="utf-8")
        log("Refreshed sources-raw.json from curated notebook", "ask-run.log")
    except Exception as e:  # noqa: BLE001
        log(f"ERROR refresh sources-raw: {e}", "ask-run.log")
    for key, question in ASKS.items():
        log(f"ASK {key}", "ask-run.log")
        try:
            r = run(["ask", question, "--json", "-n", NOTEBOOK_ID], timeout=600)
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
        "method": "Exa-curated multi-angle search (9 topics), hand-vetted, imported to NotebookLM, then per-question ask --json synthesis",
        "source_count": len(sources),
        "uuid_to_index": uuid_to_index,
        "sources": sources,
    }
    (RESEARCH_DIR / "sources.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    log(f"Wrote sources.json ({len(sources)} sources)", "ask-run.log")


if __name__ == "__main__":
    phase = sys.argv[1] if len(sys.argv) > 1 else "synthesize"
    if phase == "research":
        research(only=set(sys.argv[2:]) or None)
    elif phase == "synthesize":
        synthesize()
    elif phase == "sources":
        build_sources_index()
    else:
        raise SystemExit(f"Unknown phase: {phase} (use research | synthesize | sources)")
