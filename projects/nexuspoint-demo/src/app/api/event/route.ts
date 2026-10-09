import { NextResponse } from "next/server";
import { authorised, expired, getBusiness, logEvent } from "@/lib/db";

export const dynamic = "force-dynamic";
const KINDS = new Set(["view", "chat_view", "roi_used", "plan_click"]);

export async function POST(req: Request) {
  const { slug, t, kind } = (await req.json().catch(() => ({}))) as Record<
    string,
    string
  >;
  if (!KINDS.has(kind))
    return NextResponse.json({ ok: false }, { status: 400 });
  const b = await getBusiness(slug ?? "");
  if (!authorised(b, t))
    return NextResponse.json({ ok: false }, { status: 404 });
  if (expired(b)) return NextResponse.json({ ok: false }, { status: 410 });
  await logEvent(b.slug, kind, {
    ua: (req.headers.get("user-agent") ?? "").slice(0, 120),
  });
  return NextResponse.json({ ok: true });
}
