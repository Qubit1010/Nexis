import { Router } from 'express';
import type { Request, Response } from 'express';

import type { Db } from './db.ts';
import {
  activatePromptVersion,
  createEnquiry,
  createPromptVersion,
  getDraft,
  getEnquiry,
  listDraftsForEnquiry,
  listEnquiries,
  listPromptVersions,
  updateDraft,
} from './db.ts';
import { draftReply } from './drafter.ts';
import { AppError, notFound } from './errors.ts';
import { PRICING } from './pricing.ts';
import type { DraftProvider } from './providers.ts';
import { buildScoreboard } from './scoreboard.ts';
import { createEnquirySchema, createPromptSchema, idParamSchema, updateDraftSchema } from './schemas.ts';
import { measureEdit } from './text.ts';

export type RouteContext = {
  db: Db;
  provider: DraftProvider;
  hasApiKey: boolean;
};

/** Every id that reaches a query goes through here first. */
function parseId(raw: unknown, what: string): number {
  const parsed = idParamSchema.safeParse(raw);
  if (!parsed.success) throw new AppError('validation_error', `Invalid ${what} id`, 400);
  return parsed.data;
}

function parseBody<T>(schema: { safeParse(input: unknown): { success: boolean; data?: T; error?: unknown } }, body: unknown): T {
  const result = schema.safeParse(body);
  if (!result.success || result.data === undefined) {
    const issues =
      result.error && typeof result.error === 'object' && 'issues' in result.error
        ? (result.error as { issues: unknown }).issues
        : undefined;
    throw new AppError('validation_error', 'Request body failed validation', 400, issues);
  }
  return result.data;
}

export function createRoutes(ctx: RouteContext): Router {
  const router = Router();

  router.get('/health', (_req: Request, res: Response) => {
    res.json({
      ok: true,
      provider: ctx.provider.name,
      model: ctx.provider.model,
      hasApiKey: ctx.hasApiKey,
      pricing: {
        inputPerMTok: PRICING.inputPerMTok,
        outputPerMTok: PRICING.outputPerMTok,
        source: PRICING.source,
      },
    });
  });

  // ---- enquiries ----------------------------------------------------------------

  router.get('/enquiries', (_req: Request, res: Response) => {
    res.json(listEnquiries(ctx.db));
  });

  router.post('/enquiries', (req: Request, res: Response) => {
    const input = parseBody(createEnquirySchema, req.body);
    res.status(201).json(createEnquiry(ctx.db, input.subject, input.body));
  });

  router.get('/enquiries/:id', (req: Request, res: Response) => {
    const id = parseId(req.params.id, 'enquiry');
    const enquiry = getEnquiry(ctx.db, id);
    if (!enquiry) throw notFound('Enquiry');
    res.json({ enquiry, drafts: listDraftsForEnquiry(ctx.db, id) });
  });

  // ---- drafts -------------------------------------------------------------------

  router.post('/enquiries/:id/drafts', async (req: Request, res: Response) => {
    const id = parseId(req.params.id, 'enquiry');
    const draft = await draftReply(ctx.db, ctx.provider, id);
    res.status(201).json(draft);
  });

  router.patch('/drafts/:id', (req: Request, res: Response) => {
    const id = parseId(req.params.id, 'draft');
    const input = parseBody(updateDraftSchema, req.body);

    const existing = getDraft(ctx.db, id);
    if (!existing) throw notFound('Draft');

    const update: Parameters<typeof updateDraft>[2] = {};

    if (input.editedText !== undefined) {
      // Measured against the generated text, never against a previous edit, so the number
      // always means "distance from what the model produced".
      const measure = measureEdit(existing.generatedText, input.editedText);
      update.editedText = input.editedText;
      update.editDistance = measure.distance;
      update.editBaseWords = measure.baseWords;
    }
    if (input.rating !== undefined) update.rating = input.rating;

    const updated = updateDraft(ctx.db, id, update);
    if (!updated) throw notFound('Draft');
    res.json(updated);
  });

  // ---- prompt versions ----------------------------------------------------------

  router.get('/prompts', (_req: Request, res: Response) => {
    res.json(listPromptVersions(ctx.db));
  });

  router.post('/prompts', (req: Request, res: Response) => {
    const input = parseBody(createPromptSchema, req.body);
    res.status(201).json(createPromptVersion(ctx.db, input.systemPrompt, input.label));
  });

  router.post('/prompts/:id/activate', (req: Request, res: Response) => {
    const id = parseId(req.params.id, 'prompt version');
    const activated = activatePromptVersion(ctx.db, id);
    if (!activated) throw notFound('Prompt version');
    res.json(activated);
  });

  // ---- measurement --------------------------------------------------------------

  router.get('/stats', (_req: Request, res: Response) => {
    res.json(buildScoreboard(ctx.db));
  });

  return router;
}
