import { NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";

export async function POST(request: Request) {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return NextResponse.json({ ok: false, error: "Invalid JSON body" }, { status: 400 });
  }

  try {
    const res = await fetch(`${BACKEND_URL}/score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      // Backend pipeline can take ~25s; allow plenty of headroom
      signal: AbortSignal.timeout(60_000),
    });

    const text = await res.text();
    let parsed: unknown;
    try {
      parsed = JSON.parse(text);
    } catch {
      return NextResponse.json(
        { ok: false, error: `Backend returned non-JSON (HTTP ${res.status})` },
        { status: 502 },
      );
    }

    if (!res.ok) {
      const errorMsg =
        (parsed as { detail?: string; error?: string })?.detail ||
        (parsed as { error?: string })?.error ||
        `Backend error (HTTP ${res.status})`;
      return NextResponse.json({ ok: false, error: errorMsg }, { status: res.status });
    }

    return NextResponse.json(parsed);
  } catch (err) {
    const message = err instanceof Error ? err.message : "Unknown error";
    return NextResponse.json(
      { ok: false, error: `Failed to reach backend: ${message}` },
      { status: 502 },
    );
  }
}
