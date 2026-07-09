# Architecture Playbook

**Source basis:** `research-synthesis.md` Q1 (sources `[s1]`–`[s26]` in `_research/sources.json`). Load for architecture/system-design questions and the "recommended architecture" section of a blueprint.

## The default: modular monolith
Start here for almost everything under ~50 engineers. Clean domain boundaries inside one deployable → ~80% of microservices' organizational wins at ~20% of the running cost [s8]. Frameworks that support it: Spring Modulith, .NET Aspire, Go modules — or just disciplined module boundaries in a Next.js/Node app.

## The microservices gate (only split if YES to ≥1)
1. A component genuinely needs **independent scaling**.
2. **50+ engineers** need autonomous deployment.
3. **Domain boundaries are crystal clear** [s4][s7][s8].
If none: stay monolith. Microservices multiply observability/debugging cost by an order of magnitude [s1]. "Netflix does it" is a scale mismatch [s5].

## The right question
Not "should we go microservices?" but: *given team size, deployment cadence, data ownership, and failure tolerance, which style minimizes our next 18 months of cost?* [s9]

## Clean Architecture / DDD — apply proportionally
Maintenance is 60–80% of lifecycle cost, and architecture is the biggest driver [s12]. Separate business logic from technical detail (frameworks/DB/UI) so the expensive-to-change core stays stable [s11]. Small CRUD app → light layering. Long-lived domain-heavy system → full hexagonal/DDD is worth it [s11][s16].

## Serverless / event-driven
Workload choices, not defaults. Serverless removes ops burden for sporadic/event-driven shapes; event-driven decouples teams but hurts debugging without strong observability + ownership [s2]. (Economics in `practices-and-hosting-playbook.md`.)

## Decision checklist for a blueprint
- [ ] Named the pattern (default: modular monolith) and why it fits this scale/team.
- [ ] Stated the one future condition that would justify extracting a service.
- [ ] Sized the DDD/Clean-Architecture investment to the project's longevity.
- [ ] Chose sync (REST/tRPC) vs async (events/queues) boundaries deliberately.

**Canonical references:** Fowler's microservices corpus [s22][s23][s26]; the practical, non-FAANG system-design reference [s13].
