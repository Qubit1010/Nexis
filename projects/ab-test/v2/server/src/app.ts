import Fastify from 'fastify';
import type { FastifyError, FastifyInstance, FastifyReply } from 'fastify';
import cookie from '@fastify/cookie';
import rateLimit from '@fastify/rate-limit';
import { z } from 'zod';

import { config } from './config.ts';
import { openDb, getRules, getThresholds, setSetting } from './db.ts';
import { clearSession, isAuthed, issueSession, passwordMatches, requireAuth } from './auth.ts';
import {
  BUDGET_OPTIONS, FIELD_LABELS, FIELD_OPS, NEED_OPTIONS, OP_LABELS,
  RULE_FIELDS, RULE_OPS, STATUSES, TIMELINE_OPTIONS,
} from './catalog.ts';
import {
  fieldErrors, leadQuery, leadSubmission, leadUpdate, login, ruleCreate, ruleUpdate, settingsUpdate,
} from './schemas.ts';
import {
  deleteLead, getLead, insertLead, listLeads, rescoreAll, stats, updateLead,
} from './repo.ts';

export type AppOptions = { dbPath?: string; logger?: boolean; adminPassword?: string };

/** Returns 400 with per-field messages the form can render inline, never a raw zod dump. */
function parse<T extends z.ZodType>(schema: T, data: unknown, reply: FastifyReply): z.infer<T> | undefined {
  const result = schema.safeParse(data);
  if (result.success) return result.data;
  reply.code(400).send({ error: 'Validation failed', fields: fieldErrors(result.error) });
  return undefined;
}

const idParam = z.object({ id: z.coerce.number().int().positive() });

export async function buildApp(opts: AppOptions = {}): Promise<FastifyInstance> {
  const db = openDb(opts.dbPath ?? config.dbPath);
  const adminPassword = opts.adminPassword ?? config.adminPassword;
  const app = Fastify({
    logger: opts.logger ?? (config.isTest ? false : { level: 'info' }),
    bodyLimit: 128 * 1024,
    trustProxy: config.trustProxy,
  });

  await app.register(cookie, { secret: config.sessionSecret });
  await app.register(rateLimit, { global: false, max: 300, timeWindow: '1 minute' });

  app.addHook('onClose', async () => { db.close(); });

  app.setErrorHandler((err: FastifyError, req, reply) => {
    const status = err.statusCode ?? 500;
    if (status < 500) return reply.code(status).send({ error: err.message });
    req.log.error({ err }, 'unhandled error');
    // Never leak a stack trace or a driver message to the client.
    return reply.code(500).send({ error: 'Something went wrong' });
  });

  // ---------------------------------------------------------------- public

  app.get('/api/health', async () => ({ ok: true }));

  /** The form renders itself from this, so its options can never drift from the rules. */
  app.get('/api/form-config', async () => ({
    budget: BUDGET_OPTIONS,
    timeline: TIMELINE_OPTIONS,
    needs: NEED_OPTIONS,
  }));

  app.post('/api/leads', {
    config: { rateLimit: { max: 10, timeWindow: '1 minute' } },
  }, async (req, reply) => {
    const body = parse(leadSubmission, req.body, reply);
    if (!body) return;
    // Honeypot: accept and discard, so a bot cannot tell it was caught.
    if (body.website) return reply.code(201).send({ ok: true, id: null });
    const lead = insertLead(db, body);
    // The score is deliberately never returned to the public form.
    return reply.code(201).send({ ok: true, id: lead.id });
  });

  // ---------------------------------------------------------------- auth

  app.post('/api/auth/login', {
    config: { rateLimit: { max: 8, timeWindow: '5 minutes' } },
  }, async (req, reply) => {
    const body = parse(login, req.body, reply);
    if (!body) return;
    if (!passwordMatches(body.password, adminPassword)) {
      return reply.code(401).send({ error: 'Incorrect password' });
    }
    issueSession(reply);
    return { ok: true };
  });

  app.post('/api/auth/logout', async (_req, reply) => {
    clearSession(reply);
    return { ok: true };
  });

  app.get('/api/auth/me', async (req) => ({ authed: isAuthed(req) }));

  // ---------------------------------------------------------------- admin

  await app.register(async (admin) => {
    admin.addHook('onRequest', requireAuth);

    admin.get('/api/leads', async (req, reply) => {
      const q = parse(leadQuery, req.query, reply);
      if (!q) return;
      return { leads: listLeads(db, q), stats: stats(db) };
    });

    admin.get('/api/leads/:id', async (req, reply) => {
      const p = parse(idParam, req.params, reply);
      if (!p) return;
      const lead = getLead(db, p.id);
      if (!lead) return reply.code(404).send({ error: 'Lead not found' });
      return { lead };
    });

    admin.patch('/api/leads/:id', async (req, reply) => {
      const p = parse(idParam, req.params, reply);
      if (!p) return;
      const body = parse(leadUpdate, req.body, reply);
      if (!body) return;
      const lead = updateLead(db, p.id, body);
      if (!lead) return reply.code(404).send({ error: 'Lead not found' });
      return { lead };
    });

    admin.delete('/api/leads/:id', async (req, reply) => {
      const p = parse(idParam, req.params, reply);
      if (!p) return;
      if (!deleteLead(db, p.id)) return reply.code(404).send({ error: 'Lead not found' });
      return { ok: true };
    });

    admin.get('/api/rules', async () => ({
      rules: getRules(db),
      settings: getThresholds(db),
      meta: {
        fields: RULE_FIELDS, ops: RULE_OPS, fieldOps: FIELD_OPS,
        fieldLabels: FIELD_LABELS, opLabels: OP_LABELS,
        budget: BUDGET_OPTIONS, timeline: TIMELINE_OPTIONS, needs: NEED_OPTIONS,
        statuses: STATUSES,
      },
    }));

    admin.post('/api/rules', async (req, reply) => {
      const body = parse(ruleCreate, req.body, reply);
      if (!body) return;
      const info = db
        .prepare('INSERT INTO rules (label, field, op, value, points, enabled, sort) VALUES (?, ?, ?, ?, ?, ?, ?)')
        .run(body.label, body.field, body.op, body.value, body.points, body.enabled ? 1 : 0, body.sort);
      const rule = getRules(db).find((r) => r.id === Number(info.lastInsertRowid));
      return reply.code(201).send({ rule });
    });

    admin.patch('/api/rules/:id', async (req, reply) => {
      const p = parse(idParam, req.params, reply);
      if (!p) return;
      const body = parse(ruleUpdate, req.body, reply);
      if (!body) return;

      const existing = getRules(db).find((r) => r.id === p.id);
      if (!existing) return reply.code(404).send({ error: 'Rule not found' });

      // Validate the MERGED rule, so a partial patch cannot smuggle in an illegal field/op pair.
      const merged = { ...existing, ...body };
      const check = ruleCreate.safeParse(merged);
      if (!check.success) {
        return reply.code(400).send({ error: 'Validation failed', fields: fieldErrors(check.error) });
      }

      db.prepare(
        'UPDATE rules SET label = ?, field = ?, op = ?, value = ?, points = ?, enabled = ?, sort = ? WHERE id = ?',
      ).run(
        merged.label, merged.field, merged.op, merged.value,
        merged.points, merged.enabled ? 1 : 0, merged.sort, p.id,
      );
      return { rule: getRules(db).find((r) => r.id === p.id) };
    });

    admin.delete('/api/rules/:id', async (req, reply) => {
      const p = parse(idParam, req.params, reply);
      if (!p) return;
      const changes = db.prepare('DELETE FROM rules WHERE id = ?').run(p.id).changes;
      if (!changes) return reply.code(404).send({ error: 'Rule not found' });
      return { ok: true };
    });

    admin.patch('/api/settings', async (req, reply) => {
      const body = parse(settingsUpdate, req.body, reply);
      if (!body) return;
      const next = { ...getThresholds(db), ...body };
      if (next.hot_min <= next.warm_min) {
        return reply.code(400).send({
          error: 'Validation failed',
          fields: { hot_min: 'The hot threshold must be above the warm threshold' },
        });
      }
      setSetting(db, 'hot_min', String(next.hot_min));
      setSetting(db, 'warm_min', String(next.warm_min));
      return { settings: getThresholds(db) };
    });

    admin.post('/api/rescore', async () => rescoreAll(db));

    admin.get('/api/stats', async () => stats(db));
  });

  return app;
}
