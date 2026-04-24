# Hook Email Templates

Used by `generate_hook_email.py` in quick mode to produce a ready-to-send cold email referencing the top finding from the audit.

---

## Core pattern

Every hook email follows this 4-beat structure:

1. **Observation** — specific, concrete thing you noticed. Proves you actually looked.
2. **Implication** — what that costs them. Tie it to leads, revenue, or rankings.
3. **Credibility** — one quick line on why they should trust you can fix it.
4. **Soft ask** — low-commitment next step. Never "hop on a call." Prefer "send you the full audit" or "share 2-3 quick fixes."

Keep the whole thing **60-100 words**. If it's longer, cut.

---

## Voice principles

- **Sound human.** No "I hope this email finds you well." No "I came across your website."
- **Lead with the observation, not the intro.** The first sentence should name the specific finding.
- **No fluff adjectives.** "Amazing platform," "great company," "impressive work" — delete all of these.
- **Tactical empathy when relevant.** Label the pain without accusation. "Sounds like you're heads-down on [whatever they do], so the [issue] probably isn't top of mind."
- **No em dashes.** Use commas or periods.
- **No emojis.**
- **No fake personalization.** If you can't reference something real, don't fake it.
- **One ask only.** Either "reply and I'll send it" OR "15-min chat" — never both.

---

## Archetype 1 — Performance / speed finding

```
Subject: quick note on {{company}}'s site speed

Noticed {{company}}'s homepage scores {{score}}/100 on mobile PageSpeed. Most sites under 50 lose over half their mobile visitors before the page finishes loading, which for a business your size usually means {{leads_lost_estimate}} a month.

Ran a full audit on the rest of the site too. Covers SEO, UX, and the conversion gaps I saw.

Want me to send it over? Takes me 2 minutes to share, no call needed.

— Aleem, NexusPoint
```

---

## Archetype 2 — Value prop / messaging finding

```
Subject: {{company}} homepage — one observation

Landed on {{company}} and noticed the headline reads "{{actual_headline}}". A visitor can't tell {{specific_thing_unclear}} in the first 5 seconds, which is usually when 60%+ of them decide whether to stay.

Put together a short audit with 4-5 specific fixes for the homepage. Nothing fancy, just the gaps that tend to cost the most leads.

Happy to send it over if useful. No call, just the doc.

— Aleem, NexusPoint
```

---

## Archetype 3 — SEO / title tag finding

```
Subject: {{company}} — Google CTR leak

Spotted this quick: {{company}}'s title tag is "{{actual_title}}", which Google uses as the clickable text in search results. That specific phrasing usually tanks click-through rates by 30-40% versus a tighter, outcome-focused title.

I pulled together a short audit covering this and 3-4 other quick wins I saw. Covers SEO basics, homepage UX, and conversion gaps.

Want me to send it over?

— Aleem, NexusPoint
```

---

## Archetype 4 — Conversion / CTA finding

```
Subject: {{company}} — CTA question

Noticed {{company}}'s homepage doesn't have a clear next step above the fold on mobile. For most sites, that one change alone lifts demo requests or contact form fills by 15-25%.

Ran a full audit on the homepage and top pages. 5 findings, prioritized by what I'd fix first.

Want me to share it? Takes 2 minutes to send over, no call needed.

— Aleem, NexusPoint
```

---

## Choosing the archetype

`generate_hook_email.py` picks based on the **single highest-severity finding** from the audit:

| Top finding dimension | Archetype |
|---|---|
| Performance | Archetype 1 |
| UX & Messaging | Archetype 2 |
| SEO Basics | Archetype 3 |
| Conversion | Archetype 4 |

If multiple tie for severity, prefer: Conversion > UX > SEO > Performance (conversion drives revenue, which drives replies).

---

## Signing off

Always close with:
```
— Aleem, NexusPoint
```

If the user has given a calendar link or site URL to include, it goes on the line BELOW the signature, not in the body. Example:
```
— Aleem, NexusPoint
nexuspoint.co
```

Do not add a P.S. unless the user requests it. P.S. lines often feel contrived in short cold emails.
