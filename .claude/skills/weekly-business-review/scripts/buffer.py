"""Buffer content analytics via its GraphQL API (api.buffer.com/graphql).

The old REST API (api.bufferapp.com/1) rejects public tokens; the current GraphQL
API accepts the public token as a Bearer. Verified 2026-07-17: one org, channels
for linkedin/facebook/instagram, per-post `metrics` come through per network.
"""
import json
import urllib.error
import urllib.request

import config

_HEADERS = {"Content-Type": "application/json"}


class BufferError(RuntimeError):
    pass


def _gql(query, variables=None):
    if not config.BUFFER_TOKEN:
        raise BufferError("BUFFER_API_KEY not set in .env")
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(
        config.BUFFER_GRAPHQL_URL, data=body, method="POST",
        headers={**_HEADERS, "Authorization": f"Bearer {config.BUFFER_TOKEN}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            payload = json.loads(r.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as e:
        raise BufferError(f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:200]}")
    except Exception as e:
        raise BufferError(str(e))
    if payload.get("errors"):
        raise BufferError(json.dumps(payload["errors"])[:300])
    return payload.get("data", {})


def org_and_channels():
    """Return (organization_id, [channel dicts])."""
    data = _gql("{ account { organizations { id } } }")
    orgs = (data.get("account") or {}).get("organizations") or []
    if not orgs:
        raise BufferError("no Buffer organizations on this account")
    oid = orgs[0]["id"]
    data = _gql(
        "query($i:ChannelsInput!){ channels(input:$i){ id service displayName type isDisconnected } }",
        {"i": {"organizationId": oid}},
    )
    channels = [c for c in (data.get("channels") or []) if not c.get("isDisconnected")]
    return oid, channels


_POSTS_Q = """
query P($i:PostsInput!,$f:Int,$a:String){
  posts(input:$i, first:$f, after:$a){
    edges { node { id status channelService sentAt dueAt text externalLink
                   metrics { name value unit } } }
    pageInfo { hasNextPage endCursor }
  }
}"""


def sent_posts(org_id, start_iso, end_iso):
    """All `sent` posts with dueAt in [start_iso, end_iso]. Paginates. Returns list of post dicts."""
    out, after = [], None
    while True:
        data = _gql(_POSTS_Q, {
            "i": {
                "organizationId": org_id,
                "filter": {"status": "sent", "dueAt": {"start": start_iso, "end": end_iso}},
                "sort": {"field": "dueAt", "direction": "desc"},
            },
            "f": 50, "a": after,
        })
        res = data.get("posts") or {}
        for edge in res.get("edges") or []:
            n = edge.get("node") or {}
            n["_metrics"] = {m["name"]: m["value"] for m in (n.get("metrics") or [])}
            out.append(n)
        page = res.get("pageInfo") or {}
        if page.get("hasNextPage") and page.get("endCursor"):
            after = page["endCursor"]
        else:
            break
    return out
