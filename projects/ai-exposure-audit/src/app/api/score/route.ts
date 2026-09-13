import { NextRequest, NextResponse } from "next/server";
import { AllProvidersFailedError } from "@/lib/llm";
import { ScoringResponseError, scoreLines, type ScoreRequestLine } from "@/lib/scorer";

export const dynamic = "force-dynamic";
export const maxDuration = 120;

/**
 * Scores service lines. Returns 502 with a plain explanation when every provider is
 * down, and 422 when a provider answered but the answer was not usable.
 *
 * It never returns partial scores. The caller either gets a complete set of scores or
 * an error saying why it got none.
 */
export async function POST(req: NextRequest) {
  let body: unknown;
  try {
    body = await req.json();
  } catch {
    return NextResponse.json({ error: "Request body was not valid JSON" }, { status: 400 });
  }

  const raw = body as Record<string, unknown>;
  const rawLines = Array.isArray(raw.lines) ? raw.lines : null;
  if (!rawLines || rawLines.length === 0) {
    return NextResponse.json({ error: "No service lines were sent to score" }, { status: 400 });
  }
  if (rawLines.length > 50) {
    return NextResponse.json({ error: "Scoring is capped at 50 lines per request" }, { status: 400 });
  }

  const business = (raw.business ?? {}) as Record<string, unknown>;
  const businessName = typeof business.name === "string" ? business.name.trim() : "";
  if (!businessName) {
    return NextResponse.json({ error: "business.name is required" }, { status: 400 });
  }

  const lines: ScoreRequestLine[] = [];
  for (const [i, l] of rawLines.entries()) {
    if (typeof l !== "object" || l === null) {
      return NextResponse.json({ error: `lines[${i}] is not an object` }, { status: 400 });
    }
    const line = l as Record<string, unknown>;
    const id = typeof line.id === "string" ? line.id : "";
    const name = typeof line.name === "string" ? line.name.trim() : "";
    if (!id || !name) {
      return NextResponse.json({ error: `lines[${i}] needs an id and a name` }, { status: 400 });
    }
    lines.push({
      id,
      name: name.slice(0, 200),
      deliverable_description: String(line.deliverable_description ?? "").slice(0, 4000),
      pricing_model: String(line.pricing_model ?? "fixed").slice(0, 20),
      typical_price:
        line.typical_price === null || line.typical_price === undefined
          ? null
          : Number(line.typical_price) || null,
      revenue_share_pct: Number(line.revenue_share_pct) || 0,
    });
  }

  try {
    const result = await scoreLines(lines, {
      name: businessName.slice(0, 200),
      positioning: String(business.positioning ?? "").slice(0, 4000),
      headcount: business.headcount === null || business.headcount === undefined
        ? null
        : Number(business.headcount) || null,
    });
    return NextResponse.json(result);
  } catch (err) {
    if (err instanceof AllProvidersFailedError) {
      return NextResponse.json(
        {
          error: err.message,
          attempts: err.attempts,
          hint: "No scores were produced and nothing was defaulted. Fix a key, or score the lines by hand.",
        },
        { status: 502 }
      );
    }
    if (err instanceof ScoringResponseError) {
      return NextResponse.json(
        {
          error: `The model answered but the response was not usable: ${err.message}`,
          hint: "Retry, or score by hand. No partial scores were saved.",
        },
        { status: 422 }
      );
    }
    return NextResponse.json(
      { error: err instanceof Error ? err.message : "Scoring failed" },
      { status: 500 }
    );
  }
}
