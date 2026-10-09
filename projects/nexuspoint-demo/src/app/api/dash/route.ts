// Owner dashboard feed: every conversation for this demo with its card data and recent messages.
import { NextResponse } from "next/server";
import { authorised, expired, getBusiness, rest, type Conversation, type Message } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET(req: Request) {
  const u = new URL(req.url);
  const slug = u.searchParams.get("slug") ?? "";
  const b = await getBusiness(slug);
  if (!authorised(b, u.searchParams.get("t"))) return NextResponse.json({ error: "not found" }, { status: 404 });
  if(expired(b))return NextResponse.json({error:"Demo expired"},{status:410});
  const convs = await rest<Conversation>("GET", `demo_conversations?slug=eq.${encodeURIComponent(slug)}&order=last_at.desc&limit=20`);
  const ids = convs.map((c) => c.id);
  const msgs = ids.length
    ? await rest<Message>("GET", `demo_messages?conversation_id=in.(${ids.join(",")})&order=id.asc&limit=400`)
    : [];
  const byConv = new Map<string, Message[]>();
  for (const m of msgs) byConv.set(m.conversation_id, [...(byConv.get(m.conversation_id) ?? []), m]);
  const replies = msgs.filter((m) => m.role === "business" && m.latency_ms != null).map((m) => m.latency_ms as number);
  return NextResponse.json({
    stats: {
      conversations: convs.length,
      messages: msgs.length,
      avg_reply_s: replies.length ? Math.round(replies.reduce((a, x) => a + x, 0) / replies.length / 100) / 10 : null,
      actions: convs.filter((c) => c.action).length,
      handoffs: convs.filter((c) => c.handoff).length,
    },
    conversations: convs.map((c) => ({ ...c, visitor: undefined, messages: (byConv.get(c.id) ?? []).slice(-8) })),
  }, { headers: { "Cache-Control": "no-store" } });
}
