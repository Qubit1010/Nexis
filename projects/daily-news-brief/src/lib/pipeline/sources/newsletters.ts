import Parser from "rss-parser";
import type { RawTool } from "./tool-types";

const parser = new Parser({
  timeout: 10000,
  headers: { "User-Agent": "DailyNewsBrief/1.0" },
});

// AI newsletters that consistently highlight new tools with use cases.
// Substack/Beehiiv feeds (Ben's Bites, Rundown AI) reject server-side fetches with 403,
// so we use feeds hosted on platforms that allow RSS clients without browser headers.
const NEWSLETTER_FEEDS = [
  { url: "https://tldr.tech/api/rss/ai", name: "TLDR AI" },
  { url: "https://www.marktechpost.com/feed/", name: "MarkTechPost" },
  { url: "https://buttondown.email/ainews/rss", name: "Smol AI News" },
];

const URL_REGEX = /(https?:\/\/[^\s<>"')]+)/g;

interface ExtractedTool {
  name: string;
  url: string;
  context: string;
}

// Newsletter posts mention many tools per issue. We need to extract each tool reference
// and treat each as a separate RawTool so the pipeline can score and categorize them.
function extractToolsFromContent(content: string, sourceName: string, pubDate: string): ExtractedTool[] {
  const tools: ExtractedTool[] = [];
  const seen = new Set<string>();

  // Strip HTML for context, but keep raw to find anchor texts
  const plain = content.replace(/<[^>]*>/g, " ").replace(/\s+/g, " ").trim();

  // Look for "**Name** — description" or "Name: description" patterns common in these newsletters
  const blockPatterns = [
    /\*\*([A-Z][A-Za-z0-9 .'&-]{2,40})\*\*\s*[-—–:]\s*([^*\n]{20,300})/g,
    /\b([A-Z][A-Za-z0-9.'&]{2,40}(?:\s[A-Z][A-Za-z0-9.'&]{0,20})?)\s+is\s+(?:a|an|the)\s+(new\s+)?(AI[- ])?(tool|app|platform|agent|model|service)\b[^.]{0,200}/g,
  ];

  for (const re of blockPatterns) {
    let m: RegExpExecArray | null;
    while ((m = re.exec(plain)) !== null) {
      const name = (m[1] || "").trim();
      const context = (m[2] || m[0]).trim();
      if (name.length < 3 || name.length > 50) continue;
      if (seen.has(name.toLowerCase())) continue;
      seen.add(name.toLowerCase());
      tools.push({ name, url: "", context: context.slice(0, 400) });
    }
  }

  // Also surface raw URLs as their own tools (newsletters often link directly to tool homepages)
  const urls = content.match(URL_REGEX) || [];
  for (const rawUrl of urls.slice(0, 20)) {
    const url = rawUrl.replace(/[).,]+$/, "");
    if (!url) continue;
    // Skip newsletter-internal links and social platforms
    if (
      url.includes("tldr.tech") ||
      url.includes("marktechpost.com") ||
      url.includes("buttondown.email") ||
      url.includes("substack.com") ||
      url.includes("convertkit") ||
      url.includes("beehiiv") ||
      url.includes("/unsubscribe") ||
      url.includes("twitter.com") ||
      url.includes("x.com") ||
      url.includes("youtube.com") ||
      url.includes("linkedin.com") ||
      url.includes("facebook.com") ||
      url.includes("reddit.com")
    ) {
      continue;
    }
    try {
      const u = new URL(url);
      const host = u.hostname.replace(/^www\./, "");
      const name = host.split(".")[0];
      if (name.length < 3 || seen.has(name.toLowerCase())) continue;
      seen.add(name.toLowerCase());
      tools.push({
        name: name.charAt(0).toUpperCase() + name.slice(1),
        url,
        context: `Linked from ${sourceName} on ${pubDate.slice(0, 10)}`,
      });
    } catch {
      // ignore invalid URLs
    }
  }

  return tools;
}

export async function fetchFromNewsletters(): Promise<RawTool[]> {
  const seenFeeds = new Set<string>();
  const feeds = NEWSLETTER_FEEDS.filter((f) => {
    if (seenFeeds.has(f.name)) return true; // keep retries — try alt URLs for same source
    seenFeeds.add(f.name);
    return true;
  });

  const results = await Promise.allSettled(
    feeds.map(async (feed) => {
      const parsed = await parser.parseURL(feed.url);
      const cutoff = new Date();
      cutoff.setDate(cutoff.getDate() - 3);

      const tools: RawTool[] = [];
      for (const item of parsed.items || []) {
        if (!item.title) continue;
        const pubDate = item.pubDate ? new Date(item.pubDate) : new Date();
        if (pubDate < cutoff) continue;

        const content = item["content:encoded"] || item.content || item.contentSnippet || "";
        const isoDate = pubDate.toISOString();

        const extracted = extractToolsFromContent(
          typeof content === "string" ? content : "",
          feed.name,
          isoDate
        );

        for (const tool of extracted) {
          tools.push({
            name: tool.name,
            tagline: tool.context.slice(0, 200),
            url: tool.url || item.link || "",
            source: feed.name,
            sourceOrigin: "tool-rss",
            publishedAt: isoDate,
            description: tool.context,
          });
        }
      }
      return tools;
    })
  );

  // Dedupe across the two Rundown URLs (one may be 404)
  const tools: RawTool[] = [];
  const dedupeKey = new Set<string>();
  for (const result of results) {
    if (result.status !== "fulfilled") {
      console.error("[Newsletters]", result.reason);
      continue;
    }
    for (const t of result.value) {
      const key = `${t.source}|${t.name.toLowerCase()}`;
      if (dedupeKey.has(key)) continue;
      dedupeKey.add(key);
      tools.push(t);
    }
  }

  console.log(`[Newsletters] Extracted ${tools.length} tool mentions`);
  return tools;
}
