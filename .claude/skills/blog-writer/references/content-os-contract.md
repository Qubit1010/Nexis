# blog-writer under Content OS

Content OS (`projects/content-os/`) runs this skill headless to produce an **Astro-ready** post for
one of two sites. Its prompt names the site, the run folder and the brief. When a prompt says it
comes from Content OS, follow this file wherever it differs from SKILL.md.

| SKILL.md | Under Content OS |
|---|---|
| Voice resolution | Personal blog (aleemuh.com): `agency/personal-brand-voice.md` as usual. Agency blog (nexus-point.co): treat NexusPoint as the client, voice from `agency/14-brand-voice.md` + `agency/13-brand-strategy.md`; the personal-brand rules do not apply. |
| from-scratch mode ("propose 3 angles, let him pick") | Pick the strongest angle yourself and say why in `notes_for_reviewer`. |
| Step 2 research | As written (`--depth medium`, or `deep` for a pillar guide). Python is `python` on PATH. |
| Step 5b validate | Run seo-onpage against the draft in the run folder and save its JSON as `onpage.json`. |
| Step 7 review gate | Skipped. The Content OS review screen is the gate. |
| Step 8 save | Skipped: no Google Doc, no Blog Engine sheet. Content OS commits the file into the site repo after approval. |
| Output contract (H1 + `## SEO Metadata` block) | **Changed.** The main file is the site's content-collection file: YAML frontmatter matching the site's `src/content.config.ts`, no H1, no metadata block. The metadata package goes to `seo-metadata.md` instead. |
| Images | Render into `<run folder>/images/` and reference them as `../../assets/blog/<slug>/<file>.png`. Content OS copies them into `src/assets/blog/<slug>/` on publish. |

Finish by writing `output.json` exactly as the appended Content OS contract describes.
