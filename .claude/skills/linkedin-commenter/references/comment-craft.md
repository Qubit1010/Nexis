# What makes a comment worth writing

Read this before drafting. It is the whole quality bar, and the difference between a comment that
earns a profile visit and one that gets scrolled past is almost entirely in here.

---

## Why commenting at all

Aleem's account is efficient but small. His posts reach 40.7% of his followers, which is top quartile
(the threshold is 20%), while absolute impressions sit at median. That is a small-base problem, not a
quality problem, and posting more is not available: he is capped at 2 posts a week by his own
decision. Commenting is the only lever that adds surface area without adding posts, because it
borrows an audience that already exists.

The numbers that set the bar:

- A 10+ word substantive comment carries **5-7x the weight of a like** in LinkedIn's ranking.
- Top creators comment **~150/week**. The platform hard cap is **90/day**.
- Low-effort emoji comments are explicitly discouraged by the platform's own 2026 signals.
- LinkedIn now shows impression counts on your own comments, so this is finally measurable.

Full context: `marketing-advisor/references/linkedin-playbook.md`, "Growing the account".

---

## The bar

**Brief.** One to three sentences, roughly 15 to 45 words. Above the 10-word substance floor, well
below a mini-post. If it needs a line break, it is too long. Long comments read as someone using
another person's post as a stage, and people can feel that.

**It has to add something the post does not already say.** This is the entire test. Before writing,
ask: does this comment contain information, a distinction, or a question that was not in the post? If
no, there is no comment to write. Agreement is not a comment. Restating the post in different words
is not a comment.

The four moves that actually clear this bar:

| Move | What it looks like |
|---|---|
| **Specific counter-case** | The post's claim is right except in a case you have actually hit. Name that case. |
| **A number or detail from real work** | You have shipped something adjacent. Give the concrete figure or constraint that sharpens their point. |
| **A sharpened distinction** | The post conflates two things that behave differently. Separate them in one line. |
| **A real question** | Something you genuinely do not know the answer to and would read the reply. Not rhetorical, not a setup. |

**Never summarize the post back at the author.** They wrote it. This is the single most common
failure mode and it is the clearest tell of automation.

**Honesty gate.** Only claim experience Aleem actually has. If the post is on something outside his
work, ask a real question instead of inventing a war story. Fabricated specifics are worse than
generic praise, because they are a lie to a stranger in public and under his own name. This is
`agency/personal-brand-voice.md`'s No-Experience Fallback applied to comments: bridge
to adjacent real experience, or ask, or skip the post entirely.

**Skipping is allowed and often correct.** If a post gives you nothing true and specific to say, say
so in the output rather than manufacturing something. Twelve good comments beat twelve slots filled.

---

## Mechanics

These come from `agency/personal-brand-voice.md`, which is the source of truth for
anything written as Aleem. Load it before drafting.

- **No emojis.** LinkedIn voice, per the voice file.
- **No em dashes or en dashes.** Commas and periods. They read as AI and corrupt on paste.
- **Straight ASCII apostrophes and quotes only.** Curly quotes corrupt when copied.
- **No pitch, ever.** Never mention the agency by name, never reference services, never steer toward
  a call. A comment section is not an outreach channel. Pitching in public under a stranger's post is
  the fastest way to be remembered badly.
- **Never reference university, degree, BSAI, or student status.** Hard rule from the voice file.
- **First person, and sparing with it.** More than two "I"s in three sentences means it became about
  Aleem instead of the post.
- **Match their register.** A casual post gets a casual comment. A technical post gets precision.

---

## Banned openers

These are the phrases that mark a comment as filler on sight. If a draft starts with one, the draft
has no content and needs rewriting, not editing:

"Great post", "Great insight", "Couldn't agree more", "Thanks for sharing", "This is spot on",
"Well said", "100%", "So true", "Love this", "Absolutely", "This resonates", "Well articulated",
"Spot on", "Nailed it".

Also avoid the fake-humble opener ("Just my two cents", "Might be wrong here but") and the credential
drop ("As someone who builds AI systems"). Both are throat-clearing that costs words the comment
cannot spare.

---

## The batch check

After drafting every comment in a run, read them together as one list. This is the step that catches
the failure the individual drafts cannot see.

Two things converge without anyone noticing:

1. **Opening shape.** If eight comments open by naming a distinction the post missed, that is one
   comment wearing eight hats. Vary how they start: some open on the question, some on the specific
   case, some flatly disagree, some are markedly shorter than the rest.
2. **The move.** Count how many of each of the four moves you used. If the counter-case move is more
   than half the batch, redistribute.

This is not hypothetical. `leads-to-crm/scripts/messages.py` documents two separate incidents where
generated outreach copy converged this way, and it had to be fixed twice: once by stripping literal
phrasing out of the prompt, once by adding a mechanical similarity check. Comments are shorter and
more public than DMs, so the same convergence is more visible, not less.

The reason it happens is worth understanding rather than just guarding against: writing twelve
comments in one pass, you find a move that works on post three and it becomes the path of least
resistance for posts four through twelve. Each one feels fine in isolation. Only the list reveals it.

---

## Worked examples

**Post:** a creator arguing that most companies adopting AI agents are just rebranding their
chatbots.

- Bad: "Couldn't agree more. So many companies are just rebranding chatbots!" (Agreement, adds
  nothing, banned opener.)
- Bad: "Great point about the difference between chatbots and agents. Agents can take actions while
  chatbots just respond. This is why most AI projects fail." (Summarizes the post back, then states a
  generic claim as if it were insight.)
- Good: "The tell is whether it can fail. A chatbot that gives a wrong answer is embarrassing. An
  agent that takes a wrong action costs money, so nobody ships one without a rollback path. Most of
  what gets called an agent has nothing to roll back."

**Post:** a creator sharing that their cold email reply rate tripled after cutting personalization.

- Bad: "Interesting, thanks for sharing your results!" (Filler.)
- Good: "Curious what your volume was before and after. Cutting personalization usually raises reply
  rate and lowers meeting rate at the same time, and the two only separate once you are past a few
  hundred sends."

**Post:** a creator on a topic Aleem has not worked in, say enterprise sales compensation.

- Bad: an invented anecdote about a client. (Violates the honesty gate.)
- Good: "Does this hold when the cycle runs longer than the comp period? Every version of this I have
  seen from the outside seems to break on deals that straddle two quarters."

Note what the good ones have in common: each contains one thing the post did not, and each would
still make sense to someone who read it without the post.
