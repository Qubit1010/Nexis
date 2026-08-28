"""Build the 4-tab blog Sheet that website-creator consumes.

Reads the validated article markdown in this folder, parses the SEO Metadata block,
and writes Articles / Calendar / Keyword Map / Validation.

Reuses leads-to-crm's sheets.py rather than adding another gws client.
"""
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / ".claude" / "skills" / "leads-to-crm" / "scripts"))
import sheets  # noqa: E402

BLOG = Path(__file__).resolve().parent
NL = chr(10)
# publish order = the 12-week calendar order for batch one
ORDER = [
    ("ai-agent-vs-skill", "ai agent vs skill", "Teardown", 1),
    ("how-to-outsource-web-development", "how to outsource web development", "Buying decision", 1),
    ("ai-automation-cost", "ai automation cost", "Buying decision", 1),
    ("ai-agent-evaluation-framework", "ai agent evaluation framework", "Teardown", 2),
    ("best-n8n-projects", "best n8n projects", "Teardown", 2),
    ("ai-agent-vs-automation", "ai agent vs automation", "Refusals", 2),
]
# 3 posts a week, Mon / Wed / Fri, starting the Monday after the audit date
START = date(2026, 8, 24)
SLOTS = [0, 2, 4]  # Mon, Wed, Fri


def meta(text: str, key: str) -> str:
    m = re.search(rf"\*\*{re.escape(key)}:\*\*\s*(.+)", text)
    return m.group(1).strip() if m else ""


def parse(slug: str):
    raw = (BLOG / f"{slug}.md").read_text(encoding="utf-8")
    body, _, metablock = raw.partition("## SEO Metadata")
    body = body.rstrip().removesuffix("---").rstrip()
    h1 = re.search(r"^# (.+)$", body, re.M).group(1).strip()

    # the answer block is the first paragraph after the byline
    paras = [p.strip() for p in body.split("\n\n") if p.strip()]
    answer = next(p for p in paras if not p.startswith("#") and not p.startswith("By "))

    faq_src = body.split("## Frequently asked questions")[-1] if "## Frequently asked questions" in body else ""
    faq = re.findall(r"^### (.+?)\n+(.+?)(?=\n###|\Z)", faq_src, re.M | re.S)
    faq_pairs = [{"q": q.strip(), "a": " ".join(a.split())} for q, a in faq]

    cites = sorted(set(re.findall(r"\]\((https?://[^)]+)\)", body)))
    return {
        "slug": slug,
        "h1": h1,
        "body": body,
        "answer": " ".join(answer.split()),
        "faq": faq_pairs,
        "cites": cites,
        "title": meta(metablock, "Title tag"),
        "desc": meta(metablock, "Meta description"),
        "primary": meta(metablock, "Primary keyword"),
        "secondary": meta(metablock, "Secondary"),
        "links": meta(metablock, "Internal links"),
        "pov": meta(metablock, "POV source"),
        "quote": meta(metablock, "Expert quote"),
        "words": len(body.split()),
    }


def images(slug: str) -> dict:
    """Read the rendered image set and pull alt text from each SVG's aria-label.

    Alt text is authored in the SVG, not generated here, so the image and its
    description cannot drift apart.
    """
    d = BLOG / "images" / slug
    out = {"cover": "", "support": [], "alt": [], "svg": []}
    if not d.is_dir():
        return out
    for f in sorted(d.glob("*.svg")):
        png = f.with_suffix(".png")
        rel = f"/blog/images/{slug}/{png.name}"
        al = re.search(r'aria-label="([^"]+)"', f.read_text(encoding="utf-8"))
        alt = " ".join(al.group(1).split()) if al else ""
        if f.stem == "cover":
            out["cover"] = rel
            out["alt"].insert(0, f"cover: {alt}")
        else:
            out["support"].append(rel)
            out["alt"].append(f"{f.stem}: {alt}")
        out["svg"].append(f"/blog/images/{slug}/{f.name}")
    return out


def jsonld(a: dict) -> str:
    blocks = [{
        "@context": "https://schema.org", "@type": "Article",
        "headline": a["h1"][:110], "description": a["desc"],
        "author": {"@type": "Person", "name": "Aleem Ul Hassan",
                   "url": "https://aleemuh.com/about"},
        "mainEntityOfPage": f"https://aleemuh.com{a['slug_url']}",
    }]
    if a["faq"]:
        blocks.append({
            "@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": f["q"],
                            "acceptedAnswer": {"@type": "Answer", "text": f["a"]}}
                           for f in a["faq"]],
        })
    return json.dumps(blocks, ensure_ascii=False)


def main():
    arts = []
    for i, (slug, kw, pillar, week) in enumerate(ORDER):
        a = parse(slug)
        a["slug_url"] = f"/blog/{slug}"
        a["pillar"] = pillar
        a["week"] = week
        a["date"] = (START + timedelta(days=7 * (week - 1) + SLOTS[i % 3])).isoformat()
        a["jsonld"] = jsonld(a)
        a["img"] = images(slug)
        arts.append(a)

    if len(sys.argv) > 1:
        sid, first, gid = sys.argv[1], "Sheet1", 0
        print("reusing sheet:", sid)
    else:
        sid, first, gid = sheets.create_spreadsheet(
            "aleemuh.com Blog Engine - Articles for website-creator")
        print("created sheet:", sid)

    reqs = [{"updateSheetProperties": {"properties": {"sheetId": gid, "title": "Articles"},
                                       "fields": "title"}}]
    for t in ("Calendar", "Keyword Map", "Validation"):
        reqs.append({"addSheet": {"properties": {"title": t}}})
    sheets.batch_update(sid, reqs)
    print("tabs created (renamed", first, "-> Articles)")

    art_hdr = ["Status", "Publish Date", "Week", "Pillar", "Slug", "Title Tag",
               "Meta Description", "H1", "Answer Block", "Category",
               "Primary Keyword", "Secondary Keywords", "Body (markdown)",
               "FAQ (JSON)", "JSON-LD", "Internal Links", "Outbound Citations",
               "Expert Quote", "POV Source", "Word Count", "Hero Alt"]
    # The gws CLI passes the body as a process argument, and Windows CreateProcess
    # caps that at 32767 chars. Six full articles in one call is ~110KB, so write
    # one row per call and guard each one.
    LIMIT = 30000
    sheets.update_range(sid, f"Articles!A1:U1", [art_hdr])
    for i, a in enumerate(arts, start=2):
        row = ["Ready", a["date"], f"W{a['week']}", a["pillar"], a["slug_url"], a["title"],
               a["desc"], a["h1"], a["answer"], "AI & Automation",
               a["primary"], a["secondary"], a["body"],
               json.dumps(a["faq"], ensure_ascii=False), a["jsonld"], a["links"],
               "\n".join(a["cites"]), a["quote"], a["pov"], str(a["words"]),
               f"Illustration for {a['primary']}"]
        size = len(json.dumps([row]))
        if size > LIMIT:
            raise SystemExit(f"row {i} ({a['slug']}) is {size} chars, over the "
                             f"{LIMIT} CLI argument ceiling. Split the body column.")
        sheets.update_range(sid, f"Articles!A{i}:U{i}", [row])
        print(f"  row {i}: {a['slug']} ({size} chars)")
    print(f"Articles: {len(arts)} rows")

    # Image columns are written as their own V:Y range. Rewriting A:Y per row
    # would put the body column back in the payload and blow the 32767-char
    # CreateProcess argument ceiling that LIMIT above exists to respect.
    img_hdr = ["Cover Image", "Supporting Images", "Image Alt Text", "SVG Source"]
    sheets.update_range(sid, "Articles!V1:Y1", [img_hdr])
    for i, a in enumerate(arts, start=2):
        g = a["img"]
        sheets.update_range(sid, f"Articles!V{i}:Y{i}", [[
            g["cover"], NL.join(g["support"]),
            NL.join(g["alt"]), NL.join(g["svg"])]])
        print(f"  images row {i}: {a['slug']} "
              f"({1 if g['cover'] else 0} cover + {len(g['support'])} supporting)")

    cal = [["Week", "Publish Date", "Pillar", "Slug", "Primary Keyword",
            "Question It Answers", "Funnel Stage", "Status"]]
    stage = {"Teardown": "Awareness to consideration",
             "Buying decision": "Consideration to decision",
             "Refusals": "Awareness", "Proof": "Consideration to decision"}
    for a in arts:
        q = a["faq"][0]["q"] if a["faq"] else ""
        cal.append([f"W{a['week']}", a["date"], a["pillar"], a["slug_url"],
                    a["primary"], q, stage.get(a["pillar"], ""), "Ready"])
    sheets.update_range(sid, f"Calendar!A1:H{len(cal)}", cal)
    print(f"Calendar: {len(cal)-1} rows")

    km = [["Cluster", "Primary Keyword", "Mapped URL", "Winnability",
           "UGC on Page 1", "Median Result Age (days)", "Status"]]
    facts = {"ai agent vs skill": ("42", "5.0", "yes", "120"),
             "how to outsource web development": ("91", "5.0", "yes", "403"),
             "ai automation cost": ("22", "4.5", "yes", "78"),
             "ai agent evaluation framework": ("30", "5.0", "yes", "201"),
             "best n8n projects": ("15", "5.0", "yes", "365"),
             "ai agent vs automation": ("11", "4.5", "yes", "215")}
    for a in arts:
        c, w, u, age = facts[a["primary"]]
        km.append([c, a["primary"], a["slug_url"], w, u, age, "needs creating"])
    sheets.update_range(sid, f"'Keyword Map'!A1:G{len(km)}", km)
    print(f"Keyword Map: {len(km)-1} rows")

    val = [["Slug", "Primary Keyword", "Word Count", "Outbound Citations",
            "FAQ Count", "Title Chars", "Meta Chars", "Voice Contract",
            "Known Draft-Mode Failures"]]
    for a in arts:
        val.append([a["slug_url"], a["primary"], str(a["words"]), str(len(a["cites"])),
                    str(len(a["faq"])), str(len(a["title"])), str(len(a["desc"])),
                    "pass: no agency name, no university, no em dash, no smart quotes",
                    "eeat.author_named (cannot pass on a draft, byline is in the body); "
                    "section.length (markdown splitter artifact, measured 137-213w directly)"])
    sheets.update_range(sid, f"Validation!A1:I{len(val)}", val)
    print(f"Validation: {len(val)-1} rows")

    print(f"\nhttps://docs.google.com/spreadsheets/d/{sid}/edit")


if __name__ == "__main__":
    main()
