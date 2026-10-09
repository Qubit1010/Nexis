"""School landing isolation, scoped programs, missing data and workflow entry checks.
Usage: python tests/school_landing_checks.py [base_url] [--vercel]
Uses isolated fictional profiles, retains them expired, never changes real school records.
"""
import atexit
import copy
import html
import json
import re
import secrets
import urllib.parse
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
import healthcare_eval as h
from private_fixtures import demo_token

passed, fixtures = [], []


def check(name, condition):
    assert condition, name
    passed.append(name)
    print("PASS", name, flush=True)


def retain():
    for slug in fixtures:
        h.db("demo_businesses?slug=eq." + slug, "PATCH", {"expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()})


atexit.register(retain)


def page(slug, token=None, query=""):
    return h.request(h.BASE + "/d/" + slug + "/website?" + ("t=" + urllib.parse.quote(token) if token else "") + query)


def visible(body):
    # Next development flight debug includes server fetch responses in scripts.
    return html.unescape(re.sub(r"<!--.*?-->", "", re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.S), flags=re.S))


class Links(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.links = []
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))


def fixture(b, name, expired=False):
    data = copy.deepcopy({k: b[k] for k in ["profile", "xray", "site", "roi", "health"]})
    slug, token = "school-landing-qa-" + secrets.token_hex(4), secrets.token_urlsafe(20)
    data.update(slug=slug, token=token, code=secrets.token_hex(4).upper(), sector="education", name=name,
                expires_at=(datetime.now(timezone.utc) + timedelta(days=-1 if expired else 10)).isoformat())
    data["profile"]["facts"].update(name=name, category="Academy", address=None, hours=[], rating=None, reviews=None, maps_url="javascript:alert('unsafe')")
    data["profile"]["about"] = "Fictional academy for template isolation checks."
    data["xray"] = None
    data["site"] = {"posts": {"en": [], "ur": []}}
    h.db("demo_businesses", "POST", data)
    fixtures.append(slug)
    return slug, token


def main():
    b = json.loads((h.ROOT.parent / "quetta-local-market/data/demos/tameer-e-nau-public-college-ac62.json").read_text(encoding="utf-8"))
    status, body = page(b["slug"], b["token"])
    text = visible(body)
    check("school template loads independently", status == 200 and 'class="sl"' in body and 'class="cl"' not in body and 'class="rl"' not in body)
    check("researched business facts render", b["name"] in text and b["profile"]["facts"]["address"] in text)
    check("stored Google rating and count", "4.4" in text and "177 Google reviews" in text)
    check("programs and photography labeled illustrative", "Sample program" in text and "Illustrative learning photography" in text and "not actual premises" in text)
    check("no student, assessment, fee or server payload serialized", all(term not in body for term in ["family_id", "student_id", '"grades"', "demo_fee_invoices", h.ENV["SUPABASE_SERVICE_ROLE_KEY"]]))
    check("noindex and no-referrer metadata", 'name="robots" content="noindex, nofollow"' in body and 'name="referrer" content="no-referrer"' in body)
    check("parent, enquiry and visit entry points connect", "/parent?t=" + b["token"] + "&tab=admissions&visit=1" in text and "&enquire=1" in text and "&tab=homework" in text and "&tab=results" in text)
    classes = h.db("demo_school_classes?slug=eq." + b["slug"] + "&select=id,name")
    program_links = [x for x in Links(body).links if "&program=" in x.get("href", "")]
    ids = {c["id"] for c in classes}
    check("program enquiry identifiers belong to this school", len(program_links) == len(classes) and all(urllib.parse.parse_qs(urllib.parse.urlsplit(x["href"]).query)["program"][0] in ids for x in program_links))
    check("current stored programs are rendered", all(c["name"] in text for c in classes))
    maps = [x for x in Links(body).links if x.get("target") == "_blank"]
    check("external maps links protect prospect tokens", bool(maps) and all(x.get("rel") == "noopener noreferrer" and x.get("href", "").startswith("https://www.google.com/maps/") and b["token"] not in x["href"] for x in maps))
    status, body = page(b["slug"], b["token"], "&lang=ur&embed=1")
    check("Urdu RTL and embedded parent navigation", status == 200 and 'dir="rtl"' in body and 'target="_top"' in body and "نمونہ پروگرام" in body)
    for name, slug, token in [("missing token", b["slug"], None), ("invalid token", b["slug"], "wrong"),
        ("clinic token on school", b["slug"], demo_token("saleem-medical-complex-5702")), ("unknown school", "unknown-school-landing", b["token"]),
        ("school token on clinic", "saleem-medical-complex-5702", b["token"]), ("school token on restaurant", "usmania-restaurant-69ac", b["token"])]:
        status, body = page(slug, token)
        check(name + " refused", status == 404 and 'class="sl"' not in body)
    expired_slug, expired_token = fixture(b, "[QA] Expired academy", expired=True)
    status, body = page(expired_slug, expired_token)
    check("expiry prevents rendering programs", status == 200 and "This demo has ended" in visible(body) and 'class="sl"' not in body)
    check("expired landing does not seed school data", not h.db("demo_school_settings?slug=eq." + expired_slug))
    slug, token = fixture(b, "[QA] Cedar Learning Academy")
    status, body = page(slug, token)
    text = visible(body)
    check("template adapts to a second academy", status == 200 and "[QA] Cedar Learning Academy" in text and "Academy" in text)
    check("missing hours and address shown honestly", "Hours not recorded" in text and "Address not recorded" in text)
    check("missing rating and review excerpts stay empty", "No researched review excerpts" in text and "Google reviews" not in text and "4.4" not in text)
    check("unsafe maps data uses a safe search link", "javascript:" not in text and "https://www.google.com/maps/search/?api=1" in text)
    seeded_families = h.db("demo_families?slug=eq." + slug)
    check("landing does not link a web visitor family", all(f["visitor"].startswith("sample-") for f in seeded_families))
    other_classes = h.db("demo_school_classes?slug=eq." + slug + "&select=id,name")
    check("academy programs use academy seed and scope", len(other_classes) == 2 and all("FSc" not in c["name"] and c["id"] not in ids for c in other_classes))
    cid = other_classes[0]["id"]
    h.db("demo_school_classes?slug=eq." + slug + "&id=eq." + cid, "PATCH", {"name": "QA Creative Learning Course"})
    status, body = page(slug, token)
    check("template reads edited program names from storage", "QA Creative Learning Course" in visible(body) and other_classes[0]["name"] not in visible(body))
    status, body = page(b["slug"], b["token"])
    check("second academy data never appears in real college", "QA Creative Learning Course" not in body and all(c["id"] not in body for c in other_classes))
    status, body = page(slug, b["token"])
    check("another education business token refused", status == 404)
    # An empty seeded directory must not invent classes or enquiry identifiers.
    empty_slug, empty_token = fixture(b, "[QA] Empty academy")
    h.db("demo_school_settings", "POST", {"slug": empty_slug, "seeded": True, "hours": []})
    status, body = page(empty_slug, empty_token)
    check("empty directory has a useful office handoff", status == 200 and "No sample programs are listed yet" in visible(body) and "Ask the office" in body and "&amp;program=" not in body)
    status, body = h.request(h.BASE + "/d/" + b["slug"] + "?t=" + b["token"])
    check("hub shows full school landing stage", status == 200 and "care-web-stage" in body and "Your school &amp; academy landing page" in body and 'class="screen site"' not in body)
    for action in ["&visit=1", "&enquire=1&program=" + cid, "&enquire=1&program=00000000-0000-0000-0000-000000000000"]:
        status, body = h.request(h.BASE + "/d/" + slug + "/parent?t=" + token + "&tab=admissions" + action)
        check("parent entry renders without an automatic write " + action.split("&program")[0], status == 200 and 'class="sc"' in body)
    check("server rendering entries does not create applications or visits", not h.db("demo_admissions?slug=eq." + slug) and not h.db("demo_campus_visits?slug=eq." + slug))
    print(str(len(passed)) + " school landing checks passed.", flush=True)


if __name__ == "__main__":
    main()
