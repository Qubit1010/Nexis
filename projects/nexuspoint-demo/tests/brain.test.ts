// Brain contract tests, ported from Sixty Second Responder tests (fallback, guards, honesty, facts-only).
// Run: npm test   (node --test with native TypeScript stripping)
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  decide,
  validate,
  wrongScript,
  type BrainBusiness,
} from "../src/lib/brain.ts";
import { clean, problems } from "../src/lib/guards.ts";
import { detectLang, scriptedDecide } from "../src/lib/scripted.ts";

const clinic: BrainBusiness = {
  name: "Test Clinic",
  sector: "healthcare",
  profile: {
    about: "Clinic on Jinnah Road.",
    services_sample: ["OPD"],
    questions: [{ key: "patient", ask: "name" }],
    warm_when: "wants a slot",
    unqualified_when: "selling",
    action: "booking",
    demo_hint: "",
    fallback_reply: {
      en: "Thanks! A team member will reply shortly.",
      ur: "شکریہ! عملہ جلد جواب دے گا۔",
    },
    facts: {
      name: "Test Clinic",
      address: "Jinnah Road, Quetta",
      hours: [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
      ].map((day) => ({ day, hours: "9 AM to 4 PM" })),
    },
  },
};
const say = (text: string) => [{ role: "customer", content: text }];
const TODAY = "Wednesday 30 September 2026";

test("education admission and fee fallback retain their workflow",()=>{
  const admission=scriptedDecide('education',clinic.profile.facts!,say('Class 1 admission'));
  assert.equal(admission.action.type,'visit');
  const fee=scriptedDecide('education',clinic.profile.facts!,say('Ayesha Khan Class 6 fee baqi hai?'));
  assert.equal(fee.action.type,'fee_lookup');
  assert.ok(fee.reply.includes('Class 6'));
});

test("a failing AI provider still produces a reply (scripted brain)", async () => {
  const d = await decide(
    clinic,
    say("Assalam o alaikum, timings kya hain?"),
    async () => {
      throw new Error("402 credit");
    },
    TODAY,
  );
  assert.equal(d.source, "scripted");
  assert.ok(d.reply.length > 10);
});

test("no AI configured at all still produces a reply", async () => {
  const d = await decide(clinic, say("hello"), null, TODAY);
  assert.ok(d.reply.includes("Test Clinic"));
});

test("guard blocks an 'as an AI' reply and falls through", async () => {
  const d = await decide(
    clinic,
    say("hi"),
    async () => ({
      provider: "x",
      data: {
        reply: "As an AI language model I cannot book.",
        stage: "qualifying",
        answers: [],
        summary: "",
        action: { type: "none", details: [] },
      },
    }),
    TODAY,
  );
  assert.notEqual(d.source, "ai");
  assert.ok(!/as an ai/i.test(d.reply));
});

test("guard blocks unfilled placeholders", () => {
  assert.deepEqual(problems("Your slot is {time}"), ["placeholder"]);
  assert.deepEqual(problems(""), ["empty"]);
});

test("clean removes em dashes", () => {
  assert.ok(!clean("We open at 9 — see you").includes("—"));
});

test("a valid AI decision passes through with source ai", async () => {
  const d = await decide(
    clinic,
    say("hi"),
    async () => ({
      provider: "claude",
      data: {
        reply: "Hi! How can I help?",
        stage: "weird-stage",
        answers: [{ key: "k", value: "v" }],
        summary: "s",
        action: { type: "none", details: [] },
      },
    }),
    TODAY,
  );
  assert.equal(d.source, "ai");
  assert.equal(d.stage, "qualifying"); // unknown stages are normalised
});

test("price questions are never answered with a number; they go to staff", () => {
  const d = scriptedDecide(
    "healthcare",
    clinic.profile.facts,
    say("Doctor ki fee kitni hai?"),
  );
  assert.equal(d.stage, "needs_human");
  assert.ok(!/\d{3,}/.test(d.reply));
});

test("honest bot disclosure", () => {
  const d = scriptedDecide(
    "healthcare",
    clinic.profile.facts,
    say("kya aap bot ho?"),
  );
  assert.match(d.reply, /automated assistant/i);
});

test("replies in the customer's script", () => {
  assert.equal(detectLang("ڈاکٹر صاحب کل آئیں گے؟"), "ur");
  assert.equal(detectLang("Dr sahab kal mil sakte hain?"), "roman");
  assert.equal(detectLang("Are you open tomorrow?"), "en");
  const d = scriptedDecide(
    "healthcare",
    clinic.profile.facts,
    say("آپ کا کلینک کہاں ہے؟"),
  );
  assert.match(d.reply, /[؀-ۿ]/);
});

test("healthcare fallback cannot fabricate slots or a reservation", () => {
  const h1 = say("Dr sahab kal appointment mil sakti hai?");
  const offer = scriptedDecide("healthcare", clinic.profile.facts, h1);
  assert.doesNotMatch(offer.reply, /\d+:\d+|khali hain|are free/);
  assert.equal(offer.stage, "needs_human");
  const h2 = [
    ...h1,
    { role: "business", content: offer.reply },
    { role: "customer", content: "Ahmed Khan, pehla wala" },
  ];
  const booked = scriptedDecide("healthcare", clinic.profile.facts, h2);
  assert.notEqual(booked.action.type, "booking");
  assert.doesNotMatch(booked.reply, /Booked|Booking ho gayi|بکنگ ہو گئی/);
});

test("fallback sends requested times to stored availability", () => {
  const offer = scriptedDecide(
    "healthcare",
    clinic.profile.facts,
    say("kal shaam 5 baje appointment?"),
  );
  assert.doesNotMatch(offer.reply, /5:00 PM/);
  assert.match(offer.reply, /portal/);
});

test("validate rejects a decision without a reply", () => {
  assert.throws(() => validate({ stage: "warm" }));
});

test("emergencies point to Rescue 1122 first", () => {
  const d = scriptedDecide(
    "healthcare",
    clinic.profile.facts,
    say("I have severe chest pain right now"),
  );
  assert.equal(d.stage, "needs_human");
  assert.match(d.reply, /1122/);
  const u = scriptedDecide(
    "healthcare",
    clinic.profile.facts,
    say("سینے میں درد ہے"),
  );
  assert.match(u.reply, /1122/);
});

test("a reply in the wrong script is retried once, and the demo disclosure is added", async () => {
  const replies = ["ہاں، کل آ جائیں۔", "Haan ji, kal 10 baje aa jayein?"];
  let calls = 0;
  const d = await decide(
    clinic,
    say("Kal appointment mil sakti hai?"),
    async () => ({
      provider: "claude",
      data: {
        reply: replies[calls++],
        stage: "qualifying",
        answers: [],
        summary: "",
        action: { type: "none", details: [] },
      },
    }),
    TODAY,
  );
  assert.equal(calls, 2);
  assert.equal(d.source, "ai");
  assert.ok(!/[؀-ۿ]/.test(d.reply), "Roman Urdu in, Roman Urdu out");
  assert.match(d.reply, /NexusPoint/);
});

test("script check: Urdu replies may carry English terms, Roman replies may not carry Urdu script", () => {
  assert.equal(wrongScript("آپ کا RCT کل 4 PM پر ہو سکتا ہے۔", "ur"), false);
  assert.equal(wrongScript("Haan, kal (Juma) ہمارے پاس وقت ہے", "roman"), true);
  assert.equal(wrongScript("Yes, we open at 10 AM.", "en"), false);
});

test("an AI provider is never consulted for an emergency or a medication request", async () => {
  let called = false;
  const ask = async () => {
    called = true;
    throw new Error("must not call provider");
  };
  const emergency = await decide(
    clinic,
    say("I have severe chest pain"),
    ask,
    TODAY,
  );
  assert.match(emergency.reply, /1122/);
  const clinical = await decide(
    clinic,
    say("What medicine should I take?"),
    ask,
    TODAY,
  );
  assert.equal(clinical.stage, "needs_human");
  assert.equal(called, false);
});
