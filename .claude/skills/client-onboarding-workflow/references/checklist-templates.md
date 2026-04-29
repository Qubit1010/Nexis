# Project Checklist Templates

Reference for the project checklist Sheet generated per onboarding. Match the project type
to one of the templates below; adapt scope-specific tasks to the actual deliverables.

Each row in the Sheet has columns: `Stage | Task | Owner | Due | Status | Notes`.

- `Owner` defaults follow `context/team.md` defaults (see "Owner defaults" at bottom).
- `Due` is left blank by default unless the source proposal specified phase deadlines.
- `Status` always starts as "Not started".
- `Notes` is blank.

Pick the closest template to the project type and add 2-4 scope-specific rows under the
"Build" stage. Don't pad with generic tasks. The checklist should reflect what will
actually happen.

---

## Web Design & Development

| Stage | Task |
|---|---|
| Discovery | Kickoff call (60 min) |
| Discovery | Confirm scope, deliverables, timeline in writing |
| Discovery | Collect brand assets (logo, fonts, colors, copy) |
| Discovery | Collect access (domain, hosting, analytics, existing CMS) |
| Discovery | Confirm sitemap and page list |
| Design | Wireframes for all pages |
| Design | Hi-fi mockups (homepage + 1 inner page first) |
| Design | Client review round 1 |
| Design | Revisions and sign-off |
| Build | Frontend implementation |
| Build | Responsive QA across mobile, tablet, desktop |
| Build | CMS or content integration |
| Build | Forms, integrations, analytics wiring |
| QA | Cross-browser testing |
| QA | Performance pass (PageSpeed) |
| QA | Accessibility pass (alt text, contrast, focus states) |
| Launch | Final client review and sign-off |
| Launch | Domain pointing and SSL |
| Launch | Go-live |
| Post-launch | 7-day bug-fix window |
| Post-launch | Handoff doc + loom walkthrough |
| Post-launch | Invoice final payment |

## Full-Stack Web App

| Stage | Task |
|---|---|
| Discovery | Kickoff call |
| Discovery | Confirm scope and user stories |
| Discovery | Tech stack confirmation (frontend, backend, db, hosting) |
| Discovery | Access setup (repo, db, deployment, third-party APIs) |
| Architecture | Data model and schema |
| Architecture | API contract |
| Architecture | Auth and roles |
| Architecture | Architecture review with client |
| Build | Database setup and migrations |
| Build | Auth implementation |
| Build | Core feature 1 (replace with actual feature) |
| Build | Core feature 2 (replace with actual feature) |
| Build | Frontend integration |
| Test | Unit tests on critical paths |
| Test | Integration tests |
| Test | UAT round with client |
| Deploy | Staging deployment |
| Deploy | Production deployment |
| Deploy | Monitoring and error tracking setup |
| Post-launch | 14-day support window |
| Post-launch | Handoff doc + walkthrough |
| Post-launch | Invoice final payment |

## AI Automation & Workflows

| Stage | Task |
|---|---|
| Discovery | Kickoff call |
| Discovery | Map current workflow (input, steps, output, owners) |
| Discovery | Identify automation boundaries (what stays manual) |
| Discovery | Confirm tools and access (n8n / Make / API keys / Zapier) |
| Workflow Map | Diagram target workflow |
| Workflow Map | Define triggers, branches, edge cases |
| Workflow Map | Client review and sign-off on workflow map |
| Build | Build automation in chosen platform |
| Build | Wire integrations and credentials |
| Build | Add error handling and notifications |
| Build | Add logging |
| Test | Run dry tests with sample data |
| Test | Run live tests with low-volume real data |
| Test | Client UAT |
| Handoff | Deploy to client account |
| Handoff | Loom walkthrough of how the workflow runs |
| Handoff | Documentation of variables, credentials, retry logic |
| Handoff | 14-day monitoring window |
| Handoff | Invoice final payment |

## CMS Build (WordPress / Webflow / Shopify)

| Stage | Task |
|---|---|
| Discovery | Kickoff call |
| Discovery | Confirm template / theme starting point |
| Discovery | Collect content, brand assets, integrations needed |
| Discovery | Access setup (CMS admin, hosting, domain) |
| Design | Adapt theme to brand |
| Design | Mockup key pages |
| Design | Client review and sign-off |
| Build | Page templates |
| Build | Content population |
| Build | Plugins / apps configuration |
| Build | Forms, payments, integrations |
| QA | Cross-browser and responsive testing |
| QA | Speed and SEO basics |
| Launch | Client review and sign-off |
| Launch | Go-live |
| Post-launch | Training video for client team (Loom) |
| Post-launch | 7-day bug-fix window |
| Post-launch | Invoice final payment |

## Custom SaaS / MERN

Use the Full-Stack Web App template as the base. Add SaaS-specific rows under Build:
- Subscription / payment integration (Stripe)
- Multi-tenant data isolation
- Admin dashboard
- Email notifications

## Business / Data Analysis

| Stage | Task |
|---|---|
| Discovery | Kickoff call |
| Discovery | Define business question and success metric |
| Discovery | Data source inventory and access |
| Discovery | Confirm output format (dashboard, report, slide deck) |
| Build | Data extraction and cleaning |
| Build | Analysis |
| Build | Visualization / dashboard |
| Build | Insights and recommendations writeup |
| Review | Client walkthrough |
| Review | Revisions |
| Handoff | Final delivery |
| Handoff | Invoice final payment |

---

## Owner defaults

Drawn from `context/team.md`. Override with the actual person if known.

| Project type | Default lead |
|---|---|
| Web design & development | Areeba Noor (frontend), Sher Nadir (large UX) |
| Full-stack web app | Muzammil |
| AI automation & workflows | Muhammad Usman, Aleem |
| CMS — WordPress | Areeba Noor |
| CMS — Webflow | Hafeez |
| CMS — Shopify | Areeba Noor |
| Custom SaaS / MERN | Muzammil |
| Business / data analysis | Kaleem |
| 3D / Python automation | Ashhad |

`Aleem` is always the default owner for Discovery rows (kickoff calls, scope confirmation,
client communication) regardless of project type.

---

## Adapting per scope

When the proposal lists specific deliverables (e.g., "5-page website + booking system +
Mailchimp integration"), inject scope-specific rows in the Build stage. Drop generic rows
that don't apply (e.g., remove "Auth implementation" from a marketing site project).

The checklist is a working artifact, not a contract. Aleem will edit it.
