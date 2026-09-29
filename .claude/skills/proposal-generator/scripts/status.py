"""Who opened or signed which proposal.

Usage:
  python status.py            every rendered proposal
  python status.py <id>       one proposal
  python status.py --json     machine-readable

Reads client-projects/*/proposals/*/meta.json for local state and Supabase proposal_events
for views and signatures. If Supabase cannot be queried it says so, instead of reporting
"no views", because an unrun check that looks like an empty result is the failure to avoid.
"""
import argparse
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deploy import all_proposals, load_env  # noqa: E402

FIELDS = "proposal_id,event_type,created_at,ip,user_agent,signer_name,signer_email,option_name,amount_due,currency"


def events(env, ids):
    url, key = env.get("SUPABASE_URL"), env.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        return None, "SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing from .env"
    req = urllib.request.Request(
        f"{url}/rest/v1/proposal_events?proposal_id=in.({','.join(ids)})&select={FIELDS}&order=created_at.asc",
        headers={"apikey": key, "Authorization": f"Bearer {key}"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read()), None
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("id", nargs="?")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    props = [(home, m) for home, m in all_proposals() if not a.id or m["id"] == a.id]
    if not props:
        print(f"no rendered proposal{' with id ' + a.id if a.id else 's'} under client-projects/")
        sys.exit(1)
    rows, err = events(load_env(), [m["id"] for _, m in props])

    report = []
    for home, m in props:
        p = json.loads((home / "proposal.json").read_text(encoding="utf-8-sig"))
        item = {"id": m["id"], "client": p["client"]["company"], "status": m.get("status"),
                "valid_until": p["valid_until"], "url": m.get("url"),
                "pay_links": {o["id"]: bool(o.get("pay_url")) for o in p.get("options", [])}}
        if err:
            item["events"] = f"COULD NOT CHECK: {err}"
        else:
            mine = [r for r in rows if r["proposal_id"] == m["id"]]
            views = [r for r in mine if r["event_type"] == "view"]
            sign = next((r for r in mine if r["event_type"] == "sign"), None)
            item["views"] = {"count": len(views), "first": views[0]["created_at"] if views else None,
                             "last": views[-1]["created_at"] if views else None,
                             "distinct_ips": len({v["ip"] for v in views})}
            item["signed"] = sign and {k: sign[k] for k in ("signer_name", "signer_email", "option_name",
                                                           "amount_due", "currency", "created_at", "ip")}
        report.append(item)

    if a.json:
        print(json.dumps(report, indent=2))
        return
    for r in report:
        print(f"\n{r['id']}  ({r['client']})  status={r['status']}  valid until {r['valid_until']}")
        if r.get("url"):
            print(f"  link: {r['url']}")
        if isinstance(r.get("events"), str):
            print(f"  views/signature: {r['events']}")
            continue
        v = r["views"]
        print(f"  views: {v['count']} from {v['distinct_ips']} IP(s)" +
              (f", first {v['first']}, last {v['last']}" if v["count"] else " (not opened yet)"))
        s = r["signed"]
        if s:
            print(f"  SIGNED by {s['signer_name']} <{s['signer_email']}> on {s['created_at']}: "
                  f"{s['option_name']}, {s['currency']} {s['amount_due']:,.0f} due to start")
        else:
            print("  not signed")


if __name__ == "__main__":
    main()
