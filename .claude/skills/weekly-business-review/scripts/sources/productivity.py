"""ProductivityHub weekly completed tasks (its own Supabase project).

The project is MULTI-USER and the service_role key sees every user, so we resolve
this account's user_id by email and filter to it. `task_entries` is the per-day
completed-task log (title, category, completed_at, duration, star rating).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
import supa


def discover():
    """Build-time helper: list the tables in the ProductivityHub project."""
    return supa.list_tables(config.PRODUCTIVITY_SUPABASE_URL, config.PRODUCTIVITY_SUPABASE_KEY)


def _user_id(url, key):
    users = supa.rest_get(url, key, "users",
                          {"select": "id", "email": f"eq.{config.PRODUCTIVITY_USER_EMAIL}"})
    return users[0]["id"] if users else None


def collect(monday, sunday):
    url, key = config.PRODUCTIVITY_SUPABASE_URL, config.PRODUCTIVITY_SUPABASE_KEY
    if not (url and key):
        return {"available": False, "reason": "ProductivityHub Supabase not configured",
                "setup": "add PRODUCTIVITY_SUPABASE_URL + PRODUCTIVITY_SUPABASE_KEY to .env"}
    try:
        uid = _user_id(url, key)
        if not uid:
            return {"available": False, "reason": f"no ProductivityHub user for {config.PRODUCTIVITY_USER_EMAIL}"}
        cats = {c["id"]: c["name"] for c in supa.rest_get(url, key, "categories", {"select": "id,name"})}
        rows = supa.rest_get(url, key, config.PRODUCTIVITY_TASKS_TABLE, {
            "select": "title,category_id,completed_at,duration_minutes,star_rating",
            "and": (f"(user_id.eq.{uid},is_completed.is.true,"
                    f"completed_at.gte.{monday.isoformat()},completed_at.lte.{sunday.isoformat()}T23:59:59)"),
            "order": "completed_at.desc",
        })
    except Exception as e:
        return {"available": False, "reason": f"ProductivityHub read failed: {e}"}

    by_cat, minutes, tasks = {}, 0, []
    for r in rows if isinstance(rows, list) else []:
        cat = cats.get(r.get("category_id"), "Uncategorized")
        by_cat[cat] = by_cat.get(cat, 0) + 1
        minutes += r.get("duration_minutes") or 0
        tasks.append({
            "title": r.get("title", ""), "category": cat,
            "completed_at": r.get("completed_at"),
            "minutes": r.get("duration_minutes"), "stars": r.get("star_rating"),
        })
    # by_category sorted desc for a stable, useful display
    by_cat = dict(sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True))
    return {
        "available": True,
        "completed": len(tasks),
        "hours": round(minutes / 60, 1),
        "by_category": by_cat,
        "tasks": tasks,
    }
