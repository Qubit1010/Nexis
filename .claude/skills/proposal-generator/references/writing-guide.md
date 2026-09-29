# Writing guide

How to fill `proposal.json` so the page reads like a sharp founder who listened on the call,
not a template. `assets/example-proposal.json` is the full worked example; this file explains
the choices behind it.

## Who is reading

A founder or agency owner deciding whether to trust NexusPoint with delivery. They open the link
on a phone first, probably between meetings, and may forward it to a partner. They were on the
call, so the fastest way to earn the next minute of their attention is to show you heard them:
their words, their numbers, their stated worry.

## Why consultative, not a Hormozi stack

The previous version of this skill printed "$X,XXX value" line items, a labelled Bonuses section
and stacked performance guarantees. It is retired for three reasons:

- `sales-playbook/references/what-not-to-do.md` bans a labelled "Bonuses" section and the
  brash-closer register (Tier 6 and Tier 7) for all NexusPoint copy.
- The agency-first ICP's objection is delivery trust, not price (`agency/icp-agencies.md`).
  An inflated value stack answers a price objection nobody raised and reads like a course sales page.
- A performance guarantee on business outcomes NexusPoint does not control is a liability.

Hormozi still does the thinking; it just does not appear as page sections:

| Value-equation lever | Where it lands on the page |
|---|---|
| Dream outcome | `hero.headline`, in the client's language |
| Cost of inaction | `diagnosis.lead_emphasis`, stated once, calmly |
| Perceived likelihood | `pillars`, `proof`, the weekly evidence cadence, `scope` |
| Time delay | `timeline`, `targets` |
| Effort and sacrifice | a short `scope.from_you` list |
| Risk reversal | a pilot option, a scoped `guarantee` Aleem approved, credit toward the next tier |

## Field by field

**`client`**: company, contact name, role and email exactly as they gave them. The email pre-fills
the sign form, so get it right.

**`issued`, `valid_until`**: ISO dates. Two weeks is the default window. Over 30 days triggers a
warning, because a distant deadline is not a decision date.

**`hero.headline` + `headline_accent`**: the outcome they want, in their words, as one sentence of
roughly 8 to 16 words. The accent is the qualifier that makes it theirs ("without hiring for it",
"before the October launch"), 2 to 6 words, rendered in italic accent colour. Never a service
name. "Website redesign" is a line item; "Turn the site into the thing that books your calls" is
a headline.

**`hero.subhead`**: what the engagement is, in one plain sentence.

**`diagnosis`**:
- `heading`: two short sentences contrasting what is strong with what is missing ("The demand is
  real. The delivery capacity is not.").
- `lead`: their situation, built on one fact they told you.
- `lead_emphasis`: the cost of the gap. Rendered bold in brand blue. One sentence.
- `body`: one to three short paragraphs. Name the risk or objection they voiced, in their words,
  then say how this proposal is built around it. This is the section that shows you listened.

**`pillars`** (optional, 2 to 4): what changes, or the principles the work runs on. A short
`label`, a `title`, one or two sentences of `body`.

**`targets`** (optional): only numbers the client said or agreed on the call, or delivery facts
NexusPoint controls ("10 days to a working first workflow"). The `note` must say these are targets,
not guarantees, and what they depend on. If there are no real numbers, leave `targets` out. A
fabricated metric is the fastest way to lose a sophisticated buyer.

**`program`**: `label`, `heading`, `intro`, and 2 to 4 `phases`. Set `highlight: true` on the one
phase where the core value gets built.

**`timeline`**: rows of `when` / `what` / `deliverable`. Check `context/team.md` before promising
a pace. Give each row a concrete deliverable name.

**`scope`**: `included`, `not_included`, `from_you`. `not_included` is where scope creep gets
prevented, so always list pass-through costs (software, AI model usage, ad spend, billed at cost plus
15-25 percent per `agency/pricing-and-packages.md` unless Aleem says otherwise) and anything the
client might reasonably assume is included but is not.

**`proof`** (optional): real, relevant past work from the brain's `wiki/portfolio.md` or a written
case study. `link` must be https. If nothing is relevant, leave it out.

**`investment`**:
- `heading`: frame what they are buying, not the price ("One partner behind your delivery.").
- `intro`: what is billed separately, and anything about how prices are set (wholesale, for example).
- `recommendation`: which option you recommend and why, tied to something specific about their
  situation. It sits next to the call-to-action button, so end on the reason, not a pitch.

**`options`** (1 to 3):
- `id` (lowercase slug), `name`, `summary` (one line), `includes` (3 to 5 bullets), `term` (optional).
- `price`: a number, confirmed by Aleem. `billing`: `one_time` or `monthly`.
- `deposit_pct`: one-time only, default 50. Monthly options take the first month to start.
  A monthly option that includes a build needs a minimum term in `term` and `terms`, or the
  client can pay one month, take the build and cancel.
- `balance_due` (optional, one-time): replaces "is due on delivery", e.g. "is due at launch".
- `recommended`: exactly one when there are several.
- `pay_url`: a Payoneer or Stripe link, or `""`. See `payments.md`.

  Three options close better than one (practitioner-tier figure cited in
  `agency/pricing-and-packages.md`). Put the recommended option in the middle. The option above it
  must be a real offer NexusPoint would deliver, not a decoy. The option below it is usually a
  smaller first step. The renderer computes every price label and amount due, so never write a
  price into prose fields where it could drift from `price`.

**`payment_methods`** (optional): overrides the payment wording shown after signing. It defaults by
currency (USD: card, ACH or wire; GBP: card or UK bank transfer; EUR: card or SEPA).

**`terms`**: payment method and schedule, IP transfer, termination and notice, how change requests
are handled, and non-solicitation for agency partners. One sentence each.

**`guarantee`** (optional, `title` + `body`): only one Aleem has explicitly approved, and only
about things NexusPoint controls ("If a delivered workflow does not do what the scope says, we fix
it at no cost."). The renderer warns whenever this field is present, so the approval question
gets asked every time.

**`prepared_by`**: name, role, and the email the client should reply to.

## Voice

- Consultative, specific, calm. A sharp founder thinking alongside a peer.
- Their words over yours. One observed, verifiable detail beats three generic ones.
- Short paragraphs, because they read it on a phone. The lint warns at 90 words per string.
- Ask, never command. "Continue with the Pilot", not "Sign here now".
- No em or en dashes anywhere. No placeholder brackets. No "$X value". No labelled bonuses.
- Kill-list words the lint rejects: leverage, robust, seamless, streamline, elevate, unlock,
  empower, cutting-edge, comprehensive solution, pain points, synergy, game-changer,
  revolutionize, delve, world-class, best-in-class, next-level, supercharge, harness the power,
  tailored solution, no-brainer, irresistible, act now, limited spots. Say the plain thing instead.

## By buyer type

**Agency buying white-label** (the lead ICP): the objection is "can I put my name on your work".
Lead the diagnosis with delivery trust. Emphasise invisibility (their tools, their brand), a
checkable evidence cadence, clean handover and IP transfer on delivery. Use wholesale prices from
`agency/pricing-and-packages.md` and put mutual non-solicitation in the terms.

**Founder or SMB buying for themselves**: lead with the outcome and the time or money they said
they are losing. Sanity-check the price against the pricing file's rule (10 to 25 percent of the
client's first-year value from the work) using only numbers they gave you. Do not print ROI maths
built on assumptions.
