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
    const { channel, identityRaw, name, profile, stage, meeting_status, thread, last_draft } = body;
    if (!channel || !identityRaw) {
      return NextResponse.json({ error: "channel and identityRaw are required" }, { status: 400 });
    }
    const identity = normalizeIdentity(channel, identityRaw);
    if (!identity) {
      return NextResponse.json({ error: `could not derive a ${channel} identity from "${identityRaw}"` }, { status: 400 });
    }
    const fields: Record<string, unknown> = {};
    if (name) fields.name = name;
    if (profile) fields.profile = profile;
    if (stage) fields.stage = stage;
    if (meeting_status) fields.meeting_status = meeting_status;
    if (last_draft) fields.last_draft = last_draft;
    if (thread) {
      fields.thread = thread;
      fields.exchange_count = countExchanges(thread, identity);
      fields.last_contact = new Date().toISOString().slice(0, 10);
    }
    const row = await upsertConversation(channel, identity, fields);
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
