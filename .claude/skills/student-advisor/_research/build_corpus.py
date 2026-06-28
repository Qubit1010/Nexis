#!/usr/bin/env python3
"""Build (and refresh) the Student Advisor research corpus in NotebookLM.

Mirrors the claude-advisor / marketing-advisor research pipeline so the
student-advisor skill's ADVICE half is grounded in cited sources, per
`.claude/rules/research-backed-skills.md`. The tutor half (learn-anything)
is generative and not corpus-backed.

Phases:
  research    - run deep web-research passes into the notebook (default).
                Blocking + sequential so each pass fully imports before the next.
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

# Curated notebook: sources are Exa-gathered + hand-vetted (see gather_sources.py /
# boost_sources.py / import_to_notebooklm.py), NOT NotebookLM auto-research. The research()
# phase below is retained only as a fallback; the live pipeline uses the Exa-curated corpus.
NOTEBOOK_ID = "ffcd6d51-673d-4308-9400-c01976e3a849"
NOTEBOOK_TITLE = "Student Advisor - Curated Sources 2026"
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

# Deep web-research seed queries (one pass each). Phrased to pull current,
# evidence-based sources (cognitive science of learning + 2026 career/study data).
QUERIES = {
    "q1_learning_science": (
        "Evidence-based learning techniques from cognitive science: retrieval practice "
        "(the testing effect), spaced repetition / distributed practice, interleaving, "
        "dual coding, elaboration, and concrete examples. Effect sizes and meta-analyses "
        "(Dunlosky et al., Roediger, Bjork desirable difficulties). Which study techniques "
        "actually work versus which are ineffective (rereading, highlighting, learning styles)."
    ),
    "q2_note_taking": (
        "Best note-taking and lecture-capture methods backed by research: Cornell method, "
        "outline method, mind mapping, the Feynman technique. Handwriting versus typing notes "
        "(Mueller and Oppenheimer), generative note-taking, how to review notes, and how to "
        "read textbooks effectively (SQ3R, active reading) for university students."
    ),
    "q3_exam_prep": (
        "How to prepare for exams effectively, backed by research: practice testing, "
        "distributed practice versus cramming, mock exams, spacing a study schedule, "
        "self-testing, managing test anxiety, sleep and exam performance, and study "
        "planning strategies for college and university students."
    ),
    "q4_retention_motivation": (
        "Long-term memory retention and the forgetting curve (Ebbinghaus), how to make "
        "learning stick, spaced review schedules. Intrinsic versus extrinsic motivation, "
        "self-determination theory, how to create interest in a subject you find boring, "
        "building curiosity, habit formation, and beating procrastination for students."
    ),
    "q5_ai_careers": (
        "Career paths for artificial intelligence, machine learning, and computer science "
        "graduates in 2026: roles such as ML engineer, data scientist, AI engineer, MLOps, "
        "research scientist, applied scientist, AI product manager, prompt/AI agent engineer. "
        "Job market outlook, in-demand skills, salaries, and what new AI graduates should "
        "learn and explore next to stay competitive."
    ),
    "q6_grad_school": (
        "Planning a master's degree or graduate school in AI, machine learning, computer "
        "science, or data science: when a master's is worth it versus industry experience, "
        "MS versus PhD, application requirements (GRE, GPA, statement of purpose, letters of "
        "recommendation, research experience), timelines, and top programs, for 2026 intake."
    ),
    "q7_scholarships": (
        "Fully funded scholarships for international students in 2026: Fulbright, Chevening, "
        "DAAD, Erasmus Mundus, Commonwealth, MEXT, Australia Awards, and university funding / "
        "assistantships. Eligibility, how to win a scholarship, application strategy, deadlines, "
        "and tips for students from developing countries (including Pakistan / South Asia)."
    ),
    "q8_study_abroad": (
        "Best countries to study abroad for international students in 2026: Germany, Canada, "
        "USA, UK, Australia, Netherlands, Ireland, and others. Compare tuition and living costs, "
        "post-study work visas, permanent residency pathways, quality of universities for "
        "computer science and AI, and student-friendliness."
    ),
}

# One synthesis question per topic. Suffix pulls specifics + citations.
SUFFIX = " Give specific numbers, named techniques or programs, effect sizes where relevant, and concrete actionable steps, and cite sources."
ASKS = {
    "q1_learning_science": "Summarize the most effective evidence-based learning techniques (retrieval practice, spaced repetition, interleaving, dual coding, elaboration) with their effect sizes and the meta-analyses behind them, and contrast them with techniques shown to be ineffective." + SUFFIX,
    "q2_note_taking": "What note-taking and active-reading methods are best supported by research for university students (Cornell, mapping, Feynman, SQ3R, handwriting vs typing), and how should a student take and review notes during and after lectures?" + SUFFIX,
    "q3_exam_prep": "What is the most effective, research-backed way to prepare for an exam: how to schedule study (spacing vs cramming), use practice testing and mock exams, manage test anxiety, and the role of sleep?" + SUFFIX,
    "q4_retention_motivation": "How does long-term retention work (forgetting curve, spaced review) and how can a student make material stick? Separately, how do you build motivation and create genuine interest in a subject you find boring, and beat procrastination, per self-determination theory and habit research?" + SUFFIX,
    "q5_ai_careers": "What are the realistic career paths for an AI / ML / CS graduate in 2026, the 2026 job market and in-demand skills, salary ranges, and what a new graduate should learn and explore next to be competitive?" + SUFFIX,
    "q6_grad_school": "Lay out how to plan a master's / grad school in AI/CS/DS for 2026: is a master's worth it vs industry, MS vs PhD, the application components and timeline, and what makes a strong application." + SUFFIX,
    "q7_scholarships": "What are the top fully funded scholarships for international students in 2026 (Fulbright, Chevening, DAAD, Erasmus Mundus, Commonwealth, MEXT, assistantships), their eligibility, deadlines, and how to actually win one, especially for students from developing countries?" + SUFFIX,
    "q8_study_abroad": "Which countries are best for international students in 2026 (cost, post-study work visas, PR pathways, university quality for CS/AI)? Compare the main destinations and give a decision framework." + SUFFIX,
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
    # Refresh sources-raw.json from the CURRENT (curated) notebook so the index is accurate.
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
        research(only=set(sys.argv[2:]) or None)
    elif phase == "synthesize":
        synthesize()
    elif phase == "sources":
        build_sources_index()
    else:
        raise SystemExit(f"Unknown phase: {phase} (use research | synthesize | sources)")
