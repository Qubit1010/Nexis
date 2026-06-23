"""Per-channel configuration + identity logic for the leads-to-crm pipeline.

The whole point of this file is the *identity function*. Both reported bugs in
the old pipeline came from keying dedup off the raw profile URL: Instagram post
URLs (instagram.com/p/...) collapse to a useless ".../p" key, so a profile
already in the CRM never matches its post URL and gets re-added (duplicate), and
post URLs were also hard-dropped as "invalid" so freshly scraped rows never
reached the CRM (ignored). The fix is to derive ONE stable identity per lead
(Instagram: the @handle; LinkedIn: the /in/<slug>) and use that exact same
function for source rows, the existing-CRM set, and the dedup pass. Same input
shape in, same key out, everywhere.

Adding a new channel (e.g. Facebook) = add one Channel subclass below and
register it in CHANNELS. No changes to push.py.
"""

import re


# ---------------------------------------------------------------------------
# Shared name parsing
# ---------------------------------------------------------------------------

_BUSINESS_WORDS = {
    "agency", "marketing", "digital", "studio", "media", "group", "llc", "inc",
    "ltd", "co", "services", "solutions", "consulting", "design", "creative",
    "brand", "brands", "ventures", "labs", "tech", "technologies", "management",
    "productions", "collective",
}


def first_name_of(clean_name):
    """A person's first name, or '' if the name looks like a business/brand."""
    if not clean_name:
        return ""
    base = re.split(r"\s*[|\-–—]\s*", clean_name)[0].strip()
    words = base.split()
    if not words:
        return ""
    if {w.lower().rstrip(".,") for w in words} & _BUSINESS_WORDS:
        return ""
    if len(words) > 3:
        return ""
    first = words[0]
    if first == first.upper() and len(first) > 1:
        return ""
    if not first[0].isupper():
        return ""
    return first


def split_name_handle(raw_name):
    """'Dave Pancham (@davepancham)' -> ('Dave Pancham', '@davepancham')."""
    m = re.search(r"\(@([^)]+)\)", raw_name)
    username = "@" + m.group(1).strip() if m else ""
    clean = re.sub(r"\s*\(@[^)]+\)", "", raw_name).strip()
    return clean, username


def split_url_and_name(row, col_map):
    """Return (url, display_name) regardless of which column holds which.

    The Instant Data Scraper flips Name/Link between sessions, so the URL can
    land in either cell. Whichever one starts with http is the URL.
    """
    name_idx = col_map.get("full_name")
    link_idx = col_map.get("source_url")
    cells = []
    for idx in (name_idx, link_idx):
        cells.append(row[idx].strip() if idx is not None and idx < len(row) else "")
    if cells[0].lower().startswith("http"):
        return cells[0], cells[1]
    if cells[1].lower().startswith("http"):
        return cells[1], cells[0]
    return "", cells[0] or cells[1]


def build_col_map(header_row, aliases):
    """{canonical_field: column_index} from a header row + alias map."""
    col_map = {}
    for i, cell in enumerate(header_row):
        canonical = aliases.get(cell.strip().lower())
        if canonical and canonical not in col_map:
            col_map[canonical] = i
    return col_map


def cell(row, col_map, field, default=""):
    idx = col_map.get(field)
    if idx is None or idx >= len(row):
        return default
    return row[idx].strip()


# ---------------------------------------------------------------------------
# Base channel
# ---------------------------------------------------------------------------

class Channel:
    key = ""
    label = ""
    source_sheet_id = ""
    source_tab = "Raw"
    crm_sheet_id = ""
    crm_tab = "Leads"
    message_style = ""
    source_aliases = {}            # header(lower) -> canonical field
    status_header_names = ["include to crm", "include", "include in crm", "status"]

    def parse_row(self, row, col_map):
        """Return a lead dict, or None if the row is blank/unusable."""
        raise NotImplementedError

    def identity(self, lead):
        """Stable dedup key for a parsed source lead. '' = unresolvable."""
        raise NotImplementedError

    def crm_identity(self, crm_row, crm_cols):
        """Stable dedup key for an existing CRM row. crm_cols = {header_lower: idx}."""
        raise NotImplementedError

    def crm_record(self, lead, message, today):
        """A dict keyed by the EXACT CRM header strings. push.py places each
        value at the live header's index, so column drift can't corrupt writes."""
        raise NotImplementedError


# ---------------------------------------------------------------------------
# Instagram
# ---------------------------------------------------------------------------

_IG_SYSTEM_SEGMENTS = {
    "p", "reel", "reels", "tv", "explore", "stories", "live", "popular",
    "accounts", "direct", "about", "developer", "legal",
}


def _ig_norm_handle(text):
    h = (text or "").strip().lower().lstrip("@").rstrip("/")
    if "?" in h:
        h = h.split("?")[0]
    if not h or h in _IG_SYSTEM_SEGMENTS:
        return ""
    return h


def _ig_handle_from_url(url):
    if not url:
        return ""
    u = url.strip().lower()
    for alt in ("secure.instagram.com", "www-fallback.instagram.com",
                "www.latest.instagram.com", "m.instagram.com"):
        u = u.replace(alt, "www.instagram.com")
    m = re.search(r"instagram\.com/([^/?#]+)", u)
    return _ig_norm_handle(m.group(1)) if m else ""


class InstagramChannel(Channel):
    key = "instagram"
    label = "Instagram"
    source_sheet_id = "1kOEaNhwD3fsbpAJM6l6-dR0z6n06xgJyyWr3EHKmzyg"
    source_tab = "Raw"
    crm_sheet_id = "1xql6icDspoJxzP1_vIQpjqBWK1RYQBN1C8N28OzkGs8"
    crm_tab = "Leads"
    message_style = "ig_dm"
    source_aliases = {
        "name": "full_name", "full name": "full_name",
        "link": "source_url", "instagram url": "source_url", "instagram": "source_url",
        "url": "source_url", "profile url": "source_url", "profile link": "source_url",
        "followers": "followers", "follower count": "followers",
        "note": "bio", "bio": "bio", "notes": "bio",
        "location/designation": "title", "designation": "title", "title": "title",
        "role": "title", "position": "title",
        "location": "location",
        "company": "company", "company name": "company",
        "username": "username",
    }

    def parse_row(self, row, col_map):
        if not any(c.strip() for c in row):
            return None
        url, raw_name = split_url_and_name(row, col_map)
        clean_name, username = split_name_handle(raw_name)
        if not username:
            uname_col = cell(row, col_map, "username")
            if uname_col:
                username = uname_col if uname_col.startswith("@") else "@" + uname_col

        handle = _ig_norm_handle(username) or _ig_handle_from_url(url)
        followers = cell(row, col_map, "followers")
        if followers.lower().startswith("http"):   # scraper sometimes dumps a URL here
            followers = ""
        profile_url = f"https://www.instagram.com/{handle}/" if handle else url

        if not clean_name and not handle:
            return None
        return {
            "channel": "instagram",
            "_handle": handle,
            "name": clean_name,
            "username": ("@" + handle) if handle else username,
            "company": cell(row, col_map, "company"),
            "title": cell(row, col_map, "title"),
            "location": cell(row, col_map, "location") or cell(row, col_map, "title"),
            "profile_url": profile_url,
            "followers": followers,
            "bio": cell(row, col_map, "bio"),
            "first_name": first_name_of(clean_name),
        }

    def identity(self, lead):
        return lead.get("_handle", "")

    def crm_identity(self, crm_row, crm_cols):
        def g(names):
            for n in names:
                i = crm_cols.get(n)
                if i is not None and i < len(crm_row):
                    return crm_row[i].strip()
            return ""
        return _ig_norm_handle(g(["username"])) or _ig_handle_from_url(
            g(["instagram url", "instagram", "url"]))

    def crm_record(self, lead, message, today):
        return {
            "Name": lead["name"],
            "Username": lead["username"],
            "Company": lead["company"],
            "Role": lead["title"],
            "Instagram URL": lead["profile_url"],
            "Followers": lead["followers"],
            "Bio": lead["bio"],
            "Touch 1 Message": message,
            "Status": "New",
            "Date Added": today,
        }


# ---------------------------------------------------------------------------
# LinkedIn
# ---------------------------------------------------------------------------

def _li_slug(url):
    if not url:
        return ""
    m = re.search(r"linkedin\.com/in/([^/?#]+)", url.strip().lower())
    return m.group(1).rstrip("/") if m else ""


class LinkedinChannel(Channel):
    key = "linkedin"
    label = "LinkedIn"
    source_sheet_id = "1NpBUSFEgofelZ_BZjs6F3IQiOa34MIvLdDUtv1Ebw5Q"
    source_tab = "Raw"
    crm_sheet_id = "1rJM42Hd1kh8G4d3MGIO1SMILSyM86iU5nSD7QQTdOoo"
    crm_tab = "Leads"
    message_style = "li_note"
    source_aliases = {
        "name": "full_name", "full name": "full_name",
        "first name": "first_name", "last name": "last_name",
        "link": "source_url", "linkedin url": "source_url", "linkedin": "source_url",
        "url": "source_url", "profile url": "source_url", "profile link": "source_url",
        "title": "title", "position": "title", "headline": "title",
        "job title": "title", "designation": "title", "role": "title", "occupation": "title",
        "company": "company", "company name": "company", "organization": "company",
        "location": "location", "city": "location", "country": "location", "region": "location",
        "note": "bio", "bio": "bio", "recent post": "bio", "about": "bio",
        "followers": "followers", "connections": "followers",
    }

    def parse_row(self, row, col_map):
        if not any(c.strip() for c in row):
            return None
        url = cell(row, col_map, "source_url")
        raw_name = cell(row, col_map, "full_name")
        if not raw_name and url.lower().startswith("http") is False:
            # Name/Link flip safety (rare for LinkedIn, but cheap to guard)
            url2, name2 = split_url_and_name(row, col_map)
            url, raw_name = url2 or url, name2 or raw_name

        # Name cell is often "Roger Aguiar - Owner & CEO at RG Agency"
        clean_name = re.split(r"\s+[|\-–]\s+", raw_name)[0].strip()
        remainder = raw_name[len(clean_name):]
        first_name = cell(row, col_map, "first_name") or first_name_of(clean_name) \
            or (clean_name.split()[0] if clean_name else "")
        company = cell(row, col_map, "company")
        if not company:
            m = re.search(r"\bat\s+([A-Z0-9][^|\-–]+)", remainder)
            if m:
                company = m.group(1).strip()

        slug = _li_slug(url)
        if not clean_name and not slug:
            return None
        return {
            "channel": "linkedin",
            "_slug": slug,
            "name": clean_name or raw_name,
            "first_name": first_name,
            "company": company,
            "title": cell(row, col_map, "title"),
            "location": cell(row, col_map, "location"),
            "profile_url": url.split("?")[0].rstrip("/"),
            "bio": cell(row, col_map, "bio"),
        }

    def identity(self, lead):
        return lead.get("_slug", "")

    def crm_identity(self, crm_row, crm_cols):
        for n in ("linkedin url", "linkedin", "url"):
            i = crm_cols.get(n)
            if i is not None and i < len(crm_row):
                slug = _li_slug(crm_row[i])
                if slug:
                    return slug
        return ""

    def crm_record(self, lead, message, today):
        return {
            "Name": lead["name"],
            "First Name": lead["first_name"],
            "Company": lead["company"],
            "Role": lead["title"],
            "LinkedIn URL": lead["profile_url"],
            "Location": lead["location"],
            "Recent Post": lead["bio"],
            "Touch 1 Message": message,
            "Status": "New",
            "Date Added": today,
        }


# ---------------------------------------------------------------------------
# Facebook
# ---------------------------------------------------------------------------
#
# Facebook is different from IG/LI in one structural way: the source sheet's
# first column ("Link") holds the group POST url, not the person. The author's
# PROFILE url lives in the "Profile URL" column, filled by the facebook-lead-nav
# skill. So identity keys off Profile URL, and a row that still only has a post
# link (not yet enriched) resolves to '' -> "Needs Review" (i.e. run
# facebook-lead-nav first). Older rows that predate the post-link workflow store
# a profile url directly in "Link"; parse_row falls back to that.

_FB_SYSTEM = {
    "groups", "photo", "photo.php", "watch", "reel", "reels", "marketplace",
    "events", "gaming", "story.php", "permalink.php", "pages", "profile.php",
    "people", "pg", "help", "policies", "login", "sharer", "media", "notes",
    "bookmarks", "friends", "saved", "settings", "messages",
}


def _fb_id(url):
    """Stable Facebook identity from a profile url. '' if it isn't a person.

    'facebook.com/jane.doe.7'           -> 'slug:jane.doe.7'
    'facebook.com/profile.php?id=12345'  -> 'id:12345'
    a group/post link, or empty          -> '' (unresolvable)
    """
    if not url:
        return ""
    u = url.strip()
    if not u.lower().startswith("http"):
        return ""
    if re.search(r"/groups/[^/]+/(posts|permalink)/", u, re.I):
        return ""                      # a post, not a profile
    m = re.search(r"profile\.php\?id=(\d+)", u, re.I)
    if m:
        return "id:" + m.group(1)
    m = re.search(r"(?:facebook|fb)\.com/([^/?#]+)", u, re.I)
    if not m:
        return ""
    slug = m.group(1).strip().lower().rstrip("/")
    if not slug or slug in _FB_SYSTEM:
        return ""
    return "slug:" + slug


def _fb_profile_from_link(link):
    """Best-effort profile URL from a Facebook link, no browser needed.

    Timeline posts carry the author's slug in the path, so they're trivially
    extractable by truncating everything after the slug:
      facebook.com/{slug}/posts/123    -> https://www.facebook.com/{slug}/
      facebook.com/{slug}/photos/123   -> https://www.facebook.com/{slug}/
      facebook.com/profile.php?id=N/.. -> https://www.facebook.com/profile.php?id=N
    Group posts and videos are 'hard' (author not reliably in the url, handled
    elsewhere) -> '' so they fall through to Needs Review for later/manual work.
    """
    if not link:
        return ""
    u = link.strip()
    if not u.lower().startswith("http"):
        return ""
    if re.search(r"/groups/", u, re.I):
        return ""                                   # group post -> facebook-lead-nav
    if re.search(r"facebook\.com/(watch|reel|reels|story\.php|events|marketplace)\b", u, re.I):
        return ""
    if re.search(r"facebook\.com/[^/?#]+/videos/", u, re.I):
        return ""                                   # videos: hard, leave for later
    m = re.search(r"profile\.php\?id=(\d+)", u, re.I)
    if m:
        return "https://www.facebook.com/profile.php?id=" + m.group(1)
    m = re.search(r"facebook\.com/([^/?#]+)", u, re.I)
    if not m:
        return ""
    slug = m.group(1).strip().rstrip("/")
    if not slug or slug.lower() in _FB_SYSTEM:
        return ""
    return "https://www.facebook.com/" + slug + "/"


def _looks_like_snippet(text):
    """True if a 'name' cell is really post text, not a person/brand name."""
    if not text:
        return True
    if len(text.split()) > 4:
        return True
    if re.search(r"[#:]|\.\.\.$|[!?]$", text):
        return True
    if re.search(r"[\U0001F000-\U0001FAFF☀-➿←-⇿]", text):
        return True                                 # emoji / arrows
    return False


def _fb_name_from_slug(profile_url):
    """A display name guessed from a vanity slug. '' for id-only profiles.

    'CameronJGomezBroker' -> 'Cameron J Gomez Broker'
    'chris.salem.773'     -> 'Chris Salem'
    'forestryrealestate'  -> 'Forestryrealestate'  (best effort)
    """
    m = re.search(r"facebook\.com/([^/?#]+)", profile_url or "")
    if not m:
        return ""
    slug = m.group(1)
    if slug.lower().startswith("profile.php"):
        return ""
    slug = re.sub(r"\.?\d+$", "", slug).strip("._")     # drop trailing numeric id
    if "." in slug or "_" in slug:
        parts = [p for p in re.split(r"[._]+", slug) if p]
    else:
        parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])", slug) or [slug]
    return " ".join(p[:1].upper() + p[1:] for p in parts if p).strip()


class FacebookChannel(Channel):
    key = "facebook"
    label = "Facebook"
    source_sheet_id = "1ao7_Aam6bsI6D4xk-Mfc-EM54WZYivN9petcZU2P68U"   # Instant Facebook Leads
    source_tab = "Sheet1"
    crm_sheet_id = "1GkbzCclQsg83P_l5EgKxjceW-Y_7fQ1lByJUGH1aaNg"      # NexusPoint Facebook Outreach CRM
    crm_tab = "Leads"
    message_style = "fb_dm"
    source_aliases = {
        "link": "post_link", "post": "post_link", "post url": "post_link", "post link": "post_link",
        "profile url": "profile_url_col", "profile link": "profile_url_col", "profile": "profile_url_col",
        "lead name": "lead_name",
        "name": "raw_name", "full name": "raw_name",
        "followers": "followers", "follower count": "followers",
        "note": "bio", "bio": "bio", "notes": "bio",
        "designation": "title", "title": "title", "role": "title", "position": "title", "headline": "title",
        "location": "location", "city": "location", "country": "location",
        "company name": "company", "company": "company", "organization": "company",
        "date added": "date_added",
    }

    def parse_row(self, row, col_map):
        if not any(c.strip() for c in row):
            return None
        post_link = cell(row, col_map, "post_link")
        # Profile url: enriched "Profile URL" column wins; else extract from the
        # Link. Timeline /posts/ and /photos/ carry the slug (easy); group posts
        # and /videos/ resolve to '' -> identity '' -> Needs Review (handle later).
        profile_url = cell(row, col_map, "profile_url_col") or _fb_profile_from_link(post_link)

        # Name: enriched "Lead Name" wins; else the "Name" cell unless it's really
        # a post snippet, in which case guess a name from the profile slug.
        lead_name = cell(row, col_map, "lead_name")
        name_cell = cell(row, col_map, "raw_name")
        if lead_name:
            raw_name = lead_name
        elif name_cell and not _looks_like_snippet(name_cell):
            raw_name = name_cell
        else:
            raw_name = _fb_name_from_slug(profile_url)
        clean_name = re.split(r"\s+[|\-–—]\s+", raw_name)[0].strip() if raw_name else ""

        clean_profile = profile_url.split("?")[0] if (profile_url and "profile.php" not in profile_url) else profile_url
        is_post = bool(re.search(r"/(posts|permalink|photos|videos)/", post_link, re.I))
        return {
            "channel": "facebook",
            "_profile_url": profile_url,          # '' here -> identity '' -> Needs Review
            "name": clean_name,
            "first_name": first_name_of(clean_name),
            "company": cell(row, col_map, "company"),
            "title": cell(row, col_map, "title"),
            "location": cell(row, col_map, "location"),
            "profile_url": clean_profile,
            "post_link": post_link if is_post else "",
            "followers": cell(row, col_map, "followers"),
            "bio": cell(row, col_map, "bio"),
        }

    def identity(self, lead):
        return _fb_id(lead.get("_profile_url", ""))

    def crm_identity(self, crm_row, crm_cols):
        for n in ("profile url", "facebook url", "profile", "url"):
            i = crm_cols.get(n)
            if i is not None and i < len(crm_row):
                ident = _fb_id(crm_row[i])
                if ident:
                    return ident
        return ""

    def crm_record(self, lead, message, today):
        return {
            "Name": lead["name"],
            "Profile URL": lead["profile_url"],
            "Company": lead["company"],
            "Role": lead["title"],
            "Location": lead["location"],
            "Source Post": lead["post_link"],
            "Bio": lead["bio"],
            "Touch 1 Message": message,
            "Status": "New",
            "Date Added": today,
        }


# ---------------------------------------------------------------------------
# Registry — add new channels here
# ---------------------------------------------------------------------------

CHANNELS = {
    "instagram": InstagramChannel(),
    "linkedin": LinkedinChannel(),
    "facebook": FacebookChannel(),
}
