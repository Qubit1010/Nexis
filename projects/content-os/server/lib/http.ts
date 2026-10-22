import type { MiddlewareHandler } from "hono";
import { ALLOWED_ORIGINS } from "../config.ts";

export class HttpError extends Error {
  status: number;
  code: string;
  // Node strip-only TS: no parameter properties, assign explicitly.
  constructor(status: number, code: string, message?: string) {
    super(message ?? code);
    this.status = status;
    this.code = code;
  }
}

/**
 * Any web page can POST to 127.0.0.1, and this server can push to git and
 * Buffer. So every state-changing request must be JSON (a cross-site form or
 * no-cors fetch cannot send that without a preflight) and, when the browser
 * names an Origin, it must be one of ours. Server-to-server callers (the daily
 * brief's API routes, scripts) send no Origin and pass on the JSON rule alone.
 */
export const guardMutations: MiddlewareHandler = async (c, next) => {
  const method = c.req.method;
  if (method === "GET" || method === "HEAD" || method === "OPTIONS") return next();
  const origin = c.req.header("origin");
  if (origin && !ALLOWED_ORIGINS.has(origin)) {
    return c.json({ error: "origin not allowed", code: "ORIGIN_DENIED" }, 403);
  }
  const type = c.req.header("content-type") || "";
  const isUpload = c.req.path.endsWith("/assets") && type.startsWith("multipart/form-data");
  if (!type.startsWith("application/json") && !isUpload) {
    return c.json({ error: "JSON body required", code: "JSON_REQUIRED" }, 415);
  }
  return next();
};

export function parseJson<T>(raw: string | null | undefined, fallback: T): T {
  if (!raw) return fallback;
  try {
    return JSON.parse(raw) as T;
  } catch {
    return fallback;
  }
}
