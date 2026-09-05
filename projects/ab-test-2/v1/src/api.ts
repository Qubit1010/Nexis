import type {
  Draft,
  Enquiry,
  EnquirySummary,
  Health,
  PromptVersion,
  Rating,
  Scoreboard,
} from './types.ts';

export class ApiError extends Error {
  readonly code: string;
  constructor(code: string, message: string) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, {
      ...init,
      headers: init?.body ? { 'content-type': 'application/json' } : undefined,
    });
  } catch {
    throw new ApiError(
      'network_error',
      'Could not reach the API. Is it running on port 4200? Try: npm run dev:api',
    );
  }

  const text = await response.text();
  const payload: unknown = text.length > 0 ? JSON.parse(text) : null;

  if (!response.ok) {
    const error =
      payload && typeof payload === 'object' && 'error' in payload
        ? (payload as { error: { code?: string; message?: string } }).error
        : null;
    throw new ApiError(error?.code ?? 'unknown', error?.message ?? `Request failed (${response.status})`);
  }

  return payload as T;
}

export const api = {
  health: () => request<Health>('/health'),

  listEnquiries: () => request<EnquirySummary[]>('/enquiries'),

  createEnquiry: (subject: string, body: string) =>
    request<Enquiry>('/enquiries', {
      method: 'POST',
      body: JSON.stringify({ subject, body }),
    }),

  getEnquiry: (id: number) => request<{ enquiry: Enquiry; drafts: Draft[] }>(`/enquiries/${id}`),

  generateDraft: (enquiryId: number) =>
    request<Draft>(`/enquiries/${enquiryId}/drafts`, { method: 'POST' }),

  saveEdit: (draftId: number, editedText: string) =>
    request<Draft>(`/drafts/${draftId}`, {
      method: 'PATCH',
      body: JSON.stringify({ editedText }),
    }),

  rate: (draftId: number, rating: Rating) =>
    request<Draft>(`/drafts/${draftId}`, {
      method: 'PATCH',
      body: JSON.stringify({ rating }),
    }),

  listPrompts: () => request<PromptVersion[]>('/prompts'),

  createPrompt: (systemPrompt: string, label?: string) =>
    request<PromptVersion>('/prompts', {
      method: 'POST',
      body: JSON.stringify({ systemPrompt, label }),
    }),

  activatePrompt: (id: number) =>
    request<PromptVersion>(`/prompts/${id}/activate`, { method: 'POST' }),

  stats: () => request<Scoreboard>('/stats'),
};
