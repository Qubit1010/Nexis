import { createHash } from "node:crypto";

const TRACKING = /^(utm_|fbclid$|gclid$|mc_|ref$|ref_src$|si$|igshid$|feature$)/i;

/** Canonical form of a URL for duplicate detection: same article, same key. */
export function normalizeUrl(raw: string): string | null {
  let u: URL;
  try {
    u = new URL(raw.trim());
  } catch {
    return null;
  }
  if (!/^https?:$/.test(u.protocol)) return null;
  let host = u.hostname.toLowerCase().replace(/^(www|m)\./, "");
  let pathname = u.pathname.replace(/\/+$/, "") || "/";
  const params = new URLSearchParams();
  if (host === "youtu.be") {
    params.set("v", pathname.slice(1));
    host = "youtube.com";
    pathname = "/watch";
  } else if (host === "youtube.com" && pathname === "/watch") {
    const v = u.searchParams.get("v");
    if (v) params.set("v", v);
  } else {
    const keys = [...u.searchParams.keys()].filter((k) => !TRACKING.test(k)).sort();
    for (const k of keys) params.set(k, u.searchParams.get(k) ?? "");
  }
  const qs = params.toString();
  return `${host}${pathname}${qs ? `?${qs}` : ""}`;
}

export function normalizeTitle(title: string): string {
  return title
    .toLowerCase()
    .replace(/[‘’“”"'`]/g, "")
    .replace(/[^a-z0-9]+/g, " ")
    .trim();
}

export function dedupeKey(input: { url?: string | null; title: string }): string {
  const url = input.url ? normalizeUrl(input.url) : null;
  if (url) return `u:${url}`;
  return `t:${createHash("sha1").update(normalizeTitle(input.title)).digest("hex").slice(0, 20)}`;
}
