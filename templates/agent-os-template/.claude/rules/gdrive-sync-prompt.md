# GDrive Sync Prompt

After adding or modifying files in the gitignored/private folders (the ones in `privacy.md` plus any other local-only context), ask once at the end of the response:

> Want me to sync these changes to Drive?

**Rules:**
- Ask after the work is done, once per session per batch.
- Skip if {{PRINCIPAL}} said "don't sync" in the current message.
- The private folders sync to a **private** Drive folder only — this is their only backup since they're never committed.
