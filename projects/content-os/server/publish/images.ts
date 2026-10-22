// Buffer has no upload endpoint: an image must sit at a public URL until the post
// goes out. Default host is a public bucket in the Supabase project already in
// D:/Nexis/.env (SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY).
import fs from "node:fs";
import path from "node:path";
import { rootEnv } from "../config.ts";

const MIME: Record<string, string> = { ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif" };

function supabase() {
  const env = rootEnv();
  const url = env.SUPABASE_URL?.replace(/\/+$/, "");
  const key = env.SUPABASE_SERVICE_ROLE_KEY;
  if (!url || !key) throw new Error("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY missing from D:/Nexis/.env, so images cannot be hosted for Buffer");
  return { url, key };
}

async function ensureBucket(bucket: string): Promise<void> {
  const { url, key } = supabase();
  const head = await fetch(`${url}/storage/v1/bucket/${bucket}`, { headers: { Authorization: `Bearer ${key}`, apikey: key } });
  if (head.ok) return;
  const res = await fetch(`${url}/storage/v1/bucket`, {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, apikey: key, "Content-Type": "application/json" },
    body: JSON.stringify({ id: bucket, name: bucket, public: true }),
  });
  if (!res.ok && res.status !== 409) throw new Error(`could not create the ${bucket} bucket: ${res.status} ${(await res.text()).slice(0, 200)}`);
}

export async function uploadPublicImage(localPath: string, bucket: string, objectPath: string): Promise<string> {
  const { url, key } = supabase();
  await ensureBucket(bucket);
  const ext = path.extname(localPath).toLowerCase();
  const res = await fetch(`${url}/storage/v1/object/${bucket}/${objectPath}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${key}`, apikey: key, "Content-Type": MIME[ext] || "application/octet-stream", "x-upsert": "true" },
    body: fs.readFileSync(localPath),
  });
  if (!res.ok) throw new Error(`image upload failed: ${res.status} ${(await res.text()).slice(0, 200)}`);
  return `${url}/storage/v1/object/public/${bucket}/${objectPath}`;
}
