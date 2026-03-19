import type { RawArticle } from "./sources/types";
import type { Category } from "./categories";

export interface CategorizedArticles {
  category: Category;
  articles: RawArticle[];
}

function scoreArticleForCategory(
  article: RawArticle,
  category: Category
): number {
  const text = `${article.title} ${article.description}`.toLowerCase();
  let score = 0;
  for (const keyword of category.keywords) {
    if (text.includes(keyword.toLowerCase())) {
      score++;
    }
  }
  return score;
}

export function categorizeArticles(
  articles: RawArticle[],
  categories: Category[]
): CategorizedArticles[] {
  const buckets = new Map<string, RawArticle[]>();
  for (const cat of categories) {
    buckets.set(cat.slug, []);
  }

  let uncategorizedCount = 0;

  for (const article of articles) {
    let bestCat: Category | null = null;
    let bestScore = 0;

    for (const cat of categories) {
      const score = scoreArticleForCategory(article, cat);
      if (score > bestScore) {
        bestScore = score;
        bestCat = cat;
      }
    }

    if (bestCat && bestScore > 0) {
      buckets.get(bestCat.slug)!.push(article);
    } else {
      uncategorizedCount++;
    }
  }

  if (uncategorizedCount > 0) {
    const pct = Math.round((uncategorizedCount / articles.length) * 100);
    console.log(
      `[Categorizer] ${uncategorizedCount} articles could not be categorized (${pct}%)`
    );
    if (pct > 20) {
      console.warn(
        `[Categorizer] Warning: ${pct}% uncategorized — consider expanding keywords`
      );
    }
  }

  const result: CategorizedArticles[] = categories.map((cat) => {
    const catArticles = buckets.get(cat.slug) || [];
    // Sort by engagement score (if available) then by date
    catArticles.sort((a, b) => {
      const engDiff = (b.engagementScore ?? 0) - (a.engagementScore ?? 0);
      if (engDiff !== 0) return engDiff;
      return (
        new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime()
      );
    });
    // Cap at 12 articles per category
    return { category: cat, articles: catArticles.slice(0, 12) };
  });

  const totalCategorized = result.reduce(
    (sum, r) => sum + r.articles.length,
    0
  );
  console.log(
    `[Categorizer] ${totalCategorized} articles categorized across ${categories.length} categories`
  );
  for (const r of result) {
    console.log(`  ${r.category.name}: ${r.articles.length} articles`);
  }

  return result;
}
