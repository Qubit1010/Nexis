import { api } from './api.ts';

/**
 * The dashboard needs to render "$15,000 - $50,000" where the database holds `4`.
 *
 * These maps are filled once at app boot from /api/form-config rather than hardcoded here,
 * so the server stays the single source of truth for the option catalog and the two surfaces
 * cannot drift apart. Render reads them synchronously, which is why they are mutable maps
 * rather than state.
 */

export const BUDGET_LABELS: Record<number, string> = {};
export const TIMELINE_LABELS: Record<number, string> = {};
export const NEED_LABELS: Record<string, string> = {};

let loaded = false;

export async function loadLabels(): Promise<void> {
  if (loaded) return;
  const config = await api.formConfig();
  for (const o of config.budget) BUDGET_LABELS[o.value] = o.label;
  for (const o of config.timeline) TIMELINE_LABELS[o.value] = o.label;
  for (const o of config.needs) NEED_LABELS[o.value] = o.label;
  loaded = true;
}

export function formatDate(iso: string, withTime = false): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  const date = d.toLocaleDateString(undefined, { day: 'numeric', month: 'short', year: 'numeric' });
  if (!withTime) return date;
  return `${date}, ${d.toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}`;
}
