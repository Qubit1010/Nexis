"""Tailor a prospect's demo from hand-verified findings, then build the full report.

    python scripts/make_presence.py <demo-slug>

Reads data/demos/<slug>.json (made by make_demo.py) and data/presence/<slug>.json (written by hand from
verified sources; gitignored, because it names a real prospect). The presence file has:

  - the page-2 content (label, eyebrow, title, sub, stats, findings, moves, sources), and
  - an optional "patch" that is applied to the demo and synced to Supabase before rendering:
      name, facts{...}, about, services_sample[], fixes[{en,ur}],
      health_set{<key>: {ok, en, ur}}  (override an existing health row; the score is recomputed),
      health_extra[{key, ok, weight, en, ur}]  (extra report rows, usually weight 0)

Writes deliverables/Report-<slug>-en.pdf = Health Check (EN) + presence page, and re-renders the
Health Check EN + UR. Run unsandboxed on Python312.
"""
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import fitz  # PyMuPDF

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import make_demo as md  # noqa: E402
import render  # noqa: E402

PROJECT = HERE.parent


def apply_patch(demo: dict, patch: dict) -> None:
    prof = demo["profile"]
    if patch.get("name"):
        demo["name"] = prof["facts"]["name"] = patch["name"]
    prof["facts"].update(patch.get("facts", {}))
    for key in ("about", "services_sample"):
        if key in patch:
            prof[key] = patch[key]
    if "fixes" in patch:
        demo["xray"]["fixes"] = patch["fixes"]
    items = demo["health"]["items"]
    for key, over in patch.get("health_set", {}).items():
        row = next(i for i in items if i["key"] == key)
        row.update(over)
    extra = patch.get("health_extra", [])
    items[:] = [i for i in items if i["key"] not in {e["key"] for e in extra}] + extra
    demo["health"]["score"] = sum(i["weight"] for i in items if i["ok"])


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    slug = sys.argv[1]
    demo_path = PROJECT / "data" / "demos" / f"{slug}.json"
    demo = json.loads(demo_path.read_text(encoding="utf-8"))
    pr = json.loads((PROJECT / "data" / "presence" / f"{slug}.json").read_text(encoding="utf-8"))

    if pr.get("patch"):
        apply_patch(demo, pr["patch"])
        demo_path.write_text(json.dumps(demo, ensure_ascii=False, indent=1), encoding="utf-8")
        md.upsert(demo)
        print(f"[ok] hub row synced, health score {demo['health']['score']}/100")

    base = md.ENV.get("DEMO_BASE_URL", "https://nexuspoint-demo.vercel.app")
    hub = f"{base}/d/{demo['slug']}?t={demo['token']}"
    chat = f"{hub}&chat=1"
    md.render_pdf(demo, hub, chat)  # Health Check EN + UR, with the patched rows

    ctx = render.load_context()
    ctx.update({"demo": demo, "pr": pr, "prepared": datetime.now(timezone.utc).strftime("%Y-%m-%d")})
    asyncio.run(render.render([("presence.html.j2", f"Presence-{slug}-en", render.A4, {})], ctx))

    out = render.OUT
    merged = fitz.open()
    for f in (out / f"Health-Check-{slug}-en.pdf", out / f"Presence-{slug}-en.pdf"):
        merged.insert_pdf(fitz.open(f))
    dest = out / f"Report-{slug}-en.pdf"
    merged.save(str(dest))
    print(f"[ok] {dest.name}: {len(merged)} page(s)\nhub: {hub}")


if __name__ == "__main__":
    main()
