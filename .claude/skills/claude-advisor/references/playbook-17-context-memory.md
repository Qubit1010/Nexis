# Intermediate - Section 17: Context and Memory: How Claude Remembers

*Why Claude "forgets" you, and what to do about it.*

**Bottom line:** Claude has no persistent memory by default. Every new conversation starts blank. But there are three layers you can build to solve this: working memory (the conversation), persistent memory (Projects and the memory feature), and a knowledge base (reference documents). Understanding these three layers is what separates people who fight Claude's amnesia from people who have solved it.

---

## The three layers of Claude's memory

### Layer 1: Working memory (the conversation)

This is the context window, everything Claude can "see" in the current conversation. It includes your messages, its replies, any files you uploaded, and the content of any Skills or system context loaded at the start. It is powerful (up to one million tokens in the largest models) but temporary: it ends when the conversation ends.

**Context rot:** As conversations grow very long, early parts fall out of the active window or get compressed. You will notice this when Claude stops referencing something it knew earlier in the session, or when its answers start to drift. Signs of context rot: repetition, contradictions with earlier context, generic answers on topics it was specific about before.

**Fix:** Start a new conversation, re-load the relevant context, or break the task into smaller sessions.

### Layer 2: Persistent memory (Projects and the memory feature)

This is how you make Claude remember across conversations:

- **Projects:** Upload reference files and set custom instructions once. Every conversation inside a Project starts with that context already loaded. This is the primary tool for persistent context. One Project per role or per client.
- **The memory feature:** When enabled (in account settings), Claude can store and retrieve facts about you across conversations. It builds a lightweight profile: your preferences, your role, recurring details you have told it. This is best for personal facts and preferences; Projects are better for substantial operational context.

### Layer 3: Knowledge base (reference documents)

For large, stable bodies of knowledge (a full client brief, a product spec, a methodology document, a research archive), the answer is not to paste it into every conversation. It is to upload it into a Project and let Claude access it whenever it is relevant.

Good candidates for knowledge base documents:
- Your brand guide and tone-of-voice document
- A client's business overview
- A research synthesis you reference repeatedly
- Your standard operating procedures

## Let Claude help build your context

One of the fastest ways to build a useful Project is to let Claude structure it for you. Start a conversation and say: "I am going to describe my work and context. Help me identify what should go in a Project for this role, what custom instructions would help, and what documents I should upload." Claude will interview you and produce a setup plan.

## Signs of context rot and fixes

| Sign | Likely cause | Fix |
|------|-------------|-----|
| Claude gives generic advice on a topic it was specific about earlier | Early context has been compressed | Start a new session, re-load the key context |
| It repeats something it already did | Long conversation, context drift | Restart with a summary of where you are |
| Contradicts itself between messages | Very long session | Break the task into shorter sessions |

## Key takeaways

- Three layers: working memory (the conversation), persistent memory (Projects + memory feature), knowledge base (uploaded reference docs).
- Context rot happens in very long conversations. Watch for it and start fresh when you see the signs.
- Projects are the primary tool for persistent context. Set up one per role or client.
- The memory feature stores personal facts across conversations. Projects store operational context. Both are useful; they are not substitutes for each other.
