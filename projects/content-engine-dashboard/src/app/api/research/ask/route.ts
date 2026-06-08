import { NextRequest, NextResponse } from "next/server";
import { runScript } from "@/lib/run-script";
import type { NotebookLMAskOutput } from "@/lib/types";

export const dynamic = "force-dynamic";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const topic: string = body.topic;
    const notebookId: string = body.notebookId;
    const sourceIds: string[] = body.sourceIds ?? [];

    if (!topic || typeof topic !== "string") {
      return NextResponse.json({ error: "topic is required" }, { status: 400 });
    }
    if (!notebookId || typeof notebookId !== "string") {
      return NextResponse.json({ error: "notebookId is required" }, { status: 400 });
    }
    if (!Array.isArray(sourceIds) || sourceIds.length === 0) {
      return NextResponse.json({ error: "sourceIds must be a non-empty array" }, { status: 400 });
    }

    const sourcesArg = sourceIds.join(",");

    try {
      const stdout = await runScript(
        "research_notebooklm.py",
        ["--topic", topic, "--notebook", notebookId, "--sources", sourcesArg],
        undefined,
        300_000
      );
      const data: NotebookLMAskOutput = JSON.parse(stdout);
      return NextResponse.json(data);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      const isAuthError = /auth|login|expired|session/i.test(msg);
      if (isAuthError) {
        return NextResponse.json({
          available: false,
          error: "NotebookLM session expired — run: notebooklm login",
        });
      }
      throw err;
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
