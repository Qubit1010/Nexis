# linkedin-newsletter under Content OS

Content OS (`projects/content-os/`) runs this skill headless to write one issue for one of two
editions. When a prompt says it comes from Content OS, follow this file wherever it differs from
SKILL.md.

| Edition | Rules |
|---|---|
| `personal` (Notes from the Workbench) | As SKILL.md: personal-brand voice, never name the agency, one aleemuh.com CTA. |
| `agency` (NexusPoint) | Voice from `agency/14-brand-voice.md`. The agency name is allowed. The single CTA is "Subscribe to this newsletter". Backlinks point at nexus-point.co. Past issues: `content/linkedin-newsletter/nexuspoint/issue-log.md`. |

| SKILL.md | Under Content OS |
|---|---|
| Blog source path | The prompt gives the published blog URL and, when available, its local file in the site repo (`D:/aleem-portfolio/src/content/blog/<slug>.md` or `D:/nexuspoint-site/src/content/blog/<slug>.md`). Content OS only starts a blog-sourced issue after that blog is live. |
| Bare topic, gate fails | Rescue the angle yourself and explain it in `notes_for_reviewer`; use `status: "blocked"` only when the rescue needs a fact only Aleem has. |
| Check | `check_issue.py <issue> --edition <personal or agency> [--source-url <url>]`. Fix every failure before finishing. |
| Save as Doc, issue log | Skipped. Content OS renders a rich-text copy for pasting and appends the issue log when Aleem marks the issue published. |

Finish by writing `output.json` exactly as the appended Content OS contract describes.
