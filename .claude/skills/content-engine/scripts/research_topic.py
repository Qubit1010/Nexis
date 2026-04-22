#!/usr/bin/env python3
"""Research a content topic using Anthropic web search.

Returns SEO keywords, fresh data points, competitor angles, content gap,
people-also-ask questions, and relevant hashtags.

Usage:
    python research_topic.py --topic "Claude Code as a business tool"

Output (stdout): JSON with research results
"""

import argparse
import json
import os
import sys
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="Research a content topic using Anthropic web search"
    )
    parser.add_argument("--topic", required=True, help="Topic to research")
    args = parser.parse_args()
    topic = args.topic

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print(
            json.dumps(
                {
                    "topic": topic,
                    "available": False,
                    "error": "ANTHROPIC_API_KEY not set in environment",
                }
            )
        )
        sys.exit(0)

    try:
        import anthropic
    except ImportError:
        print(
            json.dumps(
                {
                    "topic": topic,
                    "available": False,
                    "error": "anthropic package not installed. Run: pip install anthropic",
                }
            )
        )
        sys.exit(0)

    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""Research this content topic for a personal brand creator: "{topic}"

Creator context: Aleem is a 25-year-old founder (NexusPoint AI agency) and BSAI student
in Islamabad, Pakistan. His audience is startup founders, tech entrepreneurs, developers,
and AI enthusiasts. He posts on Instagram, LinkedIn, and a personal blog.

Use web search to find fresh, recent data. Return ONLY a valid JSON object — no markdown,
no preamble, just the JSON:

{{
  "primary_keyword": "best SEO keyword for blog title (under 60 chars, natural phrasing)",
  "secondary_keywords": ["keyword2", "keyword3", "keyword4"],
  "data_points": [
    {{"fact": "specific recent statistic", "source": "publication name or URL"}},
    {{"fact": "another data point", "source": "source"}}
  ],
  "competing_angles": [
    "the most common angle other creators take on this topic",
    "second common angle",
    "third common angle"
  ],
  "content_gap": "the specific angle or perspective that is NOT well covered — this is the differentiation opportunity",
  "people_also_ask": [
    "Question people search related to this topic?",
    "Another common question?",
    "Third question?"
  ],
  "hashtags": ["#hashtag1", "#hashtag2", "#hashtag3", "#hashtag4", "#hashtag5"]
}}

Requirements:
- Include 3-5 data_points with real, recent statistics (2024-2025 preferred)
- competing_angles should reflect what you actually find creators talking about online
- content_gap should be a genuine differentiation opportunity, not generic advice
- hashtags should be relevant but not spam-tier (mix of niche and broader tags)"""

    output_text = ""
    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 3}],
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from response content blocks
        for block in response.content:
            if hasattr(block, "type") and block.type == "text":
                output_text += block.text

        text = output_text.strip()
        if "```json" in text:
            text = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            text = text.split("```")[1].split("```")[0].strip()

        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            text = text[start:end]

        result = json.loads(text)
        result["topic"] = topic
        result["searched_at"] = datetime.now().isoformat()
        result["available"] = True
        print(json.dumps(result, ensure_ascii=False, indent=2))

    except json.JSONDecodeError as e:
        print(
            json.dumps(
                {
                    "topic": topic,
                    "available": False,
                    "error": f"Could not parse JSON from Anthropic response: {e}",
                    "raw_response": output_text[:1000] if output_text else "",
                }
            )
        )
    except Exception as e:
        print(
            json.dumps(
                {
                    "topic": topic,
                    "available": False,
                    "error": str(e),
                }
            )
        )


if __name__ == "__main__":
    main()
