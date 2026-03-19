/**
 * Retry wrapper with exponential backoff.
 */
export async function withRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 1,
  baseDelay = 1000
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      if (attempt === maxRetries) throw error;
      const delay = baseDelay * Math.pow(2, attempt);
      console.warn(
        `[Retry] Attempt ${attempt + 1} failed, retrying in ${delay}ms...`
      );
      await new Promise((r) => setTimeout(r, delay));
    }
  }
  throw new Error("Unreachable");
}

/**
 * Extract the first balanced JSON object from text.
 * Handles cases where LLM wraps JSON in markdown fences or adds extra text.
 */
export function extractJSON(text: string): string | null {
  // Strip markdown code fences first
  const cleaned = text
    .replace(/^```(?:json)?\s*\n?/m, "")
    .replace(/\n?\s*```\s*$/m, "");

  // Try direct parse first
  try {
    JSON.parse(cleaned);
    return cleaned;
  } catch {
    // Fall through to balanced-brace extraction
  }

  // Find first balanced JSON object
  let depth = 0;
  let start = -1;
  for (let i = 0; i < cleaned.length; i++) {
    if (cleaned[i] === "{") {
      if (depth === 0) start = i;
      depth++;
    } else if (cleaned[i] === "}") {
      depth--;
      if (depth === 0 && start !== -1) {
        return cleaned.slice(start, i + 1);
      }
    }
  }
  return null;
}

/**
 * Normalized Levenshtein similarity (0-1, where 1 = identical).
 */
export function titleSimilarity(a: string, b: string): number {
  const na = a.toLowerCase().replace(/[^\w\s]/g, "").trim();
  const nb = b.toLowerCase().replace(/[^\w\s]/g, "").trim();
  if (na === nb) return 1;

  const maxLen = Math.max(na.length, nb.length);
  if (maxLen === 0) return 1;

  // Simple Levenshtein
  const matrix: number[][] = [];
  for (let i = 0; i <= na.length; i++) {
    matrix[i] = [i];
  }
  for (let j = 0; j <= nb.length; j++) {
    matrix[0][j] = j;
  }
  for (let i = 1; i <= na.length; i++) {
    for (let j = 1; j <= nb.length; j++) {
      const cost = na[i - 1] === nb[j - 1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i - 1][j] + 1,
        matrix[i][j - 1] + 1,
        matrix[i - 1][j - 1] + cost
      );
    }
  }

  return 1 - matrix[na.length][nb.length] / maxLen;
}
