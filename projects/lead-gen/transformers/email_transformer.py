"""Cold email sequence transformer.

Generates a 4-email sequence for each lead using:
  - Personalization package (hooks, pain points, value prop)
  - NexusPoint's proven sequence formula
  - Voss tactical empathy principles

Sequence structure:
  Email 1 (Day 0):  Personalized hook + pain signal + low-friction CTA
  Email 2 (Day 4):  Value-add (observation or insight, no pitch)
  Email 3 (Day 9):  Soft follow-up + Loom video offer
  Email 4 (Day 16): Breakup email ("Should I close your file?")
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import EMAIL_SIGNATURE


def generate_email_sequence(lead: dict, personalization: dict) -> dict:
    """Generate a 4-email cold outreach sequence.

    Args:
        lead: Lead dict from DB
        personalization: Personalization dict from DB

    Returns:
        Sequence dict with 4 email dicts
    """
    first_name = (lead.get("first_name") or "there").strip()
    company = (lead.get("company") or "your company").strip()
    industry = (lead.get("industry") or "your industry").strip()

    # Best hook — use first non-empty hook
    hooks = [
        personalization.get("hook_1", ""),
        personalization.get("hook_2", ""),
        personalization.get("hook_3", ""),
    ]
    best_hook = next((h for h in hooks if h.strip()), "")

    # Best pain point
    pain_points = personalization.get("pain_points", [])
    pain_point_text = ""
    if pain_points:
        pp = pain_points[0]
        if isinstance(pp, dict):
            pain_point_text = f"{pp.get('pain', '')} {pp.get('solution', '')}".strip()
        else:
            pain_point_text = str(pp)

    value_prop = personalization.get("value_prop", "")

    # --- Email 1: Initial outreach ---
    email_1_subjects = [
        f"quick question about {company}",
        f"noticed something about {company}",
        f"thought this might be relevant for {company}",
    ]

    if best_hook:
        email_1_body = (
            f"Hi {first_name},\n\n"
            f"{best_hook}\n\n"
            f"{pain_point_text}\n\n"
            f"I work with {industry} founders on exactly this — happy to share what's worked.\n\n"
            f"Worth a 15-min call to see if it's relevant?\n\n"
            f"{EMAIL_SIGNATURE}"
        )
    else:
        email_1_body = (
            f"Hi {first_name},\n\n"
            f"Quick question — is {company} running into any bottlenecks with operations or tech right now?\n\n"
            f"We help {industry} companies automate the manual stuff so the team can focus on growth.\n\n"
            f"Worth a 15-min call?\n\n"
            f"{EMAIL_SIGNATURE}"
        )

    # --- Email 2: Value add ---
    email_2_body = (
        f"Hi {first_name},\n\n"
        f"Thought this might be useful — one of the most common bottlenecks we see in {industry} companies "
        f"at {company}'s stage is operational work that doesn't scale with the team.\n\n"
        f"Not pitching anything. Just wanted to share the pattern in case it's useful.\n\n"
        f"{EMAIL_SIGNATURE}"
    )

    # Inject second pain point if available
    if len(pain_points) > 1:
        pp2 = pain_points[1]
        if isinstance(pp2, dict):
            insight = pp2.get("pain", "")
        else:
            insight = str(pp2)
        if insight:
            email_2_body = (
                f"Hi {first_name},\n\n"
                f"{insight}\n\n"
                f"Not pitching anything — just flagging what usually signals a scaling bottleneck at your stage.\n\n"
                f"{EMAIL_SIGNATURE}"
            )

    # --- Email 3: Soft follow-up + Loom offer ---
    email_3_body = (
        f"Hi {first_name},\n\n"
        f"Still happy to do a quick 5-minute Loom — I'll map out exactly what I'd change and why, "
        f"specific to {company}.\n\n"
        f"No strings attached. If it's not useful, you've lost nothing.\n\n"
        f"Worth a look?\n\n"
        f"{EMAIL_SIGNATURE}"
    )

    # --- Email 4: Breakup ---
    email_4_body = (
        f"Hi {first_name},\n\n"
        f"Should I close your file, or is the timing just off right now?\n\n"
        f"Either way is fine — just want to make sure I'm not missing something on my end.\n\n"
        f"{EMAIL_SIGNATURE}"
    )

    sequence = {
        "platform": "cold_email",
        "emails": [
            {
                "number": 1,
                "send_day": 0,
                "subject_options": email_1_subjects,
                "body": email_1_body,
                "merge_variables": {
                    "first_name": first_name,
                    "company": company,
                    "hook": best_hook,
                    "pain_point": pain_point_text,
                },
            },
            {
                "number": 2,
                "send_day": 4,
                "subject_options": [
                    f"something I noticed about {company}",
                    f"for {industry} founders",
                    f"re: {company}",
                ],
                "body": email_2_body,
                "merge_variables": {
                    "first_name": first_name,
                    "company": company,
                    "industry": industry,
                },
            },
            {
                "number": 3,
                "send_day": 9,
                "subject_options": [
                    f"quick Loom for {company}",
                    f"5-min audit for {company}",
                    f"re: {company}",
                ],
                "body": email_3_body,
                "merge_variables": {
                    "first_name": first_name,
                    "company": company,
                },
            },
            {
                "number": 4,
                "send_day": 16,
                "subject_options": [
                    "closing the loop",
                    f"re: {company}",
                    "should I close your file?",
                ],
                "body": email_4_body,
                "merge_variables": {
                    "first_name": first_name,
                    "company": company,
                },
            },
        ],
        "merge_variables_master": {
            "first_name": first_name,
            "company": company,
            "industry": industry,
            "value_prop": value_prop,
        },
    }

    return sequence
