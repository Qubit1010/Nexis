"""One-time: create the proposal_events table from schema.sql (idempotent).

Runs through the Supabase Management API (SUPABASE_ACCESS_TOKEN), not a direct Postgres
connection: the direct db.<ref>.supabase.co host is IPv6-only and does not resolve from this
machine. If the project is paused (free tier pauses after about a week idle), the query times
out with HTTP 544; this script detects that and says so instead of failing obscurely.
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deploy import load_env  # noqa: E402

env = load_env()
tok = env["SUPABASE_ACCESS_TOKEN"]
ref = env["SUPABASE_URL"].split("//")[1].split(".")[0]
H = {"Authorization": f"Bearer {tok}", "Content-Type": "application/json", "User-Agent": "nexis-proposals"}


def api(path, body=None):
    req = urllib.request.Request(f"https://api.supabase.com/v1/projects/{ref}{path}",
                                 data=json.dumps(body).encode() if body is not None else None, headers=H)
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.loads(r.read() or b"null")


status = api("")["status"]
if status != "ACTIVE_HEALTHY":
    sys.exit(f"project {ref} is {status}. Restore it (POST /v1/projects/{ref}/restore or the dashboard), then rerun.")

q = lambda sql: api("/database/query", {"query": sql})  # noqa: E731
q((Path(__file__).parent / "schema.sql").read_text(encoding="utf-8"))
cols = q("select count(*) as n from information_schema.columns where table_name = 'proposal_events'")[0]["n"]
rls = q("select relrowsecurity as on from pg_class where relname = 'proposal_events'")[0]["on"]
print(f"proposal_events ready: {cols} columns, RLS {'on' if rls else 'OFF'}")
