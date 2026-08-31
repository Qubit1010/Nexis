---
name: linkedin-commenter
description: 'Finds today''s best LinkedIn posts to comment on from Aleem''s target-profile list and drafts a brief, genuine, ready-to-paste comment under each. This is the daily growth habit: commenting adds reach without adding posts, which matters because his account is reach-efficient but small and posting is capped at 2x/week. Ranks by attention velocity against comment-section crowding, writes docs/linkedin-comments/YYYY-MM-DD.md. Commenting stays manual, no LinkedIn session is ever touched. Does not write his own posts (post-creator, content-engine) and never sends DMs.'
argument-hint: '[optional: "72h" after a gap, or a profile URL to add]'
---
# LinkedIn Commenter

Turns a list of profiles into a dated file of posts worth commenting on, each with a drafted comment
underneath. Aleem reads it, tweaks what he wants, pastes on LinkedIn.

**The comments are the product.** The script is just plumbing that decides where to look. Nearly all
the value of this skill is in the drafting pass, so do not rush it to get to a finished file.

## Why this exists

Aleem's posts reach 40.7% of his followers (top quartile is 20%+), but absolute impressions are only
median. That is a small-base problem, not a quality problem, and posting more is not on the table:
he is capped at 2 posts a week by his own Q4 decision. Commenting borrows audiences that already
exist, and a 10+ word substantive comment carries 5-7x the weight of a like. That diagnosis was
made 2026-07-27; the playbook holding it was deleted 2026-08-27, so the numbers above are the record.

Nothing here touches his LinkedIn account. The Apify actor runs on Apify's infrastructure with no
session or cookie, and posting the comments is manual by design.

---

## Workflow

### Step 1: Fetch and rank

```bash
python .claude/skills/linkedin-commenter/scripts/fetch_posts.py
```

Reads `docs/linkedin-profiles-posts.txt` (one profile URL per line), fetches recent posts, drops the
already-seen and hopelessly saturated ones, ranks the rest, and writes
`docs/linkedin-comments/YYYY-MM-DD.md` with an empty comment slot under each post.

Costs roughly $0.16 per run at 27 profiles (measured). Run it unsandboxed, it needs network.

**How the ranking works**, since it decides what he spends attention on: score is attention velocity
(likes plus weighted shares, per hour) divided by how crowded the comment section already is. That
single formula does two jobs at once. It surfaces posts still climbing rather than posts that already
peaked, and because large accounts have high likes *and* high comment counts, it normalises audience
size without needing follower data (which this actor does not return).

A high score means a good opportunity, not that the post is worth commenting on. Those are different
questions and step 3 answers the second one.

Useful flags:

| Flag | When |
|---|---|
| `--max-age-h 168` | Default is 96h (4 days, widened from 48h 2026-08-03). Push to 168, the actor's own "week" cap, after a longer gap. The script prints a reminder when the actual gap exceeds the current window, so watch for that line. |
| `--dry-run` | Check what would be surfaced without writing or spending a drafting pass. |
| `--limit-profiles 3` | Cheap check that the actor and keys still work. |
| `--top 30` | Default is 25 (widened from 12 2026-08-03). Push higher for an even bigger round. |
| `--ignore-seen` | Everything recent was already surfaced and he wants a second pass anyway. |
| `--per-profile 5` | The list is small or a lot of it went quiet, and you want more candidates per person. |

**If the run returns little or nothing**, that is usually correct rather than broken. The script
prints drop counts by reason (`age=`, `saturated=`, `seen=`). Read them and say which reason
dominated instead of blindly widening every filter. `age=` dominating on a daily run just means his
targets did not post much today, which no flag can fix.

**Apify keys rotate automatically** across `APIFY_API_KEY` and its numbered siblings. Key #1 was over
its monthly limit as of 2026-07-31 and the run rotated past it without intervention, so a
"quota/limit, rotating" line in the output is normal and not an error.

### Step 2: Load the drafting context

Read both before writing a single comment:

- `references/comment-craft.md` in this skill, the quality bar and the four moves that clear it
- `agency/personal-brand-voice.md`, the source of truth for anything written as Aleem

Do not skip the voice file. It carries the hard rules (no emojis, no em dashes, never name the
agency, never reference university) that a comment can violate in public under his own name.

### Step 3: Draft a comment per post

Edit the generated markdown, filling each `**Comment draft:**` slot in place. Work through the posts
one at a time, reading the full post text before drafting.

For each post, the question to answer first is: **what do I know that this post does not say?** If
there is a real answer, that is the comment. If there is not, replace the slot with
`_skipped: <the actual reason>_`. Skipping is a correct outcome and a filler comment is worse than no
comment, since it is public and attributed.

Expect to skip a meaningful share of any run. On the first live batch it was 4 of 12, for four
different and all legitimate reasons: a post that was just a meme plus a promo link, a post whose
substance lived in a video the scrape could not read, a second post by an author already commented on
that day, and a topic genuinely outside his work. Write the real reason rather than a generic one,
because the pattern of skips is what tells him his target list needs changing.

The four moves that clear the bar, per `comment-craft.md`: a specific counter-case, a number or
detail from real work, a sharpened distinction, or a real question. One to three sentences, 15 to 45
words.

**Never fabricate experience.** On a topic outside Aleem's work, ask a genuine question instead of
inventing a client story. A fabricated specific is worse than generic praise because it is a lie to a
stranger, published under his name.

### Step 4: Review the batch as a batch

This step is not optional and it is the one that is easiest to skip when the file looks finished.

Read all the drafted comments together as a list, ignoring the posts. Three things converge without
being noticeable draft by draft:

1. **Opening shape.** If most comments open the same way, they read as one comment wearing many
   hats. Vary it: some open on the question, some on the specific case, some flatly disagree.
2. **The move.** Count the four moves from `comment-craft.md`. If any one is more than half the
   batch, redistribute.
3. **Length.** The easiest one to miss. Drafting against a 15-45 word guideline pulls everything
   toward 45, so a batch can pass every other check and still read as machine-produced because all
   twelve are the same size. Some should be markedly shorter.

This failure is documented, not hypothetical. `leads-to-crm/scripts/messages.py` had to be fixed
twice for exactly this convergence in generated outreach copy. It happens because a move that works
on post three becomes the path of least resistance for posts four through twelve, and each one looks
fine in isolation.

A quick mechanical pass helps and takes seconds: grep the batch for em dashes, smart quotes, emojis,
the banned openers, and count `I` per comment (more than two means it became about him). That catches
the objective failures so the read-through can be spent on the subjective ones.

Rewrite whatever converged, then tell Aleem what you changed and why.

### Step 5: Log to the sheet (optional, on request)

```bash
python .claude/skills/linkedin-commenter/scripts/save_to_sheet.py
```

Parses the finished markdown (comments and all) and appends it to the `Log` tab of the Google Sheet
at `LINKEDIN_COMMENT_SHEET_ID` in `.env`, one row per post, with a blank `Posted` column he can check
off by hand after actually commenting. This is a durable cross-day record the local `.md` files
don't give him; run it whenever he says "save it", "log this", "put it in the sheet", or similar,
not automatically on every run.

It only runs after Step 4, never before: the sheet should hold the reviewed batch, not a
mid-draft one. It refuses to double-log the same date (exit code 1, message explains why) unless
`--force` is passed, so re-running it by accident is safe.

### Step 6: Hand it over

Report: how many posts surfaced, how many comments drafted, how many skipped and why, and the file
path (plus the sheet link if Step 5 ran). If the target mix looks off (all large creators, all one
topic), say so once, since that is a list problem he can fix rather than something to work around
silently.

---

## Managing the profile list

`docs/linkedin-profiles-posts.txt` is a plain list, one LinkedIn profile URL per line. Tracking
suffixes (`?lipi=...`) are stripped automatically, so URLs pasted straight from the feed work as-is.
Blank lines and `#` comments are ignored. A line may optionally be `url,tier,followers` if he ever
wants explicit tiers.

When he asks to add profiles, append them and mention the current count.

**Tier balance is worth raising once, not nagging about.** Large creators (100K+) saturate within an
hour, so the saturation filter will drop most of their posts, which is correct behaviour rather than
a bug. The playbook's advice is to weight toward mid-sized creators (comment sections still readable)
and peers (who comment back), and specifically toward agency founders in the ICP, marketing, AI,
design, and branding, since their audiences are who actually buy white-label. If a run is thin
because everything got dropped as saturated, that is the real fix.

---

## Boundaries

- **Writes no posts.** Aleem's own LinkedIn posts are `post-creator` and `content-engine`.
- **Sends no DMs or connection requests.** That is `sales-playbook` (copy) and `leads-to-crm`
  (pipeline). A comment section is not an outreach channel, and pitching under a stranger's post
  under his own name is the fastest way to be remembered badly.
- **Does not post the comments.** Manual by design. No LinkedIn credential is used anywhere.
- **Not a strategy skill.** For "should I be commenting at all", "what is a good reach rate", or
  benchmark questions, that is `social-media-advisor` (LinkedIn mechanics and account growth).
