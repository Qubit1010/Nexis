"""Company news intelligence via OpenAI web search.

Uses gpt-4o-mini-search-preview to find recent news, funding rounds, and
product announcements for each lead's company.

Replaces Perplexity — same intent, uses the OPENAI_API_KEY already in .env.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.rate_limit import retry, sleep_between


def get_openai_client():
    try:
        from openai import OpenAI
        api_key = os.environ.get("OPENAI_API_KEY", "").strip()
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY not set")
        return OpenAI(api_key=api_key)
    except ImportError:
        raise ImportError("openai package not installed. Run: pip install openai")


@retry(max_attempts=2, base_delay=3.0, exceptions=(Exception,))
def query_web(question: str) -> str:
    """Search the web via OpenAI gpt-4o-mini-search-preview.

    Returns:
        Answer string or "" on failure
    """
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4o-mini-search-preview",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a business researcher. Answer concisely and factually. "
                        "Focus on recent news, funding, and growth signals from 2024-2025. "
                        "If you can't find information, say 'No recent information found.' "
                        "Do not speculate. Keep answers to 3-4 sentences max."
                    ),
                },
                {"role": "user", "content": question},
            ],
        )
        return response.choices[0].message.content.strip()
    except (EnvironmentError, ImportError) as exc:
        print(f"  News intel skipped: {exc}", flush=True)
        return ""
    except Exception as exc:
        print(f"  OpenAI web search failed: {exc}", flush=True)
        return ""


def enrich_news(lead: dict) -> dict:
    """Research company news and funding for a lead.

    Args:
        lead: Lead dict from DB

    Returns:
        Enrichment data dict with company_news and funding_news
    """
    company = (lead.get("company") or "").strip()
    if not company:
        return {}

    print(f"  News intel: {company}", flush=True)

    question = (
        f"What are the most recent news, funding rounds, or product launches for "
        f"'{company}'? When did they last raise funding and how much? "
        f"Any recent product announcements or major changes in 2024-2025?"
    )
    company_news = query_web(question)

    # Extract funding-specific sentence if present
    funding_news = ""
    if company_news and any(kw in company_news.lower() for kw in ["raised", "funding", "million", "series", "seed", "round"]):
        for line in company_news.split("."):
            if any(kw in line.lower() for kw in ["raised", "funding", "million", "series", "seed", "round"]):
                funding_news = line.strip() + "."
                break

    if not company_news or "no recent information" in company_news.lower():
        company_news = ""

    sleep_between(1.0, 2.0)

    return {
        "company_news": company_news,
        "funding_news": funding_news,
    }
