export type Option = { value: number; label: string; hint?: string };
export type NeedOption = { value: string; label: string };

export type FormConfig = { budget: Option[]; timeline: Option[]; needs: NeedOption[] };

export type BreakdownEntry = { rule_id: number; label: string; points: number; matched: boolean };

export type Lead = {
  id: number;
  created_at: string;
  updated_at: string;
  name: string;
  email: string;
  company: string;
  budget: number;
  timeline: number;
  needs: string[];
  message: string;
  score: number;
  band: 'hot' | 'warm' | 'cold';
  score_breakdown: BreakdownEntry[];
  status: 'new' | 'contacted' | 'qualified' | 'dead';
  notes: string;
};

export type Rule = {
  id: number;
  label: string;
  field: string;
  op: string;
  value: string;
  points: number;
  enabled: boolean;
  sort: number;
};

export type RulesMeta = {
  fields: string[];
  ops: string[];
  fieldOps: Record<string, string[]>;
  fieldLabels: Record<string, string>;
  opLabels: Record<string, string>;
  budget: Option[];
  timeline: Option[];
  needs: NeedOption[];
  statuses: string[];
};

export type Stats = Record<string, number>;

/** Thrown for any non-2xx. `fields` carries the server's per-field validation messages. */
export class ApiError extends Error {
  status: number;
  fields: Record<string, string>;
  constructor(status: number, message: string, fields: Record<string, string> = {}) {
    super(message);
    this.status = status;
    this.fields = fields;
  }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(path, {
    credentials: 'same-origin',
    headers: init.body ? { 'content-type': 'application/json' } : undefined,
    ...init,
  });

  if (res.status === 204) return undefined as T;

  let body: unknown = null;
  try {
    body = await res.json();
  } catch {
    /* an empty or non-JSON body is handled below */
  }

  if (!res.ok) {
    const b = body as { error?: string; fields?: Record<string, string> } | null;
    throw new ApiError(res.status, b?.error ?? `Request failed (${res.status})`, b?.fields ?? {});
  }
  return body as T;
}

const post = <T>(path: string, body: unknown) =>
  request<T>(path, { method: 'POST', body: JSON.stringify(body) });
const patch = <T>(path: string, body: unknown) =>
  request<T>(path, { method: 'PATCH', body: JSON.stringify(body) });

export const api = {
  formConfig: () => request<FormConfig>('/api/form-config'),
  submitLead: (payload: unknown) => post<{ ok: true; id: number | null }>('/api/leads', payload),

  me: () => request<{ authed: boolean }>('/api/auth/me'),
  login: (password: string) => post<{ ok: true }>('/api/auth/login', { password }),
  logout: () => post<{ ok: true }>('/api/auth/logout', {}),

  leads: (query: string) => request<{ leads: Lead[]; stats: Stats }>(`/api/leads${query}`),
  lead: (id: number) => request<{ lead: Lead }>(`/api/leads/${id}`),
  updateLead: (id: number, body: { status?: string; notes?: string }) =>
    patch<{ lead: Lead }>(`/api/leads/${id}`, body),
  deleteLead: (id: number) => request<{ ok: true }>(`/api/leads/${id}`, { method: 'DELETE' }),

  rules: () => request<{ rules: Rule[]; settings: { hot_min: number; warm_min: number }; meta: RulesMeta }>('/api/rules'),
  createRule: (body: Partial<Rule>) => post<{ rule: Rule }>('/api/rules', body),
  updateRule: (id: number, body: Partial<Rule>) => patch<{ rule: Rule }>(`/api/rules/${id}`, body),
  deleteRule: (id: number) => request<{ ok: true }>(`/api/rules/${id}`, { method: 'DELETE' }),
  updateSettings: (body: { hot_min?: number; warm_min?: number }) =>
    patch<{ settings: { hot_min: number; warm_min: number } }>('/api/settings', body),
  rescore: () => post<{ rescored: number; changed: number }>('/api/rescore', {}),
};
