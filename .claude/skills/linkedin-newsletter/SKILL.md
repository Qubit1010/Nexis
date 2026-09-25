---
name: linkedin-newsletter
description: "Turns a published aleemuh.com blog post, one or more social posts, or a bare topic into a ready-to-paste issue of Aleem's LinkedIn newsletter, Notes from the Workbench: condensed edition, takeaways, backlink and one subscribe CTA, saved as a Google Doc. Say 'LinkedIn newsletter issue', 'turn this post into the newsletter'. For email or client newsletters use content-production; for a single LinkedIn post, content-engine."
argument-hint: [blog slug or URL | pasted posts | a topic]
---

# LinkedIn Newsletter

Writes one issue of **Notes from the Workbench**, Aleem's LinkedIn newsletter, and hands it
over as a Google Doc he can copy straight into LinkedIn's article editor.

The newsletter is a **distribution surface, not the list**. LinkedIn owns those subscribers and
ranks who sees each issue; the owned list is the Kit email newsletter at aleemuh.com/newsletter.
So every issue does two jobs: be worth reading on LinkedIn, and move readers somewhere he owns.
That framing comes from `content-advisor/references/format-specs/newsletter.md`, which also marks
LinkedIn-specific mechanics as unverified. Treat anything about how LinkedIn ranks or notifies as
something to check live, not a fact.

---

## Load before writing

- `agency/personal-brand-voice.md` — the voice. The Unswappable Formula governs every issue.
- `agency/personal-brand-content-engine.md` — the LinkedIn rules and the content ladder. Voice
  and platform rules live there, not here, so they cannot drift between two skills.
- `references/issue-format.md` — the issue structure, the house length, the publishing notes.
- `content/linkedin-newsletter/issue-log.md` — what has already gone out. Create it from the
  template in `issue-format.md` if it does not exist.

Personal-brand rules that are easy to break in a longer piece: never name the agency (write "the
agency I run" if it must be referenced), never mention university or the degree, no emojis, and
no em dashes anywhere. Docs corrupts them and the rule applies to body text regardless.

---

## Three inputs, three starting points

**A published blog post** (slug, URL or "the latest post"). Read the markdown from
`C:\Users\qubit\OneDrive\Documents\Automations\Website-Creator\Projects\aleem-portfolio\src\content\blog\<slug>.md`.
Confirm the post returns 200 at `https://aleemuh.com/blog/<slug>`; if it does not, the backlink
would be dead, so stop and say the post is not live yet. This is a **condensed edition**, not a
copy: the blog already holds the full argument and ranks on Google, and a verbatim copy on
LinkedIn competes with it. Keep the core argument, rebuild the opening for LinkedIn, and let the
link carry readers to the rest.

**One or more social posts** (pasted text). The posts are raw material, usually one idea each.
Find the thread that connects them and write the issue around that thread; do not stitch posts
end to end. If the posts share nothing, say so and ask which one to expand. There is no blog to
link back to unless one covers the same ground, so check `src/content/blog/` for a match.

**A bare topic.** Nothing has been written yet, so this is original writing, and the risk is a
generic issue. Run the gate from `content-engine` (RUN, "Running a row") first: ladder check,
first-person check, pillar check. If it fails, propose the rescue instead of writing. Once it
passes, get sources from the `research` skill rather than from memory, and never state a number,
result or quote that the sources or Aleem did not supply. Mark any gap as a placeholder in
square brackets and flag it; the check script will refuse to pass the issue until it is filled.

---

## Write the issue

Follow `references/issue-format.md`. The parts that matter most:

- **The first two lines** carry the issue. They are what shows before "see more" and in the
  notification. A claim with a number or a named moment beats any greeting.
- **One argument, not a digest.** A newsletter issue that tries to cover the whole blog post
  reads like a summary. Pick the part with the strongest opinion and go deep on that.
- **One CTA.** Blog-sourced issues link the full post and invite email subscription. Do not
  stack a contact pitch on top; two asks halve both.

---

## Check, save, log

1. Save the issue to `content/linkedin-newsletter/<YYYY-MM-DD>-<slug>.md`.
2. Run the checker and fix every failure before going further:
   ```bash
   python .claude/skills/linkedin-newsletter/scripts/check_issue.py content/linkedin-newsletter/<file>.md [--source-url https://aleemuh.com/blog/<slug>]
   ```
   Pass `--source-url` whenever the issue came from a blog post, so the backlink is checked. A
   run that prints no word count did not run; say so rather than reporting a pass.
3. Convert to a Google Doc. The Doc is the paste vehicle, because copying from a Doc into
   LinkedIn keeps headings, bold and links, and pasted markdown does not. So this skill saves
   by default, unlike `content-engine`:
   ```bash
   pandoc "<file>.md" -o "<file>.docx"
   gws drive files create --upload "<file>.docx" \
     --upload-content-type "application/vnd.openxmlformats-officedocument.wordprocessingml.document" \
     --json '{"name":"LinkedIn Newsletter - <issue title>","mimeType":"application/vnd.google-apps.document"}'
   rm "<file>.docx"
   ```
   If the upload fails, give him the markdown inline and say the Doc was not created.
4. Append a row to the issue log with status `drafted`. Change it to `published <date>` only
   when Aleem says it went out; the log is how the next issue knows its number and avoids
   repeating a source.

---

## Hand back

The Doc link, then the publishing notes from the end of the file: the publish date, the cover
image to upload, and the short share text. Keep the reply short; the Doc is the deliverable.

---

## Edge cases

| Situation | What to do |
|---|---|
| Blog post not live yet | Stop. The backlink would 404. Offer to draft once it is deployed |
| Post already in the issue log | Say which issue used it. Only redo it if he asks for a new angle |
| First issue ever | Say so: LinkedIn's launch invite is expected to go to his network once, so the first issue should be his strongest piece. Verify live, it is not a sourced fact |
| Asked for an email newsletter, or a client's newsletter | `content-production` owns that |
| Asked for a single LinkedIn post or a teaser | `content-engine` |
| Asked to write the full blog post first | `blog-writer`, then come back |
| Asked to publish it on LinkedIn | This skill does not post. He pastes it. No automation for personal LinkedIn articles is assumed |
| Checker fails on a placeholder | Ask Aleem for the missing fact. Never fill it with a plausible number |
