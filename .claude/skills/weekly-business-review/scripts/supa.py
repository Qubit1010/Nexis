"""Tiny Supabase PostgREST reader (stdlib urllib, no SDK) -- same pattern as
sales-playbook/scripts/convo.py. Used for ProductivityHub once its project creds exist.
"""
import json
import urllib.error
import urllib.parse
import urllib.request


def rest_get(base_url, key, path, params=None):
    """GET {base_url}/rest/v1/{path}?{params}. Returns parsed JSON (list/dict)."""
    url = f"{base_url.rstrip('/')}/rest/v1/{path}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={
        "apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def list_tables(base_url, key):
    """Table names exposed by PostgREST (from the OpenAPI root)."""
    spec = rest_get(base_url, key, "")
    return sorted(p.strip("/") for p in (spec.get("paths") or {}) if p not in ("/",) and not p.startswith("/rpc"))
