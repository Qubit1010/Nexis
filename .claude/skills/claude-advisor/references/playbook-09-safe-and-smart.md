# Beginner - Section 9: Using Claude Safely and Smartly

*What to share, what to keep out, and when to verify.*

**Bottom line:** Claude is safe enough for most business use cases as long as you apply one principle: treat it like a capable contractor, not an employee under NDA. Sensitive information requires judgment, not paranoia. And everything consequential needs a human check before it goes live.

---

## What is safe to share vs what to keep out

| Safe to share | Keep out |
|---------------|----------|
| Work documents and reports | Passwords, API keys, secrets |
| Marketing copy and briefs | Personally identifiable information for people who have not consented |
| Your own strategic thinking | Client data covered by a confidentiality agreement (check the terms) |
| Research questions | Proprietary data with high competitive sensitivity (use judgment) |
| General financial summaries | Specific client financial records (verify your obligations) |

The practical rule: if it would cause real damage if it appeared publicly, or if there is a contractual reason it cannot leave your organization, keep it out or anonymize it.

## How Anthropic handles your data

Anthropic has a privacy policy that governs what happens to your conversations. Key facts to know:

- By default on the free and Pro plans, conversations may be used to improve Claude's models. This can be turned off in your account settings under Data Controls.
- Teams and Enterprise plans have different data retention and training terms. Read the applicable policies if you are handling client data or sensitive organizational information.
- The data goes to Anthropic's servers. You are not "local-only" unless you run a Claude model on your own infrastructure, which is an advanced API use case.

## Verify what matters

Claude is comparatively accurate but not infallible. Apply verification effort proportional to the stakes:

- **Low stakes (brainstorming, drafting, internal summaries):** Use the output and move on.
- **Medium stakes (external communications, client-facing content):** Read it carefully and fact-check any specific claims before sending.
- **High stakes (legal language, medical advice, financial decisions, anything permanent):** Treat Claude as a smart first draft, not a final answer. Get a qualified human to review before acting.

## When NOT to use Claude

- **If accurate, real-time data is required:** Claude has a knowledge cutoff. Use web search for current information, but verify anything critical from a primary source.
- **For final legal, medical, or financial decisions:** These require qualified professionals. Claude can help you understand or draft, but the decision and accountability stay with a human.
- **When you cannot verify the output:** If you are in a domain where you cannot tell whether Claude is right, add expert review. Do not skip it because the answer sounds confident.

> **The mindset:** Claude is a high-quality first draft of almost everything. It saves you the blank-page problem and accelerates the 80 percent. The last 20 percent, the part that goes live, signs a contract, or gives medical advice, stays with you.

## Key takeaways

- Treat Claude like a capable contractor: give it real work, but apply judgment about what to share.
- Turn off training data use in account settings if you are handling sensitive material.
- Verify proportionally: light for internal drafts, thorough for external or high-stakes output.
- There are categories where Claude helps you think and draft, but a qualified human makes the final call: legal, medical, financial, and anything that cannot be undone.
