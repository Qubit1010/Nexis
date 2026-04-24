#!/usr/bin/env python3
"""Generate a cold outreach hook email from an audit's top finding.

Reads audit JSON from stdin (produced by analyze_audit.py --mode quick).
Picks the highest-severity finding, loads the matching archetype from
references/outreach-templates.md, and uses Claude to fill it in.

Usage:
    cat audit.json | python generate_hook_email.py [--doc-url https://...]

Output (stdout):
    {"status": "ok", "subject": "...", "body": "..."}
"""

import argparse
import json
import os
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
TEMPLATES_PATH = SKILL_DIR / "references" / "outreach-templates.md"

MODEL = "claude-sonnet-4-6"

SEV_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}

# Tie-break order per templates doc: conversion > UX > SEO > performance
DIM_RANK = {
    "Conversion": 0,
    "UX & Messaging": 1,
    "SEO Basics": 2,
    "Performance": 3,
}


def error_exit(message):
    print(json.dumps({"status": "error", "message": message}))
    sys.exit(1)


def pick_top_finding(findings):
    if not findings:
        return None
    return sorted(
        findings,
        key=lambda f: (
            SEV_RANK.get((f.get("severity") or "").lower(), 9),
            DIM_RANK.get(f.get("dimension", ""), 9),
        ),
    )[0]


def main():
    parser = argparse.ArgumentParser(description="Generate cold outreach hook email from audit")
    parser.add_argument("--doc-url", help="Optional: audit Google Doc URL to reference")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        error_exit("ANTHROPIC_API_KEY not set in environment")

    try:
        import anthropic
    except ImportError:
        error_exit("anthropic package not installed")

    if not TEMPLATES_PATH.exists():
        error_exit(f"Missing templates: {TEMPLATES_PATH}")
    templates = TEMPLATES_PATH.read_text(encoding="utf-8")

    try:
        raw = sys.stdin.read()
        if not raw.strip():
            error_exit("No input. Pipe audit JSON to this script.")
        audit = json.loads(raw)
    except json.JSONDecodeError as e:
        error_exit(f"Invalid JSON: {e}")

    findings = audit.get("findings", []) or []
    top = pick_top_finding(findings)
    if not top:
        error_exit("Audit has no findings to reference")

    company = audit.get("company") or "the site"
    url = audit.get("url") or ""

    prompt = f"""You are writing a cold outreach hook email for NexusPoint (Aleem's agency).

=== REFERENCE: TEMPLATES AND VOICE RULES ===
{templates}

=== AUDIT TOP FINDING ===
Company: {company}
Site: {url}
Dimension: {top.get('dimension')}
Severity: {top.get('severity')}
Title: {top.get('title')}
Evidence: {top.get('evidence')}
Business impact: {top.get('business_impact')}
Fix: {top.get('fix')}

=== INSTRUCTIONS ===
Pick the matching archetype from the templates doc based on the finding's dimension. Fill in the placeholders using the finding's actual evidence — do not use vague language when the finding has a concrete observation.

Constraints:
- 60-100 words total for the body
- No em dashes, no emojis
- No "I hope this email finds you well" or any formulaic opener
- Close with exactly: "- Aleem, NexusPoint"
- If a doc_url is provided below, add it on the line after the signature, nothing else

Return ONLY valid JSON, no markdown, no code fences:

{{
  "subject": "...",
  "body": "full email body including the signature"
}}

Doc URL (include if present): {args.doc_url or '(none)'}
"""

    client = anthropic.Anthropic(api_key=api_key)
    try:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
    except Exception as exc:
        error_exit(f"Anthropic API failed: {exc}")

    text = ""
    for block in response.content:
        if hasattr(block, "type") and block.type == "text":
            text += block.text

    text = text.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end <= start:
        error_exit(f"Could not find JSON in response: {text[:300]}")

    try:
        email = json.loads(text[start:end])
    except json.JSONDecodeError as exc:
        error_exit(f"Invalid JSON from model: {exc} | raw: {text[:300]}")

    email["status"] = "ok"
    email["top_finding_dimension"] = top.get("dimension")
    email["top_finding_severity"] = top.get("severity")
    print(json.dumps(email, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
