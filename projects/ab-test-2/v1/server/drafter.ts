import type { Db, Draft } from './db.ts';
import { getActivePromptVersion, getEnquiry, insertDraft } from './db.ts';
import { notFound } from './errors.ts';
import type { DraftProvider } from './providers.ts';

/**
 * Generate a draft for an enquiry using whichever prompt version is currently active, and
 * record which one that was. The attribution is the whole point: a rating on this draft is
 * only interpretable because this row remembers the prompt that produced it.
 */
export async function draftReply(
  db: Db,
  provider: DraftProvider,
  enquiryId: number,
): Promise<Draft> {
  const enquiry = getEnquiry(db, enquiryId);
  if (!enquiry) throw notFound('Enquiry');

  const promptVersion = getActivePromptVersion(db);

  const startedAt = Date.now();
  const result = await provider.draft({
    systemPrompt: promptVersion.systemPrompt,
    subject: enquiry.subject,
    body: enquiry.body,
  });
  const latencyMs = Date.now() - startedAt;

  return insertDraft(db, {
    enquiryId: enquiry.id,
    promptVersionId: promptVersion.id,
    provider: provider.name,
    model: provider.model,
    generatedText: result.text,
    inputTokens: result.inputTokens,
    outputTokens: result.outputTokens,
    latencyMs,
  });
}
