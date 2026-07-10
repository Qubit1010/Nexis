"""Touch 1 message generation: OpenAI primary, Claude fallback.

Per Aleem's call, OpenAI (gpt-5.4-mini) is the primary generator and Claude
(claude-haiku-4-5) is the fallback. Each lead is attempted on OpenAI first; if
that fails for any reason (no key, insufficient_quota, API error), it falls back
to Claude. Only if BOTH fail do we leave the message blank.

This belt-and-suspenders setup is deliberate: the lead-gen OpenAI key has a
history of hitting insufficient_quota, and the repo Anthropic key has run out of
balance — having either provider able to cover for the other means a push almost
never has to ship blank Touch 1 messages.

Messages are grounded in the sales-playbook opener archetypes (distilled in
references/message-archetypes.md). We rotate archetypes per lead so a batch reads
like many different people, not one bot.

Graceful by design: a lead in the CRM with a blank Touch 1 is recoverable
(re-run, or fill via the sales-playbook). A lead dropped on the floor is not — so
generation failures never abort the push.
"""

import os
import random
import re
from pathlib import Path

OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-5.4-mini")
ANTHROPIC_MODEL = "claude-haiku-4-5"
MODEL = f"{OPENAI_MODEL} (OpenAI) -> {ANTHROPIC_MODEL} (Claude) fallback"
_REPO_ROOT = Path(__file__).resolve().parents[4]

# Order matters: env var wins, then repo root, then project .envs that hold keys.
_ENV_FILES = (
    _REPO_ROOT / ".env",
    _REPO_ROOT / "projects" / "bid-engine" / "backend" / ".env",
    _REPO_ROOT / "projects" / "daily-news-brief" / ".env",
)


def _load_key(var_name):
    key = os.environ.get(var_name, "").strip()
    if key:
        return key
    prefix = var_name + "="
    for env_path in _ENV_FILES:
        if not env_path.exists():
            continue
        for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith(prefix) and len(line) > len(prefix):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return ""


# ---------------------------------------------------------------------------
# Archetype rotation
# ---------------------------------------------------------------------------

_ARCHETYPE_GUIDE = {
    "anti_pitch": (
        "Laid-back anti-pitch (Josh Braun). Open by removing pressure with a soft "
        "disqualifier ('probably not a fit, but') then ask one genuine question about a "
        "specific manual task they likely still do by hand. The disqualifier is what makes "
        "it work, do not soften it into a compliment."
    ),
    "specific_observation": (
        "Specific observation. Reference one concrete, real detail from their bio or post "
        "(a phrase they used, their niche, their model), then ask one curious question about "
        "their operations. No praise, just an observant peer noticing something true."
    ),
    "genuine_question": (
        "Genuine operational question (no setup). Skip the observation and ask one sharp, "
        "peer-level question about how they handle a specific workflow at their stage. "
        "Founders answer peer questions and ignore vendor questions."
    ),
    "no_pitch_connection": (
        "No-pitch connection note (LinkedIn). Reference their recent post/role specifically, "
        "say it matches a pattern you see with similar teams, and that it would be useful to "
        "connect. End with 'No pitch.' Only works if you genuinely do not pitch."
    ),
}

_STYLE = {
    "ig_dm": {
        "with_signal": [("specific_observation", 5), ("anti_pitch", 3), ("genuine_question", 2)],
        "no_signal": [("anti_pitch", 5), ("genuine_question", 4)],
        "max_chars": 400,
        "channel_rules": (
            "Channel: Instagram DM. Casual, lowercase-friendly, like a real person typing on "
            "their phone. Under 80 words. At most 1 emoji, only if it fits naturally. "
            "Start with 'Hey [FirstName]' or just a direct line if no name."
        ),
    },
    "li_note": {
        "with_signal": [("no_pitch_connection", 5), ("specific_observation", 3), ("anti_pitch", 2)],
        "no_signal": [("anti_pitch", 4), ("genuine_question", 3), ("no_pitch_connection", 2)],
        "max_chars": 300,
        "channel_rules": (
            "Channel: LinkedIn connection-request note. Hard cap 300 characters (aim for under "
            "280). Professional but human, no emojis. No formal sign-off."
        ),
    },
    "maps_email": {
        # Google Maps leads are businesses (real estate agencies, local shops), not
        # a social profile you DM — this is an email opener. Signal here is the
        # business category/name, not a personal bio, so lean on the observation
        # archetype referencing their category/location rather than "no_signal"
        # openers built for a bare handle.
        "with_signal": [("genuine_question", 5), ("specific_observation", 4), ("anti_pitch", 3)],
        "no_signal": [("genuine_question", 5), ("anti_pitch", 4)],
        "max_chars": 500,
        "channel_rules": (
            "Channel: cold email opener to a local business (e.g. a real estate agency). "
            "This is a DRAFT for Aleem to review and send manually, never auto-sent. Write the "
            "email BODY only (no subject line, no sign-off/signature). Professional but human, "
            "not corporate. Under 90 words. Reference their business category or what they do "
            "specifically. No emojis."
        ),
    },
    "fb_dm": {
        # These leads are founders/CEOs who introduced themselves in business groups,
        # so the bio/note is strong signal: lean on specific_observation.
        "with_signal": [("specific_observation", 5), ("genuine_question", 3), ("anti_pitch", 2)],
        "no_signal": [("anti_pitch", 5), ("genuine_question", 4)],
        "max_chars": 600,
        "channel_rules": (
            "Channel: Facebook DM to a founder/CEO who posted an intro in a business group. "
            "Conversational and human, like a peer messaging on Facebook. Under 100 words. "
            "At most 1 emoji, only if it fits. Reference the specific thing they shared in their "
            "intro. Start with 'Hey [FirstName]' or a direct line if no name."
        ),
    },
}

_SYSTEM = """You write the opening outreach message for Aleem Ul Hassan, founder of an AI \
automation studio. This is Touch 1 of a sequence: the only goal is to start a real \
conversation, never to pitch.

Hard rules (these are what separate a reply from a delete):
- No pitch. Never mention NexusPoint, services, "AI automation", websites, or what you sell.
- One ask maximum. A single genuine question, or a connect request. Never a question AND a CTA.
- No em-dashes ever. Use a comma or a period. (They corrupt downstream and read as AI.)
- Count your "I"s: more than two means rewrite. Make it about them, not you.
- Banned openers (instant delete): "I came across your profile", "hope this finds you well",
  "love your content", "I was impressed", "Bro", "I wanted to reach out".
- No fake compliments. Observation over flattery.
- Mirror their tone. Concise if they're concise.

Return ONLY the message text. No quotes, no preamble, no explanation."""


def _pick_archetype(style, lead):
    spec = _STYLE[style]
    has_signal = bool((lead.get("bio") or "").strip())
    pool = spec["with_signal"] if has_signal else spec["no_signal"]
    names = [a for a, _ in pool]
    weights = [w for _, w in pool]
    return random.choices(names, weights=weights, k=1)[0]


def _lead_context(lead):
    parts = []
    if lead.get("first_name"):
        parts.append(f"- First name: {lead['first_name']}")
    if lead.get("name") and not lead.get("first_name"):
        parts.append(f"- Name/brand: {lead['name']}")
    if lead.get("username"):
        parts.append(f"- Handle: {lead['username']}")
    if lead.get("title"):
        parts.append(f"- Role/title: {lead['title']}")
    if lead.get("company"):
        parts.append(f"- Company: {lead['company']}")
    if lead.get("location"):
        parts.append(f"- Location: {lead['location']}")
    if lead.get("followers"):
        parts.append(f"- Followers: {lead['followers']}")
    bio = (lead.get("bio") or "").strip()
    parts.append(f"- Bio / recent post: {bio[:300]}" if bio else "- Bio / recent post: (none available)")
    return "\n".join(parts)


def _clean(text, max_chars):
    text = text.strip()
    if text[:1] in ('"', "'") and text[-1:] in ('"', "'"):
        text = text[1:-1].strip()
    text = text.replace(" — ", ", ").replace("—", ", ")
    # Normalize smart punctuation to ASCII so it can't corrupt in the Sheet (cp1252/UTF-8)
    text = (text.replace("“", '"').replace("”", '"')
                .replace("‘", "'").replace("’", "'")
                .replace("–", "-").replace("…", "..."))
    text = re.sub(r"[ \t]+", " ", text).strip()
    if len(text) > max_chars:
        cut = text[:max_chars]
        if " " in cut:
            cut = cut[:cut.rfind(" ")]
        text = cut.rstrip(" ,.") + "..."
    return text


def _build_prompt(style, lead):
    spec = _STYLE[style]
    archetype = _pick_archetype(style, lead)
    user_prompt = (
        f"{spec['channel_rules']}\n\n"
        f"Archetype to use: {_ARCHETYPE_GUIDE[archetype]}\n\n"
        f"Lead:\n{_lead_context(lead)}\n\n"
        f"Write the opening message."
    )
    return archetype, user_prompt, spec["max_chars"]


# ---------------------------------------------------------------------------
# Generator — OpenAI primary, Claude fallback
# ---------------------------------------------------------------------------

class Generator:
    """Holds whichever providers are available and tries them in order per lead."""

    def __init__(self):
        self.openai = self._init_openai()
        self.anthropic = self._init_anthropic()

    def _init_openai(self):
        key = _load_key("OPENAI_API_KEY")
        if not key:
            return None
        try:
            from openai import OpenAI
        except ImportError:
            print("  NOTE: `openai` not installed — OpenAI disabled.", flush=True)
            return None
        return OpenAI(api_key=key)

    def _init_anthropic(self):
        key = _load_key("ANTHROPIC_API_KEY")
        if not key:
            return None
        try:
            from anthropic import Anthropic
        except ImportError:
            return None
        return Anthropic(api_key=key)

    @property
    def available(self):
        return self.openai is not None or self.anthropic is not None

    def providers_label(self):
        chain = []
        if self.openai:
            chain.append(f"OpenAI {OPENAI_MODEL}")
        if self.anthropic:
            chain.append(f"Claude {ANTHROPIC_MODEL}")
        return " -> ".join(chain) if chain else "none"

    def _via_openai(self, system, user, max_tokens):
        kwargs = {
            "model": OPENAI_MODEL,
            "messages": [{"role": "system", "content": system},
                         {"role": "user", "content": user}],
        }
        if OPENAI_MODEL.startswith("gpt-5"):
            # GPT-5 family: uses max_completion_tokens (not max_tokens), only the
            # default temperature, and reasoning_effort for latency/cost. Give
            # headroom above the text budget since reasoning also spends tokens.
            kwargs["max_completion_tokens"] = max(max_tokens * 3, 1200)
            kwargs["reasoning_effort"] = "low"
        else:
            kwargs["max_tokens"] = max_tokens
            kwargs["temperature"] = 0.9
        resp = self.openai.chat.completions.create(**kwargs)
        return resp.choices[0].message.content or ""

    def _via_anthropic(self, system, user, max_tokens):
        resp = self.anthropic.messages.create(
            model=ANTHROPIC_MODEL,
            max_tokens=max_tokens,
            temperature=0.9,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if getattr(b, "type", "") == "text")

    def generate(self, style, lead):
        """Return (message, archetype, provider). provider is '' if all failed."""
        archetype, user, max_chars = _build_prompt(style, lead)
        attempts = []
        if self.openai:
            attempts.append(("openai", self._via_openai))
        if self.anthropic:
            attempts.append(("claude", self._via_anthropic))
        for name, fn in attempts:
            try:
                text = fn(_SYSTEM, user, 350)
                cleaned = _clean(text, max_chars)
                if cleaned:
                    return cleaned, archetype, name
            except Exception as e:
                print(f"    {name} failed ({archetype}): {str(e)[:110]}", flush=True)
        return "", archetype, ""


def get_client():
    """Return a Generator if any provider is usable, else None (with a printed note)."""
    gen = Generator()
    if not gen.available:
        print("  NOTE: no OpenAI or Anthropic key found — pushing with blank Touch 1 messages.",
              flush=True)
        return None
    print(f"  message providers: {gen.providers_label()}", flush=True)
    return gen


def generate_batch(client, style, leads):
    """List of messages aligned to leads. Blank entries where all providers failed."""
    out = []
    for n, lead in enumerate(leads, 1):
        if client is None:
            out.append("")
            continue
        msg, arch, provider = client.generate(style, lead)
        tag = lead.get("first_name") or lead.get("name") or lead.get("username") or "?"
        status = f"{len(msg)} chars [{arch} via {provider}]" if msg else f"BLANK [{arch}]"
        print(f"    [{n}/{len(leads)}] {str(tag)[:30]:<30} {status}", flush=True)
        out.append(msg)
    return out
