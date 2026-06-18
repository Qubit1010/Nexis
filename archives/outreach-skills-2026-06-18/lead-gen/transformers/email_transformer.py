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

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import EMAIL_SIGNATURE


def generate_cold_email_touch1(lead: dict) -> dict:
    """Generate Touch 1 cold email subject + body. No API, pure template.

    Follows copywriting_principles.md:
      - Voss cold read opener (observable fact, not flattery)
      - No pitch in Touch 1
      - Give-first offer (free Loom teardown)
      - No-oriented CTA
    """
    company    = (lead.get("company") or "your company").strip()
    first_name = (lead.get("first_name") or "").strip()
    greeting   = f"Hi {first_name}" if first_name else "Hi"
    reviews    = (lead.get("reviews") or "").strip()
    loc_years  = (lead.get("loc_years") or "").strip()

    years_match = re.search(r'(\d+)\+?\s*years? in business', loc_years, re.I)
    years = years_match.group(1) if years_match else ""
    city = ""
    if "·" in loc_years:
        city_part = loc_years.split("·", 1)[-1].strip()
        city = city_part.split(",")[0].strip()

    subject = f"quick question about {company}"

    if reviews:
        snippet = reviews[:120].rstrip('., "\'')
        opener = (
            f"Came across {company} — a client of yours mentioned \"{snippet}...\"\n\n"
            f"That kind of result usually means the delivery is dialled in. "
            f"The challenge most agencies face at that point is whether the ops behind it "
            f"can scale without adding headcount."
        )
    elif years and city:
        opener = (
            f"It looks like {company} has been running for {years}+ years out of {city} — "
            f"that kind of track record usually means the delivery is solid, "
            f"but the backend systems are still the original ones from when you were half the size."
        )
    elif years:
        opener = (
            f"It looks like {company} has been running for {years}+ years — "
            f"that kind of longevity usually means delivery is solid, "
            f"but the ops behind it are still running on the original setup."
        )
    else:
        opener = (
            f"It looks like {company} is at the stage where the client work is running well, "
            f"but the operational side — reporting, onboarding, follow-up — "
            f"starts eating time that should go into growth."
        )

    body = (
        f"{greeting},\n\n"
        f"{opener}\n\n"
        f"I do free 5-minute Loom workflow teardowns for agencies — "
        f"map out exactly what I'd automate first, specific to how {company} operates. "
        f"No pitch, just the blueprint.\n\n"
        f"Would it be a bad idea to send one over?\n\n"
        f"Aleem | NexusPoint\nnexuspointai.com"
    )

    return {"subject": subject, "body": body}


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
    company_size = (lead.get("company_size") or "").strip()
    pain_signal = (lead.get("pain_signal") or "").strip()

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
    elif pain_signal:
        # Cold reading from observable signal (CMS, tech stack, etc.)
        email_1_body = (
            f"Hi {first_name},\n\n"
            f"It looks like {company} might be running into some friction on the tech side — {pain_signal.lower()}\n\n"
            f"I do free 5-minute Loom teardowns for {industry} founders this week — "
            f"I map out exactly what I'd fix and why, specific to {company}. No pitch, just the blueprint.\n\n"
            f"Would it be a bad idea to send one over?\n\n"
            f"{EMAIL_SIGNATURE}"
        )
    elif company_size and company_size.isdigit() and int(company_size) <= 5:
        # Small lean team — cold reading on resource constraints
        email_1_body = (
            f"Hi {first_name},\n\n"
            f"It sounds like {company} is running lean right now — which usually means "
            f"the manual operational work falls on whoever has a spare hour.\n\n"
            f"I do free 5-minute Loom workflow teardowns for {industry} founders — "
            f"I map out how to automate the stuff eating your time, specific to {company}. No pitch.\n\n"
            f"Would it be a bad idea to send one over?\n\n"
            f"{EMAIL_SIGNATURE}"
        )
    else:
        # Generic cold read on growth stage
        email_1_body = (
            f"Hi {first_name},\n\n"
            f"It looks like {company} is at the stage where operational overhead starts "
            f"compounding — more clients, same team, more manual work filling the gaps.\n\n"
            f"I do free 5-minute Loom workflow teardowns for {industry} founders — "
            f"I map out exactly what I'd automate first, specific to {company}. No pitch, just the blueprint.\n\n"
            f"Would it be a bad idea to send one over?\n\n"
            f"{EMAIL_SIGNATURE}"
        )

    # --- Email 2: Value add — quantified social proof + give-first, no pitch ---
    if len(pain_points) > 1:
        pp2 = pain_points[1]
        insight = pp2.get("pain", "") if isinstance(pp2, dict) else str(pp2)
        if insight:
            email_2_body = (
                f"Hi {first_name},\n\n"
                f"{insight}\n\n"
                f"Not pitching anything — just flagging what usually signals a scaling bottleneck at your stage.\n\n"
                f"{EMAIL_SIGNATURE}"
            )
        else:
            email_2_body = (
                f"Hi {first_name},\n\n"
                f"Wanted to share something concrete. Worked with a {industry} company recently — "
                f"they were spending 10+ hours a week on manual reporting and client data syncing. "
                f"Mapped it out in a teardown and cut it to under 90 minutes with a simple automation.\n\n"
                f"Not pitching — just figured it might be relevant given where {company} is.\n\n"
                f"{EMAIL_SIGNATURE}"
            )
    else:
        email_2_body = (
            f"Hi {first_name},\n\n"
            f"Wanted to share something concrete. Worked with a {industry} company recently — "
            f"they were spending 10+ hours a week on manual reporting and client data syncing. "
            f"Mapped it out in a teardown and cut it to under 90 minutes with a simple automation.\n\n"
            f"Not pitching — just figured it might be relevant given where {company} is.\n\n"
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
