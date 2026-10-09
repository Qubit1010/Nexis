// One JSON-returning chat call with a provider chain:
// Anthropic direct (Haiku 4.5) -> Claude Haiku via OpenRouter -> OpenAI gpt-5.4-mini.
// Each hop has its own short timeout so a live demo never hangs; the caller falls back to the
// scripted brain if every provider fails.

type Msg = { role: "system" | "user"; content: string };

async function post(url: string, headers: Record<string, string>, body: unknown, ms: number): Promise<unknown> {
  const ctrl = new AbortController();
  const t = setTimeout(() => ctrl.abort(), ms);
  try {
    const res = await fetch(url, { method: "POST", signal: ctrl.signal,
      headers: { "content-type": "application/json", ...headers }, body: JSON.stringify(body) });
    if (!res.ok) throw new Error(`${res.status} ${(await res.text()).slice(0, 160)}`);
    return await res.json();
  } finally {
    clearTimeout(t);
  }
}

export function parseJson(text: string): Record<string, unknown> {
  const m = text.match(/\{[\s\S]*\}/);
  if (!m) throw new Error("no JSON object in model output");
  return JSON.parse(m[0]);
}

// Circuit breaker: a provider that just failed (no credit, outage) is skipped for 10 minutes so a
// live demo does not pay its timeout on every message.
const downUntil = new Map<string, number>();

export async function chatJson(system: string, user: string): Promise<{ data: Record<string, unknown>; provider: string }> {
  const msgs: Msg[] = [{ role: "system", content: system }, { role: "user", content: user }];
  const errors: string[] = [];
  const hops: [string, () => Promise<string>][] = [];
  if (process.env.ANTHROPIC_API_KEY) hops.push(["claude", async () => {
    const r = await post("https://api.anthropic.com/v1/messages",
      { "x-api-key": process.env.ANTHROPIC_API_KEY!, "anthropic-version": "2023-06-01" },
      { model: "claude-haiku-4-5-20251001", max_tokens: 700,
        system: [{ type: "text", text: system, cache_control: { type: "ephemeral" } }],
        messages: [{ role: "user", content: user }] }, 9000) as { content: { text?: string }[] };
    return r.content.map((b) => b.text ?? "").join("");
  }]);
  if (process.env.OPENROUTER_API_KEY) hops.push(["claude-openrouter", async () => {
    const r = await post("https://openrouter.ai/api/v1/chat/completions",
      { Authorization: `Bearer ${process.env.OPENROUTER_API_KEY}`, "X-Title": "NexusPoint demo" },
      { model: "anthropic/claude-haiku-4.5", max_tokens: 700, messages: msgs,
        response_format: { type: "json_object" } }, 10000) as { choices: { message: { content: string } }[] };
    return r.choices[0].message.content;
  }]);
  if (process.env.OPENAI_API_KEY) hops.push(["openai", async () => {
    const r = await post("https://api.openai.com/v1/chat/completions",
      { Authorization: `Bearer ${process.env.OPENAI_API_KEY}` },
      { model: "gpt-5.4-mini", max_completion_tokens: 1200, reasoning_effort: "low", messages: msgs,
        response_format: { type: "json_object" } }, 12000) as { choices: { message: { content: string } }[] };
    return r.choices[0].message.content;
  }]);
  for (const [name, fn] of hops) {
    if ((downUntil.get(name) ?? 0) > Date.now()) continue;
    try {
      return { data: parseJson(await fn()), provider: name };
    } catch (e) {
      const msg = (e as Error).message;
      errors.push(`${name}: ${msg}`);
      if (/^(400|401|402|403|429|5\d\d)|abort/i.test(msg)) downUntil.set(name, Date.now() + 600_000);
    }
  }
  throw new Error(`all providers failed: ${errors.join(" | ")}`);
}
