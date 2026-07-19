import { NextRequest, NextResponse } from "next/server";
import {
  dbConfigured,
  listConversations,
  upsertConversation,
  deleteConversation,
  normalizeIdentity,
  countExchanges,
} from "@/lib/db";

export const dynamic = "force-dynamic";

function unavailable() {
  return NextResponse.json(
    { error: "Conversation memory unavailable: set SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY in .env.local" },
    { status: 503 }
  );
}

export async function GET() {
  if (!dbConfigured()) return unavailable();
  try {
    return NextResponse.json({ conversations: await listConversations() });
  } catch (err) {
    return NextResponse.json({ error: String(err instanceof Error ? err.message : err) }, { status: 500 });
  }
}

export async function POST(req: NextRequest) {
  if (!dbConfigured()) return unavailable();
  try {
    const body = await req.json();
    const { identityRaw, client_name, job_title, job_type, profile, situation, stage, thread, last_draft } = body;
    if (!identityRaw) {
      return NextResponse.json({ error: "identityRaw is required" }, { status: 400 });
    }
    const identity = normalizeIdentity(identityRaw);
    if (!identity) {
      return NextResponse.json({ error: `could not derive an identity from "${identityRaw}"` }, { status: 400 });
    }
    const fields: Record<string, unknown> = {};
    if (client_name) fields.client_name = client_name;
    if (job_title) fields.job_title = job_title;
    if (job_type) fields.job_type = job_type;
    if (profile) fields.profile = profile;
    if (situation) fields.situation = situation;
    if (stage) fields.stage = stage;
    if (last_draft) fields.last_draft = last_draft;
    if (thread) {
      fields.thread = thread;
      fields.exchange_count = countExchanges(thread, client_name);
      fields.last_contact = new Date().toISOString().slice(0, 10);
    }
    const row = await upsertConversation(identity, fields);
    return NextResponse.json({ conversation: row });
  } catch (err) {
    return NextResponse.json({ error: String(err instanceof Error ? err.message : err) }, { status: 500 });
  }
}

export async function DELETE(req: NextRequest) {
  if (!dbConfigured()) return unavailable();
  try {
    const id = Number(new URL(req.url).searchParams.get("id"));
    if (!id) return NextResponse.json({ error: "id query param required" }, { status: 400 });
    await deleteConversation(id);
    return NextResponse.json({ deleted: id });
  } catch (err) {
    return NextResponse.json({ error: String(err instanceof Error ? err.message : err) }, { status: 500 });
  }
}
