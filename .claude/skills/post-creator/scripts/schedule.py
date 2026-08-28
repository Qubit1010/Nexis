"""SM Schedule row I/O for the post-creator skill.

Reads the Weekly Posting Schedule sheet, resolves columns by header name (the
sheet has hidden/renamed columns, so positional indexing would silently break),
parses a row into the clean dict the orchestration needs, and writes the Doc
URL + Status back.

Reuses sheets.py (copied from leads-to-crm) for all gws plumbing.

CLI:
    python schedule.py next                       # next actionable Draft row
    python schedule.py get --row 208              # one row by sheet row number
    python schedule.py find --topic "Ponytail"    # rows whose Topic matches
    python schedule.py write --row 208 --doc-url "https://docs.google.com/..." [--status Draft]
    python schedule.py write --row 208 --doc-url "..." --pillars "Founder Journey" \
        --content-mode "Personal Story"

All commands emit JSON to stdout. Row numbers are the real 1-based sheet rows.

Two pillar axes, deliberately kept apart (see references/column-map.md):
  * INGREDIENT_KEYS - the 7 Unswappable qualities every piece must contain
    (agency/personal-brand-voice.md). A per-piece craft check; nothing to balance.
  * TOPICAL_PILLAR_KEYS - the 4 subjects a piece is about
    (agency/personal-brand-pillars.md). This is the axis the target mix in
    agency/personal-brand-content-engine.md is measured in.
The Pillars cell parses as either and reports each separately; --pillars writes
the topical axis, because that is the one with a mix to balance.
"""

import argparse
import io
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

import sheets

SHEET_ID = "13RiOJpxWly5BztZdpLhGK5kT_Unna8Lnc-8GboApJ74"
TAB = "SM Schedule"

# Header aliases -> canonical field. Matched case-insensitively via
# sheets.header_index so the sheet can evolve without breaking us.
FIELD_HEADERS = {
    "date": ["Date"],
    "day": ["Day"],
    "platform": ["Platform", "Media Platform"],
    "post_type": ["Post Type"],
    "content_theme": ["Content Theme"],
    "topic": ["Topic / Idea", "Topic/Idea", "Topic"],
    "description": ["Post Description", "Description"],
    "reference": ["Reference"],
    "format": ["Format"],
    "content_mode": ["Content Mode"],
    "pillars": ["Pillars"],
    "design_template": ["Design Template"],
    "final_post": ["Final Video/Post", "Final Post", "Final Video / Post"],
    "publish_time": ["Publish Time"],
    "status": ["Status"],
    "editor": ["Editor"],
}

CONTENT_MODE_KEYS = {
    "news/analysis": "news",
    "news / analysis": "news",
    "opinion/pov": "opinion",
    "opinion / pov": "opinion",
    "personal story": "story",
    "tutorial/how-to": "tutorial",
    "tutorial / how-to": "tutorial",
}

CONTENT_MODE_LABELS = {
    "news": "News/Analysis",
    "opinion": "Opinion/POV",
    "story": "Personal Story",
    "tutorial": "Tutorial/How-to",
}

# Axis 1: the 7 Unswappable INGREDIENTS - qualities every piece must contain.
# Defined in agency/personal-brand-voice.md. A craft check, not a mix to balance:
# every post needs at least two, so there is nothing to weight.
INGREDIENT_KEYS = {
    "lived exp": "lived_experience",
    "lived exp.": "lived_experience",
    "lived experience": "lived_experience",
    "strong pov": "strong_pov",
    "cross-domain": "cross_domain",
    "cross domain": "cross_domain",
    "taste & judgment": "taste_judgment",
    "taste and judgment": "taste_judgment",
    "identity": "identity_voice",
    "practical stakes": "practical_stakes",
    "content specific": "content_specific",
}

# Axis 2: the 4 TOPICAL PILLARS - what a piece is about. Defined in
# agency/personal-brand-pillars.md, and the axis the target mix in
# agency/personal-brand-content-engine.md section 5 is expressed in. This is what
# the Pillars cell should hold; it is empty on every row to date.
TOPICAL_PILLAR_KEYS = {
    "ai & automation": "ai_automation",
    "ai and automation": "ai_automation",
    "ai automation": "ai_automation",
    "founder journey": "founder_journey",
    "tech insights": "tech_insights",
    "tech insight": "tech_insights",
    "young builder": "young_builder",
    "young builder / learning in public": "young_builder",
    "young builder/learning in public": "young_builder",
    "learning in public": "young_builder",
}

TOPICAL_PILLAR_LABELS = {
    "ai_automation": "AI & Automation",
    "founder_journey": "Founder Journey",
    "tech_insights": "Tech Insights",
    "young_builder": "Young Builder",
}

# Templates that actually exist on disk. A row naming anything else is an error
# the orchestrator must surface, not guess around. Globbed, not hardcoded — new
# templates get onboarded regularly and a stale list rejects valid rows.
_SKILLS = Path(__file__).resolve().parents[2]


def _template_numbers(skill, prefix):
    d = _SKILLS / skill / "references"
    return {int(m.group(1))
            for p in d.glob(f"{prefix}-*") if p.is_dir()
            for m in [re.fullmatch(rf"{prefix}-(\d+)", p.name)] if m}


LINKEDIN_TEMPLATES = _template_numbers("linkedin-infographics", "LinkedIn-Template")
INSTAGRAM_TEMPLATES = _template_numbers("carousel", "Instagram-Template")


def _parse_templates(cell):
    """Parse the Design Template cell into {linkedin: N|None, instagram: N|None, errors: []}.

    Cells look like: "LinkedIn Infographic — Template 11,\nInstagram-Template-6"
    (any dash style, any separator).
    """
    out = {"linkedin": None, "instagram": None, "errors": []}
    if not cell:
        return out
    li = re.search(r"linkedin[^0-9]*template\s*[-—–]?\s*(\d+)", cell, re.I)
    ig = re.search(r"instagram[^0-9]*template\s*[-—–]?\s*(\d+)", cell, re.I)
    if li:
        n = int(li.group(1))
        if n in LINKEDIN_TEMPLATES:
            out["linkedin"] = n
        else:
            out["errors"].append(
                f"LinkedIn Template {n} has no folder on disk (have: {sorted(LINKEDIN_TEMPLATES)})")
    if ig:
        n = int(ig.group(1))
        if n in INSTAGRAM_TEMPLATES:
            out["instagram"] = n
        else:
            out["errors"].append(
                f"Instagram Template {n} has no folder on disk (have: {sorted(INSTAGRAM_TEMPLATES)})")
    return out


def _parse_pillars(cell):
    """Split the Pillars cell across both axes.

    Returns (ingredients, topical_pillars, unrecognized). A cell may legitimately
    carry either axis or both; anything matching neither is surfaced rather than
    dropped, so a typo shows up instead of silently becoming an empty list.
    """
    ingredients, topical, unknown = [], [], []
    for part in re.split(r"[,\n]+", cell or ""):
        p = part.strip().lower().rstrip(".")
        if not p:
            continue
        if p in INGREDIENT_KEYS:
            ingredients.append(INGREDIENT_KEYS[p])
        elif p in TOPICAL_PILLAR_KEYS:
            topical.append(TOPICAL_PILLAR_KEYS[p])
        else:
            unknown.append(part.strip())
    return ingredients, topical, unknown


def _col_map(header_row):
    """Resolve every canonical field to a 0-based column index (or None)."""
    return {field: sheets.header_index(header_row, aliases)
            for field, aliases in FIELD_HEADERS.items()}


def _cell(row, idx):
    if idx is None or idx >= len(row):
        return ""
    return (row[idx] or "").strip()


def _parse_row(row, cols, row_num):
    mode_raw = _cell(row, cols["content_mode"])
    ingredients, topical_pillars, pillar_unknown = _parse_pillars(
        _cell(row, cols["pillars"]))
    templates = _parse_templates(_cell(row, cols["design_template"]))
    return {
        "row": row_num,
        "date": _cell(row, cols["date"]),
        "day": _cell(row, cols["day"]),
        "platform": _cell(row, cols["platform"]),
        "post_type": _cell(row, cols["post_type"]),
        "topic": _cell(row, cols["topic"]),
        "description": _cell(row, cols["description"]),
        "reference": _cell(row, cols["reference"]),
        "format": _cell(row, cols["format"]),
        "content_mode": mode_raw,
        "content_mode_key": CONTENT_MODE_KEYS.get(mode_raw.strip().lower()),
        "ingredients": ingredients,
        "topical_pillars": topical_pillars,
        "pillars_unrecognized": pillar_unknown,
        "design_template": _cell(row, cols["design_template"]),
        "templates": templates,
        "final_post": _cell(row, cols["final_post"]),
        "publish_time": _cell(row, cols["publish_time"]),
        "status": _cell(row, cols["status"]),
        "editor": _cell(row, cols["editor"]),
    }


def _load():
    rows = sheets.read_values(SHEET_ID, f"{TAB}!A1:AE")
    if not rows:
        raise SystemExit(json.dumps({"error": "Could not read the SM Schedule tab. Check gws auth (gws auth login)."}))
    cols = _col_map(rows[0])
    missing = [f for f in ("topic", "final_post", "status") if cols[f] is None]
    if missing:
        raise SystemExit(json.dumps({"error": f"Header row is missing expected columns: {missing}", "header": rows[0]}))
    return rows, cols


def _row_date(parsed, today=None):
    """Parse the Date cell ("Jul 8") into a date, assuming the current year.

    ponytail: no-year cells make Dec->Jan rollover ambiguous; fine for a weekly
    sheet that's re-planned every few days.
    """
    raw = parsed["date"].strip()
    if not raw:
        return None
    today = today or date.today()
    # Append the year for year-less cells ("Jul 8") — strptime without a year is
    # deprecated and can't parse leap days.
    for raw_try, fmts in ((raw, ("%b %d %Y", "%B %d %Y")),
                          (f"{raw} {today.year}", ("%b %d %Y", "%B %d %Y"))):
        for fmt in fmts:
            try:
                return datetime.strptime(raw_try, fmt).date()
            except ValueError:
                continue
    return None


def _actionable(parsed, today=None):
    """A row `next` should pick: dated today-or-later, explicit Draft status,
    has a topic, is not a Reel, and has no final post yet.

    Blank-status rows are unscheduled backlog ideas and past-dated Drafts are
    stale weeks — both reachable via `get`/`find`, never via `next`.
    """
    if not parsed["topic"]:
        return False
    if "reel" in parsed["post_type"].lower():
        return False  # reel rows belong to the reel-creator skill
    if parsed["final_post"]:
        return False
    if parsed["status"].lower() != "draft":
        return False
    d = _row_date(parsed, today)
    return d is not None and d >= (today or date.today())


def cmd_next(_args):
    rows, cols = _load()
    for i, row in enumerate(rows[1:], start=2):
        parsed = _parse_row(row, cols, i)
        if _actionable(parsed):
            return parsed
    return {"error": "No actionable Draft rows found (topic present, not a Reel, Final Video/Post empty)."}


def cmd_get(args):
    rows, cols = _load()
    idx = args.row - 1
    if idx < 1 or idx >= len(rows):
        return {"error": f"Row {args.row} is out of range (sheet has {len(rows)} rows)."}
    return _parse_row(rows[idx], cols, args.row)


def cmd_find(args):
    rows, cols = _load()
    needle = args.topic.strip().lower()
    hits = []
    for i, row in enumerate(rows[1:], start=2):
        parsed = _parse_row(row, cols, i)
        if needle in parsed["topic"].lower():
            hits.append(parsed)
    return {"matches": hits, "count": len(hits)}


def _normalize_pillars(raw):
    """Accept keys or sheet labels on the topical axis; emit canonical labels.

    Raises on anything unrecognized. Writing a typo into the column the mix is
    measured from is worse than refusing, because the cell then looks filled.
    """
    out = []
    for part in re.split(r"[,\n]+", raw or ""):
        p = part.strip()
        if not p:
            continue
        low = p.lower().rstrip(".")
        if low in TOPICAL_PILLAR_KEYS:
            out.append(TOPICAL_PILLAR_LABELS[TOPICAL_PILLAR_KEYS[low]])
        elif p in TOPICAL_PILLAR_LABELS:
            out.append(TOPICAL_PILLAR_LABELS[p])
        elif low in INGREDIENT_KEYS:
            raise ValueError(
                "%r is an Unswappable ingredient, not a topical pillar. The Pillars "
                "column holds the 4 topical pillars (%s); ingredients are a per-piece "
                "craft check, not a mix to balance."
                % (p, ", ".join(TOPICAL_PILLAR_LABELS.values())))
        else:
            raise ValueError("Unrecognized pillar %r. Expected one of: %s"
                             % (p, ", ".join(TOPICAL_PILLAR_LABELS.values())))
    return out


def _normalize_content_mode(raw):
    """Accept a canonical key ("story") or a sheet label ("Personal Story")."""
    p = (raw or "").strip()
    if not p:
        return None
    if p in CONTENT_MODE_LABELS:
        return CONTENT_MODE_LABELS[p]
    if p.lower() in CONTENT_MODE_KEYS:
        return CONTENT_MODE_LABELS[CONTENT_MODE_KEYS[p.lower()]]
    raise ValueError("Unrecognized content mode %r. Expected one of: %s"
                     % (p, ", ".join(CONTENT_MODE_LABELS.values())))


def _shell_safe(values):
    """Guard the shell=True gws fallback.

    The active path here is `node run.js` with shell=False, where any value is
    safe. But _find_gws falls back to gws.cmd with shell=True, and "AI & Automation"
    would be split by cmd.exe there. Refuse rather than write a truncated cell.
    """
    if not sheets._GWS_SHELL:
        return
    bad = [v for v in values if any(c in v for c in "&|<>^")]
    if bad:
        raise ValueError(
            "gws resolved to a shell invocation and these values carry cmd.exe "
            "metacharacters: %s. Write them by hand, or reinstall the gws node CLI."
            % bad)


def cmd_write(args):
    # Validate BEFORE _load(), which is a network read. A bad label then fails
    # instantly and offline, instead of after a round-trip, and can never leave
    # the row half-written (doc URL in, pillars rejected).
    try:
        pillar_labels = _normalize_pillars(args.pillars) if args.pillars else None
        mode_label = _normalize_content_mode(args.content_mode)
        _shell_safe([v for v in (", ".join(pillar_labels) if pillar_labels else None,
                                 mode_label) if v])
    except ValueError as e:
        return {"status": "error", "row": args.row, "error": str(e)}

    rows, cols = _load()
    col_final = sheets.col_letter(cols["final_post"])
    ok = sheets.update_range(SHEET_ID, f"{TAB}!{col_final}{args.row}", [[args.doc_url]])
    out = {"row": args.row, "final_post_cell": f"{col_final}{args.row}",
           "wrote_status": args.status}

    if cols["status"] is not None:
        col_status = sheets.col_letter(cols["status"])
        ok = sheets.update_range(
            SHEET_ID, f"{TAB}!{col_status}{args.row}", [[args.status]]) and ok

    for field, value in (("pillars", ", ".join(pillar_labels) if pillar_labels else None),
                         ("content_mode", mode_label)):
        if value is None:
            continue
        if cols[field] is None:
            out.setdefault("skipped", []).append(
                f"no {field!r} column in the header row")
            continue
        letter = sheets.col_letter(cols[field])
        ok = sheets.update_range(
            SHEET_ID, f"{TAB}!{letter}{args.row}", [[value]]) and ok
        out[f"wrote_{field}"] = value
        out[f"{field}_cell"] = f"{letter}{args.row}"

    out["status"] = "ok" if ok else "error"
    return out


def selftest():
    """Offline check of the parsing logic (no network)."""
    t = _parse_templates("LinkedIn Infographic — Template 11,\nInstagram-Template-6")
    assert t["linkedin"] == 11 and t["instagram"] == 6 and not t["errors"], t
    t = _parse_templates("LinkedIn Infographic - Template 3")
    assert t["linkedin"] is None and t["errors"], t
    t = _parse_templates("Instagram-Template-1")
    assert t["instagram"] == 1 and t["linkedin"] is None, t
    ing, top, unknown = _parse_pillars("Practical Stakes, Content Specific")
    assert ing == ["practical_stakes", "content_specific"], ing
    assert not top and not unknown, (top, unknown)
    ing, top, unknown = _parse_pillars("Lived Exp\nStrong POV")
    assert ing == ["lived_experience", "strong_pov"] and not top, (ing, top)
    # The two axes coexist in one cell and stay separated; junk is surfaced.
    ing, top, unknown = _parse_pillars("Founder Journey, Lived Exp, Nonsense")
    assert ing == ["lived_experience"], ing
    assert top == ["founder_journey"], top
    assert unknown == ["Nonsense"], unknown
    ing, top, _ = _parse_pillars("AI & Automation\nYoung Builder / Learning in Public")
    assert top == ["ai_automation", "young_builder"] and not ing, (top, ing)
    assert CONTENT_MODE_KEYS["news/analysis"] == "news"
    # Write-side normalization takes keys or labels and refuses the wrong axis.
    assert _normalize_pillars("founder journey, Tech Insights") == \
        ["Founder Journey", "Tech Insights"]
    assert _normalize_pillars("AI and Automation") == ["AI & Automation"]
    assert _normalize_content_mode("story") == "Personal Story"
    assert _normalize_content_mode("Tutorial/How-to") == "Tutorial/How-to"
    assert _normalize_content_mode("") is None
    for bad, why in (("Lived Exp", "ingredient must be rejected on the pillar axis"),
                     ("Bogus Pillar", "unknown pillar label must be rejected")):
        try:
            _normalize_pillars(bad)
        except ValueError:
            pass
        else:
            raise AssertionError(why)
    try:
        _normalize_content_mode("Ranting")
    except ValueError:
        pass
    else:
        raise AssertionError("unknown content mode must be rejected")
    hdr = ["Date", "Day", "Platform", "Post Type", "Media Type", "Content Theme",
           "Topic / Idea", "Post Description", "Reference", "Format", "Content Mode",
           "Pillars", "Design Template", "Final Video/Post", "Publish Time", "Status", "Editor"]
    cols = _col_map(hdr)
    row = ["Jul 8", "Wednesday", "All", "Text + I...", "Text + Co...", "Tech Tutorial",
           "codegraph", "For businesses...", "", "Text Post", "Personal Story",
           "Lived Exp, Identity", "LinkedIn Infographic — Template 10,\nInstagram-Template-1",
           "", "3:00 pm", "Draft", "Aleem"]
    p = _parse_row(row, cols, 210)
    assert p["topic"] == "codegraph" and p["content_mode_key"] == "story", p
    assert p["ingredients"] == ["lived_experience", "identity_voice"], p
    assert p["topical_pillars"] == [], p
    assert p["templates"]["linkedin"] == 10 and p["templates"]["instagram"] == 1, p
    today = date(2026, 7, 7)
    assert _actionable(p, today)  # Jul 8 >= Jul 7
    assert not _actionable(dict(p, post_type="Reel"), today)
    assert not _actionable(dict(p, status=""), today)   # blank status = backlog idea
    assert not _actionable(dict(p, date="May 30"), today)  # stale past-dated Draft
    assert not _actionable(dict(p, date=""), today)     # undated Draft = not scheduled
    assert _row_date(dict(p, date="Jul 12"), today) == date(2026, 7, 12)
    print("selftest: all assertions passed")


def main():
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="SM Schedule row I/O for post-creator.")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("next")
    g = sub.add_parser("get")
    g.add_argument("--row", type=int, required=True)
    f = sub.add_parser("find")
    f.add_argument("--topic", required=True)
    w = sub.add_parser("write")
    w.add_argument("--row", type=int, required=True)
    w.add_argument("--doc-url", required=True)
    w.add_argument("--status", default="Draft")
    w.add_argument("--pillars", default=None,
                   help="Topical pillar(s) for the Pillars column, comma-separated. "
                        "One of: " + ", ".join(TOPICAL_PILLAR_LABELS.values()))
    w.add_argument("--content-mode", default=None,
                   help="Content Mode cell value. One of: "
                        + ", ".join(CONTENT_MODE_LABELS.values()))
    sub.add_parser("selftest")
    args = ap.parse_args()
    if args.cmd == "selftest":
        selftest()
        return
    fn = {"next": cmd_next, "get": cmd_get, "find": cmd_find, "write": cmd_write}[args.cmd]
    print(json.dumps(fn(args), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
