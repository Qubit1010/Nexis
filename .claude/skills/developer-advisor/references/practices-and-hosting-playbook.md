# Practices & Hosting Playbook (ship + deploy)

**Source basis:** `research-synthesis.md` Q8 (practices `[s175]`–`[s201]`) + Q9 (hosting `[s202]`–`[s226]`). Load for testing/CI/CD/security questions and the deployment section of a blueprint.

## Engineering practices

**Pillars:** planning, clean code, testing, CI/CD [s176]. Measure with **DORA**:
| Metric | Elite signal |
|---|---|
| Deployment frequency | On-demand / multiple/day |
| Lead time for changes | < 1 day |
| Change failure rate | < 5% [s182] |
| MTTR | < 1 hour |
| Reliability | Meets SLOs [s197] |
DORA's 2025 report reframed pipeline friction as a **talent-retention risk** [s183].

**Testing** [s185][s179]:
- Test pyramid (mostly unit, some integration, few E2E) [s185][s186], but not dogma — **testing trophy** for frontends/integration-heavy; pyramid for backends with deep logic [s179].
- **Risk-based testing over coverage-chasing** [s181]. Playwright/Cypress + POM + visual regression [s191].
- AI-assisted testing is real but **human-in-the-loop is non-negotiable** [s181][s178].

**CI/CD** [s177]: pipelines < 10 min, security scan every stage, Git-based automation baseline. **Shift-left** (defect caught early ~$10 vs ~$10K late) **+ shift-right** (feature flags + observability) as a continuous loop [s178][s180].

**Trunk-based dev** [s187][s189]: one branch, short-lived work, main always shippable; needs feature flags + fast CI + merge queue.

**Security** [s200]: everyone's job, shifted into daily work; high performers spend 50% less time remediating. Change approval = peer review + automation, not heavyweight gates [s201]. OWASP is the baseline [s176].

## Hosting

**Default: Vercel** for a Next.js SaaS — best DX, $20/seat covers early traffic [s203]. Then match workload:
| If… | Deploy | Why |
|---|---|---|
| Next.js SaaS, early | **Vercel** | DX; watch egress trap (Hobby capped, no commercial) [s205][s209] |
| High bandwidth / global edge / cost-sensitive | **Cloudflare** | 330+ PoPs, ~free bandwidth, 70–95% cheaper >1TB [s216][s217] |
| Full-stack + persistent state | Railway / Render | Long-running (weigh Railway reliability incidents) [s206] |
| VM control / global | Fly.io | Docker-first micro-VMs [s209] |
| Max flexibility, have DevOps | AWS | Everything, you run it [s205] |
| Escape platform pricing | Hetzner / Coolify / Kamal | Cents/month VPS [s208] |

**Serverless vs containers** [s210][s211]: event-driven/sporadic → serverless (scale-to-zero); sustained RPS / long-running / stateful → containers. Most systems use both (containers for API, serverless for queue consumer). AWS Lambda-vs-Fargate + CloudFront-vs-Lambda@Edge decision guides [s224][s225].

**2026 pricing warnings** [s218][s214]: credit-based pricing replacing flat-rate (Vercel Jan 2026, Netlify Sep 2025); $5/mo entry for always-on compute; normalize to one workload before comparing — pricing pages hide the real bill.

## Checklist for ship + deploy sections
- [ ] Testing model chosen (pyramid vs trophy) + risk-based.
- [ ] CI/CD baseline: < 10 min, security scanning, trunk-based.
- [ ] OWASP-relevant security items for *this* app.
- [ ] Hosting matched to workload + bandwidth profile; egress/pricing traps flagged.
- [ ] Serverless vs container decision per service.
