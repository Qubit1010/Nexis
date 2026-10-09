import { NextResponse } from "next/server";
import { authorised, expired, getBusiness, rest, transcript } from "@/lib/db";
import { respond } from "@/lib/respond";
import type { Choice } from "@/lib/healthcare-types";

export const dynamic = "force-dynamic";
export const maxDuration = 30;

const recent = new Map<string, number[]>(); // per-instance rate limit: 20 messages / 5 min / visitor

// Restore this visitor's conversation when the page is reopened.
export async function GET(req: Request) {
  const u = new URL(req.url);
  const b = await getBusiness(u.searchParams.get("slug") ?? "");
  if (!authorised(b, u.searchParams.get("t"))) return NextResponse.json({ messages: [] }, { status: 404 });
  if(expired(b)) return NextResponse.json({error:"Demo expired"},{status:410});
  const visitor = (u.searchParams.get("visitor") ?? "").slice(0, 64);
  const conv = (await rest<{ id: string }>("GET",
    `demo_conversations?slug=eq.${encodeURIComponent(b.slug)}&channel=eq.web&visitor=eq.${encodeURIComponent(visitor)}&limit=1`))[0];
  const messages = conv ? await transcript(conv.id) : [];
  const state=conv?(await rest<{staff_mode:boolean}>("GET",`demo_conversations?id=eq.${conv.id}&limit=1`))[0]:null;
  return NextResponse.json({ staffMode:state?.staff_mode??false,messages: messages.map((m) => ({ role: m.role, content: m.content, at: m.at,source:m.source,cards:m.cards??[] })) },{headers:{"Cache-Control":"no-store"}});
}

export async function POST(req: Request) {
  const { slug, t, visitor, text,choice } = (await req.json().catch(() => ({}))) as {slug:string;t:string;visitor:string;text:string;choice?:Choice};
  if([slug,t,visitor,text].some(v=>typeof v!=="string")) return NextResponse.json({error:"bad request"},{status:400});
  if(choice&&(!["doctor","slot","mode","cancel","reschedule","food_item","food_mode","food_confirm","food_clear","table_party","table_time","table_confirm","school_student","school_program","school_visit","school_time","school_confirm"].includes(choice.kind)||typeof choice.value!=="string"||choice.value.length>200||typeof choice.label!=="string")) return NextResponse.json({error:"bad choice"},{status:400});
  if (!slug || !visitor || !text?.trim()) return NextResponse.json({ error: "bad request" }, { status: 400 });
  const b = await getBusiness(slug);
  if (!authorised(b, t)) return NextResponse.json({ error: "not found" }, { status: 404 });
  if (expired(b)) return NextResponse.json({ reply: "This demo has ended. Message NexusPoint on WhatsApp for a new one: +92 311 8340514.", stage: "expired" });
  const now = Date.now();
  const hits = (recent.get(visitor) ?? []).filter((x) => now - x < 300_000);
  if (hits.length >= 20) return NextResponse.json({ error: "slow down" }, { status: 429 });
  recent.set(visitor, [...hits, now]);
  try {
    const out = await respond(b, "web", visitor.slice(0, 64), text.trim(),choice);
    return NextResponse.json(out);
  } catch {
    return NextResponse.json({error:"The demo connection is unavailable. Please try again."},{status:503});
  }
}
