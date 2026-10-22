# Onboarding a new client

Build the profile before the first script. Everything here either changes what may appear on
screen or is needed by the build, and getting it wrong later means regenerating paid footage.

## Gather (ask the user, or read the client workspace)

1. **Brand:** primary, accent and dark hex colours; logo (convert an SVG to a cropped PNG first,
   e.g. a headless Edge or Chrome screenshot); Latin font files; the RTL font name if relevant.
2. **Language:** which language is primary on screen, whether every line gets a translation
   underneath, and who signs off the copy (a native speaker for dialect).
3. **Regulator and guardrails:** where the compliance file lives, and the hard rules:
   - banned words
   - claims that need sign-off
   - roles that must never be AI (doctors, staff, patients)
   - consent rules for children
   - the AI-labelling requirement
4. **Culture and taboos:** what must never be generated (national symbols, religious
   architecture, specific dress rules, gestures, objects that read as religious), plus positive
   motifs worth using.
5. **End card:** the call-to-action lines, legal footer lines, any QR.
6. **Higgsfield workspace and budget:** which workspace pays, and a soft cap per film.
7. **Recurring characters:** create them once (see the playbook) and store the element ids.
8. **Voices:** audition per role with `voice_pitch.py` and store the picks with their pitch.

## Write it

Save `video-profile.json` in the client's gitignored folder (e.g. `client-projects/<client>/`),
following `spec-format.md`. Put the hard rules in plain sentences; they are read by you, not
parsed. Keep CURE's profile as the reference example:
`client-projects/primara/cure/video-profile.json`.

## Never

Do not put client data (brand files, element ids, rules) inside this skill folder. The skill is
generic and lives in the repo; client material stays in the client's gitignored workspace.
