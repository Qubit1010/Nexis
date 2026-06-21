export interface OpenRouterModel {
  id: string;
  name: string;
  created?: number; // unix seconds
  description?: string;
}

/**
 * Best-effort "what's new in models" signal. OpenRouter has no stable public
 * usage-ranking endpoint, so we use the public model list and surface the NEWEST
 * models (by `created`) as a proxy for what's freshly available. Fails open.
 */
export async function fetchOpenRouterNewModels(limit = 6): Promise<OpenRouterModel[]> {
  try {
    const res = await fetch("https://openrouter.ai/api/v1/models", {
      headers: { "User-Agent": "DailyNewsBrief/1.0" },
    });
    if (!res.ok) throw new Error(`OpenRouter models: ${res.status}`);
    const json = (await res.json()) as { data?: OpenRouterModel[] };
    const models = json.data || [];
    return models
      .filter((m) => typeof m.created === "number")
      .sort((a, b) => (b.created || 0) - (a.created || 0))
      .slice(0, limit);
  } catch (error) {
    console.error("[OpenRouter] Error (skipping):", error);
    return [];
  }
}
