"""Personalization engine — generates custom outreach intelligence per lead.

Uses OpenAI API (gpt-4o-mini) to produce:
  - 3 personalized opener hook options
  - 2-3 pain points with evidence and NexusPoint solution
  - Tailored value proposition
  - Best channel recommendation with reasoning

Called for HOT and STRONG tier leads only.
WARM leads get template-based hooks from the transformers.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import NEXUSPOINT_CONTEXT, PERSONALIZATION
from utils.rate_limit import retry, sleep_between


def get_openai_client():
    """Get OpenAI client. Lazy import to avoid hard dependency at module load."""
    try:
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY not set")
        return OpenAI(api_key=api_key)
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")


def build_lead_context(lead: dict, enrichment: dict = None) -> str:
    """Build a rich context string about the lead for the personalization prompt."""
    parts = []

    parts.append(f"Lead: {lead.get('full_name') or lead.get('first_name', '')} {lead.get('last_name', '')}")
    parts.append(f"Title: {lead.get('title', 'Unknown')}")
    parts.append(f"Company: {lead.get('company', 'Unknown')}")

    if lead.get("industry"):
        parts.append(f"Industry: {lead['industry']}")
    if lead.get("company_size"):
        parts.append(f"Company size: {lead['company_size']} employees")
    if lead.get("company_website"):
        parts.append(f"Website: {lead['company_website']}")
    if lead.get("location"):
        parts.append(f"Location: {lead['location']}")
    if lead.get("pain_signal"):
        parts.append(f"Pain signal: {lead['pain_signal']}")
    if lead.get("recent_activity"):
        parts.append(f"Recent activity: {lead['recent_activity'][:300]}")
    if lead.get("funding_signal"):
        parts.append("Funding signal: Yes (recent launch or funding)")

    if enrichment:
        if enrichment.get("company_news"):
            parts.append(f"Company news: {enrichment['company_news'][:400]}")
        if enrichment.get("funding_news"):
            parts.append(f"Funding news: {enrichment['funding_news'][:200]}")

        website_tech = enrichment.get("website_tech", {})
        if isinstance(website_tech, str):
            try:
                website_tech = json.loads(website_tech)
            except (json.JSONDecodeError, TypeError):
                website_tech = {}
        if website_tech.get("cms") and website_tech["cms"] != "unknown":
            parts.append(f"Website CMS: {website_tech['cms']}")

        pagespeed = enrichment.get("pagespeed_mobile", -1)
        if isinstance(pagespeed, (int, float)) and pagespeed >= 0:
            parts.append(f"Website PageSpeed (mobile): {pagespeed}/100")

        recent_posts = enrichment.get("recent_posts", [])
        if isinstance(recent_posts, str):
            try:
                recent_posts = json.loads(recent_posts)
            except (json.JSONDecodeError, TypeError):
                recent_posts = []
        if recent_posts:
            post_texts = [p.get("text", "")[:200] for p in recent_posts[:2] if p.get("text")]
            if post_texts:
                parts.append(f"Recent LinkedIn posts: {' | '.join(post_texts)}")

    return "\n".join(parts)


SYSTEM_PROMPT = f"""You are NexusPoint's lead research analyst.

{NEXUSPOINT_CONTEXT}"""

USER_PROMPT_TEMPLATE = """Here is the lead you need to research and prepare outreach intelligence for:

{lead_context}

---

Based on this information, generate a personalization package. Be specific and evidence-based.
Every hook and pain point MUST reference something concrete from the lead's data above.
If a signal isn't available, skip that hook type — don't make up generic hooks.

Respond ONLY with valid JSON in exactly this format:
{{
  "hook_1": "Personalized opener based on website tech/performance (empty string if no website data)",
  "hook_2": "Personalized opener based on job posting or pain signal (empty string if no pain data)",
  "hook_3": "Personalized opener based on funding, PH launch, or recent news (empty string if no signal)",
  "pain_points": [
    {{
      "pain": "Specific problem statement",
      "evidence": "What signal in the data revealed this",
      "solution": "How NexusPoint specifically solves this"
    }}
  ],
  "value_prop": "One sentence connecting NexusPoint's services to their specific situation",
  "social_proof": "The most relevant NexusPoint result/capability for this industry and stage",
  "best_channel": "cold_email or linkedin or instagram",
  "channel_reasoning": "Why this channel for this specific lead (1 sentence)"
}}

Rules for hooks:
- Under 2 sentences each
- Must reference something specific about this lead
- No pitch — just an observation or question that shows you did your homework
- If you reference PageSpeed, mention the actual score
- If you reference their CMS, be specific (e.g., "your Wix site" not "your website")
- Empty string if there's no evidence for that hook type

Rules for pain_points:
- 2-3 pain points only
- Each must reference specific evidence from the lead's data
- Solutions must be specific to NexusPoint's actual services

Respond with JSON only — no markdown, no explanation."""


@retry(max_attempts=2, base_delay=5.0, exceptions=(Exception,))
def generate_personalization(lead: dict, enrichment: dict = None) -> dict:
    """Generate personalization package for a lead using OpenAI API.

    Args:
        lead: Lead dict from DB
        enrichment: Enrichment dict from DB (optional but improves quality)

    Returns:
        Personalization dict matching the personalization table schema
    """
    client = get_openai_client()
    model = PERSONALIZATION["model"]
    max_tokens = PERSONALIZATION["max_tokens"]

    lead_context = build_lead_context(lead, enrichment)
    user_prompt = USER_PROMPT_TEMPLATE.format(lead_context=lead_context)

    print(f"  Personalizing: {lead.get('full_name', '?')} @ {lead.get('company', '?')}", flush=True)

    response = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content.strip()

    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        print(f"  OpenAI returned invalid JSON: {exc}", flush=True)
        return _fallback_personalization(lead)

    result = {
        "hook_1": data.get("hook_1", ""),
        "hook_2": data.get("hook_2", ""),
        "hook_3": data.get("hook_3", ""),
        "pain_points": data.get("pain_points", []),
        "value_prop": data.get("value_prop", ""),
        "social_proof": data.get("social_proof", ""),
        "best_channel": data.get("best_channel", "cold_email"),
        "channel_reasoning": data.get("channel_reasoning", ""),
    }

    sleep_between(1.0, 2.0)
    return result


def _fallback_personalization(lead: dict) -> dict:
    """Template-based fallback when OpenAI API fails or for WARM leads."""
    company = lead.get("company", "your company")
    industry = lead.get("industry", "your industry")
    pain = lead.get("pain_signal", "")

    return {
        "hook_1": f"I looked at {company}'s setup and have some thoughts on what could be improved.",
        "hook_2": f"Noticed {pain}" if pain else f"Wondering if {company} is running into any scaling bottlenecks.",
        "hook_3": "",
        "pain_points": [
            {
                "pain": f"Growing {industry} companies often struggle with manual operational tasks.",
                "evidence": "Industry pattern",
                "solution": "NexusPoint builds automation systems that handle these tasks without adding headcount.",
            }
        ],
        "value_prop": f"NexusPoint helps {industry} companies like {company} automate their operations and build tech that scales.",
        "social_proof": "We've built AI automation + web systems for founders at similar growth stages.",
        "best_channel": "cold_email",
        "channel_reasoning": "Cold email allows for detailed personalization with the pain signal context.",
    }


def generate_personalization_with_fallback(lead: dict, enrichment: dict = None) -> dict:
    """Generate personalization, falling back to templates if OpenAI is unavailable."""
    try:
        return generate_personalization(lead, enrichment)
    except (EnvironmentError, ImportError) as exc:
        print(f"  OpenAI API unavailable ({exc}) — using template fallback.", flush=True)
        return _fallback_personalization(lead)
