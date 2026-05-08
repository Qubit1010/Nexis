import type { ScoreResponse } from "./types";

export async function scoreUrl(url: string): Promise<ScoreResponse> {
  const res = await fetch("/api/proxy/score", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  return (await res.json()) as ScoreResponse;
}
