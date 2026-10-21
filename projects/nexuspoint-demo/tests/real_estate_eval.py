"""Isolated real-estate checks: API transactions, atomic site-visit reservations and the assistant's
chat rules, against a fictional Islamabad property office. Archives its activity afterwards.

    python tests/real_estate_eval.py [base_url] [--vercel]      (default http://localhost:4400)
"""
import concurrent.futures
import json
import re
import secrets
import sys
import urllib.parse
from datetime import datetime, timedelta, timezone

import healthcare_eval as h

ROOT = h.ROOT; BASE = h.BASE; PKT = h.PKT
TOKEN = secrets.token_urlsafe(20); SLUG = "re-qa-" + secrets.token_hex(4); VISITOR = "re-test-buyer-" + secrets.token_hex(3)
URDU = re.compile(r"[؀-ۿ]")
passed = []


def check(name, value):
    assert value, name
    passed.append(name); print("PASS", name, flush=True)


def api(body=None, role="buyer", visitor=VISITOR, **params):
    fields = {"slug": SLUG, "t": TOKEN, "visitor": visitor, "role": role, **params}
    if body is not None:
        return h.request(BASE + "/api/real-estate", "POST", {**fields, **body})
    return h.request(BASE + "/api/real-estate?" + urllib.parse.urlencode(fields))


def chat(text, choice=None, visitor=VISITOR):
    return h.request(BASE + "/api/chat", "POST", {"slug": SLUG, "t": TOKEN, "visitor": visitor, "text": text, **({"choice": choice} if choice else {})})


def rules(reply, question=""):
    """The shared honest-bot rules every assistant reply must keep."""
    problems = []
    if "—" in (reply or ""): problems.append("em dash")
    if len((reply or "").split()) > 80: problems.append("too long")
    if URDU.search(question) and not URDU.search(reply or ""): problems.append("not Urdu")
    if not URDU.search(question) and re.search(r"\b(chahiye|mein|hai|kitna)\b", question, re.I) and URDU.search(reply or ""): problems.append("Urdu script for Roman Urdu")
    return problems


def fixture():
    sectors = json.loads((ROOT / "src/data/sectors.json").read_text(encoding="utf-8"))
    S = sectors["real-estate"]
    facts = {"name": "QA Margalla Estates", "category": "Real estate agency", "address": "Office 4, Sample Plaza, Blue Area, Islamabad",
             "neighborhood": "Blue Area", "city": "Islamabad", "hours": [{"day": d, "hours": "10 AM to 7 PM"} for d in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]],
             "extras": [], "rating": 4.6, "reviews": 30, "maps_url": "https://www.google.com/maps/search/?api=1&query=Blue+Area+Islamabad"}
    profile = {"city": "Islamabad", "market": "islamabad", "facts": facts, "about": "QA Margalla Estates is a real estate agency in Blue Area. " + S["about_default"].replace("{city}", "Islamabad"),
               "sector": "real-estate", "services_sample": S["services_sample"], "questions": S["questions"], "warm_when": S["warm_when"], "unqualified_when": S["unqualified_when"],
               "action": S["action"], "demo_hint": S["demo_hint"], "fallback_reply": {"en": "Thanks! An agent will reply shortly.", "ur": "شکریہ! ایجنٹ جلد جواب دے گا۔"}}
    h.db("demo_businesses", "POST", {"slug": SLUG, "token": TOKEN, "code": "E" + secrets.token_hex(3).upper(), "sector": "real-estate", "name": facts["name"],
                                     "profile": profile, "xray": None, "site": {"posts": {"en": [], "ur": []}}, "roi": S["roi"], "health": None,
                                     "expires_at": (datetime.now(timezone.utc) + timedelta(days=14)).isoformat()})


def main():
    fixture()
    try:
        status, s = api()
        check("seeded Islamabad office: 3 agents, 8 listings, sample pipeline", status == 200 and s["city"] == "Islamabad" and len(s["agents"]) == 3 and len(s["listings"]) == 8 and len(s["leads"]) == 0)
        _, staff = api(role="agent")
        check("agents see the sample pipeline across every stage", {l["stage"] for l in staff["leads"]} >= {"new", "qualified", "visit_booked", "negotiating", "won", "lost"})
        _, again = api()
        check("buyer session persists across refresh", s["buyer"]["id"] == again["buyer"]["id"])

        enquiry = {"action": "enquiry", "requestId": "re-qa-enquiry-1", "name": "Sample Buyer", "budget": 25000000, "area": "DHA Phase 2", "size": "10 marla", "kind": "plot",
                   "timeline": "1-3 months", "overseas": True, "country": "UAE", "message": "Prefer a park-facing plot"}
        status, out = api(enquiry)
        lead = out["result"]
        check("website enquiry becomes a qualified lead with a summary", status == 200 and lead["source"] == "website" and lead["stage"] == "qualified" and "PKR 2.5 crore" in lead["summary"] and lead["first_reply_at"])
        status, out = api(enquiry)
        check("enquiry retry returns the same lead", status == 200 and out["result"]["id"] == lead["id"])
        status, _ = api({**enquiry, "budget": 30000000})
        check("retry identifier cannot be reused for a different enquiry", status == 409)
        _, staff = api(role="agent")
        check("enquiry reaches the agent pipeline", any(l["id"] == lead["id"] for l in staff["leads"]))
        _, other = api(visitor="re-other-buyer-0001")
        check("another buyer cannot read this buyer's leads", not other["leads"] and not other["visits"])
        status, _ = api({"action": "enquiry", "requestId": "re-qa-enquiry-2", "name": "X", "budget": 5})
        check("invalid enquiry refused", status == 400)

        day = (datetime.now(PKT) + timedelta(days=2)).date().isoformat()
        status, a = api(date=day)
        slots = a["slots"]
        check("visit slots are hourly in PKT office hours", status == 200 and slots and datetime.fromisoformat(slots[0].replace("Z", "+00:00")).astimezone(PKT).hour == 10)
        target = slots[3]
        buyers = ["re-race-buyer-" + str(i) + "000" for i in range(4)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            results = list(pool.map(lambda v: api({"action": "reserve", "start": target, "requestId": "re-race-" + v}, visitor=v), buyers))
        check("4 simultaneous bookings for one hour with 3 agents: exactly 3 succeed", sorted(r[0] for r in results) == [200, 200, 200, 409])
        check("each winner got a different agent", len({r[1]["result"]["agent_id"] for r in results if r[0] == 200}) == 3)
        winner = next(v for v, r in zip(buyers, results) if r[0] == 200)
        status, out = api({"action": "reserve", "start": target, "requestId": "re-race-" + winner}, visitor=winner)
        check("reservation retry returns the same visit", status == 200 and out["result"]["id"] == next(r[1]["result"]["id"] for v, r in zip(buyers, results) if v == winner))
        status, a = api(date=day)
        check("a fully booked hour disappears from availability", target not in a["slots"] and slots[2] in a["slots"])

        status, out = api({"action": "reserve", "start": slots[1], "requestId": "re-qa-visit-1", "listingId": s["listings"][0]["id"]})
        visit = out["result"]
        _, mine = api()
        check("buyer booking moves the lead to visit booked with an agent", status == 200 and next(l for l in mine["leads"] if l["id"] == lead["id"])["stage"] == "visit_booked" and visit["agent_id"])
        status, _ = api({"action": "visit", "id": visit["id"], "status": "completed"})
        check("buyer cannot mark a visit completed", status == 400)
        status, _ = api({"action": "stage", "id": lead["id"], "stage": "won"})
        check("buyer cannot move the pipeline", status == 400)
        status, _ = api({"action": "visit", "id": visit["id"], "status": "completed"}, role="agent")
        check("a future visit cannot be marked completed", status == 400)
        status, _ = api({"action": "visit", "id": visit["id"], "status": "cancelled"}, visitor="re-other-buyer-0001")
        check("another buyer cannot cancel this visit", status == 404)
        status, _ = api({"action": "visit", "id": visit["id"], "start": target})
        check("rescheduling into a fully booked hour is refused", status == 409)
        status, out = api({"action": "visit", "id": visit["id"], "start": slots[5]})
        check("atomic reschedule to a free hour", status == 200 and datetime.fromisoformat(out["result"]["starts_at"]) == datetime.fromisoformat(slots[5].replace("Z", "+00:00")))
        status, _ = api({"action": "settings", "openMin": 900, "closeMin": 1080}, role="manager")
        check("office hours cannot strand a booked visit", status == 409)
        status, _ = api({"action": "agent", "id": visit["agent_id"], "active": False}, role="manager")
        check("an agent with booked visits cannot be switched off", status == 409)
        status, _ = api({"action": "visit", "id": visit["id"], "status": "cancelled"})
        _, mine = api()
        check("cancelling the only visit returns the lead to qualified", status == 200 and next(l for l in mine["leads"] if l["id"] == lead["id"])["stage"] == "qualified")
        status, _ = api({"action": "stage", "id": lead["id"], "stage": "won"}, role="agent")
        check("pipeline refuses to skip stages", status == 409)
        status, _ = api({"action": "stage", "id": lead["id"], "stage": "lost"}, role="agent")
        check("a lost lead needs a reason", status == 400)
        status, _ = api({"action": "stage", "id": lead["id"], "stage": "negotiating"}, role="agent")
        check("agent moves a qualified lead to negotiating", status == 200)
        status, _ = api({"action": "assign", "id": lead["id"], "agentId": s["agents"][1]["id"]}, role="manager")
        status2, _ = api({"action": "note", "id": lead["id"], "text": "Called back, prefers Sector J"}, role="agent")
        check("manager assigns and agent notes", status == 200 and status2 == 200)
        _, mgr = api(role="manager")
        check("manager sees sources, activity and every buyer", len(mgr["buyers"]) >= 9 and any(a["kind"] == "re_visit" for a in mgr["activity"]))
        status, _ = api(t="wrong-token")
        check("invalid token refused", status == 404)

        # ----- assistant rules -----
        q = "10 marla plot chahiye DHA phase 2 mein, budget 2.5 crore"
        status, out = chat(q)
        check("Roman Urdu qualification asks the next missing field in Roman Urdu", status == 200 and not rules(out["reply"], q) and out["cards"] and out["cards"][0]["kind"] == "re_timeline" and "NexusPoint" in out["reply"])
        _, staff = api(role="agent")
        chat_lead = next((l for l in staff["leads"] if l["source"] == "chat"), None)
        check("chat lead lands in the pipeline with budget and area", chat_lead and chat_lead["budget"] == 25000000 and "DHA" in chat_lead["area"] and chat_lead["first_reply_at"])
        status, out = chat(out["cards"][1]["label"], out["cards"][1])
        check("one question per message: overseas next", status == 200 and out["cards"] and out["cards"][0]["kind"] == "re_overseas")
        uae = next(c for c in out["cards"] if c["value"].startswith("true|UAE"))
        status, out = chat(uae["label"], uae)
        prices = [float(x) for x in re.findall(r"PKR ([\d.]+) crore", out["reply"])]
        check("qualified buyer sees only stored listings within budget", status == 200 and "sample demand" in out["reply"] and prices and max(prices) <= 3.0 and any(c["kind"] == "re_listing" for c in out["cards"]))
        listing_card = next(c for c in out["cards"] if c["kind"] == "re_listing")
        status, out = chat(listing_card["label"], listing_card)
        check("assistant offers concrete visit slots", status == 200 and len([c for c in out["cards"] if c["kind"] == "re_time"]) >= 3)
        status, out = chat(out["cards"][0]["label"], out["cards"][0])
        confirm = next(c for c in out["cards"] if c["kind"] == "re_confirm")
        status, out = chat(confirm["label"], confirm)
        print("   booking reply:", out.get("reply"), flush=True)
        check("assistant books the visit through the reservation", status == 200 and re.search(r"booked|book hai", out["reply"]) and out["stage"] == "warm" and not rules(out["reply"], q))
        _, staff = api(role="agent")
        chat_lead = next(l for l in staff["leads"] if l["id"] == chat_lead["id"])
        check("chat visit reaches the agent board with a summary", chat_lead["stage"] == "visit_booked" and "Site visit" in chat_lead["summary"] and any(v["source"] == "chat" for v in staff["visits"]))
        conv = next(c for c in staff["conversations"] if c["visitor"] == VISITOR)
        check("conversation card carries the visit action", conv["summary"] and "Site visit" in conv["summary"])
        for text in ["Is this society NOC approved?", "Transfer aur possession kab milega?"]:
            status, out = chat(text)
            check("legal question goes to an agent: " + text[:24], status == 200 and out["stage"] == "needs_human" and "agent" in out["reply"].lower() and not re.search(r"\d", out["reply"]))
        status, out = chat("Final price kya hai, discount milega?")
        check("final price and discount go to an agent with no number", status == 200 and out["stage"] == "needs_human" and not re.search(r"PKR|\d", out["reply"]))
        u = "ڈی ایچ اے میں دس مرلہ پلاٹ چاہیے، بجٹ ڈھائی کروڑ"
        status, out = chat(u, visitor="re-urdu-buyer-0001")
        check("Urdu buyer is answered in Urdu script", status == 200 and not rules(out["reply"], u))
        status, out = chat("Are you a bot?", visitor="re-bot-buyer-0001")
        check("honest bot disclosure", status == 200 and re.search(r"automated|assistant|اسسٹنٹ|خودکار", out["reply"] or "", re.I))
        status, out = chat("My father has chest pain at the site", visitor="re-urgent-buyer-01")
        check("emergency overrides the property flow", status == 200 and "1122" in out["reply"] and out["stage"] == "needs_human")
        api({"action": "conversation", "id": conv["id"], "staffMode": True, "assignedTo": "Bilal Ahmed"}, role="agent")
        status, out = chat("Any update?")
        check("agent takeover pauses the assistant", status == 200 and out["reply"] is None)
        status, _ = api({"action": "conversation", "id": conv["id"], "text": "Sample agent reply"}, role="agent")
        check("agent replies after takeover", status == 200)
        h.db("demo_businesses?slug=eq." + SLUG, "PATCH", {"expires_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()})
        status, _ = api()
        check("expired preview refused", status == 410)
    finally:
        events = h.db("demo_events?slug=eq." + SLUG + "&select=id")
        h.db("rpc/demo_re_action", "POST", {"p_slug": SLUG, "p_visitor": "system-reset", "p_role": "system", "p_action": "reset", "p_data": {}})
        check("reset archives activity and keeps analytics", bool(h.db("demo_re_archives?slug=eq." + SLUG)) and len(h.db("demo_events?slug=eq." + SLUG + "&select=id")) == len(events))
        h.db("demo_businesses?slug=eq." + SLUG, "PATCH", {"expires_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()})
    print(str(len(passed)) + " real-estate checks passed.", flush=True)


if __name__ == "__main__":
    main()
