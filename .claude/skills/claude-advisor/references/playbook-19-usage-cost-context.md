# Intermediate - Section 19: Usage, Cost, and Context Windows Explained

*What you are actually paying for and how to get more from it.*

**Bottom line:** Claude charges for tokens (chunks of text), not for time. Understanding how usage works, what burns through it fastest, and which habits preserve it lets you get significantly more value from the same plan without upgrading.

---

## How usage actually works

Claude does not bill by the minute or per question. It charges for **tokens**, pieces of text roughly four characters each. Every time you send a message, the full conversation, including everything Claude can currently see, gets tokenized and counts toward usage.

The key insight: **every message carries the full conversation cost.** A 50-message conversation where each message is long can cost more in a single session than 10 short sessions. This is why context rot appears as conversations extend: the system is compressing earlier content to manage the window, not just forgetting randomly.

Usage on paid plans runs on a **rolling window** (typically five hours), not a monthly counter. You can run as intensively as you want, but hitting the ceiling within a window means waiting for the window to reset.

## What burns allowance fastest

- **Very long conversations:** Every message re-sends the full context.
- **Large file uploads:** A 200-page PDF loaded into a conversation counts toward the window on every subsequent message.
- **Running Opus for routine tasks:** The most capable model costs the most per token.
- **Cowork or Code sessions with many tool calls:** Each tool call and result adds to the context.

## Token-smart habits

- **Start a new conversation when the topic changes significantly.** Do not carry old context you no longer need.
- **Summarize and compact.** For long sessions, ask Claude "summarize everything we have decided so far in under 300 words." Start a new session with that summary as the opening context.
- **Upload files selectively.** If you have a 300-page document but only care about three sections, paste those sections rather than uploading the full file.
- **Route routine work to Haiku.** Quick questions, first-pass summaries, and formatting tasks do not need Sonnet. Haiku does them faster at lower cost.
- **Use Projects for standing context.** Project documents count differently than in-conversation uploads; they are loaded once and shared efficiently across sessions.

## Upgrade vs get efficient: when each makes sense

| You should get more efficient if... | You should upgrade your plan if... |
|-------------------------------------|-----------------------------------|
| You often carry old context you do not need | You consistently hit the ceiling mid-project on important work |
| You use Opus for tasks Haiku would handle | You run multiple long sessions every single day |
| You upload entire documents when you need sections | You are building automations that need unlimited throughput |
| You rarely think about what you are asking | Efficiency gains have not solved the problem after trying |

## Technical extra: context window sizes

Different models have different maximum context windows. Smaller models like Haiku have smaller windows. Opus and the top Sonnet variants support up to one million tokens, which is roughly several thick books. For most everyday use cases you will not come close to these limits. They become relevant when processing very large documents, running very long agent sessions, or building specialized systems.

## Key takeaways

- Claude charges for tokens. Every message re-sends the full conversation, so long conversations cost proportionally more.
- Usage runs on rolling windows, not monthly counters. Heavy short bursts can drain your allowance faster than spread-out use.
- The biggest efficiency gains come from: starting new sessions when topics shift, routing routine work to Haiku, and uploading only the relevant parts of large documents.
- Upgrade when efficiency habits cannot solve the problem. Optimize first.
