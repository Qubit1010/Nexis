import { NextResponse } from "next/server";
import { sendToContentOs, type ContentOsIdea } from "@/lib/content-os";

/**
 * Browser -> Content OS proxy for one-click news bookmarks. The browser cannot call
 * 127.0.0.1:4600 directly (no CORS there, on purpose), so this server route does.
 */
export async function POST(request: Request) {
  const body = (await request.json().catch(() => null)) as ContentOsIdea | null;
  if (!body?.title?.trim() || !body.source) {
    return NextResponse.json({ error: "title and source are required" }, { status: 400 });
  }
  const result = await sendToContentOs(body);
  if (!result) return NextResponse.json({ error: "Content OS is not running (127.0.0.1:4600)" }, { status: 503 });
  return NextResponse.json({ success: true, ...result });
}
