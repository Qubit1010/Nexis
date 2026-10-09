"""One-time (idempotent): create the demo tables from sql/demo_schema.sql.

Uses the Supabase Management API (SUPABASE_ACCESS_TOKEN): the direct db.<ref>.supabase.co host is
IPv6-only from this machine. Detects a paused project (free tier pauses after about a week idle).
Pattern from .claude/skills/proposal-generator/scripts/setup_db.py.
"""
import json
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]


def load_env() -> dict:
    env = {}
    for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, v = line.strip().split("=", 1)
            env[k] = v.strip().strip('"').strip("'")
    return env


env = load_env()
ref = env["SUPABASE_URL"].split("//")[1].split(".")[0]
H = {"Authorization": f"Bearer {env['SUPABASE_ACCESS_TOKEN']}", "Content-Type": "application/json",
     "User-Agent": "nexuspoint-demo"}


def api(path, body=None):
    req = urllib.request.Request(f"https://api.supabase.com/v1/projects/{ref}{path}",
                                 data=json.dumps(body).encode() if body is not None else None, headers=H)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read() or b"null")


status = api("")["status"]
if status != "ACTIVE_HEALTHY":
    sys.exit(f"project {ref} is {status}. Restore it (POST /v1/projects/{ref}/restore), then rerun.")

q = lambda sql: api("/database/query", {"query": sql})  # noqa: E731
q((ROOT / "sql" / "demo_schema.sql").read_text(encoding="utf-8"))
q((ROOT / "sql" / "healthcare_schema.sql").read_text(encoding="utf-8"))
q((ROOT / "sql" / "restaurant_schema.sql").read_text(encoding="utf-8"))
q((ROOT / "sql" / "school_schema.sql").read_text(encoding="utf-8"))
rows = q("select relname, relrowsecurity from pg_class where relname like 'demo_%' and relkind = 'r' order by 1")
for r in rows:
    print(f"{r['relname']:20} RLS {'on' if r['relrowsecurity'] else 'OFF'}")
