import type { RawTool } from "./tool-types";

const HF_API = "https://huggingface.co/api";

interface HFSpace {
  id: string;
  author?: string;
  likes?: number;
  trendingScore?: number;
  cardData?: {
    title?: string;
    short_description?: string;
    sdk?: string;
  };
  lastModified?: string;
}

interface HFModel {
  id: string;
  author?: string;
  likes?: number;
  downloads?: number;
  trendingScore?: number;
  pipeline_tag?: string;
  lastModified?: string;
}

// We're after Spaces (live demos people can try) and Models (new releases)
// trendingScore sort gives the freshest interesting items.

async function fetchSpaces(): Promise<RawTool[]> {
  const url = `${HF_API}/spaces?sort=trendingScore&direction=-1&limit=30`;
  const res = await fetch(url, {
    headers: { "User-Agent": "DailyNewsBrief/1.0", Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`HF Spaces: ${res.status}`);
  const data = (await res.json()) as HFSpace[];

  return data.map((s) => {
    const title =
      s.cardData?.title ||
      s.id.split("/").pop() ||
      s.id;
    const desc =
      s.cardData?.short_description ||
      `Interactive demo by ${s.author || s.id.split("/")[0]}${s.cardData?.sdk ? ` (${s.cardData.sdk})` : ""}`;
    return {
      name: title.replace(/^[\s_-]+|[\s_-]+$/g, ""),
      tagline: desc.slice(0, 200),
      url: `https://huggingface.co/spaces/${s.id}`,
      source: "Hugging Face Spaces",
      sourceOrigin: "tool-rss",
      publishedAt: s.lastModified || new Date().toISOString(),
      description: desc,
      upvotes: s.likes ?? 0,
    } satisfies RawTool;
  });
}

async function fetchModels(): Promise<RawTool[]> {
  const url = `${HF_API}/models?sort=trendingScore&direction=-1&limit=20`;
  const res = await fetch(url, {
    headers: { "User-Agent": "DailyNewsBrief/1.0", Accept: "application/json" },
  });
  if (!res.ok) throw new Error(`HF Models: ${res.status}`);
  const data = (await res.json()) as HFModel[];

  return data
    // Only surface task-tagged models that are usable as tools, not raw research checkpoints
    .filter((m) =>
      m.pipeline_tag &&
      [
        "text-generation",
        "image-to-image",
        "text-to-image",
        "text-to-video",
        "text-to-speech",
        "automatic-speech-recognition",
        "image-to-text",
        "video-classification",
        "translation",
      ].includes(m.pipeline_tag)
    )
    .map((m) => {
      const name = m.id.split("/").pop() || m.id;
      return {
        name,
        tagline: `${m.pipeline_tag} model by ${m.author || m.id.split("/")[0]}`,
        url: `https://huggingface.co/${m.id}`,
        source: "Hugging Face Models",
        sourceOrigin: "tool-rss",
        publishedAt: m.lastModified || new Date().toISOString(),
        description: `${m.pipeline_tag} model. ${(m.downloads ?? 0).toLocaleString()} downloads, ${m.likes ?? 0} likes on Hugging Face.`,
        upvotes: m.likes ?? 0,
      } satisfies RawTool;
    });
}

export async function fetchFromHuggingFace(): Promise<RawTool[]> {
  const [spaces, models] = await Promise.allSettled([fetchSpaces(), fetchModels()]);

  const tools: RawTool[] = [];
  if (spaces.status === "fulfilled") tools.push(...spaces.value);
  else console.error("[HF Spaces]", spaces.reason);
  if (models.status === "fulfilled") tools.push(...models.value);
  else console.error("[HF Models]", models.reason);

  console.log(`[HuggingFace] Fetched ${tools.length} trending items (spaces + models)`);
  return tools;
}
