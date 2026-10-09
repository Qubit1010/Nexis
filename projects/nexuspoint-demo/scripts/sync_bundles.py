"""Copy the approved PKR tiers (quetta-local-market/data/kit.json) and their Urdu text
(nexuspoint-quetta-landing/content/site.json) into src/data/bundles.json, so the demo hub,
the landing site and the PDFs always quote the same prices. Re-run after any price change."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJ = ROOT.parent
kit = json.loads((PROJ / "quetta-local-market/data/kit.json").read_text(encoding="utf-8"))
site = json.loads((PROJ / "nexuspoint-quetta-landing/content/site.json").read_text(encoding="utf-8"))
out = {"terms": kit["terms"], "sectors": {}}
for s in kit["sectors"]:
    if s["key"] not in ("healthcare", "food", "education"):
        continue
    ur = site["tiers_ur"][s["key"]]
    out["sectors"][s["key"]] = [
        {"name": t["name"], "tag_en": t["tag"], "tag_ur": ur["tags"][i], "setup": t["setup"], "monthly": t["monthly"],
         "rec": bool(t.get("rec")), "items_en": t["items"], "items_ur": ur["items"][i]}
        for i, t in enumerate(s["tiers"])]
(ROOT / "src/data/bundles.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
print("bundles synced:", {k: [t["setup"] for t in v] for k, v in out["sectors"].items()})
