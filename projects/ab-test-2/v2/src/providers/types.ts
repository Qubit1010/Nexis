export type DraftRequest = {
  systemPrompt: string;
  subject: string;
  body: string;
  sender: string | null;
};

export type DraftResult = {
  text: string;
  provider: 'mock' | 'anthropic';
  model: string;
  /** Null unless a real API response reported usage. Never estimated. */
  inputTokens: number | null;
  outputTokens: number | null;
  costUsd: number | null;
  latencyMs: number;
};

export type Provider = {
  name: 'mock' | 'anthropic';
  model: string;
  draft(req: DraftRequest): Promise<DraftResult>;
};
