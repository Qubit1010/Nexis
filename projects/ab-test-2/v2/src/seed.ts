import type { DatabaseSync } from 'node:sqlite';
import { createEnquiry, createPrompt, listPrompts } from './service.ts';

export const STARTER_PROMPT = `You are drafting email replies on behalf of Aleem, who runs a small
agency building AI automation, web apps and internal tools for startups.

Voice:
- Direct and warm. Write like a sharp founder, not a corporate template.
- Short paragraphs. No filler, no "I hope this email finds you well".
- No emojis. No em dashes.
- Confident about what you can do, honest about what you cannot.

Every reply should:
- Open by naming what they actually asked for, so they know they were read.
- Say plainly whether this is a fit.
- End with one concrete next step.

Keep it under 150 words unless the enquiry genuinely needs more.`;

/**
 * The bench: a fixed, deliberately varied set of enquiries.
 *
 * Variety is the point. A bench of six polite, well-specified briefs would make every
 * prompt version look good. These include the awkward shapes a real inbox produces: no
 * budget signal, an unrealistic budget, pure price-shopping, and a brief that is out of
 * scope, because those are where prompt changes actually show up.
 */
const BENCH: Array<{ subject: string; sender: string; body: string }> = [
  {
    subject: 'Website redesign enquiry',
    sender: 'Dana Whitfield',
    body: `Hi,

We are a 12-person B2B SaaS company and our marketing site is four years old. It looks dated
and converts badly. We would want a full redesign plus a CMS the marketing team can update
without engineering.

Do you take on projects like this, and roughly what would it cost? We would like to launch
before end of quarter.

Dana`,
  },
  {
    subject: 'quick question',
    sender: 'Marcus',
    body: `how much for a website`,
  },
  {
    subject: 'AI agent for our support inbox',
    sender: 'Priya Raghunathan',
    body: `Hello,

We handle roughly 400 support emails a week, most of them the same eight questions. We want
something that drafts replies for our team to approve, pulling from our help centre.

We have a Zendesk instance and our docs are in Notion. Budget is flexible for the right
partner, but we need to see a working prototype before committing to a full build.

What would your process look like?

Priya
Head of Operations`,
  },
  {
    subject: 'Re: Following up on my last email',
    sender: 'Tom Beckett',
    body: `Just checking whether you saw my message from last week. Still keen to talk about the
dashboard project. Happy to jump on a call whenever suits.

Tom`,
  },
  {
    subject: 'Mobile app - $500 budget',
    sender: 'Kieran Doyle',
    body: `Looking for someone to build a two-sided marketplace app, iOS and Android, with payments,
chat and a rating system. Similar to Airbnb but for equipment rental.

Budget is $500 and I need it in three weeks. Let me know if you can do it.`,
  },
  {
    subject: 'Referred by Sam Ortega',
    sender: 'Nadia Hassan',
    body: `Hi Aleem,

Sam Ortega suggested I get in touch. She said you built the internal reporting tool that saved
her team most of a day a week.

We have a similar problem. Our ops team pulls numbers out of four systems by hand every Monday
and rebuilds the same spreadsheet. It takes two people most of the morning.

Would you have capacity to look at this in the next month or so?

Nadia`,
  },
];

/** Seed a starter prompt version and the bench, only into an empty database. */
export function seedIfEmpty(db: DatabaseSync): boolean {
  if (listPrompts(db).length > 0) return false;

  createPrompt(db, { label: 'v1 baseline', system_prompt: STARTER_PROMPT, activate: true });
  for (const e of BENCH) {
    createEnquiry(db, { subject: e.subject, body: e.body, sender: e.sender, in_bench: true });
  }
  return true;
}
