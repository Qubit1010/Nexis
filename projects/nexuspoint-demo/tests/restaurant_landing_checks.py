"""Restaurant landing access, scoped menu, missing-data and workspace checks.
Usage: python tests/restaurant_landing_checks.py [base_url] [--vercel]
QA profiles are isolated and retained. Real restaurant operations are unchanged.
"""
import copy
import atexit
import html
import json
import re
import secrets
import urllib.parse
from datetime import datetime, timedelta, timezone
from html.parser import HTMLParser
import healthcare_eval as h
from private_fixtures import demo_token

passed = []
fixtures = []


def retain_expired_fixtures():
    for slug in fixtures:
        h.db("demo_businesses?slug=eq." + slug, "PATCH", {"expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()})


atexit.register(retain_expired_fixtures)


def check(name, condition):
    assert condition, name
    passed.append(name)
    print("PASS", name, flush=True)


def page(slug, token=None, query=""):
    return h.request(h.BASE + "/d/" + slug + "/website?" + ("t=" + urllib.parse.quote(token) if token else "") + query)


class Links(HTMLParser):
    def __init__(self, body):
        super().__init__()
        self.links = []
        self.feed(body)

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))


def main():
    b = json.loads((h.ROOT.parent / "quetta-local-market/data/demos/usmania-restaurant-69ac.json").read_text(encoding="utf-8"))
    status, body = page(b["slug"], b["token"])
    check("restaurant landing loads", status == 200 and 'class="rl"' in body and 'class="cl"' not in body)
    decoded = html.unescape(body)
    check("researched business facts render", b["name"] in decoded and b["profile"]["facts"]["address"] in decoded)
    check("stored Google review count and rating", "2,766 Google reviews" in decoded and "4.1" in decoded)
    check("menu and imagery disclosures", "Fictional menu &amp; prices" in body and "Illustrative food photography" in body)
    check("private indexing and referrer rules", 'name="robots" content="noindex, nofollow"' in body and 'name="referrer" content="no-referrer"' in body)
    check("orders and reservations connect to existing workspace", "/customer?t=" + b["token"] + "&tab=menu" in decoded and "&tab=reservations&reserve=1" in decoded)
    menu = h.db("demo_menu_items?slug=eq." + b["slug"] + "&order=category,name")
    links = Links(body).links
    item_links = [x for x in links if "&item=" in x.get("href", "")]
    ids = {x["id"] for x in menu}
    check("dish links use stored business-owned identifiers", len(item_links) > 0 and all(urllib.parse.parse_qs(urllib.parse.urlsplit(x["href"]).query)["item"][0] in ids for x in item_links))
    check("sample prices match stored menu", all(m["name"] not in ["Chicken karahi", "Chicken sajji", "BBQ platter"] or f'PKR {m["price"]:,}' in decoded for m in menu))
    check("external maps links protect prospect token", all(x.get("rel") == "noopener noreferrer" and x.get("href", "").startswith("https://www.google.com/maps/") for x in links if x.get("target") == "_blank"))
    check("no credentials or order payload in landing", all(term not in body for term in [h.ENV["SUPABASE_SERVICE_ROLE_KEY"], "demo_orders", "customer_id", "demo_reservations"]))
    status, body = page(b["slug"], b["token"], "&lang=ur&embed=1")
    check("Urdu RTL and embedded workflow navigation", status == 200 and 'dir="rtl"' in body and 'target="_top"' in body and "نمونہ مینو" in body)
    for name, slug, token in [
        ("missing token", b["slug"], None),
        ("invalid token", b["slug"], "wrong-token"),
        ("another business token", b["slug"], demo_token("saleem-medical-complex-5702")),
        ("unknown restaurant", "unknown-food-landing", b["token"]),
        ("school route refuses restaurant token", "tameer-e-nau-public-college-ac62", b["token"]),
    ]:
        status, body = page(slug, token)
        check(name + " refused", status == 404 and 'class="rl"' not in body)

    # A second, synthetic restaurant proves this is a reusable template and menu query.
    suffix = secrets.token_hex(4)
    slug, token = "food-landing-check-" + suffix, secrets.token_urlsafe(20)
    fixture = {key: copy.deepcopy(b[key]) for key in ["profile", "site", "roi", "health"]}
    fixture["profile"]["facts"].update(name="QA Cafe " + suffix, address="Fictional Restaurant Lane, Quetta", neighborhood="Sample area", hours=[], rating=None, reviews=None, maps_url="")
    fixture.update(slug=slug, token=token, code=suffix.upper(), sector="food", name="QA Cafe " + suffix, xray=None, expires_at=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat())
    fixture = json.loads(json.dumps(fixture, ensure_ascii=False).replace(b["name"], fixture["name"]))
    h.db("demo_businesses", "POST", fixture)
    fixtures.append(slug)
    status, body = page(slug, token)
    check("second restaurant uses its own profile", status == 200 and fixture["name"] in body and "Fictional Restaurant Lane" in body and "Usmania Restaurant" not in body)
    check("missing hours and review excerpts have clear states", "Hours are not listed" in body and "for guest reviews and public information" in body and "Based on 2,766" not in body)
    other_menu = h.db("demo_menu_items?slug=eq." + slug)
    karahi = next(m for m in other_menu if m["name"] == "Chicken karahi")
    h.db("demo_menu_items?slug=eq." + slug + "&id=eq." + karahi["id"], "PATCH", {"available": False, "price": 2711})
    status, body = page(slug, token)
    check("stored sold-out state and changed price render", status == 200 and "Sold out in demo" in body and "PKR 2,711" in body)
    fixture_links = Links(body).links
    other_ids = {m["id"] for m in other_menu}
    linked_ids = {urllib.parse.parse_qs(urllib.parse.urlsplit(x["href"]).query)["item"][0] for x in fixture_links if "&item=" in x.get("href", "")}
    check("sold-out dish cannot be selected from landing", karahi["id"] not in linked_ids)
    check("no cross-business menu identifiers in links", linked_ids <= other_ids and not (linked_ids & ids))
    check("cross-business tokens also fail on second restaurant", page(slug, b["token"])[0] == 404)
    empty_slug, empty_token = "food-empty-check-" + suffix, secrets.token_urlsafe(20)
    h.db("demo_businesses", "POST", {**fixture, "slug": empty_slug, "token": empty_token, "code": "EMPTY" + suffix})
    fixtures.append(empty_slug)
    h.db("demo_restaurant_settings", "POST", {"slug": empty_slug, "open_min": 720, "close_min": 1440, "seeded": True})
    status, body = page(empty_slug, empty_token)
    check("empty stored menu is not replaced with invented dishes", status == 200 and "sample menu is being prepared" in body and 'class="rl-menu-card' not in body)
    h.db("demo_businesses?slug=eq." + slug, "PATCH", {"expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()})
    status, body = page(slug, token)
    rendered = re.sub(r"<script\b[^>]*>.*?</script>", "", body, flags=re.DOTALL)
    check("expired restaurant shows only expiry notice", status == 200 and "This demo has ended" in rendered and 'class="rl"' not in rendered and "Fictional Restaurant Lane" not in rendered)
    expired_slug, expired_token = "food-expired-check-" + suffix, secrets.token_urlsafe(20)
    h.db("demo_businesses", "POST", {**fixture, "slug": expired_slug, "token": expired_token, "code": "EXP" + suffix, "expires_at": (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()})
    fixtures.append(expired_slug)
    status, body = page(expired_slug, expired_token)
    check("expired visitor cannot seed an unseeded restaurant", status == 200 and not h.db("demo_restaurant_settings?slug=eq." + expired_slug))
    # Existing sectors and roles remain accessible after route changes.
    for route, token, marker in [
        ("/d/saleem-medical-complex-5702/website", demo_token("saleem-medical-complex-5702"), 'class="cl"'),
        ("/d/" + b["slug"], b["token"], "Your restaurant landing page"),
        ("/d/" + b["slug"] + "/customer", b["token"], "Tableflow"),
        ("/d/" + b["slug"] + "/restaurant", b["token"], "Tableflow"),
        ("/d/" + b["slug"] + "/kitchen", b["token"], "Tableflow"),
        ("/d/tameer-e-nau-public-college-ac62", demo_token("tameer-e-nau-public-college-ac62"), 'Your school &amp; academy landing page'),
    ]:
        status, body = h.request(h.BASE + route + "?t=" + token)
        check("existing " + route + " loads", status == 200 and marker in body)
    print(str(len(passed)) + " restaurant landing checks passed.", flush=True)


if __name__ == "__main__":
    main()
