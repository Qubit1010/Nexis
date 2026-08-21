# Live query — when the corpus is silent or stale

**Never fill an evidence gap with a plausible number.**

This skill needs a live tier more than any sibling. Brand theory keeps for years; a feed-ranking
change keeps for a quarter. Every `[P*]` page in `platform-specs/` was retrieved **2026-08-21**
and every one of them is revised without notice.

---

## The ladder

### Tier 1 — the local corpus

`references/research-synthesis.md`, `platform-scoreboard.md`, `platform-specs/`,
`what-not-to-do.md`, `growth-playbooks.md`. Resolve `[sN]` in `_research/sources.json` **on the
`index` field, not list position**. The file has deliberate gaps where nine junk sources were
purged; that is correct and existing citations still resolve.

### Tier 2 — platform documentation (**higher here than in any sibling skill**)

In `content-advisor`'s ladder, platform docs sit below NotebookLM. **Here they sit second,
because they are the primary source.** When the question is "how does this platform rank", the
best available answer is what the platform published and when.

Go straight to the host, not to an article about the host:

| Platform | Where |
|---|---|
| LinkedIn | `linkedin.com/blog/engineering/feed`, `news.linkedin.com` |
| Instagram | `creators.instagram.com`, `about.instagram.com`, `help.instagram.com` |
| Facebook / Meta | `transparency.meta.com`, `facebook.com/business/help`, `about.fb.com/news` |
| YouTube | `support.google.com/youtube`, `blog.youtube` |
| TikTok | `newsroom.tiktok.com`, `support.tiktok.com` |
| Pinterest | `help.pinterest.com/business` |
| Snapchat | `help.snapchat.com` |
| X | `help.x.com` (thin; see below) |
| Reddit | `business.reddithelp.com` (nothing in this corpus) |

**Always record the retrieval date**, and add anything load-bearing to
`research-synthesis.md` under **Live Query Additions** so the next person does not re-fetch it.

### Tier 3 — self-research via the `research` skill

```
python .claude/skills/research/scripts/research.py --query "<gap question>" --depth deep --save
```

Use `--mode practical` for platform and tactic questions; the default routing sends anything
mentioning studies or evidence to the journals, which is wrong for "what changed on TikTok".

**Query-wording warning, learned expensively on this corpus.** Two live failures worth not
repeating:

- **Never lead with the bare word "social".** The q14 query led with "social listening" and the
  engines returned the Social Security Administration, two dictionaries and a bar in Birmingham.
  Ten of twelve sources were junk. Use "brand mention monitoring", "community manager", or name
  the platform.
- **Never use "founder", "CEO", "owner" or "who is" in a research query.** `research.py`'s
  `_PERSON_HINT` matches them and forces the pass into `entity` mode, which searches for
  *people* and returns profiles instead of research. Use "entrepreneur" or "senior leader".

### Tier 4 — NotebookLM

Not mirrored for this skill. `push_to_notebooklm.py` was deliberately not cloned: the corpus
plus a first-party platform-doc tier that must be checked live anyway covers the fallback, and a
mirror of a corpus that decays this fast would be stale on arrival. Add it if Tier 2 and Tier 3
prove insufficient in real use.

---

## When to go live without being asked

- **Any `[P*]` claim being repeated to a client** where the retrieval date is more than roughly
  two quarters old.
- **Anything about TikTok's 2026 changes.** Explicitly weak in this corpus.
- **Anything about Reddit, Threads or Bluesky.** Effectively no coverage.
- **Anything about X's current ranking.** The audit literature is strong but predates recent
  platform changes, and the one first-party doc is a media-literacy policy.
- **Any claim that a platform "just changed" something.** Check the newsroom, not a blog.

## What a live answer must carry

State the tier, the source, and the retrieval date, and mark it as **not part of the locked
corpus**. `marketing-advisor` does this with a `[Ln]` tag for its live LinkedIn pass; do the
same rather than silently blending live findings into `[sN]` numbering, which would break
`gather.py verify`.
