#!/usr/bin/env python3
"""Run AI analysis over crawl + pagespeed data and produce a structured audit.

Reads crawl data (from crawl_site.py) and pagespeed data (from pagespeed.py)
as JSON, either from --crawl-file / --pagespeed-file paths or piped via stdin
as a combined {"crawl": {...}, "pagespeed": {...}, "context": {...}} object.

Uses Claude Sonnet 4.6 to produce audit findings per the rubric in
references/audit-framework.md.

Usage:
    python analyze_audit.py --mode quick --crawl-file crawl.json --pagespeed-file ps.json
    cat combined.json | python analyze_audit.py --mode deep

Output (stdout): JSON audit
    {
      "mode": "quick" | "deep",
      "url": "...",
      "company": "...",
      "summary": "2-3 sentence executive summary",
      "findings": [
        {"dimension": "...", "severity": "critical|high|medium|low",
         "title": "...", "evidence": "...", "business_impact": "...",
         "fix": "...", "effort": "quick|medium|significant"}
      ],
      "scores": {"ux": 0-10, "seo": 0-10, "performance": 0-10, "conversion": 0-10}  // deep only
    }
"""

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FRAMEWORK_PATH = SKILL_DIR / "references" / "audit-framework.md"

MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 4096

# Budget how much crawl text we send to the model. ~20k chars per page keeps
# deep mode (up to 8 pages) within a sane prompt size.
PAGE_TEXT_BUDGET = 20_000


def error_exit(message: str):
    print(json.dumps({"status": "error", "message": message}))
    sys.exit(1)


def load_inputs(args):
    """Resolve crawl + pagespeed + context from CLI args or stdin."""
    crawl = None
    pagespeed = None
    context = {}

    if args.crawl_file:
        crawl = json.loads(Path(args.crawl_file).read_text(encoding="utf-8"))
    if args.pagespeed_file:
        pagespeed = json.loads(Path(args.pagespeed_file).read_text(encoding="utf-8"))

    if crawl is None or pagespeed is None:
        raw = sys.stdin.read().strip()
        if raw:
            combined = json.loads(raw)
            if crawl is None:
                crawl = combined.get("crawl")
            if pagespeed is None:
                pagespeed = combined.get("pagespeed")
            context = combined.get("context") or {}

    if not crawl:
        error_exit("No crawl data provided. Use --crawl-file or pipe combined JSON.")
    if pagespeed is None:
        pagespeed = {"status": "error", "notes": "PageSpeed not run"}

    # Merge CLI context overrides
    if args.company:
        context["company"] = args.company
    if args.industry:
        context["industry"] = args.industry

    return crawl, pagespeed, context


def condense_crawl(crawl: dict) -> str:
    """Build a compact text blob the model can reason over."""
    lines = [f"URL: {crawl.get('url')}", f"Mode: {crawl.get('mode')}", f"Pages: {crawl.get('page_count', 0)}", ""]
    for page in crawl.get("pages", []) or []:
        lines.append("=" * 60)
        lines.append(f"PAGE: {page.get('url')}")
        meta = page.get("metadata") or {}
        for key in ("title", "description", "ogTitle", "ogDescription", "language", "statusCode"):
            if meta.get(key):
                lines.append(f"  meta.{key}: {meta[key]}")
        markdown = (page.get("markdown") or "")[:PAGE_TEXT_BUDGET]
        lines.append("")
        lines.append("--- markdown ---")
        lines.append(markdown)
        html_snippet = (page.get("html_snippet") or "")[:4000]
        if html_snippet:
            lines.append("--- html head (truncated) ---")
            lines.append(html_snippet)
        lines.append("")
    return "\n".join(lines)


def condense_pagespeed(ps: dict) -> str:
    if not ps or ps.get("status") == "error":
        return f"PageSpeed: unavailable. Notes: {ps.get('notes', 'not run') if ps else 'not run'}"
    m = ps.get("mobile") or {}
    d = ps.get("desktop") or {}
    return (
        f"PageSpeed mobile: score={m.get('score', -1)}/100, "
        f"LCP={m.get('lcp', '?')}, CLS={m.get('cls', '?')}, TBT={m.get('tbt', '?')}, FCP={m.get('fcp', '?')}\n"
        f"PageSpeed desktop: score={d.get('score', -1)}/100, "
        f"LCP={d.get('lcp', '?')}, CLS={d.get('cls', '?')}, TBT={d.get('tbt', '?')}"
    )


def build_prompt(mode: str, crawl_text: str, ps_text: str, context: dict, framework: str) -> str:
    context_lines = []
    for key in ("company", "industry", "offer", "goal"):
        if context.get(key):
            context_lines.append(f"- {key}: {context[key]}")
    context_block = "\n".join(context_lines) if context_lines else "(none provided)"

    if mode == "quick":
        finding_guidance = (
            "Produce 3-5 findings total, prioritized by severity. This is a cold outreach opener, "
            "so favor findings that are specific, observable, and easy to tie to business impact. "
            "Do NOT include a scores object."
        )
    else:
        finding_guidance = (
            "Produce 8-14 findings covering all 4 dimensions. Include a scores object with a 1-10 "
            "score for each dimension (ux, seo, performance, conversion). This is a paid deliverable, "
            "so be thorough but not padded. Every finding must meet the writing rules."
        )

    return f"""You are auditing a prospect's website for NexusPoint, a digital agency. Use the framework below to produce a structured audit in strict JSON.

=== AUDIT FRAMEWORK ===
{framework}

=== PROSPECT CONTEXT ===
{context_block}

=== CRAWL DATA ===
{crawl_text}

=== PAGESPEED DATA ===
{ps_text}

=== INSTRUCTIONS ===
{finding_guidance}

Return ONLY a valid JSON object. No markdown, no preamble, no code fences. Schema:

{{
  "summary": "2-3 sentences. Honest but respectful. No fluff.",
  "company": "Business name as you'd address them",
  "findings": [
    {{
      "dimension": "UX & Messaging" | "SEO Basics" | "Performance" | "Conversion",
      "severity": "critical" | "high" | "medium" | "low",
      "title": "Under 60 chars, problem in plain English",
      "evidence": "Concrete observation. Quote actual copy or name the specific element.",
      "business_impact": "One sentence. Use ranges, not fake precision.",
      "fix": "One concrete recommendation a developer could act on.",
      "effort": "quick" | "medium" | "significant"
    }}
  ]{", \"scores\": {\"ux\": 0-10, \"seo\": 0-10, \"performance\": 0-10, \"conversion\": 0-10}" if mode == "deep" else ""}
}}

Critical rules:
- No em dashes anywhere. Use commas or periods.
- No emojis.
- No jargon without translation (e.g., "LCP" alone is bad; "main content takes 5+ seconds to load" is good).
- If PageSpeed is unavailable, omit Performance findings instead of guessing scores. Do not fabricate numbers.
- If evidence requires quoting the site's copy, quote it exactly.
"""


def extract_json(text: str) -> dict:
    text = text.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end <= start:
        raise ValueError("No JSON object in response")
    return json.loads(text[start:end])


def main():
    parser = argparse.ArgumentParser(description="Analyze crawl + pagespeed data into a structured audit")
    parser.add_argument("--mode", choices=["quick", "deep"], required=True)
    parser.add_argument("--crawl-file", help="Path to crawl JSON (from crawl_site.py)")
    parser.add_argument("--pagespeed-file", help="Path to pagespeed JSON (from pagespeed.py)")
    parser.add_argument("--company", help="Optional: company name for personalization")
    parser.add_argument("--industry", help="Optional: industry/vertical")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        error_exit("ANTHROPIC_API_KEY not set in environment")

    try:
        import anthropic
    except ImportError:
        error_exit("anthropic package not installed. Run: pip install anthropic")

    if not FRAMEWORK_PATH.exists():
        error_exit(f"Missing framework file: {FRAMEWORK_PATH}")
    framework = FRAMEWORK_PATH.read_text(encoding="utf-8")

    crawl, pagespeed, context = load_inputs(args)
    crawl_text = condense_crawl(crawl)
    ps_text = condense_pagespeed(pagespeed)
    prompt = build_prompt(args.mode, crawl_text, ps_text, context, framework)

    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        error_exit(f"Anthropic API call failed: {exc}")

    output_text = ""
    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            output_text += block.text

    try:
        audit = extract_json(output_text)
    except (ValueError, json.JSONDecodeError) as exc:
        error_exit(f"Could not parse JSON from model response: {exc} | raw: {output_text[:500]}")

    audit["mode"] = args.mode
    audit["url"] = crawl.get("url")
    audit.setdefault("company", context.get("company", ""))

    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
