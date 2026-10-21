// Real-estate sector + city awareness: parsing, pipeline rules, visit slots, statistics, prices per market.
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  canMove, formatPkr, leadSummary, matchListings, nextQuestion, parseArea, parseBudget, parseKind, parseOverseas, parseSize,
  parseTimeline, responseStats, visitSlots, type Lead, type Listing, type ReSettings,
} from "../src/lib/real-estate-types.ts";
import { cityOf, cityUr, fillCity, marketOf } from "../src/lib/city.ts";
import { tiersFor, type Bundles } from "../src/lib/bundles.ts";
import { systemPrompt, type BrainBusiness } from "../src/lib/brain.ts";
import { scriptedDecide } from "../src/lib/scripted.ts";

test("PKR amounts read in crore and lakh, in English and Urdu", () => {
  assert.equal(formatPkr(25_000_000), "PKR 2.5 crore");
  assert.equal(formatPkr(7_200_000), "PKR 72 lakh");
  assert.equal(formatPkr(23_500_000, "ur"), "2.35 کروڑ روپے");
  assert.equal(formatPkr(null), "Not given");
});

test("buyer messages yield budget, size, area, timeline and overseas status in all three scripts", () => {
  const roman = "Salam, 10 marla plot chahiye Gulberg ya DHA phase 2 mein. Budget around 2.5 crore.";
  assert.equal(parseBudget(roman), 25_000_000);
  assert.equal(parseSize(roman)?.label, "10 marla");
  assert.equal(parseKind(roman), "plot");
  assert.equal(parseArea(roman), "Gulberg Greens or DHA Phase 2");
  const urdu = "دس مرلہ پلاٹ چاہیے ڈی ایچ اے فیز ٹو میں۔ بجٹ تقریباً ڈھائی کروڑ۔";
  assert.equal(parseBudget(urdu), 25_000_000);
  assert.equal(parseSize(urdu)?.label, "10 marla");
  assert.equal(parseArea(urdu), "DHA Phase 2");
  assert.equal(parseBudget("50 lac se 80 lac"), 8_000_000);
  assert.equal(parseBudget("1.2cr max"), 12_000_000);
  assert.equal(parseBudget("call me tomorrow"), null);
  assert.equal(parseArea("apartment in E-11/2 please"), "E-11/2");
  assert.deepEqual(parseOverseas("Dubai mein hoon, December mein aa raha hoon"), { overseas: true, country: "UAE" });
  assert.deepEqual(parseOverseas("I live in Islamabad mein"), { overseas: false, country: "Pakistan" });
  assert.equal(parseOverseas("10 marla plot"), null);
  assert.equal(parseTimeline("2-3 months"), "2-3 months");
  assert.equal(parseTimeline("دو تین مہینے"), "2-3 months");
  assert.equal(parseTimeline("just looking for now"), "Exploring, no fixed date");
});

test("qualification asks one missing field at a time and the summary never invents a value", () => {
  const q = { budget: null, area: "", size: "", kind: "", timeline: "", overseas: null, country: "" };
  assert.equal(nextQuestion(q), "budget");
  assert.equal(nextQuestion({ ...q, budget: 1 }), "area");
  assert.equal(nextQuestion({ ...q, budget: 1, area: "B-17", size: "8 marla", timeline: "Ready now" }), "overseas");
  assert.equal(nextQuestion({ ...q, budget: 1, area: "B-17", size: "8 marla", timeline: "Ready now", overseas: false }), null);
  const partial = leadSummary({ ...q, kind: "house", area: "Bahria Town" });
  assert.match(partial, /house in Bahria Town/);
  assert.doesNotMatch(partial, /PKR|budget|timeline/);
  assert.match(leadSummary({ ...q, budget: 25_000_000, size: "10 marla", kind: "plot", overseas: true, country: "UAE" }, { visit: "Sat 25 Oct", agent: "Bilal" }), /Overseas buyer \(UAE\).*PKR 2\.5 crore.*with Bilal/);
});

test("pipeline moves mirror the database transition table", () => {
  assert.ok(canMove("new", "qualified"));
  assert.ok(canMove("negotiating", "won"));
  assert.ok(canMove("lost", "new"));
  assert.ok(!canMove("new", "won"));
  assert.ok(!canMove("won", "lost"));
  assert.ok(!canMove("qualified", "new"));
});

const agents = [{ id: "a1", active: true }, { id: "a2", active: true }];
const settings: ReSettings = { open_min: 600, close_min: 1080, visit_minutes: 60 };
const now = new Date("2026-10-21T05:30:00Z"), expiry = "2026-11-04T05:30:00Z"; // 10:30 PKT
test("site-visit slots are hourly inside PKT office hours, from now, within 14 days and before expiry", () => {
  const today = visitSlots("2026-10-21", agents, [], settings, expiry, now);
  assert.equal(today[0], "2026-10-21T06:00:00.000Z"); // 11:00 PKT, the 10:00 slot has passed
  assert.equal(today.at(-1), "2026-10-21T12:00:00.000Z"); // 17:00 PKT, ends at closing
  assert.equal(today.length, 7);
  assert.equal(visitSlots("2026-10-22", agents, [], settings, expiry, now).length, 8);
  assert.deepEqual(visitSlots("2026-10-20", agents, [], settings, expiry, now), []);
  assert.deepEqual(visitSlots("2026-11-04", agents, [], settings, expiry, now), []);
  assert.equal(visitSlots("2026-10-22", agents, [], settings, "2026-10-22T07:00:00Z", now).length, 2);
  assert.deepEqual(visitSlots("2026-10-22", [{ id: "a1", active: false }], [], settings, expiry, now), []);
});

test("a slot disappears only when every active agent is busy, and cancelled visits release it", () => {
  const busy = [{ agent_id: "a1", starts_at: "2026-10-22T06:00:00Z", ends_at: "2026-10-22T07:00:00Z", status: "confirmed" as const }];
  assert.ok(visitSlots("2026-10-22", agents, busy, settings, expiry, now).includes("2026-10-22T06:00:00.000Z"));
  const both = [...busy, { ...busy[0], agent_id: "a2" }];
  assert.ok(!visitSlots("2026-10-22", agents, both, settings, expiry, now).includes("2026-10-22T06:00:00.000Z"));
  both[1] = { ...both[1], status: "cancelled" as never };
  assert.ok(visitSlots("2026-10-22", agents, both, settings, expiry, now).includes("2026-10-22T06:00:00.000Z"));
});

const listing = (over: Partial<Listing>): Listing => ({ id: "x", code: "NP-1", title: "", title_ur: "", kind: "plot", society: "DHA Phase 2", society_ur: "", block: "",
  size_value: 10, size_unit: "marla", beds: null, baths: null, price: 23_500_000, status: "available", features: [], description: "", description_ur: "", art: "plot", ...over });
test("matching only returns stored, available listings within budget", () => {
  const ls = [listing({ id: "fit" }), listing({ id: "sold", status: "sold" }), listing({ id: "dear", price: 90_000_000 }), listing({ id: "other", society: "B-17", size_value: 8, price: 7_200_000 })];
  const m = matchListings(ls, { budget: 25_000_000, area: "Gulberg Greens or DHA Phase 2", size: "10 marla", kind: "plot" });
  assert.equal(m[0].id, "fit");
  assert.ok(!m.some((l) => l.id === "sold" || l.id === "dear"));
});

test("manager statistics: median first reply, share under five minutes, visit rate, unanswered", () => {
  const base = { created_at: "2026-10-21T00:00:00Z", stage: "new", source: "chat" } as Lead;
  const leads = [
    { ...base, id: "1", first_reply_at: "2026-10-21T00:00:30Z" }, { ...base, id: "2", first_reply_at: "2026-10-21T00:01:30Z" },
    { ...base, id: "3", source: "phone", first_reply_at: "2026-10-21T04:00:00Z" }, { ...base, id: "4", source: "facebook", first_reply_at: null },
  ] as Lead[];
  const s = responseStats(leads, [{ lead_id: "1", status: "confirmed" }, { lead_id: "3", status: "cancelled" }]);
  assert.equal(s.medianReply, 90);
  assert.equal(s.underFiveMin, 67);
  assert.equal(s.unanswered, 1);
  assert.equal(s.visitRate, 25);
  assert.equal(s.sources.find((x) => x.source === "chat")?.medianReply, 60);
});

test("demos default to Quetta and Islamabad demos take their city and price list from the place", () => {
  assert.equal(cityOf(null), "Quetta");
  assert.equal(cityOf({ facts: { city: null, address: "Jinnah Road, Quetta" } }), "Quetta");
  assert.equal(cityOf({ city: "Islamabad", facts: { city: "Greens" } }), "Islamabad");
  assert.equal(cityOf({ facts: { city: "rawalpindi" } }), "Rawalpindi");
  assert.equal(cityOf({ facts: { city: "Sector:", address: "G-9 Markaz, Islamabad, 44000, Pakistan" } }), "Islamabad");
  assert.equal(marketOf({ facts: { city: "Rawalpindi" } }), "islamabad");
  assert.equal(marketOf({ facts: { city: null } }), "quetta");
  assert.equal(cityUr("Islamabad"), "اسلام آباد");
  assert.equal(fillCity("Restaurant in {city} taking orders.", "Islamabad"), "Restaurant in Islamabad taking orders.");
  const tier = { name: "Growth", tag_en: "", tag_ur: "", setup: 1, monthly: 1, rec: true, items_en: [], items_ur: [] };
  const legacy: Bundles = { terms: {}, sectors: { food: [tier] } };
  assert.equal(tiersFor(legacy, "quetta", "food")?.length, 1);
  assert.equal(tiersFor(legacy, "islamabad", "food"), null);
  const markets: Bundles = { markets: { islamabad: { terms: {}, sectors: { "real-estate": [{ ...tier, setup: 240000 }] } } } };
  assert.equal(tiersFor(markets, "islamabad", "real-estate")?.[0].setup, 240000);
  assert.equal(tiersFor(markets, "islamabad", "education"), null);
});

const office: BrainBusiness = {
  name: "Test Estates", sector: "real-estate",
  profile: { city: "Islamabad", about: "Property agency in {city}.", services_sample: ["Plots"], questions: [{ key: "budget", ask: "budget" }], warm_when: "", unqualified_when: "",
    action: "visit", demo_hint: "", fallback_reply: { en: "Thanks", ur: "شکریہ" }, facts: { name: "Test Estates", address: "Blue Area, Islamabad", city: "Islamabad", hours: [] } },
};
test("the assistant prompt carries the demo's city and the property honesty rules", () => {
  const p = systemPrompt(office, "Tuesday");
  assert.match(p, /property enquiries assistant for Test Estates in Islamabad/);
  assert.match(p, /Property agency in Islamabad\./);
  assert.match(p, /Today in Islamabad: Tuesday/);
  assert.match(p, /Legal, NOC, approval, transfer, possession and tax questions always go to an agent/);
  const quetta = systemPrompt({ ...office, sector: "food", profile: { ...office.profile, city: undefined, about: "x", facts: { ...office.profile.facts, city: null, address: null } } }, "Tuesday");
  assert.match(quetta, /in Quetta, replying/);
});

test("scripted fallback sends legal questions to an agent and never states a price", () => {
  const legal = scriptedDecide("real-estate", office.profile.facts, [{ role: "customer", content: "Is the society NOC approved?" }]);
  assert.equal(legal.stage, "needs_human");
  const price = scriptedDecide("real-estate", office.profile.facts, [{ role: "customer", content: "10 marla plot ka rate kitna hai?" }]);
  assert.equal(price.stage, "needs_human");
  assert.doesNotMatch(price.reply, /\d/);
});
