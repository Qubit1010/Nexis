"""Config + env loading for the Weekly Business Review skill.

One place for sheet IDs, tunable constants, and credentials. Loads the repo-root
.env (same convention as youtube-daily-brief/config.py). No secrets live here.
"""
import os
from pathlib import Path

# repo root = .../Nexis (this file is at .claude/skills/weekly-business-review/scripts/config.py)
REPO_ROOT = Path(__file__).resolve().parents[4]
SNAPSHOT_DIR = REPO_ROOT / "projects" / "weekly-business-review" / "data" / "weeks"


def _load_env():
    """Minimal .env loader (no python-dotenv dependency needed for a handful of keys)."""
    env_path = REPO_ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_env()

# --- Google Sheets sources (id + the tab that holds the rows) ---
SHEETS = {
    "upwork": {"id": "1mDzFkxBOzvxq6joYO9K86EZim30qeXV11Rjhm4jgQBM", "tab": "Sheet1"},
    "linkedin": {"id": "1rJM42Hd1kh8G4d3MGIO1SMILSyM86iU5nSD7QQTdOoo", "tab": "Leads"},
    "instagram": {"id": "1xql6icDspoJxzP1_vIQpjqBWK1RYQBN1C8N28OzkGs8", "tab": "Leads"},
    "facebook": {"id": "1GkbzCclQsg83P_l5EgKxjceW-Y_7fQ1lByJUGH1aaNg", "tab": "Leads"},
}

# ponytail: Upwork sells connects in bundles that work out to ~$0.15 each; there is
# no per-proposal dollar column, so spend is derived. Tune here if your bundle price differs.
UPWORK_CONNECT_USD = 0.15

# --- Buffer (content analytics) ---
BUFFER_TOKEN = os.environ.get("BUFFER_API_KEY", "")
BUFFER_GRAPHQL_URL = "https://api.buffer.com/graphql"

# --- ProductivityHub (separate Supabase project from the sales-playbook one) ---
# Not configured yet: needs the ProductivityHub project's URL + a key. When present the
# productivity source activates automatically.
PRODUCTIVITY_SUPABASE_URL = os.environ.get("PRODUCTIVITY_SUPABASE_URL", "")
PRODUCTIVITY_SUPABASE_KEY = os.environ.get("PRODUCTIVITY_SUPABASE_KEY", "")
# task_entries = the per-day completed-task log. The project is multi-user, so the
# service_role key sees everyone -- always filter to this account's user_id.
PRODUCTIVITY_TASKS_TABLE = os.environ.get("PRODUCTIVITY_TASKS_TABLE", "task_entries")
PRODUCTIVITY_USER_EMAIL = os.environ.get("PRODUCTIVITY_USER_EMAIL", "hassanaleem86@gmail.com")
