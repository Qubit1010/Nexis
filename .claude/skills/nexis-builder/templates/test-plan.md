# Test Plan Template

> Written in Phase 5. Read `references/test-strategy.md` first. Right-sized to the complexity tier — cover the paths that hurt when they break, not a coverage percentage.

---

```yaml
---
project: {{PROJECT_NAME}}
shape: {{trophy | pyramid}}
runner: {{e.g., Vitest + Playwright | pytest + Playwright}}
complexity: {{simple|standard|complex}}
created: {{ISO_TIMESTAMP}}
---
```

## 1. Strategy

- **Shape:** {{trophy | pyramid}} — {{one line: why this shape fits this app}}
- **Runner(s):** {{unit/integration runner + E2E tool, from the blueprint's stack}}
- **Test data / fixtures:** {{test DB, seed data, provider sandbox/test mode}}

## 2. Prioritized Coverage

> In priority order. Map each to a real flow, not a file.

| # | Area | What it verifies | Level | Priority |
|---|------|------------------|-------|----------|
| 1 | Auth + authz | {{unauth blocked; cross-user access denied; wrong role denied; RLS if used}} | integration | critical |
| 2 | Money path | {{server-side amounts; webhook signature; idempotency (no double-charge on replay); failure/refund}} | integration | critical |
| 3 | Core loop | {{the primary journey the product exists for}} | integration / E2E | critical |
| 4 | Data integrity | {{uniqueness, required relations, computed/denormalized fields}} | integration | high |
| 5 | Non-trivial logic | {{date/time, parsing, aggregation, pricing, state machines}} | unit | high |
| {{n}} | {{...}} | {{...}} | {{...}} | {{...}} |

## 3. Deliberately Not Tested (and why)

{{Trivial CRUD, framework behavior, and anything that can't be meaningfully tested in the MVP — e.g. a third-party sandbox that isn't available. Be honest; note what a real test would need.}}

## 4. How to Run

```
{{install/setup}}
{{run command — e.g. npm test / pytest}}
{{E2E command, if separate}}
```

Environment / prerequisites: {{test DB URL, provider test keys, etc.}}

## 5. Plug into Review

code-reviewer (Phase 6) runs this suite as part of verification. A failing critical test blocks the build. {{Note anything the reviewer must set up to run it.}}
