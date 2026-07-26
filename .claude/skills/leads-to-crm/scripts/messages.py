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

import difflib
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

# Each entry describes a STRATEGY and an intent. None of them supply phrasing.
#
# This is deliberate and is the whole point of the 2026-07-25 rewrite. The previous guide handed the
# model literal strings ("probably not a fit, but", "it would be useful to connect", "End with 'No
# pitch.'") and the model, correctly, used them verbatim on every lead -- so a batch of 300 prospects
# got three interchangeable messages wearing different names. Describe the move, never the words: the
# model writes fresh copy per lead, and the batch stops reading as one template.
_ARCHETYPE_GUIDE = {
    "earned_credibility": (
        "Their reputation, taken seriously. Refer to the standing they have built IN WORDS ('the "
        "reputation you've built', 'the kind of feedback that follows you'). NEVER cite a rating, a "
        "score, a star count, or a number of reviews: quoting a scraped figure proves a machine read "
        "a listing and is the fastest way to sound automated. Say what that standing implies about "
        "how they operate, then ask one real question about how they hold it up. Do NOT reach for "
        "the 'consistent, not just occasional' contrast, it is the first reading everyone lands on "
        "and it makes every message sound alike."
    ),
    "specific_observation": (
        "One concrete detail, followed by curiosity. Pick a single real, given detail (their "
        "specialization, their own tagline, where they operate) and say the true thing you notice "
        "about it. Then one curious question about how they actually work. An observant peer, not "
        "a vendor doing research."
    ),
    "genuine_question": (
        "Straight to the question, no setup. Skip the observation entirely and ask one sharp, "
        "peer-level question about how a team like theirs handles a specific part of the work. "
        "Deliberately the most abrupt shape in the rotation, it should not sound like an opener."
    ),
    "craft_respect": (
        "Respect for the hard part of their craft. Name the specific thing that is genuinely "
        "difficult about the work they do (from their given specialization) and why most teams get "
        "it wrong. Then ask how they handle it. Warm and knowledgeable, one practitioner to another."
    ),
    "peer_pattern": (
        "Shared pattern, no name-dropping. You work adjacent to their space and keep running into a "
        "specific recurring pattern with teams in it. State the pattern concretely, then ask where "
        "they have landed on it. Never claim a client, a peer name, or a result you were not given."
    ),
    "understated": (
        "Short and low-key. Two sentences at most. One honest line about what you noticed, one "
        "genuine question. No preamble, no windup, no closing tag. The point is that it reads like "
        "a quick message a busy person actually typed, so keep it markedly shorter than the others."
    ),
}

_STYLE = {
    "ig_dm": {
        "with_signal": [("specific_observation", 4), ("earned_credibility", 3), ("understated", 3),
                        ("craft_respect", 2)],
        "no_signal": [("genuine_question", 4), ("understated", 3), ("peer_pattern", 2)],
        "max_chars": 340,
        "channel_rules": (
            "Channel: Instagram DM. Casual, lowercase-friendly, like a real person typing on "
            "their phone. Under 60 words, hard. At most 1 emoji, only if it fits naturally. "
            "Start with 'Hey [FirstName]' or just a direct line if no name."
        ),
    },
    "li_note": {
        # earned_credibility deliberately NOT dominant: it is the archetype most prone to converging
        # (every lead's fact has the same shape, "N reviews at X"), so it shares the pool rather than
        # leading it. Craft/observation angles pull from richer, more lead-specific material.
        "with_signal": [("craft_respect", 4), ("specific_observation", 4), ("earned_credibility", 2),
                        ("peer_pattern", 2)],
        "no_signal": [("peer_pattern", 4), ("genuine_question", 3), ("understated", 2)],
        "max_chars": 300,
        "channel_rules": (
            "Channel: LinkedIn connection-request note. Hard cap 300 characters (aim for under "
            "280). Professional but human, no emojis. No formal sign-off. Do NOT end with a "
            "connect-request tag of any kind, the request itself already says that."
        ),
    },
    "maps_email": {
        # Google Maps leads are businesses (real estate agencies, local shops), not
        # a social profile you DM — this is an email opener. Signal here is the
        # business category/name, not a personal bio, so lean on the observation
        # archetype referencing their category/location rather than "no_signal"
        # openers built for a bare handle.
        "with_signal": [("genuine_question", 4), ("specific_observation", 4), ("craft_respect", 3)],
        "no_signal": [("genuine_question", 5), ("peer_pattern", 3)],
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
        "with_signal": [("specific_observation", 4), ("craft_respect", 3), ("earned_credibility", 3),
                        ("genuine_question", 2)],
        "no_signal": [("genuine_question", 4), ("peer_pattern", 3), ("understated", 2)],
        "max_chars": 600,
        "channel_rules": (
            "Channel: Facebook DM to a founder/CEO who posted an intro in a business group. "
            "Conversational and human, like a peer messaging on Facebook. Under 100 words. "
            "At most 1 emoji, only if it fits. Reference the specific thing they shared in their "
            "intro. Start with 'Hey [FirstName]' or a direct line if no name."
        ),
    },
    "ig_dm_company": {
        # Company/brand-page variant of ig_dm: no lead.first_name is ever set for these
        # (the identity anchor is the company's own account, not a specific person), so
        # the message must never open with "Hey [FirstName]" and should read like one
        # business account messaging another, not a person DMing a stranger.
        "with_signal": [("earned_credibility", 4), ("specific_observation", 4), ("understated", 3),
                        ("craft_respect", 2)],
        "no_signal": [("genuine_question", 4), ("understated", 3), ("peer_pattern", 2)],
        "max_chars": 340,
        "channel_rules": (
            "Channel: Instagram DM to a BUSINESS/brand account, not a person -- never use a "
            "first name or 'Hey [Name]'. Write like one small business account messaging another, "
            "casual and human. Under 60 words, hard. At most 1 emoji, only if it fits naturally. "
            "Reference their category or what they do specifically, not a person's bio."
        ),
    },
    "fb_dm_company": {
        # Company/brand-page variant of fb_dm -- same no-first-name constraint as
        # ig_dm_company.
        "with_signal": [("earned_credibility", 4), ("specific_observation", 4), ("craft_respect", 3),
                        ("understated", 2)],
        "no_signal": [("genuine_question", 4), ("peer_pattern", 3), ("understated", 2)],
        "max_chars": 600,
        "channel_rules": (
            "Channel: Facebook DM to a BUSINESS/brand Page, not a person -- never use a first "
            "name or 'Hey [Name]'. Conversational and human, like one business account messaging "
            "another. Under 100 words. At most 1 emoji, only if it fits. Reference their category "
            "or what they do specifically, not a person's bio."
        ),
    },
}

_SYSTEM = """You write the opening outreach message for Aleem Ul Hassan, founder of an AI \
automation studio. This is Touch 1 of a sequence: the only goal is to start a real \
conversation, never to pitch.

Voice: warm and genuinely appreciative, the way one practitioner writes to another whose work they
respect. Not sales-y, not flattering, not clever. End on one real question you would actually want
the answer to.

Truth rules (violating these is worse than a bad message, it is a lie to a stranger):
- Use ONLY the facts given below. Never invent a post, a client, a peer, a result, or a number.
- Anything labelled "third-party review summary" was written ABOUT them by a directory, NOT by them.
  Never call it "your post", "you wrote", "you shared", or "your note". You may reference the
  underlying fact (what they specialize in), never the wording as if it were theirs.
- If a fact is not given, leave it out. A shorter true message beats a longer padded one.
- NEVER cite a rating, score, star count, or number of reviews ("4.9 across 27 reviews", "5 stars",
  "rated 4.8"). Praise their reputation in words instead. Quoting a scraped figure is the single
  clearest sign a machine wrote the message.

Hard rules (these are what separate a reply from a delete):
- No pitch. Never mention NexusPoint, services, "AI automation", websites, or what you sell.
- One ask maximum. A single genuine question. Never a question AND a CTA.
- No em-dashes ever. Use a comma or a period. (They corrupt downstream and read as AI.)
- Count your "I"s: more than two means rewrite. Make it about them, not you.
- Banned openers (instant delete): "I came across your profile", "hope this finds you well",
  "love your content", "I was impressed", "Bro", "I wanted to reach out", "I noticed".
- Appreciation must be anchored to a specific given fact. Generic praise reads as manipulation.
- No closing tag lines. Never end with "No pitch", "Would be useful to connect", or any
  variation. Never open with a disqualifier like "probably not a fit".
- Vary your sentence shape. Do not write every message as observation-then-question in the same
  rhythm; some should open on the question, some should be markedly shorter.
- Mirror their tone. Concise if they're concise.

Return ONLY the message text. No quotes, no preamble, no explanation."""


def _has_signal(lead):
    """Any real, citable fact -- their own words (bio), a verifiable number (rating/reviews), their
    own tagline, or a specialization. Previously this was bio-only, which sent every directory lead
    down the no_signal path even when a 5.0-across-125-reviews fact was sitting right there."""
    return any((lead.get(k) or "").strip()
               for k in ("bio", "rating", "reviews", "slogan", "specialization", "review_summary"))


def _pick_archetype(style, lead):
    spec = _STYLE[style]
    pool = spec["with_signal"] if _has_signal(lead) else spec["no_signal"]
    names = [a for a, _ in pool]
    weights = [w for _, w in pool]
    return random.choices(names, weights=weights, k=1)[0]


def _lead_context(lead):
    """Facts block. Self-authored text and third-party text are labelled DIFFERENTLY and on purpose:
    `bio` is the prospect's own words (a real IG bio or scraped post) and is safe to reference as
    theirs; `review_summary` is directory copy written ABOUT them and must never be quoted back as
    something they said. Conflating the two is what produced messages opening 'your post about an
    experienced, creative team' for copy the prospect never wrote."""
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
    if lead.get("specialization"):
        parts.append(f"- What they do (verified): {lead['specialization']}")
    if lead.get("location"):
        parts.append(f"- Location: {lead['location']}")
    if lead.get("followers"):
        parts.append(f"- Followers: {lead['followers']}")

    # Deliberately the BAND, never the raw rating/review numbers. The figures are not passed into the
    # prompt at all, so the model cannot recite them even if it wants to.
    band = reputation_band(lead.get("rating"), lead.get("reviews"))
    if band:
        parts.append(f"- Reputation (describe in words, NEVER cite a number or review count): {band}")
    if lead.get("slogan"):
        parts.append(f"- Their own tagline (their words, safe to reference): {lead['slogan']}")

    bio = (lead.get("bio") or "").strip()
    if bio:
        parts.append(f"- Their own bio / recent post (their words, safe to reference): {bio[:300]}")
    summary = (lead.get("review_summary") or "").strip()
    if summary:
        parts.append(f"- Third-party review summary (written ABOUT them by a directory, NOT their "
                     f"words, do NOT quote back as theirs): {summary[:300]}")
    if not bio and not summary:
        parts.append("- Their own bio / recent post: (none available)")
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


# Enforcement the playbook already specified but nobody had built: what-not-to-do.md:9 says the
# generators "should reject-and-regenerate any output containing these strings before showing them".
# Until now nothing checked, so burned phrases shipped straight to the CRM. Tier 1/2/6 strings plus
# the three phrases Aleem flagged by hand on 2026-07-25.
_BANNED = (
    "probably not a fit", "not sure if it's a fit", "no pitch", "would be useful to connect",
    "useful to be connected", "worth a quick chat", "quick 15-minute", "15-minute chat",
    "i came across your profile", "hope this finds you well", "love your content",
    "i was impressed", "i wanted to reach out", "i noticed", "just following up",
    "i'd love to learn more", "let me know if", "pain points", "circle back",
    "leverage", "robust", "seamless", "streamline", "cutting-edge", "empower",
    "comprehensive solution", "your post about",
)


def banned_hits(text):
    """Every banned phrase (plus any em-dash) present in `text`. Empty list means clean."""
    low = (text or "").lower()
    hits = [p for p in _BANNED if p in low]
    if "—" in (text or "") or "--" in (text or ""):
        hits.append("em-dash")
    return hits


def _num(val):
    m = re.search(r"\d+(?:\.\d+)?", str(val or "").replace(",", ""))
    return float(m.group(0)) if m else None


def reputation_band(rating, reviews):
    """Rating + review count -> a QUALITATIVE description, never the raw figures.

    Reciting "4.9 across 27 reviews" is scrape-specific personalization: it proves a machine read a
    directory listing, which the 2026 corpus lists as an AI tell as damaging as being generic
    (what-not-to-do.md Tier 6). Aleem rejected it on sight in the live CRM for exactly that reason.
    Banding it keeps the claim true and earned while removing the number the model would otherwise
    parrot into every message. Returns "" when there is nothing real to characterise, so a message
    with no basis for praise simply makes none."""
    r, v = _num(rating), _num(reviews) or 0
    if r is None:
        return ""
    if r >= 4.8 and v >= 25:
        return "a strong reputation, earned across a large amount of client feedback"
    if r >= 4.8:
        return "a strong reputation with the clients they have worked with"
    if r >= 4.5 and v >= 25:
        return "consistently good client feedback across a lot of projects"
    if r >= 4.5:
        return "consistently good client feedback"
    if r >= 4.0:
        return "solid client feedback"
    return ""


# A digit next to review/rating vocabulary is the tell Aleem flagged. Cheap to detect, so it is
# enforced rather than merely discouraged in the prompt.
_NUMBER_TELL = re.compile(
    r"\d+(?:\.\d+)?\s*(?:\+)?\s*(?:star|stars|rating|ratings|review|reviews)\b"
    r"|(?:rating|rated|stars?|reviews?)\s*(?:of|at|is)?\s*\d+(?:\.\d+)?"
    r"|\d+(?:\.\d+)?\s*(?:/|out of)\s*5",
    re.I,
)


def number_hits(text):
    """Citations of a scraped rating/review figure. Empty list means clean."""
    return [m.group(0).strip() for m in _NUMBER_TELL.finditer(text or "")]


def _words(text):
    """Lowercased word list with digits and a leading name-greeting stripped. Digits go because
    '4.9 across 26 reviews' and '4.9 across 28 reviews' are the SAME frame; the leading name goes
    because 'Alex, 4.9 across...' would otherwise dodge a collision with '4.9 across...'."""
    body = re.sub(r"^\s*(?:hey|hi|hello)?[\s,]*[A-Z][\w.'-]*\s*,\s*", " ", (text or "").strip())
    return re.findall(r"[a-z']+", body.lower())


def _opening_shape(text):
    """First 5 content words, normalized. Two messages sharing this are the 'every message looks the
    same' complaint in its most literal form."""
    return " ".join(_words(text)[:5])


def _ngrams(text, n=4):
    w = _words(text)
    return {" ".join(w[i:i + n]) for i in range(max(0, len(w) - n + 1))}


_SIMILARITY_LIMIT = 0.60  # above this two messages read as the same message with names swapped


def repeat_hits(text, previous):
    """Why this message reads as a clone of one already in the batch: a shared opening shape, or
    overall text similarity above _SIMILARITY_LIMIT.

    ENFORCED, not advisory. The first version only ASKED the model in the prompt not to reuse
    shapes and it ignored that, shipping three near-identical "X across N reviews suggests a
    consistent way of working" messages in one 8-lead sample.

    Similarity, NOT shared n-grams. The n-gram version looked right on a 6-message sample and was
    useless at batch scale: across 92 messages it fired on ordinary English ("how do you keep",
    "where have you landed on that") so ~90% of leads burned their full rewrite budget fighting a
    check they could never pass, while the actual clones still got through. Two messages sharing a
    question stem are fine; two messages that are 70% the same text are not, and that is the thing
    worth spending a rewrite on."""
    if not text:
        return []
    shape, hits = _opening_shape(text), []
    for prev in previous:
        if shape and shape == _opening_shape(prev):
            hits.append(f"same opening: '{shape}'")
        elif difflib.SequenceMatcher(None, text, prev).ratio() > _SIMILARITY_LIMIT:
            hits.append(f"too similar to: '{prev[:60]}...'")
    return hits[:2]


_MAX_REWRITES = 2  # rewrites per lead before shipping a tagged draft; keeps a bad batch bounded


def _build_prompt(style, lead, previous=()):
    spec = _STYLE[style]
    archetype = _pick_archetype(style, lead)
    avoid = ""
    if previous:
        recent = "\n".join(f"  - {m}" for m in list(previous)[-5:])
        avoid = ("\n\nMessages already written in this batch. Yours must not reuse their opening, "
                 "their sentence structure, or any distinctive phrase from them. Take a visibly "
                 f"different angle:\n{recent}\n")
    user_prompt = (
        f"{spec['channel_rules']}\n\n"
        f"Archetype to use: {_ARCHETYPE_GUIDE[archetype]}\n\n"
        f"Lead:\n{_lead_context(lead)}"
        f"{avoid}\n"
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

    def generate(self, style, lead, previous=()):
        """Return (message, archetype, provider). provider is '' if all failed.

        A draft that uses banned phrasing OR clones another message already in this batch is
        regenerated with the specific problem named, up to _MAX_REWRITES times. A draft that is
        still bad after the last attempt comes back tagged ('!banned:' / '!repeat:') rather than
        silently shipped, so the caller can surface it instead of it reaching a CRM unnoticed."""
        archetype, user, max_chars = _build_prompt(style, lead, previous)
        attempts = []
        if self.openai:
            attempts.append(("openai", self._via_openai))
        if self.anthropic:
            attempts.append(("claude", self._via_anthropic))
        for name, fn in attempts:
            try:
                prompt, last = user, ""
                for attempt in range(_MAX_REWRITES + 1):
                    cleaned = _clean(fn(_SYSTEM, prompt, 350), max_chars)
                    if not cleaned:
                        break
                    last = cleaned
                    banned = banned_hits(cleaned)
                    numbers = number_hits(cleaned)
                    repeats = repeat_hits(cleaned, previous)
                    if not banned and not numbers and not repeats:
                        return cleaned, archetype, name
                    if attempt == _MAX_REWRITES:
                        tag = (f"!banned:{','.join(banned)}" if banned
                               else f"!number:{numbers[0]}" if numbers
                               else f"!repeat:{repeats[0]}")
                        return cleaned, archetype + tag, name
                    problems = []
                    if banned:
                        problems.append(f"banned phrasing ({', '.join(banned)})")
                    if numbers:
                        problems.append(f"it cites a scraped rating/review figure ({', '.join(numbers)}), "
                                        "which reads as automated. Describe their reputation in words instead")
                    if repeats:
                        problems.append(f"it repeats another message in this batch ({'; '.join(repeats)})")
                    prompt = user + (
                        f"\n\nYour previous draft was rejected: {' and '.join(problems)}.\n"
                        f"Rejected draft: {cleaned}\n"
                        "Rewrite from scratch. Say something genuinely different about THIS lead, "
                        "with a different sentence structure and a different opening. Do not just "
                        "swap synonyms into the same frame."
                    )
                if last:
                    continue
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
    """List of messages aligned to leads. Blank entries where all providers failed.

    Carries the batch's opening shapes forward so each message is told what the previous ones
    already sounded like. Without this every lead is generated in isolation and the batch converges
    on one shape, which is exactly what made the last run read as a template."""
    out, previous, flagged = [], [], 0
    for n, lead in enumerate(leads, 1):
        if client is None:
            out.append("")
            continue
        msg, arch, provider = client.generate(style, lead, previous)
        tag = lead.get("first_name") or lead.get("name") or lead.get("username") or "?"
        status = f"{len(msg)} chars [{arch} via {provider}]" if msg else f"BLANK [{arch}]"
        print(f"    [{n}/{len(leads)}] {str(tag)[:30]:<30} {status}", flush=True)
        if any(t in arch for t in ("!banned:", "!number:", "!repeat:")):
            flagged += 1
        if msg:
            previous.append(msg)
        out.append(msg)
    if flagged:
        print(f"    WARNING: {flagged}/{len(leads)} message(s) still looked banned or duplicated "
              f"after {_MAX_REWRITES} rewrites (tagged above). Review before sending.", flush=True)
    return out


def demo():
    """Self-check: no prompt hands the model phrasing, the banned filter catches the 2026-07-25
    offenders, and third-party review text is labelled distinctly from the prospect's own words.
    No network, no API key needed."""
    # 1. The regression that started this: no archetype may contain literal copy for the model to
    # parrot. If any of these reappear in the guide, batches converge on one template again.
    guide_text = " ".join(_ARCHETYPE_GUIDE.values()).lower()
    for leaked in ("probably not a fit", "no pitch", "useful to connect", "not sure if it's a fit"):
        assert leaked not in guide_text, f"archetype guide leaks phrasing: {leaked}"

    # 2. Every style's weighted pools must reference archetypes that actually exist.
    for style, spec in _STYLE.items():
        for pool in ("with_signal", "no_signal"):
            for name, _ in spec[pool]:
                assert name in _ARCHETYPE_GUIDE, f"{style}.{pool} -> unknown archetype {name}"

    # 3. Banned filter catches exactly what Aleem flagged by hand, and stays quiet on clean copy.
    assert banned_hits("Probably not a fit, but do you still handle SEO by hand?")
    assert banned_hits("Would be useful to connect. No pitch.")
    assert banned_hits("I noticed your recent post")
    assert banned_hits("we help you streamline and leverage robust workflows")
    assert banned_hits("Nice work — really strong") == ["em-dash"]
    assert not banned_hits("125 reviews and still a 5.0 is rare. How do you hold that at volume?")

    # 4. Third-party review text must never be presented as the prospect's own words, and the raw
    # rating/review figures must never reach the prompt at all (Aleem's 2026-07-26 review: citing
    # "4.9 across 27 reviews" reads as machine-written). Only the qualitative band goes through.
    ctx = _lead_context({"name": "Bop Design", "rating": "5", "reviews": "125 reviews",
                         "review_summary": "Bop Design is praised for modern websites."})
    assert "NOT their words" in ctx, ctx
    assert "125" not in ctx and "5 rating" not in ctx, f"raw figures leaked into prompt: {ctx}"
    assert "strong reputation" in ctx, ctx
    assert reputation_band("4.9", "27 reviews").startswith("a strong reputation")
    assert reputation_band("4.6", "8 reviews") == "consistently good client feedback"
    assert reputation_band("", "") == "" and reputation_band("3.2", "5") == ""

    # The exact tells from the live CRM screenshot must be caught, and clean praise must pass.
    assert number_hits("The 4.9 rating across 27 reviews stood out.")
    assert number_hits("A 5 rating across 21 reviews says a lot")
    assert number_hits("22 reviews at 5.0 says a lot about")
    assert number_hits("Steptech's 5 rating across 20 reviews")
    assert number_hits("rated 4.8 by clients") and number_hits("4.9/5 overall")
    assert not number_hits("the reputation you've built with clients speaks for itself")
    assert not number_hits("Founded in 2014, working across 3 continents")
    own = _lead_context({"name": "X", "bio": "we ship B2B sites"})
    assert "safe to reference" in own, own

    # 5. A verifiable number alone counts as signal (bio-only was the old, too-narrow test).
    assert _has_signal({"rating": "4.9", "reviews": "40 reviews"})
    assert not _has_signal({"name": "No Facts Co"})

    # 6. Anti-repeat. Digits are stripped on purpose: "125 reviews and still holding" and "40 reviews
    # and still holding" are the SAME burned shape even though the number differs, and that
    # number-swapped repetition is precisely what a batch converges on.
    assert _opening_shape("125 reviews and still holding on") == _opening_shape("40 Reviews, and still holding on!")
    assert _opening_shape("saw the work you do here") != _opening_shape("125 reviews and still holding on")
    # A leading first-name greeting must not let a clone dodge the check.
    assert _opening_shape("Alex, 4.9 across 28 reviews suggests consistency") == \
           _opening_shape("4.9 across 26 reviews suggests consistency")

    # The exact near-duplicates a live 8-lead sample produced on 2026-07-25, which the first
    # (advisory-only) version of this guard failed to stop. These must now be caught.
    a = "4.9 across 26 reviews suggests a pretty consistent way of running things, not just a few good outcomes."
    b = "Alex, 4.9 across 28 reviews suggests a very consistent way of working, not just one good outcome."
    c = "CRM and ERP implementations look straightforward until data and process line up."
    assert repeat_hits(b, [a]), "near-duplicate must be caught"
    assert not repeat_hits(c, [a]), "a genuinely different message must pass"
    assert not repeat_hits(a, []), "first message in a batch has nothing to repeat"

    # The n-gram version's failure, found only after a 92-message live batch: it fired on ordinary
    # shared question stems, so nearly every lead burned its whole rewrite budget on an unpassable
    # check while real clones slipped through. Two messages may share a closing question and still
    # be completely different messages.
    q1 = "Lickability's iOS and Android split is the interesting part. How do you keep that consistent?"
    q2 = "Diffco ships AI that survives real users, which is the rare bit. How do you keep that steady?"
    assert not repeat_hits(q2, [q1]), "shared question stem alone must NOT count as a repeat"

    _, prompt, _ = _build_prompt("li_note", {"name": "X", "rating": "5"}, [a])
    assert "already written in this batch" in prompt and a in prompt
    print("messages self-check OK")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Touch 1 message generator (self-check entrypoint).")
    p.add_argument("--selftest", action="store_true")
    if p.parse_args().selftest:
        demo()
    else:
        p.error("pass --selftest (this module is normally imported, not run)")
