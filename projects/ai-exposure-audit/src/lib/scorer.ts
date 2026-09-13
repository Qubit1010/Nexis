import { complete, extractJson } from "./llm";
import { getRubric } from "./rubric";
import { DIMENSION_IDS, type DimensionId, type ScoreValue } from "./types";

/**
 * Turns a service line description into per-dimension scores with reasoning.
 *
 * The rubric text is injected from rubric/rubric.v1.json rather than written into a
 * prompt string, so scoring and citation always move together when the rubric changes.
 *
 * The response is validated strictly. A missing dimension, an out-of-range value or an
 * empty justification is an error, never a default. Defaulting an unscored dimension to
 * 3 would be the exact failure this product is sold to prevent.
 */

export interface ScoreRequestLine {
  id: string;
  name: string;
  deliverable_description: string;
  pricing_model: string;
  typical_price: number | null;
  revenue_share_pct: number;
}

export interface ScoredDimension {
  value: ScoreValue;
  reasoning: string;
}

export interface ScoredLine {
  line_id: string;
  scores: Record<DimensionId, ScoredDimension>;
}

export class ScoringResponseError extends Error {}

function buildSystemPrompt(): string {
  const rubric = getRubric();

  const dimensionBlocks = rubric.dimensions
    .map((d) => {
      const anchors = Object.entries(d.anchors)
        .sort(([a], [b]) => Number(a) - Number(b))
        .map(([n, text]) => `    ${n} = ${text}`)
        .join("\n");
      return [
        `### ${d.id} (${d.name})`,
        `Question: ${d.question}`,
        `A 5 means: ${d.high_means}`,
        `Anchors:`,
        anchors,
      ].join("\n");
    })
    .join("\n\n");

  return `You score service lines of a service business for AI substitution exposure. You are the measuring instrument in a paid diagnostic, not a consultant trying to win the work.

ORIENTATION: ${rubric.orientation}

Score every dimension from 1 to 5 against the anchor text below. Pick the anchor the line genuinely matches. Do not average toward the middle, and do not reserve 5s for hypothetical worse cases.

${dimensionBlocks}

HOW TO REASON
- Justify each score by naming the specific anchor you matched and the fact about this line that puts it there.
- Reason about the deliverable actually described, not the label. "Web design" that is bespoke design systems work scores differently from "web design" that is template installs.
- Where the description is too thin to judge a dimension, say so in the reasoning and score against what is stated rather than what you assume. Do not invent detail about the business.

DO NOT FLATTER. The person reading this is paying to be told which of their revenue lines is in trouble. A comfortable score that is wrong costs them money. If a line is highly exposed, score it 5 and say why plainly. Under-scoring to be kind is the worst failure available to you.

Return ONLY a JSON object in exactly this shape, with no commentary before or after:

{
  "lines": [
    {
      "line_id": "<the id given to you>",
      "scores": {
${DIMENSION_IDS.map((d) => `        "${d}": { "value": <1-5>, "reasoning": "<one or two sentences>" }`).join(",\n")}
      }
    }
  ]
}

Every line you were given must appear, and every dimension must be present on every line.`;
}

function buildUserPrompt(
  lines: ScoreRequestLine[],
  business: { name: string; positioning?: string; headcount?: number | null }
): string {
  const context = [
    `Business: ${business.name}`,
    business.headcount ? `Headcount: ${business.headcount}` : null,
    business.positioning ? `Positioning: ${business.positioning}` : null,
  ]
    .filter(Boolean)
    .join("\n");

  const lineBlocks = lines
    .map((l) =>
      [
        `- line_id: ${l.id}`,
        `  name: ${l.name}`,
        `  share of revenue: ${l.revenue_share_pct}%`,
        `  pricing model: ${l.pricing_model}`,
        l.typical_price ? `  typical price: ${l.typical_price}` : null,
        `  what is actually delivered: ${l.deliverable_description || "(not described)"}`,
      ]
        .filter(Boolean)
        .join("\n")
    )
    .join("\n\n");

  return `${context}\n\nScore these service lines:\n\n${lineBlocks}`;
}

function validateResponse(parsed: unknown, expectedIds: string[]): ScoredLine[] {
  if (typeof parsed !== "object" || parsed === null || !Array.isArray((parsed as any).lines)) {
    throw new ScoringResponseError("Model response had no 'lines' array");
  }
  const rawLines = (parsed as { lines: unknown[] }).lines;

  const out: ScoredLine[] = [];
  for (const raw of rawLines) {
    if (typeof raw !== "object" || raw === null) {
      throw new ScoringResponseError("A scored line was not an object");
    }
    const r = raw as Record<string, unknown>;
    const lineId = String(r.line_id ?? "");
    if (!expectedIds.includes(lineId)) {
      throw new ScoringResponseError(
        `Model returned scores for an unknown line_id "${lineId}". Expected one of: ${expectedIds.join(", ")}`
      );
    }

    const rawScores = r.scores;
    if (typeof rawScores !== "object" || rawScores === null) {
      throw new ScoringResponseError(`Line "${lineId}" had no scores object`);
    }
    const sr = rawScores as Record<string, unknown>;

    const scores = {} as Record<DimensionId, ScoredDimension>;
    for (const d of DIMENSION_IDS) {
      const entry = sr[d];
      if (typeof entry !== "object" || entry === null) {
        throw new ScoringResponseError(
          `Line "${lineId}" is missing dimension "${d}". Refusing to default it: an unscored dimension must stay unscored.`
        );
      }
      const e = entry as Record<string, unknown>;
      const value = Number(e.value);
      if (!Number.isInteger(value) || value < 1 || value > 5) {
        throw new ScoringResponseError(
          `Line "${lineId}" dimension "${d}" returned ${JSON.stringify(e.value)}, which is not an integer from 1 to 5.`
        );
      }
      const reasoning = typeof e.reasoning === "string" ? e.reasoning.trim() : "";
      if (!reasoning) {
        throw new ScoringResponseError(
          `Line "${lineId}" dimension "${d}" returned a score with no reasoning. A number without a justification is not usable in this report.`
        );
      }
      scores[d] = { value: value as ScoreValue, reasoning };
    }
    out.push({ line_id: lineId, scores });
  }

  const missing = expectedIds.filter((id) => !out.some((l) => l.line_id === id));
  if (missing.length > 0) {
    throw new ScoringResponseError(
      `Model did not score ${missing.length} line(s): ${missing.join(", ")}`
    );
  }
  return out;
}

export async function scoreLines(
  lines: ScoreRequestLine[],
  business: { name: string; positioning?: string; headcount?: number | null }
): Promise<{ lines: ScoredLine[]; provider: string; model: string }> {
  if (lines.length === 0) throw new ScoringResponseError("No lines to score");

  const result = await complete(buildSystemPrompt(), buildUserPrompt(lines, business));
  const parsed = extractJson<unknown>(result.text);
  const validated = validateResponse(
    parsed,
    lines.map((l) => l.id)
  );

  return { lines: validated, provider: result.provider, model: result.model };
}

export const __test = { buildSystemPrompt, validateResponse };
