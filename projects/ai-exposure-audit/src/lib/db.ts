import Database from "better-sqlite3";
import fs from "node:fs";
import path from "node:path";
import { randomUUID } from "node:crypto";
import {
  DIMENSION_IDS,
  type Audit,
  type Business,
  type DimensionId,
  type DimensionScore,
  type PricingModel,
  type Provenance,
  type ScoreValue,
  type ServiceLine,
  type Weights,
} from "./types";

/**
 * Local SQLite. Chosen over a hosted Postgres so a live client call never depends
 * on a network round-trip, and so client revenue figures stay on this machine.
 *
 * Everything that touches SQL lives in this file. Swapping to Postgres means
 * rewriting this module and nothing else.
 *
 * The database file sits in data/, which is gitignored. Nexis is a public repo and
 * this file holds real revenue splits.
 */

const DATA_DIR = path.join(process.cwd(), "data");
const DB_PATH = process.env.AUDIT_DB_PATH ?? path.join(DATA_DIR, "audits.db");

let _db: Database.Database | null = null;

export function getDb(): Database.Database {
  if (_db) return _db;

  const dir = path.dirname(DB_PATH);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  const db = new Database(DB_PATH);
  db.pragma("journal_mode = WAL");
  db.pragma("foreign_keys = ON");
  migrate(db);
  _db = db;
  return db;
}

function migrate(db: Database.Database): void {
  db.exec(`
    CREATE TABLE IF NOT EXISTS audits (
      id                TEXT PRIMARY KEY,
      business_name     TEXT NOT NULL,
      headcount         INTEGER,
      avg_project_value REAL,
      positioning       TEXT NOT NULL DEFAULT '',
      weights_json      TEXT NOT NULL,
      rubric_version    TEXT NOT NULL,
      pricebook_version TEXT NOT NULL,
      created_at        TEXT NOT NULL,
      updated_at        TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS service_lines (
      id                      TEXT PRIMARY KEY,
      audit_id                TEXT NOT NULL REFERENCES audits(id) ON DELETE CASCADE,
      name                    TEXT NOT NULL,
      revenue_share_pct       REAL NOT NULL,
      deliverable_description TEXT NOT NULL DEFAULT '',
      pricing_model           TEXT NOT NULL,
      typical_price           REAL,
      replacement_json        TEXT,
      sort_order              INTEGER NOT NULL DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS scores (
      id         TEXT PRIMARY KEY,
      line_id    TEXT NOT NULL REFERENCES service_lines(id) ON DELETE CASCADE,
      dimension  TEXT NOT NULL,
      value      INTEGER NOT NULL,
      reasoning  TEXT NOT NULL DEFAULT '',
      provenance TEXT NOT NULL,
      UNIQUE (line_id, dimension)
    );

    CREATE INDEX IF NOT EXISTS idx_lines_audit ON service_lines(audit_id);
    CREATE INDEX IF NOT EXISTS idx_scores_line ON scores(line_id);
  `);
}

/* ---------- validation ---------- */

const PRICING_MODELS: PricingModel[] = ["hourly", "fixed", "retainer", "outcome"];
const PROVENANCES: Provenance[] = ["llm", "llm-adjusted", "manual"];

export class ValidationError extends Error {}

function str(v: unknown, field: string, max = 2000): string {
  if (typeof v !== "string") throw new ValidationError(`${field} must be a string`);
  const t = v.trim();
  if (t.length > max) throw new ValidationError(`${field} exceeds ${max} characters`);
  return t;
}

function optNum(v: unknown, field: string): number | null {
  if (v === null || v === undefined || v === "") return null;
  const n = Number(v);
  if (!Number.isFinite(n)) throw new ValidationError(`${field} must be a number`);
  return n;
}

function pct(v: unknown, field: string): number {
  const n = Number(v);
  if (!Number.isFinite(n) || n < 0 || n > 100) {
    throw new ValidationError(`${field} must be between 0 and 100`);
  }
  return n;
}

export function validateWeights(v: unknown): Weights {
  if (typeof v !== "object" || v === null) throw new ValidationError("weights must be an object");
  const raw = v as Record<string, unknown>;
  const out = {} as Weights;
  for (const d of DIMENSION_IDS) {
    const n = Number(raw[d]);
    if (!Number.isFinite(n) || n < 0) {
      throw new ValidationError(`weights.${d} must be a non-negative number`);
    }
    out[d] = n;
  }
  if (DIMENSION_IDS.reduce((s, d) => s + out[d], 0) <= 0) {
    throw new ValidationError("At least one weight must be greater than zero");
  }
  return out;
}

export function validateScoreValue(v: unknown, field: string): ScoreValue {
  const n = Number(v);
  if (!Number.isInteger(n) || n < 1 || n > 5) {
    throw new ValidationError(`${field} must be an integer from 1 to 5`);
  }
  return n as ScoreValue;
}

function validateLine(v: unknown, index: number): Omit<ServiceLine, "id"> & { id?: string } {
  if (typeof v !== "object" || v === null) {
    throw new ValidationError(`lines[${index}] must be an object`);
  }
  const raw = v as Record<string, unknown>;
  const pricingModel = str(raw.pricing_model ?? "fixed", `lines[${index}].pricing_model`, 20);
  if (!PRICING_MODELS.includes(pricingModel as PricingModel)) {
    throw new ValidationError(
      `lines[${index}].pricing_model must be one of ${PRICING_MODELS.join(", ")}`
    );
  }

  const scores: Partial<Record<DimensionId, DimensionScore>> = {};
  const rawScores = (raw.scores ?? {}) as Record<string, unknown>;
  for (const d of DIMENSION_IDS) {
    const s = rawScores[d];
    if (!s) continue;
    if (typeof s !== "object") throw new ValidationError(`lines[${index}].scores.${d} must be an object`);
    const sr = s as Record<string, unknown>;
    const provenance = str(sr.provenance ?? "manual", `lines[${index}].scores.${d}.provenance`, 20);
    if (!PROVENANCES.includes(provenance as Provenance)) {
      throw new ValidationError(
        `lines[${index}].scores.${d}.provenance must be one of ${PROVENANCES.join(", ")}`
      );
    }
    scores[d] = {
      value: validateScoreValue(sr.value, `lines[${index}].scores.${d}.value`),
      reasoning: str(sr.reasoning ?? "", `lines[${index}].scores.${d}.reasoning`, 4000),
      provenance: provenance as Provenance,
    };
  }

  let replacement: ServiceLine["replacement"] = null;
  if (raw.replacement && typeof raw.replacement === "object") {
    const rr = raw.replacement as Record<string, unknown>;
    if (rr.archetype_id) {
      replacement = {
        archetype_id: str(rr.archetype_id, `lines[${index}].replacement.archetype_id`, 64),
        rationale: str(rr.rationale ?? "", `lines[${index}].replacement.rationale`, 4000),
      };
    }
  }

  return {
    id: typeof raw.id === "string" ? raw.id : undefined,
    name: str(raw.name, `lines[${index}].name`, 200),
    revenue_share_pct: pct(raw.revenue_share_pct, `lines[${index}].revenue_share_pct`),
    deliverable_description: str(
      raw.deliverable_description ?? "",
      `lines[${index}].deliverable_description`,
      4000
    ),
    pricing_model: pricingModel as PricingModel,
    typical_price: optNum(raw.typical_price, `lines[${index}].typical_price`),
    scores,
    replacement,
    sort_order: Number(raw.sort_order) || index,
  };
}

export interface AuditInput {
  business: Business;
  weights: Weights;
  rubric_version: string;
  pricebook_version: string;
  lines: (Omit<ServiceLine, "id"> & { id?: string })[];
}

export function validateAuditInput(body: unknown): AuditInput {
  if (typeof body !== "object" || body === null) throw new ValidationError("Body must be an object");
  const raw = body as Record<string, unknown>;
  const b = (raw.business ?? {}) as Record<string, unknown>;

  const name = str(b.name, "business.name", 200);
  if (!name) throw new ValidationError("business.name is required");

  const rawLines = Array.isArray(raw.lines) ? raw.lines : [];
  if (rawLines.length > 50) throw new ValidationError("An audit is capped at 50 service lines");

  return {
    business: {
      name,
      headcount: optNum(b.headcount, "business.headcount"),
      avg_project_value: optNum(b.avg_project_value, "business.avg_project_value"),
      positioning: str(b.positioning ?? "", "business.positioning", 4000),
    },
    weights: validateWeights(raw.weights),
    rubric_version: str(raw.rubric_version ?? "1.0.0", "rubric_version", 32),
    pricebook_version: str(raw.pricebook_version ?? "1.0.0", "pricebook_version", 32),
    lines: rawLines.map(validateLine),
  };
}

/* ---------- reads ---------- */

interface AuditRow {
  id: string;
  business_name: string;
  headcount: number | null;
  avg_project_value: number | null;
  positioning: string;
  weights_json: string;
  rubric_version: string;
  pricebook_version: string;
  created_at: string;
  updated_at: string;
}

interface LineRow {
  id: string;
  audit_id: string;
  name: string;
  revenue_share_pct: number;
  deliverable_description: string;
  pricing_model: string;
  typical_price: number | null;
  replacement_json: string | null;
  sort_order: number;
}

interface ScoreRow {
  line_id: string;
  dimension: string;
  value: number;
  reasoning: string;
  provenance: string;
}

export interface AuditSummary {
  id: string;
  business_name: string;
  line_count: number;
  created_at: string;
  updated_at: string;
}

export function listAudits(): AuditSummary[] {
  const db = getDb();
  return db
    .prepare(
      `SELECT a.id, a.business_name, a.created_at, a.updated_at,
              (SELECT COUNT(*) FROM service_lines l WHERE l.audit_id = a.id) AS line_count
         FROM audits a
        ORDER BY a.updated_at DESC`
    )
    .all() as AuditSummary[];
}

export function getAudit(id: string): Audit | null {
  const db = getDb();
  const row = db.prepare(`SELECT * FROM audits WHERE id = ?`).get(id) as AuditRow | undefined;
  if (!row) return null;

  const lineRows = db
    .prepare(`SELECT * FROM service_lines WHERE audit_id = ? ORDER BY sort_order, name`)
    .all(id) as LineRow[];

  const scoreRows =
    lineRows.length > 0
      ? (db
          .prepare(
            `SELECT s.* FROM scores s
               JOIN service_lines l ON l.id = s.line_id
              WHERE l.audit_id = ?`
          )
          .all(id) as ScoreRow[])
      : [];

  const scoresByLine = new Map<string, Partial<Record<DimensionId, DimensionScore>>>();
  for (const s of scoreRows) {
    if (!DIMENSION_IDS.includes(s.dimension as DimensionId)) continue;
    const bucket = scoresByLine.get(s.line_id) ?? {};
    bucket[s.dimension as DimensionId] = {
      value: s.value as ScoreValue,
      reasoning: s.reasoning,
      provenance: s.provenance as Provenance,
    };
    scoresByLine.set(s.line_id, bucket);
  }

  return {
    id: row.id,
    business: {
      name: row.business_name,
      headcount: row.headcount,
      avg_project_value: row.avg_project_value,
      positioning: row.positioning,
    },
    weights: JSON.parse(row.weights_json) as Weights,
    rubric_version: row.rubric_version,
    pricebook_version: row.pricebook_version,
    created_at: row.created_at,
    updated_at: row.updated_at,
    lines: lineRows.map((l) => ({
      id: l.id,
      name: l.name,
      revenue_share_pct: l.revenue_share_pct,
      deliverable_description: l.deliverable_description,
      pricing_model: l.pricing_model as PricingModel,
      typical_price: l.typical_price,
      scores: scoresByLine.get(l.id) ?? {},
      replacement: l.replacement_json ? JSON.parse(l.replacement_json) : null,
      sort_order: l.sort_order,
    })),
  };
}

/* ---------- writes ---------- */

/**
 * Replaces the whole audit in one transaction. The document is small (tens of rows)
 * and always edited as a whole, so a diffing update would add risk for no gain.
 */
export function saveAudit(id: string | null, input: AuditInput): Audit {
  const db = getDb();
  const now = new Date().toISOString();
  const auditId = id ?? randomUUID();

  const tx = db.transaction(() => {
    const existing = db.prepare(`SELECT id, created_at FROM audits WHERE id = ?`).get(auditId) as
      | { id: string; created_at: string }
      | undefined;

    if (existing) {
      db.prepare(
        `UPDATE audits SET business_name = ?, headcount = ?, avg_project_value = ?,
                positioning = ?, weights_json = ?, rubric_version = ?, pricebook_version = ?,
                updated_at = ?
          WHERE id = ?`
      ).run(
        input.business.name,
        input.business.headcount,
        input.business.avg_project_value,
        input.business.positioning,
        JSON.stringify(input.weights),
        input.rubric_version,
        input.pricebook_version,
        now,
        auditId
      );
      db.prepare(`DELETE FROM service_lines WHERE audit_id = ?`).run(auditId);
    } else {
      db.prepare(
        `INSERT INTO audits (id, business_name, headcount, avg_project_value, positioning,
                             weights_json, rubric_version, pricebook_version, created_at, updated_at)
         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
      ).run(
        auditId,
        input.business.name,
        input.business.headcount,
        input.business.avg_project_value,
        input.business.positioning,
        JSON.stringify(input.weights),
        input.rubric_version,
        input.pricebook_version,
        now,
        now
      );
    }

    const insLine = db.prepare(
      `INSERT INTO service_lines (id, audit_id, name, revenue_share_pct, deliverable_description,
                                  pricing_model, typical_price, replacement_json, sort_order)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
    );
    const insScore = db.prepare(
      `INSERT INTO scores (id, line_id, dimension, value, reasoning, provenance)
       VALUES (?, ?, ?, ?, ?, ?)`
    );

    input.lines.forEach((line, i) => {
      const lineId = line.id ?? randomUUID();
      insLine.run(
        lineId,
        auditId,
        line.name,
        line.revenue_share_pct,
        line.deliverable_description,
        line.pricing_model,
        line.typical_price,
        line.replacement ? JSON.stringify(line.replacement) : null,
        line.sort_order ?? i
      );
      for (const d of DIMENSION_IDS) {
        const s = line.scores[d];
        if (!s) continue;
        insScore.run(randomUUID(), lineId, d, s.value, s.reasoning, s.provenance);
      }
    });
  });

  tx();
  const saved = getAudit(auditId);
  if (!saved) throw new Error("Audit vanished immediately after saving");
  return saved;
}

export function deleteAudit(id: string): boolean {
  const db = getDb();
  return db.prepare(`DELETE FROM audits WHERE id = ?`).run(id).changes > 0;
}
