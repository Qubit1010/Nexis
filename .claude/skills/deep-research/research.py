#!/usr/bin/env python3
"""Deep Research skill for NexusPoint — context-aware research via OpenAI."""

import argparse
import os
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]  # .claude/skills/deep-research -> root


def load_env():
    """Read OPENAI_API_KEY from .env at project root."""
    env_path = PROJECT_ROOT / ".env"
    if not env_path.exists():
        print("Error: .env file not found at project root.", file=sys.stderr)
        print("Create it with: OPENAI_API_KEY=your-key-here", file=sys.stderr)
        sys.exit(1)
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key or api_key == "your-key-here":
        print("Error: OPENAI_API_KEY not set. Paste your key into .env", file=sys.stderr)
        sys.exit(1)
    return api_key


def build_system_prompt(context: str) -> str:
    """Build system prompt with optional business context."""
    base = (
        "You are a research analyst working for NexusPoint, a digital agency "
        "specializing in AI systems, web development, and automation. "
        "Your founder is Aleem Ul Hassan. "
        "Produce thorough, actionable research. Cite sources with URLs.\n\n"
    )
    if context:
        base += f"## Business Context\n{context}\n\n"
    return base


def build_deep_instructions(query: str) -> str:
    """Build instructions for deep research mode."""
    return (
        f"Research the following topic thoroughly:\n\n{query}\n\n"
        "Structure your response as:\n"
        "## Executive Summary\nA 2-3 sentence overview of key findings.\n\n"
        "## Key Findings\nNumbered list of the most important discoveries.\n\n"
        "## Detailed Analysis\nIn-depth exploration with evidence and sources.\n\n"
        "## Recommendations\nActionable next steps for NexusPoint.\n\n"
        "## Sources\nList all sources with URLs.\n\n"
        "Be thorough. Use multiple searches. Cross-reference information. "
        "Prioritize recent, authoritative sources."
    )


def build_quick_instructions(query: str) -> str:
    """Build instructions for quick search mode."""
    return (
        f"Answer this question concisely:\n\n{query}\n\n"
        "Give a direct answer first, then brief supporting details. "
        "Include source URLs. Keep it under 300 words."
    )


def run_research(api_key: str, query: str, mode: str, context: str) -> str:
    """Call OpenAI Responses API with web search."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    system_prompt = build_system_prompt(context)

    if mode == "deep":
        model = "gpt-5"
        user_msg = build_deep_instructions(query)
        search_context = "high"
    else:
        model = "gpt-4.1-mini"
        user_msg = build_quick_instructions(query)
        search_context = "low"

    try:
        response = client.responses.create(
            model=model,
            instructions=system_prompt,
            input=user_msg,
            tools=[{"type": "web_search_preview", "search_context_size": search_context}],
        )
        return response.output_text
    except Exception as e:
        # Fallback: try gpt-4.1-mini if gpt-5 fails
        if mode == "deep" and "model" in str(e).lower():
            print(f"Note: Falling back to gpt-4.1-mini ({e})", file=sys.stderr)
            response = client.responses.create(
                model="gpt-4.1-mini",
                instructions=system_prompt,
                input=user_msg,
                tools=[{"type": "web_search_preview"}],
            )
            return response.output_text
        raise


def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return text[:60].rstrip("-")


def save_report(query: str, mode: str, result: str) -> Path:
    """Save research report to research/ directory."""
    research_dir = PROJECT_ROOT / "research"
    research_dir.mkdir(exist_ok=True)
    date_str = datetime.now().strftime("%Y-%m-%d")
    slug = slugify(query)
    filename = f"{date_str}-{slug}.md"
    filepath = research_dir / filename

    header = (
        f"# {query}\n\n"
        f"*Research mode: {mode} | Date: {date_str}*\n\n---\n\n"
    )
    filepath.write_text(header + result, encoding="utf-8")
    return filepath


def main():
    parser = argparse.ArgumentParser(description="NexusPoint Deep Research")
    parser.add_argument("--query", required=True, help="Research query")
    parser.add_argument("--mode", choices=["deep", "quick"], default="quick",
                        help="Research mode (default: quick)")
    parser.add_argument("--context", default="", help="Business context string")
    parser.add_argument("--save", action="store_true", help="Save report to research/")
    args = parser.parse_args()

    api_key = load_env()
    result = run_research(api_key, args.query, args.mode, args.context)

    print(result)

    if args.save or args.mode == "deep":
        filepath = save_report(args.query, args.mode, result)
        print(f"\n---\nReport saved to: {filepath.relative_to(PROJECT_ROOT)}", file=sys.stderr)


if __name__ == "__main__":
    main()
