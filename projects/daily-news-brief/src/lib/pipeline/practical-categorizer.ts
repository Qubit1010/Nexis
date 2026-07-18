import type { MarketingTopic } from "./practical-topics";
import type { PracticalItem } from "./sources/practical-index";

export interface CategorizedPractical {
  topic: MarketingTopic;
  items: PracticalItem[];
}

const MAX_ITEMS_PER_TOPIC = 12;

/**
 * Group evidence by the marketing topic that fetched it (items carry their
 * topic slug from the fetch layer — no keyword routing needed). Each topic is
 * capped and ordered by cross-source corroboration so the strongest evidence
 * leads.
 */
export function categorizePractical(
  items: PracticalItem[],
  topics: MarketingTopic[]
): CategorizedPractical[] {
  const result: CategorizedPractical[] = [];
  for (const topic of [...topics].sort((a, b) => a.sortOrder - b.sortOrder)) {
    const topicItems = items
      .filter((i) => i.domain === topic.slug)
      .sort((a, b) => (b.sourceCount ?? 1) - (a.sourceCount ?? 1))
      .slice(0, MAX_ITEMS_PER_TOPIC);
    result.push({ topic, items: topicItems });
    console.log(`[PracticalCategorizer] ${topic.name}: ${topicItems.length} items`);
  }
  return result;
}
