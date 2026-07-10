# Review Report Template

> Written by **code-reviewer** in Phase 6, then extended by the ponytail/impeccable polish pass. Verify against `.builder/architecture.md` and run the Phase-5 suite.

---

```yaml
---
status: {{pass|fail|blocked}}
critical_issues: {{count}}
warnings: {{count}}
suggestions: {{count}}
tests: {{passing}}/{{total}}
reviewed: {{ISO_TIMESTAMP}}
---
```

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Critical Issues | {{n}} | MUST FIX |
| Warnings | {{n}} | SHOULD FIX |
| Suggestions | {{n}} | NICE TO HAVE |
| **Overall** | | **{{PASS / FAIL / BLOCKED}}** |

{{1-2 sentence state of the build.}}

---

## Contract Verification (architecture Section 6)

| Endpoint | Backend Implements | Frontend Calls | Request Match | Response Match | Status |
|----------|-------------------|----------------|---------------|----------------|--------|
| `{{METHOD /path}}` | {{OK/MISSING}} | {{OK/MISSING}} | {{OK/MISMATCH}} | {{OK/MISMATCH}} | {{OK/FAIL}} |

## Completeness (architecture Sections 5, 7, 8)

| Item | Type | Exists | Correct | Status |
|------|------|--------|---------|--------|
| {{route / endpoint / table}} | {{page/endpoint/table}} | {{Yes/No}} | {{Yes/No/Untested}} | {{OK/MISSING}} |

## Security Baseline (references/code-standards.md)

| Check | Result |
|-------|--------|
| No secrets in source | {{OK/FAIL}} |
| Input validated at boundary | {{OK/FAIL}} |
| Authz re-checked on mutations (RLS if used) | {{OK/FAIL}} |
| Webhooks verified / idempotency on money paths | {{OK/FAIL/NA}} |
| Parameterized queries | {{OK/FAIL}} |

---

## Critical Issues (MUST FIX)

### C{{n}}: {{Title}}
- **Location:** `{{file:line}}`
- **Problem:** {{what's wrong}}
- **Impact:** {{what breaks}}
- **Fix:** {{specific, implementable}}

## Warnings (SHOULD FIX)

### W{{n}}: {{Title}}
- **Location:** `{{file:line}}`
- **Problem:** {{...}}
- **Recommendation:** {{...}}

## Suggestions (NICE TO HAVE)

### S{{n}}: {{Title}} — {{description + benefit}}

---

## Build / Type / Test Results

- **Typecheck:** {{PASS / FAIL — n errors}}
- **Frontend build:** {{PASS / FAIL}}
- **Backend start:** {{PASS / FAIL}}
- **Test suite (Phase 5):** {{passing}}/{{total}} — {{PASS / FAIL}}

```
{{key output snippets}}
```

---

## Fix Log (one pass)

| Issue | Fix Applied | Verified | Status |
|-------|-------------|----------|--------|
| C{{n}} | {{fix}} | {{Yes/No}} | {{FIXED / STILL BROKEN}} |

**Post-fix status:** {{pass|blocked}}
{{If blocked: what remains and why it needs the user.}}

---

## Polish Pass (ponytail / impeccable)

> Only runs if review is not blocked. Behavior unchanged; the diff only removes and tightens. Re-run typecheck + tests after.

| Change | Kind |
|--------|------|
| {{removed dead code / collapsed duplication / dropped a needless dep / tightened naming}} | {{remove/simplify}} |

**Post-polish:** typecheck {{PASS}} · tests {{passing}}/{{total}}.
