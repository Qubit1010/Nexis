#!/usr/bin/env python3
"""Pull content ideas from 3 sources:
  1. daily-news-brief SQLite database
  2. youtube-daily-brief JSON file
  3. Saved Topics Google Sheet

Emits combined JSON to stdout. Pure read — no writes to any source.

Usage:
    python pull_ideas.py
"""

import json
import os
import shutil
import sqlite3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
# SKILL_DIR = .claude/skills/content-engine/
# parents[0] = .claude/skills/, parents[1] = .claude/, parents[2] = Nexis/ (repo root)
REPO_ROOT = SKILL_DIR.parents[2]

NEWS_DB_PATH = REPO_ROOT / "projects" / "daily-news-brief" / "data" / "news.db"
YOUTUBE_JSON_PATH = Path(
    "C:/Users/qubit/OneDrive/Documents/Automations/youtube-daily-brief/.tmp/analysis.json"
)
SAVED_TOPICS_SHEET_ID = "1TwAuLDKak3hpPWqlojpNL_OTsUyCOBaAVjRRncOpb9Q"

# ---------------------------------------------------------------------------
# gws helpers (same pattern as save_marketing_plan.py)
# ---------------------------------------------------------------------------

def find_gws():
    npm_dir = Path(os.environ.get("APPDATA", "")) / "npm"
    gws_js = npm_dir / "node_modules" / "@googleworkspace" / "cli" / "run-gws.js"
    if gws_js.exists():
        node_exe = None
        for candidate in [
            npm_dir / "node.exe",
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs" / "node.exe",
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs" / "node.exe",
        ]:
            if candidate.exists():
                node_exe = str(candidate)
                break
        if not node_exe:
            node_exe = shutil.which("node")
        if node_exe:
            return ([node_exe, str(gws_js)], False)
    gws_path = shutil.which("gws")
    if gws_path:
        return ([gws_path], True)
    gws_cmd = npm_dir / "gws.cmd"
    if gws_cmd.exists():
        return ([str(gws_cmd)], True)
    return (["gws"], True)


GWS_CMD, GWS_USE_SHELL = find_gws()


def run_gws(args, json_body=None):
    cmd = GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]
    result = subprocess.run(
        cmd, capture_output=True, text=True, timeout=60,
        shell=GWS_USE_SHELL, encoding="utf-8", errors="replace"
    )
    if result.returncode != 0:
        raise RuntimeError(f"gws failed: {result.stderr.strip()}")
    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


# ---------------------------------------------------------------------------
# Platform affinity tagging
# Maps content format -> platform order (first = best fit)
# These are signals for Claude, not hard assignments.
# ---------------------------------------------------------------------------

FORMAT_AFFINITY = {
    "thread": ["linkedin", "instagram"],
    "blog": ["blog", "linkedin"],
    "newsletter": ["blog"],
    "tutorial": ["blog", "linkedin"],
    "explainer": ["linkedin", "instagram"],
    "opinion": ["linkedin", "instagram"],
    "comparison": ["linkedin", "blog"],
    "news": ["instagram", "linkedin"],
    "demo": ["instagram", "linkedin"],
    "interview": ["blog", "linkedin"],
    "carousel": ["instagram", "linkedin"],
}


def get_affinity(fmt, timeliness=None, interest=None, momentum=None):
    fmt = (fmt or "").lower().strip()
    affinity = list(FORMAT_AFFINITY.get(fmt, ["linkedin", "blog"]))

    # Breaking news = Instagram first (timely, scroll-friendly)
    if timeliness == "breaking" and "instagram" not in affinity:
        affinity.insert(0, "instagram")

    # High interest or rising momentum = bump Instagram forward
    if (interest == "high" or momentum == "rising") and "instagram" in affinity:
        affinity.remove("instagram")
        affinity.insert(0, "instagram")

    return affinity


# ---------------------------------------------------------------------------
# Source 1: Daily News Brief (SQLite)
# ---------------------------------------------------------------------------

def pull_news_brief():
    result = {
        "available": False,
        "date": None,
        "ideas": [],
        "trends": [],
        "error": None,
    }
    try:
        if not NEWS_DB_PATH.exists():
            result["error"] = f"DB not found at: {NEWS_DB_PATH}"
            return result

        conn = sqlite3.connect(str(NEWS_DB_PATH))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        # Get the most recent brief
        cur.execute("SELECT id, date FROM briefs ORDER BY id DESC LIMIT 1")
        row = cur.fetchone()
        if not row:
            result["error"] = "No briefs in database yet"
            conn.close()
            return result

        brief_id = row["id"]
        result["date"] = row["date"]

        # Pull content ideas for this brief
        cur.execute(
            """
            SELECT title, angle, format, hook, key_points,
                   timeliness, related_trend_slugs, sort_order
            FROM content_ideas
            WHERE brief_id = ?
            ORDER BY sort_order
            """,
            (brief_id,),
        )
        for r in cur.fetchall():
            # key_points and related_trend_slugs are stored as JSON strings
            try:
                key_points = json.loads(r["key_points"]) if r["key_points"] else []
            except (json.JSONDecodeError, TypeError):
                key_points = [r["key_points"]] if r["key_points"] else []

            try:
                related_trends = (
                    json.loads(r["related_trend_slugs"])
                    if r["related_trend_slugs"]
                    else []
                )
            except (json.JSONDecodeError, TypeError):
                related_trends = []

            result["ideas"].append(
                {
                    "source": "news-brief",
                    "title": r["title"],
                    "angle": r["angle"],
                    "format": r["format"],
                    "hook": r["hook"],
                    "key_points": key_points,
                    "timeliness": r["timeliness"],
                    "related_trends": related_trends,
                    "platform_affinity": get_affinity(r["format"], r["timeliness"]),
                }
            )

        # Pull top trends for context
        cur.execute(
            """
            SELECT title, slug, summary, momentum_signal, content_potential_score
            FROM trends
            WHERE brief_id = ?
            ORDER BY content_potential_score DESC
            LIMIT 5
            """,
            (brief_id,),
        )
        for r in cur.fetchall():
            result["trends"].append(
                {
                    "title": r["title"],
                    "slug": r["slug"],
                    "summary": r["summary"],
                    "momentum_signal": r["momentum_signal"],
                    "content_potential_score": r["content_potential_score"],
                }
            )

        conn.close()
        result["available"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


# ---------------------------------------------------------------------------
# Source 2: YouTube Daily Brief (JSON)
# ---------------------------------------------------------------------------

def pull_youtube_brief():
    result = {
        "available": False,
        "analyzed_at": None,
        "content_opportunities": [],
        "suggested_topics": [],
        "trending_topics": [],
        "error": None,
    }
    try:
        if not YOUTUBE_JSON_PATH.exists():
            result["error"] = f"YouTube JSON not found at: {YOUTUBE_JSON_PATH}"
            return result

        with open(YOUTUBE_JSON_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        # analyzed_at may be at top level or nested in metadata
        result["analyzed_at"] = data.get("analyzed_at") or (
            data.get("metadata", {}).get("analyzed_at")
        )

        for opp in data.get("content_opportunities", []):
            fmt = opp.get("format_suggestion", "")
            interest = opp.get("estimated_interest", "medium")
            result["content_opportunities"].append(
                {
                    "source": "youtube-brief",
                    "idea": opp.get("idea", ""),
                    "reasoning": opp.get("reasoning", ""),
                    "format_suggestion": fmt,
                    "estimated_interest": interest,
                    "platform_affinity": get_affinity(fmt, interest=interest),
                }
            )

        for topic in data.get("suggested_topics", []):
            fmt = topic.get("target_format", "")
            result["suggested_topics"].append(
                {
                    "source": "youtube-brief",
                    "topic": topic.get("topic", ""),
                    "angle": topic.get("angle", ""),
                    "why_now": topic.get("why_now", ""),
                    "target_format": fmt,
                    "competition_level": topic.get("competition_level", "medium"),
                    "reference_videos": topic.get("reference_videos", []),
                    "platform_affinity": get_affinity(fmt),
                }
            )

        for t in data.get("trending_topics", []):
            result["trending_topics"].append(
                {
                    "topic": t.get("topic", ""),
                    "mention_count": t.get("mention_count", 0),
                    "sentiment": t.get("sentiment", "neutral"),
                    "summary": t.get("summary", ""),
                }
            )

        result["available"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


# ---------------------------------------------------------------------------
# Source 3: Saved Topics Google Sheet
# ---------------------------------------------------------------------------

def pull_saved_topics():
    result = {"available": False, "ideas": [], "error": None}
    try:
        data = run_gws(
            [
                "sheets",
                "spreadsheets",
                "values",
                "get",
                "--params",
                json.dumps(
                    {
                        "spreadsheetId": SAVED_TOPICS_SHEET_ID,
                        "range": "Content Opportunities",
                    }
                ),
            ]
        )
        values = data.get("values", [])
        if not values:
            result["error"] = "Sheet is empty or has no data"
            return result

        headers = [h.strip() for h in values[0]]

        def col(row, name):
            """Get a cell value by column header name."""
            try:
                idx = headers.index(name)
                return row[idx] if idx < len(row) else ""
            except ValueError:
                return ""

        for row in values[1:]:
            if not row:
                continue

            # Skip rows already used — include empty status and "New"
            status = col(row, "Status").strip().lower()
            if status and status not in ("new", ""):
                continue

            title = col(row, "Title").strip()
            if not title:
                continue

            fmt = col(row, "Format").strip().lower()
            timeliness = col(row, "Timeliness").strip().lower()

            # Key Points: try JSON parse first, then comma-split
            kp_raw = col(row, "Key Points").strip()
            try:
                if kp_raw.startswith("["):
                    key_points = json.loads(kp_raw)
                else:
                    key_points = [p.strip() for p in kp_raw.split(",") if p.strip()]
            except (json.JSONDecodeError, AttributeError):
                key_points = [kp_raw] if kp_raw else []

            rt_raw = col(row, "Related Trends").strip()
            related_trends = (
                [t.strip() for t in rt_raw.split(",") if t.strip()] if rt_raw else []
            )

            result["ideas"].append(
                {
                    "source": "saved-topics",
                    "title": title,
                    "format": fmt,
                    "timeliness": timeliness,
                    "angle": col(row, "Angle").strip(),
                    "hook": col(row, "Hook").strip(),
                    "key_points": key_points,
                    "related_trends": related_trends,
                    "date_saved": col(row, "Date Saved").strip(),
                    "brief_date": col(row, "Brief Date").strip(),
                    "platform_affinity": get_affinity(fmt, timeliness),
                    "saved_bonus": True,
                }
            )

        result["available"] = True

    except Exception as e:
        result["error"] = str(e)

    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    errors = []

    news_brief = pull_news_brief()
    if news_brief.get("error"):
        errors.append(f"news-brief: {news_brief['error']}")

    youtube_brief = pull_youtube_brief()
    if youtube_brief.get("error"):
        errors.append(f"youtube-brief: {youtube_brief['error']}")

    saved_topics = pull_saved_topics()
    if saved_topics.get("error"):
        errors.append(f"saved-topics: {saved_topics['error']}")

    output = {
        "generated_at": datetime.now().isoformat(),
        "news_brief": news_brief,
        "youtube_brief": youtube_brief,
        "saved_topics": saved_topics,
        "errors": errors,
    }

    sys.stdout.buffer.write(json.dumps(output, ensure_ascii=False, indent=2).encode("utf-8"))
    sys.stdout.buffer.write(b"\n")


if __name__ == "__main__":
    main()
