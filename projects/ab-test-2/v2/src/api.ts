import { createServer } from 'node:http';
import type { IncomingMessage, Server, ServerResponse } from 'node:http';
import type { DatabaseSync } from 'node:sqlite';
import {
  LIMITS,
  optBool,
  optId,
  optString,
  queryEnum,
  queryId,
  readJsonBody,
  reqEnum,
  reqId,
  reqString,
  reqText,
  sendJson,
} from './http.ts';
import * as svc from './service.ts';
import { BadRequest, NotFound } from './service.ts';
import { hasApiKey, selectProvider } from './providers/index.ts';
import type { Provider } from './providers/index.ts';
import { MIN_N_FOR_VERDICT } from './metrics.ts';

const SCOPES = ['all', 'bench', 'live'] as const;
const VERDICTS = ['good', 'bad'] as const;

export type ApiDeps = {
  db: DatabaseSync;
  provider: Provider;
  /** Reported by /api/health so the UI can say which drafter is live. */
  liveKey: boolean;
};

type Handler = (
  ctx: ApiDeps,
  req: IncomingMessage,
  url: URL,
  params: string[],
) => Promise<unknown> | unknown;

/** `status` overrides the default (201 for POST, 200 otherwise) where 201 would lie. */
type Route = { method: string; pattern: RegExp; handler: Handler; status?: number };

const routes: Route[] = [
  // ---- health -------------------------------------------------------------------------
  {
    method: 'GET',
    pattern: /^\/api\/health$/,
    handler: (ctx) => ({
      ok: true,
      // A boolean, never the key itself.
      live_api_key: ctx.liveKey,
      provider: ctx.provider.name,
      model: ctx.provider.model,
      min_n_for_verdict: MIN_N_FOR_VERDICT,
    }),
  },

  // ---- prompt versions ----------------------------------------------------------------
  { method: 'GET', pattern: /^\/api\/prompts$/, handler: (ctx) => svc.listPrompts(ctx.db) },
  {
    method: 'POST',
    pattern: /^\/api\/prompts$/,
    handler: async (ctx, req) => {
      const body = await readJsonBody(req);
      return svc.createPrompt(ctx.db, {
        label: reqString(body, 'label', LIMITS.label),
        system_prompt: reqString(body, 'system_prompt', LIMITS.systemPrompt),
        activate: body.activate === undefined ? true : optBool(body, 'activate'),
      });
    },
  },
  {
    method: 'POST',
    pattern: /^\/api\/prompts\/(\d+)\/activate$/,
    status: 200,
    handler: (ctx, _req, _url, p) => {
      const updated = svc.activatePrompt(ctx.db, Number(p[0]));
      if (!updated) throw new NotFound('prompt version not found');
      return updated;
    },
  },

  // ---- enquiries ----------------------------------------------------------------------
  { method: 'GET', pattern: /^\/api\/enquiries$/, handler: (ctx) => svc.listEnquiries(ctx.db) },
  {
    method: 'POST',
    pattern: /^\/api\/enquiries$/,
    handler: async (ctx, req) => {
      const body = await readJsonBody(req);
      return svc.createEnquiry(ctx.db, {
        subject: reqString(body, 'subject', LIMITS.subject),
        body: reqString(body, 'body', LIMITS.body),
        sender: optString(body, 'sender', LIMITS.sender),
        in_bench: optBool(body, 'in_bench'),
      });
    },
  },
  {
    method: 'GET',
    pattern: /^\/api\/enquiries\/(\d+)$/,
    handler: (ctx, _req, _url, p) => {
      const id = Number(p[0]);
      const enquiry = svc.getEnquiry(ctx.db, id);
      if (!enquiry) throw new NotFound('enquiry not found');
      return { enquiry, drafts: svc.listDrafts(ctx.db, id) };
    },
  },
  {
    method: 'POST',
    pattern: /^\/api\/enquiries\/(\d+)\/bench$/,
    status: 200,
    handler: async (ctx, req, _url, p) => {
      const body = await readJsonBody(req);
      if (typeof body.in_bench !== 'boolean') throw new BadRequest('in_bench must be a boolean');
      const updated = svc.setBenchMembership(ctx.db, Number(p[0]), body.in_bench);
      if (!updated) throw new NotFound('enquiry not found');
      return updated;
    },
  },

  // ---- drafting -----------------------------------------------------------------------
  {
    method: 'POST',
    pattern: /^\/api\/drafts$/,
    handler: async (ctx, req) => {
      const body = await readJsonBody(req);
      return svc.generateDraft(ctx.db, ctx.provider, {
        enquiryId: reqId(body, 'enquiry_id'),
        promptVersionId: optId(body, 'prompt_version_id'),
      });
    },
  },

  // ---- reviews ------------------------------------------------------------------------
  {
    method: 'POST',
    pattern: /^\/api\/reviews$/,
    status: 200,
    handler: async (ctx, req) => {
      const body = await readJsonBody(req);
      return svc.saveReview(ctx.db, {
        draftId: reqId(body, 'draft_id'),
        verdict: reqEnum(body, 'verdict', VERDICTS),
        finalText: reqText(body, 'final_text', LIMITS.finalText),
        note: optString(body, 'note', LIMITS.note),
      });
    },
  },

  // ---- measurement --------------------------------------------------------------------
  {
    method: 'GET',
    pattern: /^\/api\/scoreboard$/,
    handler: (ctx, _req, url) => ({
      scope: queryEnum(url.searchParams, 'scope', SCOPES, 'all'),
      min_n_for_verdict: MIN_N_FOR_VERDICT,
      versions: svc.scoreboard(ctx.db, queryEnum(url.searchParams, 'scope', SCOPES, 'all')),
    }),
  },
  {
    method: 'GET',
    pattern: /^\/api\/compare$/,
    handler: (ctx, _req, url) => {
      const a = queryId(url.searchParams, 'a');
      const b = queryId(url.searchParams, 'b');
      if (a === null || b === null) throw new BadRequest('a and b must be prompt version ids');
      if (!svc.getPrompt(ctx.db, a) || !svc.getPrompt(ctx.db, b)) {
        throw new NotFound('prompt version not found');
      }
      const scope = queryEnum(url.searchParams, 'scope', SCOPES, 'all');
      return { a, b, scope, ...svc.comparison(ctx.db, a, b, scope) };
    },
  },

  // ---- bench --------------------------------------------------------------------------
  { method: 'GET', pattern: /^\/api\/bench\/runs$/, handler: (ctx) => svc.listBenchRuns(ctx.db) },
  {
    method: 'GET',
    pattern: /^\/api\/bench\/runs\/(\d+)$/,
    handler: (ctx, _req, _url, p) => svc.benchRunDrafts(ctx.db, Number(p[0])),
  },
  {
    method: 'POST',
    pattern: /^\/api\/bench\/run$/,
    handler: async (ctx, req) => {
      const body = await readJsonBody(req);
      return svc.runBench(ctx.db, ctx.provider, reqId(body, 'prompt_version_id'));
    },
  },
];

/**
 * Reject cross-origin and non-local Host requests.
 *
 * There is no login on a 127.0.0.1 tool and adding one would be theatre, but that leaves
 * two real holes: any page in the browser can POST to localhost, and DNS rebinding can
 * point an attacker-controlled hostname at the loopback address. Checking Origin closes
 * the first and checking Host closes the second. Requests with no Origin (curl, the
 * same-origin proxy) are allowed through.
 */
export function isLocalRequest(req: IncomingMessage): boolean {
  const host = req.headers.host ?? '';
  const hostname = host.replace(/:\d+$/, '').toLowerCase();
  if (hostname !== '127.0.0.1' && hostname !== 'localhost' && hostname !== '[::1]') return false;

  const origin = req.headers.origin;
  if (origin === undefined) return true;
  try {
    const h = new URL(origin).hostname.toLowerCase();
    return h === '127.0.0.1' || h === 'localhost' || h === '::1';
  } catch {
    return false;
  }
}

export function createApiHandler(deps: ApiDeps) {
  return async function handle(req: IncomingMessage, res: ServerResponse): Promise<void> {
    try {
      if (!isLocalRequest(req)) {
        sendJson(res, 403, { error: 'this API only serves local requests' });
        return;
      }

      const url = new URL(req.url ?? '/', 'http://127.0.0.1');
      const route = routes.find(
        (r) => r.method === req.method && r.pattern.test(url.pathname),
      );

      if (!route) {
        const pathExists = routes.some((r) => r.pattern.test(url.pathname));
        sendJson(res, pathExists ? 405 : 404, {
          error: pathExists ? 'method not allowed' : 'not found',
        });
        return;
      }

      const params = (url.pathname.match(route.pattern) ?? []).slice(1);
      const result = await route.handler(deps, req, url, params);
      sendJson(res, route.status ?? (req.method === 'POST' ? 201 : 200), result);
    } catch (err) {
      if (err instanceof BadRequest) return sendJson(res, 400, { error: err.message });
      if (err instanceof NotFound) return sendJson(res, 404, { error: err.message });

      // Anything else is either a drafting failure or a genuine bug. Drafting failures
      // carry a message we constructed (never containing the key), so surfacing it helps.
      // A stack trace never leaves the process.
      const message = err instanceof Error ? err.message : 'unknown error';
      console.error('[api]', err);
      sendJson(res, 502, { error: message });
    }
  };
}

export function createApiServer(deps: ApiDeps): Server {
  return createServer(createApiHandler(deps));
}

export function defaultDeps(db: DatabaseSync): ApiDeps {
  return { db, provider: selectProvider(), liveKey: hasApiKey() };
}
