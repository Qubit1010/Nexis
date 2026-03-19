import type { RawArticle } from "./sources/types";

function normalizeTitle(title: string): string {
  return title
    .toLowerCase()
    .replace(/[^\w\s]/g, "")
    .replace(/\s+/g, " ")
    .trim();
}

function titlesMatch(a: string, b: string): boolean {
  const na = normalizeTitle(a);
  const nb = normalizeTitle(b);
  if (na === nb) return true;
  // Check if one title contains 80%+ of the other
  const shorter = na.length < nb.length ? na : nb;
  const longer = na.length < nb.length ? nb : na;
  if (shorter.length < 10) return false;
  return longer.includes(shorter);
}

export function deduplicateArticles(articles: RawArticle[]): RawArticle[] {
  const groups: RawArticle[][] = [];

  for (const article of articles) {
    let foundGroup = false;
    for (const group of groups) {
      if (titlesMatch(article.title, group[0].title)) {
        group.push(article);
        foundGroup = true;
        break;
      }
    }
    if (!foundGroup) {
      groups.push([article]);
    }
  }

  const deduplicated: RawArticle[] = groups.map((group) => {
    // Pick the article with the richest description
    const best = group.reduce((a, b) =>
      (b.description?.length || 0) > (a.description?.length || 0) ? b : a
    );

    // Merge engagement scores (take highest)
    const maxEngagement = Math.max(
      ...group.map((a) => a.engagementScore ?? 0)
    );
    const maxComments = Math.max(
      ...group.map((a) => a.commentCount ?? 0)
    );

    return {
      ...best,
      sourceCount: group.length,
      engagementScore: maxEngagement || undefined,
      commentCount: maxComments || undefined,
    };
  });

  const removed = articles.length - deduplicated.length;
  if (removed > 0) {
    console.log(
      `[Dedup] Removed ${removed} duplicates (${articles.length} → ${deduplicated.length})`
    );
  }

  return deduplicated;
}
