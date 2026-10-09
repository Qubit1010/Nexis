"""Clear a demo's conversations (messages cascade) so the owner dashboard starts empty in the meeting.

    python scripts/reset_demo.py <slug> [<slug> ...]
    python scripts/reset_demo.py --all
Keeps demo_events (views, reopens) because those tell Aleem when to follow up.
"""
import json
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
env = {}
for line in (REPO / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.strip().split("=", 1)
        env[k] = v.strip().strip('"').strip("'")
URL, KEY = env["SUPABASE_URL"].rstrip("/"), env["SUPABASE_SERVICE_ROLE_KEY"]
H = {"apikey": KEY, "Authorization": f"Bearer {KEY}", "Content-Type": "application/json"}


def call(method, path, prefer=None, body=None):
    req = urllib.request.Request(f"{URL}/rest/v1/{path}", method=method, data=json.dumps(body).encode() if body is not None else None, headers={**H, **({"Prefer": prefer} if prefer else {})})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read()
        return json.loads(body) if body else []


args = sys.argv[1:]
if not args:
    sys.exit(__doc__)
slugs = [r["slug"] for r in call("GET", "demo_businesses?select=slug")] if args == ["--all"] else args
for slug in slugs:
    business=call("GET",f"demo_businesses?slug=eq.{slug}&select=sector")
    if business and business[0]["sector"]=="healthcare":
        call("POST","rpc/demo_reset_healthcare",body={"p_slug":slug})
        print(f"{slug}: archived healthcare activity; the next visit seeds a fresh sample workspace")
        continue
    if business and business[0]["sector"]=="food":
        call("POST","rpc/demo_restaurant_action",body={"p_slug":slug,"p_visitor":"system-reset","p_role":"system","p_action":"reset","p_data":{}})
        print(f"{slug}: archived restaurant activity; the next visit seeds a fresh sample workspace")
        continue
    if business and business[0]["sector"]=="education":
        call("POST","rpc/demo_school_action",body={"p_slug":slug,"p_visitor":"system-reset","p_role":"system","p_action":"reset","p_data":{}})
        print(f"{slug}: archived school activity; the next visit seeds a fresh sample workspace")
