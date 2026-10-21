"""Copy the approved PKR tiers per market into src/data/bundles.json, so the demo hub, the landing
sites and the PDFs always quote the same prices. Re-run after any price change.

    {"markets": {"quetta": {"terms", "sectors"}, "islamabad": {"terms", "sectors"}}}

- quetta:    quetta-local-market/data/kit.json + Urdu tiers from nexuspoint-quetta-landing/content/site.json.
             If either file is missing in this checkout, the quetta entry already in bundles.json is kept
             unchanged (a legacy top-level {terms, sectors} file is read as quetta).
             Set QUETTA_PROJECTS_DIR to read them from another checkout (e.g. D:/Work/nexis-team/projects).
- islamabad: islamabad-local-market/data/kit.json, which carries its own Urdu tags and items.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROJ = ROOT.parent
OUT = ROOT / "src/data/bundles.json"
SECTORS = ("healthcare", "food", "education", "real-estate")


def tier(t: dict, tag_ur: str, items_ur: list) -> dict:
    return {"name": t["name"], "tag_en": t["tag"], "tag_ur": tag_ur, "setup": t["setup"], "monthly": t["monthly"],
            "rec": bool(t.get("rec")), "items_en": t["items"], "items_ur": items_ur}


def quetta_from_kit() -> dict | None:
    base = Path(os.environ.get("QUETTA_PROJECTS_DIR") or PROJ)
    kit_path = base / "quetta-local-market/data/kit.json"
    site_path = base / "nexuspoint-quetta-landing/content/site.json"
    if not (kit_path.exists() and site_path.exists()):
        return None
    kit = json.loads(kit_path.read_text(encoding="utf-8"))
    site = json.loads(site_path.read_text(encoding="utf-8"))
    out = {"terms": kit["terms"], "sectors": {}}
    for s in kit["sectors"]:
        ur = site.get("tiers_ur", {}).get(s["key"])
        if s["key"] not in SECTORS or not ur:
            continue
        out["sectors"][s["key"]] = [tier(t, ur["tags"][i], ur["items"][i]) for i, t in enumerate(s["tiers"])]
    return out


def islamabad_from_kit() -> dict:
    kit = json.loads((PROJ / "islamabad-local-market/data/kit.json").read_text(encoding="utf-8"))
    out = {"terms": kit["terms"], "sectors": {}}
    for s in kit["sectors"]:
        if s["key"] in SECTORS:
            out["sectors"][s["key"]] = [tier(t, t.get("tag_ur") or t["tag"], t.get("items_ur") or t["items"]) for t in s["tiers"]]
    return out


def existing_quetta() -> dict | None:
    if not OUT.exists():
        return None
    old = json.loads(OUT.read_text(encoding="utf-8"))
    if "markets" in old:
        return old["markets"].get("quetta")
    if "sectors" in old:  # legacy single-market file
        return {"terms": old.get("terms", {}), "sectors": old["sectors"]}
    return None


def main() -> None:
    quetta = quetta_from_kit()
    if quetta is None:
        quetta = existing_quetta()
        if quetta is None:
            example = json.loads((ROOT / "src/data/bundles.example.json").read_text(encoding="utf-8"))
            quetta = example["markets"]["quetta"]
            print("WARNING: Quetta kit and site.json are missing and bundles.json had no quetta entry; "
                  "using the zero-price example for quetta. Restore the private Quetta files before a Quetta demo.",
                  file=sys.stderr)
        else:
            print("Quetta kit or site.json missing in this checkout: kept the existing quetta entry unchanged.")
    out = {"markets": {"quetta": quetta, "islamabad": islamabad_from_kit()}}
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    for market, data in out["markets"].items():
        print(f"{market}:", {k: [t["setup"] for t in v] for k, v in data["sectors"].items()})


if __name__ == "__main__":
    main()
