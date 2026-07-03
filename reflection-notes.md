# Reflection Notes — Session Audit 2026-07-03

Diagnosis of 19 Claude Code sessions in Nexis (Jun 4 to Jul 3, 2026), ~26MB of transcripts. Raw signals pulled per session by subagents, clustered here, ranked by leverage: recurrence x cost per occurrence / build cost. Verdict per cluster: **fix** (environment/config), **rule** (SOP text), **skill/automation** (build), or **nothing**.

Sessions cited as: date + topic (short id). Full transcripts in `~/.claude/projects/c--Users-Aleem-OneDrive-Documents-Nexis/`.

---

## Ranked candidates

### 1. Machine environment manifest + PATH fix — **fix, do first**

The single most repeated friction in the corpus: Python is not on PATH in either shell, so every session re-discovers `C:\Users\Aleem\AppData\Local\Programs\Python\Python313\python.exe` by trial and error. Roughly 25-30 failed invocations across 9 of 19 sessions. Blocked skill-creator's entire eval tooling once (facebook-lead-nav shipped with unexecuted evals). Same class: `notebooklm.exe` hunted by recursive disk search, `gh` missing (token mined from `.git-credentials` instead), `ffmpeg` missing (npm-installed into temp), `pdftoppm` missing. Plus the cp1252 console encoding crash requiring `PYTHONUTF8=1` / `PYTHONIOENCODING=utf-8`, hit in 3 sessions including this one.

- Evidence: Jun 4-7 sales build (a380bba0, 5 errors + disk hunt), Jun 22-23 facebook build (254d750e, 4 incidents, "No Python in this environment at all"), Jun 14 API check (3f71b949, 4 attempts), Jun 18 giveaway (938fa097), Jun 26 ponytail (d3ce8032), Jun 27 notebooklm (a509c400) and gdrive-sync (57445b17), Jun 28 student-advisor (25787bfb), Jul 3 this session (71fb76ec, 9 identical failures in one loop).
- Fix: add Python313 + its Scripts dir to user PATH, set `PYTHONUTF8=1` as a user env var, install `gh`. Then add a short "Machine Environment" section to `.claude/rules/tool-integrations.md`: exact interpreter path as fallback, notebooklm.exe path, shell dialect notes (PowerShell cmdlets never in Bash tool, no inline `node -e`, `/c/` vs `C:/` path trap). The rule file is loaded every session, so the knowledge stops being re-derived.
- Cost: under 30 minutes once. Payback: every future session.

### 2. Content production batch mode — **skill extension**

The per-post content loop ran ~13 times in one sitting on Jun 27: paste post, manually pick template number, approve content map, say "generate", copy the Gemini prompt block, repeat. Every post needs BOTH a LinkedIn infographic and an Instagram carousel, always as two separate invocations with two approval gates. Template selection is manual every time. This is the highest-volume recurring workflow in the repo and it directly serves priority #2 (3x/week publishing).

- Evidence: Jun 27 ponytail session (e665f2ec): 7 LinkedIn infographics + 6 Instagram carousels, user typed "generate" 9 times and "Instagram-Template-N" 6 times; Jun 7 (1a61b451) same paste-post-repurpose pattern. Mid-loop the session also surfaced two codifiable preferences live: handle `@aleem_uh` missing from context, and "I want a single output so I can copy all of it at once".
- Build: extend `linkedin-infographics` + `carousel` with (a) a bundled "post package" mode: one post in, both content maps out, one approval, both prompt blocks in one copyable output; (b) a template-recommendation step so Aleem confirms instead of choosing from memory. No new infra, prompt-level changes to two existing skills.
- Cost: one session. Payback: ~half the turns on every content batch, forever.

### 3. Live-lead capture + follow-up in the sales flow — **skill extension + one asset**

Live DM threads get pasted and answered (the core sales-playbook loop, 5+ times in the sample), but nothing is captured afterward. The Logan thread (Jun 28) ended with "I'll keep in touch" and no follow-up trigger, no CRM entry, no log. Worse: the drafted reply offered a "top 3 bottlenecks that kill 7-day timelines" map as a lead magnet, and that asset does not exist. Priority #1 is converting pipeline leads, and the stated bottleneck is "closing the conversations that come back". Leads that come back are currently leaking on the way out.

- Evidence: Jun 28 Logan thread (98bf35f0): two session-limit hits mid-live-conversation, no capture step at the end; Jun 4-7 (a380bba0): three live threads pasted (Tyrus, VA Hub PRO, realtor) with the same pattern, reply drafted, nothing logged.
- Build: (a) add a closing step to `sales-playbook`'s live-reply flow: after a reply is chosen, append prospect + thread state + next-touch date to the matching outreach CRM (the gws plumbing already exists in leads-to-crm); (b) build the bottleneck-map lead magnet once, it was already promised to a real prospect.
- Cost: small extension + one content asset. Payback: direct revenue-path leverage; also note the sales-playbook-dashboard already exists precisely so live replies do not burn Claude Code session limits (98bf35f0 hit the limit twice mid-thread).

### 4. Auth preflight + OAuth-URL convention — **rule + tiny script**

Google auth expiry derailed tasks in at least 5 sessions, and each time the same dance was re-improvised: detect expired token, run login in background, dig the OAuth URL out of task output, hand it over, verify. Three different auth surfaces (gws, gdrive-sync's own Drive token, NotebookLM) expired in the same 36-hour window Jun 26-27. Aleem's preference is on record twice: "give me the oauth url I will login", he does not want assistant-driven browser logins.

- Evidence: Jun 4 (a380bba0) gws expiry mid-task with a false "exit 255" failure; Jun 22 (254d750e) identical detour, user interrupt "give me the oauth url"; Jun 26 (733af7c8) an entire session that is just "auth gws"; Jun 26 (d3ce8032) gdrive OAuth blocked, needed a new-window workaround because `run_console()` no longer exists; Jun 27 (a509c400) NotebookLM expired, interactive login blocked in the embedded terminal, fixed by piping ENTER.
- Build: one line each in `tool-integrations.md`: the known-good re-auth recipe per surface (command, where the URL appears, the piped-ENTER hack for notebooklm, "always hand URL, never drive the browser"). Optionally a 20-line `tools/auth-check.ps1` probing all three tokens at session start of heavy gws work.
- Cost: minutes. Payback: turns a 10-minute detour into a 1-minute handoff, several times a month.

### 5. Verification-before-done rule — **rule**

Three separate incidents where "done" was claimed and Aleem was the one who found it half-done. Jun 5: dashboards silently loaded stale responder content after a partial wiring pass, user caught it by output quality, and the fallout was a full delete-and-rebuild day (Jun 6). Jun 22: push.py tagged 104 rows "Added" that were never actually in the CRM, user spotted it ("you changed the tag Include to CRM as Added why?"), and the fix exposed 244 more stale rows across IG/LI. Jun 22: a new CRM sheet was created at My Drive root where the user could not find it.

- Evidence: a380bba0 06-05 "The wiring is only half-done"; 254d750e 06-22T23:33 and 23:59.
- Build: a short rule in `.claude/rules/`: after multi-file wiring or any bulk data write, verify by reading back the actual state (not the script's own report) and show the evidence before saying done; for Drive artifacts, state the folder path where the thing landed. The dry-run-first discipline that caught the 134-junk-row batch on Jun 22 is the positive example the rule should codify.
- Cost: trivial. Payback: one avoided rebuild day pays for it many times over.

### 6. Secrets intake rule — **rule**

Four exposure events: OpenAI key pasted in chat (Jun 5), Anthropic key pasted (Jun 6), the SAME compromised Anthropic key re-pasted when asked for the rotated one, and the Exa key written into `decisions/log.md` (Jun 28), which is Drive-synced; only the permission classifier stopped a GitHub push. Rotation after the first leak was advised and never confirmed; the Anthropic key sat compromised ~9 hours.

- Evidence: a380bba0 06-05T23:03, 06-06T14:23, 06-06T22:58 "That's the same key that was already exposed"; 25787bfb 03:11 credential-leak block.
- Build: rule: keys never go in chat, logs, or decisions; user puts them in `.env` directly and names the variable; assistant references names only, and any accidental paste triggers an immediate rotation prompt.
- Cost: trivial. Security, not convenience.

### 7. Researcher skill — **skill, promote from backlog**

The research-corpus pipeline has now run four times (sales-playbook, marketing-advisor, claude-advisor, student-advisor), each time by hand-adapting a copied `build_corpus.py` and improvising. The Jun 28 run added three throwaway Exa scripts (gather/boost/import) after NotebookLM auto-research produced "garbage" sources and burned the daily quota that then blocked importing the good ones. Aleem himself parked "researcher skill" in ideas.md that night. The foundation (`tools/exa/`) already exists; the recurrence is proven, and every future research-backed skill (per the research-backed-skills rule) will run this pipeline again.

- Evidence: 25787bfb 01:18-02:46: CLI flag mismatch, deep-research quota wall at pass 3 of 8, add-source wall at 139/217, "most of the sources are garbage" correction, PENDING-IMPORT.md left behind with 78 sources still unimported.
- Build: the ideas.md spec is right: Exa-powered, caller-controlled depth (deep/medium/light), multi-angle sourcing, markdown + JSON output, optional NotebookLM mirror. Fold the three throwaway scripts in as the starting point. Also record NotebookLM's real quota limits and flag set in the notebooklm skill's ops file so the walls stop being rediscovered.
- Cost: medium (one focused session). Payback: every future research-backed skill build, and the unfinished student-advisor import (78 sources) is the first test case.

### 8. Git hygiene at skill-creation time — **rule addendum**

The "in gitignore but still tracked" cleanup happened twice in two days (Jun 25 decisions/, Jun 26 a 35-file / ~23k-line purge of playwright logs and research artifacts), and the commit history shows repeated untrack churn across Jun 25-27. Root cause is upstream: skills generate runtime artifacts into tracked paths and gitignore entries arrive after the first commit.

- Evidence: 162bae62 (Jun 25), fd0e63df (Jun 26, "24 .playwright-cli/ logs, cache-stuck sources.json"); commit log 6/25-6/27 (5 chore/untrack commits); the fullwidth-colon junk file dodged in every git add across a380bba0.
- Build: one checklist line in `.claude/rules/skill-creation.md`: before first commit of a new skill, declare its runtime artifact paths and add them to .gitignore; `git status` must be clean of generated files. No new tooling.
- Cost: one line. Payback: ends a recurring cleanup class.

### 9. Project run commands documented — **fix (docs)**

Starting the content-engine dashboard has been re-derived at least 3 times across 2 sessions: glob for the project (two 20-second ripgrep timeouts on Jun 27), read package.json, npm run dev, poll readiness, open browser.

- Evidence: 660beafe (May 21 + Jun 5, "server stopped run it again"), d2c6909b (Jun 27, 3 tool failures just locating the folder).
- Build: a "Run commands" table in CLAUDE.md or one `README` line per project: path + start command + port. The built-in `/run` skill can then resolve instantly.
- Cost: 10 minutes. Payback: every dashboard start.

### 10. Plugin sanitize script — **automation, build on third use**

The sanitization pipeline in `plugin-publishing.md` ran twice end-to-end by hand in one session (claude-advisor, then marketing-advisor), including 5+ repeated leak-scan greps, and the manual PowerShell batch-replace corrupted two reference files mid-run. A third run is already anticipated (student-advisor was built "publishable-generic").

- Evidence: 938fa097 (Jun 18): full pipeline x2, 06:00 file corruption incident, leak greps at 04:55 x2, 05:00, 06:00, 06:04.
- Build: a `sanitize.py` implementing the existing checklist (scan terms, env-var swaps, path rewrites, README stub) run against a staging copy. The rule already defines the spec; the script just executes it.
- Cost: low-medium. Trigger: build it when the third giveaway actually happens, not before.

### 11. NotebookLM notebook cleanup — **automation, small**

243 notebooks had accumulated by Jun 27 (100+ auto-generated daily-brief research notebooks, April-June), requiring a manual purge session with two failed batch scripts before the right delete syntax was found. If the daily-brief pipeline still creates notebooks per run, this re-accumulates; the Jun 28 decision moved source curation to Exa, so first verify whether the generator is even still active.

- Evidence: a509c400 (Jun 27): "You have 243 notebooks", delete syntax found only via --help after 2 failed runs.
- Build: check daily-brief's pipeline for the notebook-creation step; if live, add a delete-after-synthesis step or a weekly purge. Record the delete syntax in the notebooklm ops file either way.
- Cost: small. Conditional on the generator still running.

### 12. Drive placement convention — **rule, one line**

Programmatically created Drive files land at My Drive root and get lost ("where did you push I dont see it in CRM", Jun 22; user moved it by hand next day). One line in tool-integrations.md: new Drive artifacts always go inside the matching Work folder, and the response must name the folder.

- Evidence: 254d750e 06-22T23:59, 06-23T00:38. Related: the gdrive-scope memory (Jun 27) exists because the sync boundary was also unclear.

---

## Meta-observation — where the sessions actually went

Of 19 sessions, roughly 13 were building or maintaining tooling; about 3 touched revenue directly (live DM replies, content production). Priorities say the bottleneck is execution consistency (outreach in inboxes weekly, closing conversations) and "every hour closing beats an hour building internal tools". The session mix is inverted relative to that. The highest-leverage items above (2, 3) are the ones that shorten the revenue loops rather than add new infrastructure; most of the rest are deliberately cheap rules/fixes rather than new builds for exactly this reason.

Also worth knowing: session limits and context compaction interrupted work 12+ times across the sample (including twice mid-live-sales-thread on Jun 28). Not fixable from inside the repo; the mitigations are the dashboard for live replies (item 3) and commit-early discipline on long builds.

## Explicitly not proposing

- **Central model config across projects**: one migration session (Jun 14) touched 7+ hardcoded model IDs, but a cross-project config refactor costs more than the next migration. The API-inventory generator script from that session already exists; keeping its output current is enough. Note the open landmine: `gpt-5.2` was set in 7+ files without live verification.
- **Anything for Edit-before-Read / "string not found" tool errors** (8+ occurrences): harness mechanics, not fixable by repo structure.
- **Session-limit workarounds**: plan-level, not buildable.
- **Sheet data contracts for lead scraping**: the header-name mapping in leads-to-crm already absorbed a column reorg with zero code changes; the junk-row triage rules Aleem gave on Jun 22 are now encoded. Watch, don't build.

## What already works (don't touch)

- Dry-run-first discipline in leads-to-crm caught the 134-junk-row batch and a 244-row re-push regression before any bad writes (Jun 22).
- The template skills' approval-gate loop: 13 assets in one sitting with 9 consecutive one-word approvals and zero rework (Jun 27).
- session-closeout as a ritual: accurate git-grounded summary, decisions logged, ~2 minutes (Jun 23).
- gdrive-sync core (MD5 dedup, idempotent re-runs) once authenticated.
- sales-playbook's live-thread classification: immediately named "Objection #7" and produced framework-grounded replies visibly better than the pre-skill ad-hoc draft (Jun 28).
