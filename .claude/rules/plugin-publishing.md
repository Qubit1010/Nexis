# Plugin Publishing (nexuspoint-claude-skills)

When converting any internal skill into a plugin for `Qubit1010/nexuspoint-claude-skills`,
scrub all personal and agency-specific details before pushing. The plugin must work
out of the box for any team or client, with zero NexusPoint identity baked in.

## What to strip

| Type | Examples to remove |
|---|---|
| Names | "Aleem", "Aleem Ul Hassan", any team member name |
| Email / accounts | `hassanaleem86@gmail.com`, any personal email or Google account |
| Agency branding | "NexusPoint", `nexus-point.co`, agency-specific sheet names ("NexusPoint ... Outreach CRM") |
| Internal paths | `.env` lookups in `projects/bid-engine/`, `projects/daily-news-brief/`, or any Nexis-specific project path |
| Internal skill cross-references | Paths like `.claude/skills/sales-playbook/` — replace with "edit the references folder" or similar |
| Internal trigger language | "Aleem wants", "when Aleem mentions" — replace with "you want", "when the user mentions" |

## What to replace it with

- Hard-coded identity (name, role, agency) → env var with a generic default.
  Example: `SENDER_IDENTITY` defaulting to `"a founder at a digital agency"`.
- Hard-coded sheet names → env vars + generic descriptions in docs
  (e.g. `LEADS_IG_CRM_SHEET_ID` with a comment explaining what it points to).
- Internal `.env` fallback paths → only `REPO_ROOT / ".env"` (the standard location).
- "NexusPoint ... CRM" → "your ... CRM" or "the outreach CRM".
- Auth references → "authenticated to your Google account".

## Checklist before pushing a plugin

- [ ] Grep for "Aleem", "NexusPoint", "nexus-point", "hassanaleem" across all plugin files — zero hits.
- [ ] Any identity used in prompts or messages is behind an env var with a sensible default.
- [ ] Sheet names / IDs are env-var-driven, not hardcoded.
- [ ] Only `REPO_ROOT / ".env"` in env-file fallback lists — no internal project paths.
- [ ] SKILL.md trigger phrases say "you" / "the user", not a person's name.
- [ ] README section added (or updated) for the new plugin.
- [ ] `plugins/` directory in the cloned `nexuspoint-claude-skills` repo, not the Nexis subfolder.

## Workflow

1. Clone / pull `https://github.com/Qubit1010/nexuspoint-claude-skills` to `C:\tmp\nexuspoint-claude-skills`.
2. Copy the skill folder into `plugins/<skill-name>/`.
3. Apply the strip checklist above.
4. Update `README.md` with a section for the new plugin.
5. Commit and push.
6. Sync the stripped version back into `projects/nexuspoint-claude-skills/plugins/<skill-name>/` in Nexis if you want both in sync.
