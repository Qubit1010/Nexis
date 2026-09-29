---
name: proposal-generator
description: "Turns a call transcript, meeting notes or a scope brief into a signable web proposal for a direct (non-Upwork) client: a branded page with priced options, e-signature and a Payoneer pay step, deployed to a private link, then reports who opened or signed it. Say 'proposal for X', 'turn this call into a proposal', 'has X signed'. Upwork job posts go to upwork-proposal-studio; after payment, client-onboarding-workflow."
argument-hint: [transcript, scope brief, or client name]
---

# Proposal Generator

Produces one private web page per deal: diagnosis, plan, timeline, scope, 1-3 priced options with
one recommended, terms, then sign-to-start and a payment step. The client signs on the page; the
signature is stored server-side with name, email, time, IP and a hash of the exact version they
saw. Aleem gets an email when they open it for the first time and when they sign.

The page is static HTML on Vercel. Signatures go to Supabase through one serverless function.
Proposal content stays in `client-projects/<slug>/proposals/` (gitignored), never in the public repo.

## Boundaries, before anything else

- **Upwork-sourced client: stop.** If the client came from Upwork, payment has to run through
  Upwork. Taking it off-platform within 24 months of meeting there breaks Upwork's terms and
  risks the account. Say so, and point to `upwork-proposal-studio`.
- **Prices are Aleem's call.** Propose options anchored on `agency/pricing-and-packages.md`, then
  wait for him to confirm every number. If he has not, do not render. Never invent a price, a
  client metric, a case study or a guarantee.
- **Nothing goes to the client from here.** Deploying makes the page reachable. Aleem sends the link.
- **Deploy only after Aleem has looked at the rendered page** and said yes. It goes live on the
  public internet under an unguessable URL.

## What to read

Always: `references/writing-guide.md` (section by section, voice, what the lint enforces) and
`assets/example-proposal.json` (the exact JSON shape, a complete worked example).

As needed:
- `agency/pricing-and-packages.md`: price anchors, the $500 floor, "move scope, never rate",
  the risk premium, wholesale prices for agency partners.
- `agency/white-label-partnership-model.md` and `agency/icp-agencies.md` when the buyer is an agency.
- `context/team.md` for delivery realism, so timelines match who is actually available.
- The second brain's `wiki/portfolio.md` for real proof. Only real, relevant work goes in `proof`.
- `references/payments.md` when a pay link, deposit or retainer question comes up.
- `references/infra.md` when deploying for the first time, when a check fails, or to change setup.
- Anything already in `client-projects/<slug>/` (a `discovery-call-prep` brief or `meeting-insights` notes).

## Workflow

**1. Brief.** Read the input and write `client-projects/<slug>/proposals/brief.md`: company,
contact name, role and email; what they want, in their own words (short quotes); every number
they said; constraints; decision process and timing; budget signals; the objection or risk they
voiced; and open questions. Flag contradictions rather than resolving them silently. A gap stays
a gap, because a proposal built on a guessed fact gets caught by the one person who knows the truth.

**2. Gate: Aleem confirms scope and prices.** Show him a compact version of the brief, the
proposed options (name, what is in each, price, one-time or monthly, deposit, which one you
recommend and why), and the open questions. Wait for his answers.

**3. Write the proposal JSON** following the writing guide. Save it as
`client-projects/<slug>/proposals/draft.json`. Leave out `id`; the renderer assigns one.

**4. Render and lint.**
```bash
python .claude/skills/proposal-generator/scripts/render.py client-projects/<slug>/proposals/draft.json
```
It validates the fields, lints the copy (em dashes, placeholders, "$X value" stacking, the
sales-playbook kill-list words, price floor, pay link hosts, dates) and computes every price
label and amount due. On success it moves the JSON into `client-projects/<slug>/proposals/<id>/`
next to `index.html` and `meta.json`. Edit that `proposal.json` from then on and re-run
`render.py` on it. Fix every error; treat each warning as a question to answer, not noise.

**5. Look at it.** Open the rendered `index.html` in the browser pane, or screenshot it at desktop
and phone widths. Most clients open the link on a phone first, so check that the hero and the
option cards read well at 390px. Then hand Aleem the local file to review.

**6. Deploy after his yes.**
```bash
python .claude/skills/proposal-generator/scripts/deploy.py --approve <id>
```
It refuses to deploy if the files disagree on the content hash, if a signed proposal's content
changed, or if it cannot reach Supabase to check. After deploying it fetches the live page and
confirms the approved hash is what is being served, then prints the client link and a preview
link with `?internal=1`. Aleem should use the preview link so his own visits are not logged as
client views.

**7. Hand over.** Give Aleem the client link, the preview link, the options with price and amount
due to start, the expiry date, and what happens when they sign. Draft a short cover message for
him to send: two or three plain sentences, what is inside, the date it is valid until. He sends it.

**8. Follow up.** `python .claude/skills/proposal-generator/scripts/status.py [<id>]` shows views
(count, first, last, distinct IPs) and the signature if there is one. If it says COULD NOT CHECK,
report that, not "no views". When a client signs an option with no pay link, the alert email
tells Aleem to send a Payoneer payment request for the amount due. Once paid, hand off to
`client-onboarding-workflow`.

## Changing a proposal

| Situation | What to do |
|---|---|
| Not signed yet, content changes | Edit `proposal.json`, re-render (status drops back to draft), get Aleem's yes, `deploy.py --approve <id>`. Same URL. |
| Adding or changing a pay link | Edit `pay_url` and re-render. Pay links are outside the content hash, so approval stands; run `deploy.py`. |
| Already signed | Never edit it. The signed version is the record, and `deploy.py` will refuse. Issue a new proposal (a change order) with its own id. |
| Expired | Signing is closed on the page and on the server. Extending means a new `valid_until`, which is a content change: re-render, re-approve, deploy. |
| Take it down | `deploy.py --withdraw <id>`. |

## Edge cases

- **Transcript with no prices, or a budget that contradicts the scope:** list both in the brief and
  ask. Moving scope is fine; cutting the rate for the same scope is not (pricing file).
- **Buyer is an agency buying white-label:** use wholesale prices, lead the diagnosis with delivery
  trust, and put non-solicitation and IP transfer in the terms. The example proposal is this case.
- **Retainer only:** a single monthly option is fine. The amount due to start is the first month.
- **Several deliverables:** one proposal with one program, not a proposal per deliverable.
- **Resend not configured:** everything works, but there are no alert emails. `deploy.py` prints a
  note and `status.py` still reports views and signatures.
