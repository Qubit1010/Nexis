"""Healthcare landing page access and business isolation checks.
Usage: python tests/landing_checks.py [base_url] [--vercel]
Creates one expired QA profile, never changes the real prospects.
"""
import html
import json
import secrets
import urllib.parse
from datetime import datetime, timedelta, timezone
import healthcare_eval as h
from private_fixtures import demo_token

passed = []

def check(name, condition):
    assert condition, name
    passed.append(name)
    print("PASS", name, flush=True)

def page(slug, token=None, query=""):
    return h.request(h.BASE + "/d/" + slug + "/website" + ("?t=" + urllib.parse.quote(token) if token else "?") + query)

def main():
    clinic = json.loads((h.ROOT.parent / "quetta-local-market/data/demos/saleem-medical-complex-5702.json").read_text(encoding="utf-8"))
    dental = json.loads((h.ROOT.parent / "quetta-local-market/data/demos/maher-dental-aesthetics-clinic-q-b959.json").read_text(encoding="utf-8"))
    for b in [clinic, dental]:
        status, body = page(b["slug"], b["token"])
        decoded = html.unescape(body)
        check(b["sector"] + " " + b["slug"] + " landing loads", status == 200 and 'class="cl"' in body)
        check("business details render for " + b["slug"], b["name"] in decoded and b["profile"]["facts"]["address"] in decoded)
        check("stored rating remains accurate for " + b["slug"], str(b["profile"]["facts"]["rating"]) in body)
        check("booking links stay in this business", "/d/" + b["slug"] + "/patient?t=" + b["token"] in decoded)
        check("doctors and services marked illustrative", "Sample profile" in body and "Sample service categories" in body)
        check("no clinical records or server credentials serialized", all(term not in body for term in ["Seasonal allergic rhinitis", "Dental plaque buildup", h.ENV["SUPABASE_SERVICE_ROLE_KEY"]]))
        check("private page cannot be indexed or leak a referrer", 'name="robots" content="noindex, nofollow"' in body and 'name="referrer" content="no-referrer"' in body)
        status, body = page(b["slug"], b["token"], "&lang=ur&embed=1")
        check("Urdu and embedded mode", status == 200 and 'dir="rtl"' in body and 'target="_top"' in body)
    for name, slug, token in [
        ("missing token", clinic["slug"], None),
        ("invalid token", clinic["slug"], "invalid"),
        ("another business token", clinic["slug"], dental["token"]),
        ("unknown business", "missing-healthcare-landing", clinic["token"]),
        ("food route refuses healthcare token", "usmania-restaurant-69ac", clinic["token"]),
        ("education route refuses healthcare token", "tameer-e-nau-public-college-ac62", clinic["token"]),
    ]:
        status, body = page(slug, token)
        check(name + " refused", status == 404 and 'class="cl"' not in body)
    slug = "landing-expiry-check-" + secrets.token_hex(4)
    token = secrets.token_urlsafe(16)
    b = {key: clinic[key] for key in ["profile", "xray", "site", "roi", "health"]}
    b.update(slug=slug, token=token, code=secrets.token_hex(3).upper(), sector="healthcare", name="[QA] Expired landing", expires_at=(datetime.now(timezone.utc) - timedelta(days=1)).isoformat())
    h.db("demo_businesses", "POST", b)
    status, body = page(slug, token)
    check("expired preview reveals no template or doctors", status == 200 and "This demo has ended" in body and 'class="cl"' not in body and "Dr. Sara Ahmed" not in body)
    seed = h.db("demo_healthcare_seed?slug=eq." + slug)
    check("expired visit does not seed clinical data", not seed)
    # The expired QA profile is retained, consistent with the archive policy.
    for slug, token in [("usmania-restaurant-69ac", demo_token("usmania-restaurant-69ac")), ("tameer-e-nau-public-college-ac62", demo_token("tameer-e-nau-public-college-ac62"))]:
        status, body = h.request(h.BASE + "/d/" + slug + "?t=" + token)
        check("sector website preview still renders", status == 200 and 'care-web-stage' in body and ('Your restaurant landing page' in body if slug.startswith('usmania') else 'Your school &amp; academy landing page' in body))
    print(str(len(passed)) + " landing page checks passed.", flush=True)

if __name__ == "__main__":
    main()
