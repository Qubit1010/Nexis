# Research During the Build

The blueprint decided the stack. But building it well still raises implementation questions that are version-sensitive or easy to get subtly wrong: the current recommended way to wire a payment provider, the right data-fetching pattern for a framework version, a security nuance, a library's 2026 API. When you hit one, do not write it from memory and hope. Escalate to `developer-advisor`'s three-tier resolution, the same loop the advisor uses.

The advisor already owns this machinery. This file just tells the builder when and how to reach for it.

## When to escalate (not for everything)

Escalate when the answer is load-bearing AND any of these is true:
- It is version-sensitive (framework/library/service released or changed recently).
- Getting it wrong has real cost (payments, auth, data integrity, security).
- It is unfamiliar or you are unsure which of two approaches is current.
- The blueprint named a service but not the exact integration pattern.

Do not escalate for routine, stable code (standard CRUD, well-known component patterns). Escalation is for the genuinely uncertain, version-sensitive call. Note any escalated finding in `.builder/decisions.md`.

## The three tiers (delegate to developer-advisor)

Follow `developer-advisor`'s `references/research-fallback.md`. In order, stop at the first that answers:

**Tier 1 — Local references.** The advisor's curated corpus: `stack-scoreboard.md`, `research-synthesis.md` (`[sN]` -> `_research/sources.json`), the topic playbooks, `what-not-to-do.md`. Fastest; cite `[sN]`.

**Tier 2 — NotebookLM.** The advisor's notebook (`Developer Advisor - Curated Sources 2026`, `5c8257d3-cdb3-469e-8d8c-da500a99ea14`). PowerShell (Python is not on the Bash PATH):
```powershell
$env:PYTHONIOENCODING="utf-8"
& "C:\Users\Aleem\AppData\Local\Programs\Python\Python313\Scripts\notebooklm.exe" `
  ask "<implementation question, phrased for specifics/version/API>" `
  --json -n 5c8257d3-cdb3-469e-8d8c-da500a99ea14
```

**Tier 3 — Exa live research (research THIS implementation question).** When the corpus misses, research the specific problem. Shared client `tools/exa/exa_client.py` (loads `EXA_API_KEY` from repo `.env`; needs the sandbox disabled for network):
```bash
# Fast cited answer for a single implementation decision:
"C:/Users/Aleem/AppData/Local/Programs/Python/Python313/python.exe" tools/exa/exa_client.py \
  answer "current recommended way to <do X with service Y> in 2026"

# Multi-source compare when you need to read the tradeoffs:
"C:/Users/Aleem/AppData/Local/Programs/Python/Python313/python.exe" tools/exa/exa_client.py \
  search "<framework/service> <specific integration> 2026 best practice" --num 8 --type deep --highlights
```
Run with `PYTHONIOENCODING=utf-8`. Prefer official docs and vendor engineering blogs over listicles. Flag anything from Tier 3 as fresh live research, not from the locked corpus, and record the source in `decisions.md`.

## Worked example (from the Athllo blueprint)

The Athllo blueprint chose Stripe Connect but the exact 2026 integration is version-sensitive. During Phase 4, the builder would escalate: local refs (thin on payment specifics) -> notebook -> Exa live on "Stripe Connect Express destination charges recommended integration 2026", surfacing the current guidance (Express via the v2 Accounts API, destination charges for one-payee deals, the exact webhooks to handle, platform-as-merchant-of-record liability). That is exactly how the blueprint's own Stripe section was sourced, and the builder implements against that fresh finding rather than a remembered, possibly-stale pattern.

## The rule

Build from the current best answer, sourced, not from memory that may have drifted. When a load-bearing implementation detail is uncertain, go one tier deeper before you write the code.
