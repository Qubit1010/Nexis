// WhatsApp Cloud API webhook (Phase 2; dormant until the WHATSAPP_* env vars are set).
// GET: Meta's verification handshake. POST: incoming messages. The first message carries the demo
// code from the QR deep link ("DEMO-AB12C ..."); later messages from the same number continue the
// most recent demo conversation. The demo number never starts a conversation.
import { NextResponse } from "next/server";
import { createHash, createHmac, timingSafeEqual } from "node:crypto";
import { expired, getBusiness, getBusinessByCode, latestConversationForVisitor } from "@/lib/db";
import { respond } from "@/lib/respond";

export const dynamic = "force-dynamic";
export const maxDuration = 30;

const GRAPH = "https://graph.facebook.com/v23.0";

export async function GET(req: Request) {
  const u = new URL(req.url);
  if (u.searchParams.get("hub.mode") === "subscribe" && u.searchParams.get("hub.verify_token") === process.env.WHATSAPP_VERIFY_TOKEN)
    return new Response(u.searchParams.get("hub.challenge") ?? "", { status: 200 });
  return new Response("forbidden", { status: 403 });
}

async function send(to: string, body: string) {
  await fetch(`${GRAPH}/${process.env.WHATSAPP_PHONE_NUMBER_ID}/messages`, {
    method: "POST",
    headers: { Authorization: `Bearer ${process.env.WHATSAPP_TOKEN}`, "Content-Type": "application/json" },
    body: JSON.stringify({ messaging_product: "whatsapp", to, type: "text", text: { body, preview_url: false } }),
  });
}

type Incoming = { from: string; type: string; text?: { body: string } };

export async function POST(req: Request) {
  if (!process.env.WHATSAPP_TOKEN || !process.env.WHATSAPP_PHONE_NUMBER_ID) return NextResponse.json({ ok: true });
  const raw = await req.text();
  const secret = process.env.WHATSAPP_APP_SECRET;
  if (secret) { // reject anything not signed by Meta
    const sig = req.headers.get("x-hub-signature-256") ?? "";
    const want = "sha256=" + createHmac("sha256", secret).update(raw).digest("hex");
    if (sig.length !== want.length || !timingSafeEqual(Buffer.from(sig), Buffer.from(want)))
      return new Response("bad signature", { status: 401 });
  }
  let parsed: unknown = null;
  try { parsed = JSON.parse(raw); } catch { /* ignore */ }
  const payload = parsed as { entry?: { changes?: { value?: { messages?: Incoming[] } }[] }[] } | null;
  const messages = payload?.entry?.flatMap((e) => e.changes ?? []).flatMap((c) => c.value?.messages ?? []) ?? [];
  for (const m of messages) {
    const visitor = createHash("sha256").update(`wa:${m.from}`).digest("hex").slice(0, 40);
    if (m.type !== "text" || !m.text?.body) {
      await send(m.from, "I can read text messages for now. Please type your question. (Voice notes are coming soon.)");
      continue;
    }
    let text = m.text.body.trim();
    const code = text.match(/\bDEMO-([A-Z0-9]{5})\b/i)?.[1];
    let b = code ? await getBusinessByCode(code) : null;
    if (code) text = text.replace(/\bDEMO-[A-Z0-9]{5}\b/i, "").trim() || "Assalam o alaikum";
    if (!b) {
      const last = await latestConversationForVisitor(visitor);
      b = last ? await getBusiness(last.slug) : null;
    }
    if (!b) {
      await send(m.from, "This is the NexusPoint demo number. Scan the QR code from your demo page to start. For NexusPoint itself, message +92 311 8340514.");
      continue;
    }
    if (expired(b)) {
      await send(m.from, `The demo for ${b.name} has ended. Message NexusPoint on +92 311 8340514 for a new one.`);
      continue;
    }
    const out = await respond(b, "whatsapp", visitor, text);
    if(out.reply) await send(m.from, out.reply);
  }
  return NextResponse.json({ ok: true });
}
