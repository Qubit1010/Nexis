# Intermediate - Section 13: Choosing the Right Claude Model

*One choice that affects speed, cost, and quality on every task.*

**Bottom line:** Claude comes in four models, each with a different speed-intelligence tradeoff. The default (Sonnet) handles about 80 percent of tasks well. The other three cover the extremes. Master the pattern once and you will make a better call in five seconds.

---

## The model family

| Model | Analogy | Speed | Cost | Best for |
|-------|---------|-------|------|----------|
| Haiku | The fast intern | Fastest | Lowest | Volume tasks, quick summaries, real-time responses, anything where speed matters more than depth |
| Sonnet | The reliable senior | Fast | Mid | Most everyday work, the smart default for 80% of tasks |
| Opus | The expert specialist | Slower | Highest | Complex reasoning, nuanced judgment, high-stakes writing where quality matters more than speed |
| Fable | The marathoner | Variable | High | Very long documents, extended multi-step reasoning, tasks that need a huge context window |

## The simple rule

**Start on Sonnet.** Upgrade to Opus when the task demands it. Downgrade to Haiku when you need speed or volume. Consider Fable when the document or task is unusually large.

Most professionals using Claude for work operate on Sonnet the vast majority of the time and rarely need to change.

## The 70/20/10 pro pattern

Once you are using Claude intensively and thinking about cost, this is the sustainable routing pattern:

- **70% on Haiku:** Fast, routine work. Processing lists, quick summaries, first-pass drafts, formatting tasks.
- **20% on Sonnet:** Standard professional work. Analysis, solid drafts, client-facing output.
- **10% on Opus:** The hardest decisions. Complex strategy, nuanced editing, anything where quality genuinely moves the needle.

This pattern keeps cost manageable while reserving the best model for the work that benefits from it.

## Token costs matter at scale

If you are building automations or running Claude at high volume through the API, the cost difference between models is significant. Haiku is a fraction of the cost of Opus per token. For automated pipelines processing thousands of items, routing to Haiku for routine steps and only escalating to Sonnet or Opus for decisions can cut costs by 80 percent or more.

## The mistake to avoid

Using Opus for everything feels like you are getting the best output, but you are paying the highest cost and accepting the slowest speed for work that Sonnet handles equally well. Conversely, using Haiku for everything misses the judgment and quality that Sonnet or Opus bring to the work that actually matters. Match the model to the task.

> **Quick rule:** Sonnet for the work day. Haiku when you need volume or speed. Opus when you cannot afford to get it wrong or when the reasoning is genuinely complex. Fable when the document is enormous.

## Key takeaways

- Four models: Haiku (fast/light), Sonnet (reliable default), Opus (deep specialist), Fable (long-context marathoner).
- Start on Sonnet. It handles about 80 percent of professional use cases well.
- The 70/20/10 pattern (Haiku/Sonnet/Opus) is sustainable and cost-efficient for intensive users.
- At API scale, model routing saves substantial money. Automate the Haiku steps; reserve Opus for genuine decisions.
