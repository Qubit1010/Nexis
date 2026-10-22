/**
 * Bookmarks flow straight into Content OS (projects/content-os, 127.0.0.1:4600)
 * as ideas, alongside the Google Sheet write. Fire-and-forget with a short
 * timeout: if Content OS is not running, the sheet save still succeeds.
 */
export interface ContentOsIdea {
  title: string;
  url?: string | null;
  summary?: string | null;
  source: "youtube_topic" | "youtube_video" | "youtube_idea" | "news_article" | "practical_idea";
  sourceRef?: string | null;
  payload?: Record<string, unknown>;
}

export interface ContentOsResult {
  id: string;
  duplicate: boolean;
  seenCount: number;
}

export async function sendToContentOs(idea: ContentOsIdea): Promise<ContentOsResult | null> {
  const base = process.env.CONTENT_OS_URL || "http://127.0.0.1:4600";
  try {
    const res = await fetch(`${base}/api/ideas`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(idea),
      signal: AbortSignal.timeout(2500),
    });
    if (!res.ok) return null;
    return (await res.json()) as ContentOsResult;
  } catch {
    return null;
  }
}

/** Sheet + Content OS together: success if either one saved the item. */
export async function saveEverywhere<T>(sheetSave: () => Promise<T>, idea: ContentOsIdea) {
  const [sheet, contentOs] = await Promise.allSettled([sheetSave(), sendToContentOs(idea)]);
  const os = contentOs.status === "fulfilled" ? contentOs.value : null;
  return {
    sheet: sheet.status === "fulfilled" ? sheet.value : null,
    sheetError: sheet.status === "rejected" ? sheet.reason : null,
    contentOs: os,
    ok: sheet.status === "fulfilled" || !!os,
  };
}
