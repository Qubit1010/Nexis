Use the **blog-writer** skill (`.claude/skills/blog-writer/SKILL.md`) to write one post for
**aleemuh.com** in Aleem's personal-brand voice, following its Content OS contract in
`.claude/skills/blog-writer/references/content-os-contract.md`.

Run folder: `{{RUN_DIR}}`
Item brief (also saved as `{{RUN_DIR}}/input.json`):

```json
{{INPUT_JSON}}
```

Do blog-writer steps 1 to 6 (intake, research, keyword and outline, write, SEO/AEO pass, validate
with seo-onpage, human-tone pass). Skip step 7 (Content OS is the review gate) and step 8 (no Doc,
no Blog Engine sheet).

Output, all inside the run folder:

- `{{SLUG_HINT}}.md` (or a better slug you choose): the **Astro-ready** post. YAML frontmatter
  matching `D:/aleem-portfolio/src/content.config.ts` exactly: `title`, `seoTitle`, `excerpt`
  (doubles as the meta description, 105-155 chars), `category` (one of {{CATEGORIES}}), `draft:
  false`, `primaryKeyword`, `secondaryKeywords`, `keyTakeaways`, `faq` (question/answer list),
  `datePublished` and `dateModified` as `{{PUBLISH_DATE}}`, and, only if you made a cover,
  `coverImage: "../../assets/blog/<slug>/cover.png"` plus `coverImageAlt`. The body starts with
  the answer-first intro: **no H1** (the layout renders `title`) and **no `## SEO Metadata`
  section**. Look at two existing posts in `D:/aleem-portfolio/src/content/blog/` for the house
  pattern and to avoid an existing slug.
- `seo-metadata.md`: the full SEO metadata package from step 5a (title tag, meta, slug, keywords,
  answer callouts, JSON-LD stubs, internal-link suggestions, sources).
- `onpage.json`: the seo-onpage result (`--draft` mode, `--fails-only`), saved with `> onpage.json`.
- Images, optional: if you run blog-images, render PNGs into `{{RUN_DIR}}/images/` and reference
  them in the post as `../../assets/blog/<slug>/<file>.png`. Content OS copies `images/` into the
  site on publish.

`files.main` is the post file. `meta` must include: `slug`, `primary_keyword`, `word_count`,
`category`, `seo_title`, `excerpt`.
