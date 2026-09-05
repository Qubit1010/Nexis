import type { IncomingMessage, ServerResponse } from 'node:http';
import { BadRequest } from './service.ts';

/** Hard ceiling on a request body. Well above a long email, well below a memory problem. */
export const MAX_BODY_BYTES = 256 * 1024;

export const LIMITS = {
  label: 120,
  subject: 500,
  sender: 200,
  body: 50_000,
  systemPrompt: 20_000,
  finalText: 50_000,
  note: 2_000,
} as const;

export function sendJson(res: ServerResponse, status: number, payload: unknown): void {
  const data = JSON.stringify(payload);
  res.writeHead(status, {
    'content-type': 'application/json; charset=utf-8',
    'content-length': Buffer.byteLength(data),
    'cache-control': 'no-store',
    'x-content-type-options': 'nosniff',
  });
  res.end(data);
}

/**
 * Read and parse a JSON body, refusing anything oversized.
 *
 * The length is counted as bytes are received rather than trusted from content-length, so
 * a lying header cannot get a large body through.
 */
export async function readJsonBody(req: IncomingMessage): Promise<Record<string, unknown>> {
  const chunks: Buffer[] = [];
  let size = 0;

  for await (const chunk of req) {
    const buf = chunk as Buffer;
    size += buf.length;
    if (size > MAX_BODY_BYTES) {
      throw new BadRequest(`request body exceeds ${MAX_BODY_BYTES} bytes`);
    }
    chunks.push(buf);
  }

  if (chunks.length === 0) return {};
  const raw = Buffer.concat(chunks).toString('utf8');
  if (raw.trim() === '') return {};

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw);
  } catch {
    throw new BadRequest('body is not valid JSON');
  }
  if (parsed === null || typeof parsed !== 'object' || Array.isArray(parsed)) {
    throw new BadRequest('body must be a JSON object');
  }
  return parsed as Record<string, unknown>;
}

/**
 * Strip NUL bytes.
 *
 * SQLite stores TEXT as a C string, so a NUL silently truncates everything after it: a
 * pasted email carrying one would be stored as its own first half with no error anywhere.
 * Dropping the NUL and keeping the rest turns unbounded silent data loss into a single
 * removed control character. Nothing legitimate in an email body needs one.
 */
export function stripNul(value: string): string {
  return value.includes('\u0000') ? value.replaceAll('\u0000', '') : value;
}

// --------------------------------------------------------------------------------------
// Field validation. Every endpoint runs everything it reads through these.
// --------------------------------------------------------------------------------------

export function reqString(
  obj: Record<string, unknown>,
  key: string,
  max: number,
): string {
  const v = obj[key];
  if (typeof v !== 'string') throw new BadRequest(`${key} is required and must be a string`);
  const trimmed = stripNul(v).trim();
  if (trimmed === '') throw new BadRequest(`${key} must not be empty`);
  if (v.length > max) throw new BadRequest(`${key} exceeds ${max} characters`);
  return trimmed;
}

/** Like reqString but allows an empty string, for text the user may legitimately clear. */
export function reqText(obj: Record<string, unknown>, key: string, max: number): string {
  const v = obj[key];
  if (typeof v !== 'string') throw new BadRequest(`${key} is required and must be a string`);
  if (v.length > max) throw new BadRequest(`${key} exceeds ${max} characters`);
  return stripNul(v);
}

export function optString(
  obj: Record<string, unknown>,
  key: string,
  max: number,
): string | null {
  const v = obj[key];
  if (v === undefined || v === null || v === '') return null;
  if (typeof v !== 'string') throw new BadRequest(`${key} must be a string`);
  if (v.length > max) throw new BadRequest(`${key} exceeds ${max} characters`);
  const trimmed = stripNul(v).trim();
  return trimmed === '' ? null : trimmed;
}

export function reqId(obj: Record<string, unknown>, key: string): number {
  const v = obj[key];
  if (typeof v !== 'number' || !Number.isInteger(v) || v <= 0) {
    throw new BadRequest(`${key} must be a positive integer`);
  }
  return v;
}

export function optId(obj: Record<string, unknown>, key: string): number | undefined {
  const v = obj[key];
  if (v === undefined || v === null) return undefined;
  return reqId(obj, key);
}

export function optBool(obj: Record<string, unknown>, key: string): boolean {
  const v = obj[key];
  if (v === undefined || v === null) return false;
  if (typeof v !== 'boolean') throw new BadRequest(`${key} must be a boolean`);
  return v;
}

export function reqEnum<T extends string>(
  obj: Record<string, unknown>,
  key: string,
  allowed: readonly T[],
): T {
  const v = obj[key];
  if (typeof v !== 'string' || !allowed.includes(v as T)) {
    throw new BadRequest(`${key} must be one of: ${allowed.join(', ')}`);
  }
  return v as T;
}

/** Parse a query-string enum, falling back to a default rather than erroring. */
export function queryEnum<T extends string>(
  params: URLSearchParams,
  key: string,
  allowed: readonly T[],
  fallback: T,
): T {
  const v = params.get(key);
  return v !== null && allowed.includes(v as T) ? (v as T) : fallback;
}

export function queryId(params: URLSearchParams, key: string): number | null {
  const v = params.get(key);
  if (v === null) return null;
  const n = Number(v);
  return Number.isInteger(n) && n > 0 ? n : null;
}
