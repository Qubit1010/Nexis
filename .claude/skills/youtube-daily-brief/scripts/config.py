"""Shared configuration for YouTube Intelligence skill."""

import os
from pathlib import Path

from dotenv import load_dotenv

# ── Paths ──────────────────────────────────────────────────────────────────────
SKILL_DIR = Path(__file__).resolve().parent.parent   # .claude/skills/youtube-daily-brief/
SCRIPTS_DIR = SKILL_DIR / "scripts"
TMP_DIR = SKILL_DIR / ".tmp"
HISTORY_DIR = TMP_DIR / "history"
RAW_VIDEOS_PATH = TMP_DIR / "raw_videos.json"
ANALYSIS_PATH = TMP_DIR / "analysis.json"

TMP_DIR.mkdir(exist_ok=True)
HISTORY_DIR.mkdir(exist_ok=True)

# ── Environment ────────────────────────────────────────────────────────────────
# When run via Node subprocess the keys may already be in process.env, but a long-running
# dev server snapshots .env only at startup — so also load the files from disk.
# override=False: a fresh process.env still wins; otherwise the file supplies the key.
load_dotenv(SCRIPTS_DIR / ".env", override=False)                        # direct-run convenience
REPO_ROOT = SKILL_DIR.parents[2]                                          # .claude/skills/X -> repo root
load_dotenv(REPO_ROOT / "projects" / "daily-news-brief" / ".env", override=False)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ── Channel List ───────────────────────────────────────────────────────────────
# Edit this list to add/remove channels.
# handle — the @username (used to resolve the channel via YouTube Data API)
# name   — display name (shown in the dashboard and analysis)
CHANNELS = [
    {"handle": "@theAIsearch",   "name": "AI Search"},
    {"handle": "@airevolutionx", "name": "AI Revolution"},
    {"handle": "@Itssssss_Jack", "name": "Jack Roberts"},
    {"handle": "@danmartell",    "name": "Dan Martell"},
    {"handle": "@TechWithTim",   "name": "Tech With Tim"},
    {"handle": "@AIDailyBrief",  "name": "AI Daily Brief"},
    {"handle": "@mreflow",       "name": "MreFlow"},
    {"handle": "@TheAiGrid",     "name": "TheAIGrid"},
    {"handle": "@DaveShap",      "name": "Dave Shap"},
    {"handle": "@nicksaraev",    "name": "Nick Saraev"},
    {"handle": "@LiamOttley",    "name": "Liam Ottley"},
    {"handle": "@nateherk",      "name": "Nate Herk"},
    {"handle": "@NateBJones",    "name": "Nate B Jones"},
]

# ── Scraper Settings ───────────────────────────────────────────────────────────
VIDEOS_PER_CHANNEL = 5
TRANSCRIPT_MAX_CHARS = 2000      # Max chars of transcript to include per video
HISTORY_DAYS = 7                 # Days of history to keep for trend comparison
