# Architecture Document Template

> Used by **senior-architect** in Phase 1. Fill sections applicable to the complexity tier; delete placeholders that don't apply.
>
> The tech stack comes from `.builder/blueprint.md`. Do NOT introduce defaults here. Every stack row's rationale should trace to the blueprint's reasoning.

---

```yaml
---
project: {{PROJECT_NAME}}
complexity: {{simple|standard|complex}}
tech_stack:              # copied from blueprint.md, not chosen here
  frontend: {{from blueprint}}
  backend: {{from blueprint}}
  database: {{from blueprint}}
  auth: {{from blueprint}}
  hosting: {{from blueprint}}
created: {{ISO_TIMESTAMP}}
source_blueprint: .builder/blueprint.md
---
```

## 1. Overview

{{1-3 sentences: what this application does and who it's for. Pull from the blueprint's problem statement.}}

## 2. Complexity Assessment

| Dimension | Score (1-5) | Rationale |
|-----------|-------------|-----------|
| Data | {{score}} | {{why}} |
| Auth | {{score}} | {{why}} |
| UI | {{score}} | {{why}} |
| Integrations | {{score}} | {{why}} |
| Scale | {{score}} | {{why}} |
| **Total** | **{{sum}}** | **Tier: {{simple/standard/complex}}** |

### Scoring guide
- **Simple (5-8):** landing page, single-resource CRUD, portfolio.
- **Standard (9-14):** blog/e-commerce MVP, dashboard, multi-resource app.
- **Complex (15-25):** SaaS, multi-tenant, real-time, marketplace.

## 3. Tech Stack (from the blueprint)

| Layer | Choice | Rationale (traces to blueprint) |
|-------|--------|---------------------------------|
| Frontend / rendering | {{from blueprint}} | {{blueprint's reason}} |
| UI | {{from blueprint}} | {{reason}} |
| Backend | {{from blueprint}} | {{reason}} |
| API style | {{from blueprint}} | {{reason}} |
| Database | {{from blueprint}} | {{reason}} |
| Data access / ORM | {{from blueprint}} | {{reason}} |
| Auth | {{from blueprint}} | {{reason}} |
| Payments / integrations | {{from blueprint}} | {{reason}} |
| Background jobs | {{from blueprint, if any}} | {{reason}} |
| Hosting | {{from blueprint}} | {{reason}} |

> If a needed layer is missing from the blueprint, go back to `developer-advisor` for it. Do NOT fill it with a default.

## 4. Project Structure

```
{{project-name}}/
├── .builder/                # pipeline artifacts
├── {{structure per the chosen framework — never assumed}}
└── {{config, env.example, etc.}}
```

## 5. Database Schema

> Standard and Complex tiers. Omit for Simple with no persistence.

### Tables

#### {{table_name}}

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | {{type}} | PK | {{description}} |
| {{col}} | {{type}} | {{constraints}} | {{description}} |

### Relationships
{{Foreign keys and relationships in prose or a small diagram.}}

### Access control
{{If the blueprint uses row-level security / role-based access, specify the policy per table here. This is the security backbone for multi-role apps.}}

### Schema reference
```
{{Schema pseudocode in the blueprint's ORM/migration format — senior-backend implements from this.}}
```

## 6. API Contract

> The critical handshake between frontend and backend. Both build against it independently.

### {{Resource / feature group}}

| Method | Path | Request Body | Response | Auth |
|--------|------|-------------|----------|------|
| GET | /{{...}} | — | `{ ... }` | {{Yes/No}} |
| POST | /{{...}} | `{ ... }` | `{ ... }` | {{Yes/No}} |

{{Repeat per resource. Include the auth/session endpoints and any webhook endpoints.}}

### Error response shape
```json
{ "error": "Human-readable message", "code": "MACHINE_CODE", "details": {} }
```

### Status codes
| Code | Usage |
|------|-------|
| 200 | Success | 
| 201 | Created |
| 400 | Validation error |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not found |
| 500 | Server error |

## 7. Frontend Breakdown

### Pages / routes
| Route | Component | Purpose |
|-------|-----------|---------|
| {{path}} | {{Component}} | {{description}} |

### Component hierarchy
```
{{tree}}
```

### State management
{{Server state + client state approach, per the blueprint's stack. Scale to tier.}}

### Design system reference
{{Point to .builder/design-system.md — tokens, components, and treatments the frontend must implement.}}

### Key libraries
| Library | Purpose |
|---------|---------|
| {{lib}} | {{purpose}} |

## 8. Backend Breakdown

### Endpoint groups
{{Group endpoints by feature; note the non-CRUD business logic in each.}}

### Middleware / request pipeline
| Order | Layer | Purpose |
|-------|-------|---------|
| 1 | {{...}} | {{...}} |

### Business logic modules
| Module | Responsibility |
|--------|---------------|
| {{module}} | {{what it does}} |

## 9. Environment Variables

| Variable | Description | Example | Required |
|----------|-------------|---------|----------|
| {{VAR}} | {{description}} | {{example}} | {{Yes/No}} |

## 10. Implementation Order

> Standard and Complex tiers. Sequence so a demoable slice lands early.

1. {{scaffold + schema}}
2. {{core API}}
3. {{...}}

## 11. Scaling Considerations

> Complex tier only. Indexing, caching, rate limiting, connection pooling, background jobs, CDN, horizontal scaling — only those the blueprint's scale actually warrants.
