# Issue format

The structure of one issue of Notes from the Workbench, and what each part is for.

## House rules, not benchmarks

Two numbers in this file are **house choices**, not sourced findings. Say so if anyone asks:

- **Body length 400-600 words.** Long enough for one argument with evidence, short enough to
  read in the feed. The checker warns outside 350-750 and does not fail on length alone.
- **Publish 3-7 days after the blog post.** Practitioner advice about letting Google index the
  original before a high-authority copy exists on LinkedIn. LinkedIn offers no canonical tag, so
  the delay and the condensing are the only protection the blog has.

Nothing in `content-advisor` or `social-media-advisor` covers LinkedIn newsletter mechanics with
evidence. If a question turns on reach, notification behaviour or length performance, say it
is unverified.

## The file

```markdown
# <Issue title>

<Opening: two lines. A first-person claim with a number or a named moment. No greeting,
no "in this issue".>

<Body: one argument, 400-600 words. Two or three ## subheads at most, only where the
argument genuinely turns. Short paragraphs. Specifics over adjectives.>

## The short version

- <3 to 5 takeaways, each one a claim a reader could act on>

<Blog-sourced only:> [Read the full note](https://aleemuh.com/blog/<slug>)

<One CTA line. Default:> Get the full notes by email as they come out: [aleemuh.com/newsletter](https://aleemuh.com/newsletter)

Aleem

<!-- end issue -->

## Publishing notes (not part of the issue)

- **Publish on:** <date, 3-7 days after the blog's datePublished; for non-blog issues, any day>
- **Cover image:** <blog: src/assets/blog/<slug>/cover*.png in the site repo. Otherwise
  suggest `blog-images` for a cover>
- **Share text:** <2-3 lines for the post LinkedIn attaches to the issue. Its own hook, not
  the issue's opening repeated>
```

Everything above `<!-- end issue -->` is what he pastes. The checker only counts and checks that
part. Pandoc drops the HTML comment, so it never reaches the Doc.

### Title

Specific and arguable, the same test as a blog headline. "Gemini RSI leak: what the evidence
actually proves" works. "Thoughts on AI this week" does not. The newsletter's own name already
tells readers which series this is, so the title does not need to repeat it.

### The CTA, by source

| Source | Link | CTA |
|---|---|---|
| Blog post | Full post | Email subscribe (`/newsletter`) |
| Social posts with a matching blog post | That post | Email subscribe |
| Social posts or topic, no blog | None | Email subscribe, or `/contact` if the issue is explicitly about a problem he solves for clients. One or the other, never both |

## Issue log template

`content/linkedin-newsletter/issue-log.md` (gitignored; backed up by gdrive-sync):

```markdown
# Notes from the Workbench - issue log

| # | Date drafted | Title | Source | Doc | Status |
|---|---|---|---|---|---|
```

Status is `drafted` until Aleem confirms it went out, then `published YYYY-MM-DD`.
