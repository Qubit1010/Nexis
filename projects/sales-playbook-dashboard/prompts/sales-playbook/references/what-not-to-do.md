# What Not To Do — The Cadence-Smell Kill List

> Every phrase below was specifically flagged in `references/research-synthesis.md` (Q1, Q2, Q3) as cadence-smell, spam-trigger, or sales-junior-tell. Sources include: Martal Group's 2026 cold-call dataset, Sopro's 59 cold-outreach stats 2026, Mailforge response benchmarks, CreatorFlow Instagram DM data, Expandi's 13.2M data point study, Outbound Squad, and Black Swan Group.

## How to use this file

Before sending any cold message, run it through the kill list. If any of these phrases appear, rewrite.

The OpenAI generators (linkedin-outreach, instagram-outreach) should reject-and-regenerate any output containing these strings before showing them.

---

## Tier 1 — The Cadence Tells (instant delete)

These are the phrases that trigger founders' "this is templated outbound" pattern recognition in under 2 seconds.

| Phrase | Why kill it | Source |
|---|---|---|
| "Hey [Name], hope this finds you well" | Every templated email opens with this. Triggers instant template recognition. | Outbound Squad, Sopro |
| "I came across your profile" | The single most-used opener in junior LinkedIn outbound. Tells the prospect a bot scraped them. | Sopro |
| "I noticed you're in [industry]" | Same — could match 10,000 prospects identically. | Expandi |
| "Love your content" / "Love the shit you're doing" | Specifically called out by CreatorFlow as the #1 "tells me you copy-pasted" line | CreatorFlow |
| "Your work is truly inspiring" | Performative compliment, zero specificity | Sopro |
| "I'd love to learn more about your business" | Costs the prospect time without offering value. Reads as a junior SDR. | Outbound Squad |
| "Just following up" / "Just want to circle back" / "I wanted to follow up" | Universally flagged. Voss specifically calls these out as anti-rapport. | Martal Group, Black Swan |
| "Just bumping this to the top of your inbox" | Same category. | Martal Group |
| "Did I catch you at a bad time?" | Martal's 2026 data: lowest converter in their dataset of cold-call openers | Martal Group |
| "How are you today?" | Same — cold-call lowest converter, transfers to DM | Martal Group |

---

## Tier 2 — The Salesy Tells (signals you're selling, not helping)

| Phrase | Why kill it | Source |
|---|---|---|
| "Are you the decision-maker?" | Insulting. Treats the prospect as a gatekeeper. | Martal Group |
| "Do you have budget for this?" | Same — qualifying before earning the right | Martal Group |
| "I know you're busy, but..." | Self-cancelling — if you knew, you wouldn't be writing | Outbound Squad |
| "Let me know..." | Lazy CTA. Puts the work on the prospect. | Outbound Squad |
| "I'd be happy to..." | Filler. Performative agreeableness. | Outbound Squad |
| "Does that make sense?" | Talks down to the prospect. | Outbound Squad |
| "Do you know what we do?" | Insulting frame. | Outbound Squad |
| "We are the #1 provider..." | Unverifiable, sounds like an ad. | Outbound Squad |
| "Worth a quick chat?" | Most-burned outbound CTA on LinkedIn. Pattern-matched in <1 sec. | Multiple |
| "Open to a 15-min call?" | Generic. Replace with anchored deliverable. | Multiple |
| "Hop on a quick call" | Same. | Multiple |

---

## Tier 3 — Spam Triggers (will get you flagged or shadowbanned)

These get you bucketed as spam by platform filters or by the prospect's email client.

| Phrase | Risk | Source |
|---|---|---|
| "Free money" | Email spam filter trigger | CreatorFlow, Mailforge |
| "Act now" / "Limited time offer" | Spam filter | CreatorFlow, Mailforge |
| "Guaranteed" (in opener) | Spam filter | Mailforge |
| "Click here" (as standalone CTA) | Spam filter + IG flag | CreatorFlow |
| "Free" (over-used) | Reduces deliverability | Mailforge |
| 3+ URLs in single Instagram DM | Triggers IG spam filter | CreatorFlow |
| ALL CAPS WORDS | IG + email spam trigger | CreatorFlow |
| Multiple !!!  | IG + email spam trigger | CreatorFlow |
| 10+ emojis in one message | IG flag — looks unprofessional / bot | CreatorFlow |

---

## Tier 4 — Instagram-Specific Kills

| Pattern | Why | Source |
|---|---|---|
| "Bro" (in cold DM, especially to women) | Specifically called out as kill-on-sight. Tone deaf. | CreatorFlow |
| Identical copy-pasted DMs (no per-prospect variation) | #1 shadowban trigger on IG | CreatorFlow |
| 50+ DMs in 30 minutes | Bot-pacing signal — account gets soft-banned | CreatorFlow |
| 150+ DMs/day | Hard daily cap before flag | CreatorFlow |
| Messaging accounts you don't follow first | "Cold messaging penalty" — DM goes to Message Requests, prospect never sees it | CreatorFlow |
| Messages over 200 words | 30% drop in response (mobile skim) | CreatorFlow |
| Robotic / formal phrasing | "Thank you for your inquiry regarding our services" — kills tone | CreatorFlow |
| Emoji-stuffed DMs | "Hey 👋 girl 💁♀️! Here's 🎉 your meal 🍽️ plan 📋..." | CreatorFlow (literal bad example) |

---

## Tier 5 — LinkedIn-Specific Kills

| Pattern | Why | Source |
|---|---|---|
| Pitch in the first touch | Almost never works (Expandi, GetReplies) | Expandi |
| Self-centered aggression: "I can help you grow! Hire me!" | Documented worst-performer | Expandi |
| Generic templates that pitch from line 1 | Lowest acceptance + reply rates | Expandi |
| Reaching out to people far outside ICP | Reply rate craters | Expandi |
| Messages so long they truncate in LinkedIn's preview | Get skimmed past | GetReplies |
| Sales-pitch tone (vs. peer tone) | Documented worst tone for the platform | Outbound Squad |

---

## Tier 6 — AI-Tells (2026 buyer pattern-match)

Sourced from `references/research-synthesis.md` Q6 (FirstSales, LinkedInsider, MarketingProfs, The Selling Collective, 2026). Buyers now pattern-match these in the first five words, before reading content. Stack two and the message is deleted; get spotted twice and they report spam, which damages the sending account.

| Tell | Why kill it | Source |
|---|---|---|
| Em dashes (any) | The single most reliable AI tell in written copy. Humans use 1-2 per thousand words; AI uses 3 in a 4-sentence message. | FirstSales |
| The tricolon (3 parallel items in a row) | Models love balanced lists; busy humans don't write them in DMs. | LinkedInsider |
| Over-polished structure (context / pain / solution / CTA, every time) | Readers recognize the shape before the content. Add a fragment, an aside, a crooked route to the point. | FirstSales |
| "I noticed you..." | Humans do not narrate their noticing. The most diagnostic single word in fake personalization. | FirstSales |
| Scrape-specific personalization ("your April 14th post on X") | Proves a machine did the reading. As bad as generic. | FirstSales |
| "Leverage" / "robust" / "seamless" / "streamline" / "elevate" / "unlock" / "empower" / "cutting-edge" / "comprehensive solution" | The vocabulary fingerprint. Replace each with the word you'd say out loud. | FirstSales, LinkedInsider |
| "Pain points" as a standalone noun | Same cluster. | FirstSales |
| Generic praise ("impressive background", "love what you're doing in the space") | Reads as a manipulation tactic, triggers distrust. Specific evidence or skip the compliment entirely. | FirstSales, LinkedInsider |
| The fake question | A question bolted on to seem curious that you don't actually want answered. | LinkedInsider |
| "Would you be open to a quick 15-minute chat?" | The templated CTA every other AI message also used. | LinkedInsider |
| Essay paragraphs that don't fit a phone screen | Format tell, independent of content. | LinkedInsider |

**The countermeasure (Q6):** exactly ONE observed, verifiable detail per prospect. It's the cheapest humanizing move and the only thing a machine can't fake, because a model cannot invent a true fact about a stranger. One detail beats three. Then the read-aloud test: would one real person say this to another?

---

## Tier 7 — Hormozi-Brash Tells (keep the logic, drop the aggression)

The upgrade imports Alex Hormozi's objection *psychology* (`frameworks/objection-psychology.md`, `frameworks/hormozi-selling-principles.md`) but **not his gym-floor delivery.** His raw phrasing is high-pressure closer energy that fails NexusPoint's natural bar and, per the research, *loses* deals: rigid-script pushing "creates pressure, breaks trust, triggers resistance, and leaves 75-85% of opportunities on the table" (`research-synthesis.md` Q12). Strip these registers when re-voicing any Hormozi overcome:

| Pattern to kill | Why | Say instead |
|---|---|---|
| Command closes — "Just take the card," "shut up and buy," "sign here" | Pressure; destroys the back-foot posture | Ask, don't command. "Want me to walk you through getting started?" |
| Shame / insult framing — "you're broke," "you're the problem," calling out their failure | Humiliation is not persuasion in B2B text | Name the cost neutrally, on their side |
| Profanity / hype-bro tone — "crushing it," "balls to bones," swearing | Reads as a closer script, not a colleague | Plain, calm, lowercase register |
| Hard ultimatums — "draw the line in the sand right now," "decide this second" | Manufactured urgency; trips the "salesy" pattern-match | Soft, real next step: "no rush — want to settle it now or think on one specific thing?" |
| Guilt / fear pressure — "another year of almost," "you'll regret this forever" as a hammer | The *idea* (cost of inaction) is fine; the hammering isn't | State the cost once, gently, then go quiet |
| Stacking 3-4 overcomes in one message | Barrage = pressure = distrust | ONE angle, resolve the specific concern, wait |
| Manipulative anchoring theatrics — throwing out a shock number to force a gasp | Reads as a tactic in text | Give context before any number (`objection-psychology.md §2`) |

**Rule:** if a drafted overcome sounds like a high-ticket closer on a stage, rewrite it in the register of a sharp founder thinking alongside a peer. Delivery beats content (`hormozi-selling-principles.md §12`).

---

## Formatting kills (apply everywhere)

- **No em-dashes** (—) in any cold message. Use hyphens with spaces (` - `) or commas. Em-dashes are now widely associated with AI-generated text.
- **No formal sign-offs**: "Best regards," / "Cheers," / "Looking forward to hearing from you," / "Warm regards," all flagged as cadence-smell on cold DMs. End on the question.
- **No `[FirstName]` placeholder showing through** — obvious tell that you didn't QA your send.
- **No "I" pile-up** — count Is. More than 2 in a cold message means rewrite. Make it about them.
- **No 3-paragraph cold messages** — kept short or get skimmed.

---

## The pre-send checklist

Before any cold message goes out, it must pass:

1. ☐ Does NOT contain any Tier 1-7 phrase or pattern
2. ☐ Under platform character/word limit (LinkedIn connection: 280 / IG DM: 100 words / Cold email: 120 words)
3. ☐ Specific to this prospect — would NOT make sense sent to 10 other prospects in the same batch
4. ☐ Max 2 instances of "I" / "we" / "my" / "our"
5. ☐ Zero em-dashes
6. ☐ Zero formal sign-offs
7. ☐ One ask max (one question OR one CTA, never both)
8. ☐ For LinkedIn: opening line doesn't match "Hey [Name], it looks like..." pattern
9. ☐ For Instagram: 1–3 emojis MAX (and only if tone-appropriate)
10. ☐ The "would a real human write this at 11pm to a peer?" test — read it aloud, does it sound human?

If any check fails → rewrite.

---

## What this file is NOT

This isn't a complete style guide. The opener archetypes file (`frameworks/opener-archetypes.md`) covers what TO write. This file covers what NOT to write. Use both.

When in doubt: the test is "does this sound like a template a human wrote one-off, or a template a tool generated for 30 prospects?" If the answer is the latter, kill it.
