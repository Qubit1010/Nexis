// Port of Sixty Second Responder src/responder/guards.py: clean a model reply and flag
// anything that must never reach a customer (empty text, unfilled placeholders, "as an AI" leaks).

const AI_LEAK = /\b(as an ai|as a language model|i am an ai|i'm an ai|large language model|openai|anthropic|chatgpt)\b/i;
const PLACEHOLDER = /(\{[^}]*\}|\[[^\]]*\]|<[^>]+>|TODO|XXX)/;

export function clean(text: string, maxChars = 700): string {
  let t = (text ?? "").replace(/—|–/g, ", ").replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();
  t = t.replace(/^(business|assistant)\s*:\s*/i, "");
  if (t.length > maxChars) {
    const cut = t.slice(0, maxChars);
    const end = Math.max(cut.lastIndexOf(". "), cut.lastIndexOf("۔"), cut.lastIndexOf("? "));
    t = end > 200 ? cut.slice(0, end + 1) : cut;
  }
  return t;
}

export function problems(text: string): string[] {
  const out: string[] = [];
  if (!text.trim()) out.push("empty");
  if (PLACEHOLDER.test(text)) out.push("placeholder");
  if (AI_LEAK.test(text)) out.push("ai-leak");
  return out;
}
