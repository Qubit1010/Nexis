Use the **blog-writer** skill (`.claude/skills/blog-writer/SKILL.md`) to write one post for the
**NexusPoint agency blog (nexus-point.co)**, following its Content OS contract in
`.claude/skills/blog-writer/references/content-os-contract.md`.

This is an **agency** post, not Aleem's personal brand. Resolve the voice the way blog-writer's
client mode does, with the agency as the client:

- Voice: `agency/14-brand-voice.md`. Positioning and what the brand rules out:
  `agency/13-brand-strategy.md`. Blog plan: `agency/21-blog-engine.md` if relevant.
- The personal-brand rules do **not** apply (naming NexusPoint is fine, "we" voice is fine).
  Never present Aleem's personal projects as client results.
- Look at two existing posts in `D:/nexuspoint-site/src/content/blog/` for the house pattern and to
  avoid an existing slug.

Run folder: `{{RUN_DIR}}`
Item brief (also saved as `{{RUN_DIR}}/input.json`):

```json
{{INPUT_JSON}}
```

Do blog-writer steps 1 to 6. Skip step 7 (Content OS is the review gate) and step 8.

Output, all inside the run folder:

- `{{SLUG_HINT}}.md` (or a better slug): the **Astro-ready** post. YAML frontmatter matching
  `D:/nexuspoint-site/src/content.config.ts`: `title`, `seoTitle`, `excerpt` (105-155 chars),
  `category` (one of {{CATEGORIES}}), `draft: false`, `primaryKeyword`, `secondaryKeywords`,
  `keyTakeaways`, `faq`, `datePublished` and `dateModified` as `{{PUBLISH_DATE}}`, and only if a
  cover exists `coverImage: "../../assets/blog/<slug>/cover.png"`, `coverImageAlt`,
  `coverFit: "contain"` for text-led covers. **No H1** in the body, **no `## SEO Metadata`**
  section.
- `seo-metadata.md` and `onpage.json` as blog-writer steps 5a and 5b produce them.
- Do not run blog-images for agency posts (it renders the personal palette). Leave the cover out;
  the reviewer uploads one.

`files.main` is the post file. `meta` must include: `slug`, `primary_keyword`, `word_count`,
`category`, `seo_title`, `excerpt`.
