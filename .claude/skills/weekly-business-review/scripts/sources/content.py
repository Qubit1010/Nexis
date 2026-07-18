"""Content performance for the week from Buffer (LinkedIn / Instagram / Facebook).

Pulls `sent` posts whose dueAt falls in the week window and aggregates each network's
own metric set (Buffer returns different metrics per platform). Only posts published
THROUGH Buffer are visible.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import buffer

# metrics that must be averaged across posts, not summed (they're percentages / rates)
_AVG_METRICS = {"Eng. Rate"}


def collect(monday, sunday):
    start_iso = f"{monday.isoformat()}T00:00:00.000Z"
    end_iso = f"{sunday.isoformat()}T23:59:59.999Z"  # UTC week window
    try:
        org_id, _channels = buffer.org_and_channels()
        posts = buffer.sent_posts(org_id, start_iso, end_iso)
    except buffer.BufferError as e:
        return {"available": False, "reason": str(e)}

    platforms = {}
    post_list = []
    for p in posts:
        svc = p.get("channelService") or "unknown"
        mets = p.get("_metrics", {})
        pl = platforms.setdefault(svc, {"posts": 0, "_sums": {}, "_rate_sum": {}, "_rate_n": {}})
        pl["posts"] += 1
        for name, val in mets.items():
            if not isinstance(val, (int, float)):
                continue
            if name in _AVG_METRICS:
                pl["_rate_sum"][name] = pl["_rate_sum"].get(name, 0) + val
                pl["_rate_n"][name] = pl["_rate_n"].get(name, 0) + 1
            else:
                pl["_sums"][name] = pl["_sums"].get(name, 0) + val
        post_list.append({
            "platform": svc,
            "sentAt": p.get("sentAt"),
            "text": (p.get("text") or "").strip()[:160],
            "link": p.get("externalLink"),
            "metrics": mets,
        })

    # finalize: merge summed + averaged metrics into one rounded dict per platform
    for svc, pl in platforms.items():
        metrics = {k: round(v, 2) for k, v in pl["_sums"].items()}
        for name, total in pl["_rate_sum"].items():
            metrics[name] = round(total / pl["_rate_n"][name], 2)
        pl["metrics"] = metrics
        del pl["_sums"], pl["_rate_sum"], pl["_rate_n"]

    post_list.sort(key=lambda x: x.get("sentAt") or "", reverse=True)
    return {
        "available": True,
        "platforms": platforms,
        "totals": {"posts": len(post_list)},
        "posts": post_list,
    }
