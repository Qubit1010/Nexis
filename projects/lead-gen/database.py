"""SQLite database models and connection management.

Tables:
  leads             — core lead data
  scores            — 5-layer ICP scores per lead
  enrichment        — website intel, email, LinkedIn, news data
  personalization   — Claude-generated hooks, pain points, value props
  outreach_sequences — platform-specific outreach copy (email/LinkedIn/Instagram)
  exports           — export history (idempotency guard)
  app_config        — key-value config (e.g., hunter monthly usage counter)
"""

import json
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

from config import DB_PATH


# ---------------------------------------------------------------------------
# Connection
# ---------------------------------------------------------------------------

def get_connection():
    """Open a SQLite connection with foreign keys enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row  # rows accessible as dicts
    return conn


@contextmanager
def db():
    """Context manager — auto-commits on success, rolls back on error."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Schema creation
# ---------------------------------------------------------------------------

CREATE_LEADS = """
CREATE TABLE IF NOT EXISTS leads (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id          TEXT UNIQUE NOT NULL,
    source           TEXT NOT NULL,        -- linkedin_jobs|linkedin_profiles|google_search|product_hunt
    first_name       TEXT DEFAULT '',
    last_name        TEXT DEFAULT '',
    full_name        TEXT DEFAULT '',
    title            TEXT DEFAULT '',
    company          TEXT DEFAULT '',
    company_size     TEXT DEFAULT '',
    industry         TEXT DEFAULT '',
    company_website  TEXT DEFAULT '',
    linkedin_url     TEXT DEFAULT '',
    company_linkedin TEXT DEFAULT '',
    instagram_url    TEXT DEFAULT '',
    instagram_handle TEXT DEFAULT '',
    email            TEXT DEFAULT '',
    email_verified   TEXT DEFAULT '',      -- Y|Unverified|N|''
    location         TEXT DEFAULT '',
    pain_signal      TEXT DEFAULT '',
    pain_keywords    TEXT DEFAULT '',      -- CSV of matched keywords
    recent_activity  TEXT DEFAULT '',      -- LinkedIn post or search snippet
    funding_signal   INTEGER DEFAULT 0,   -- 0|1
    date_discovered  TEXT NOT NULL
)
"""

CREATE_SCORES = """
CREATE TABLE IF NOT EXISTS scores (
    lead_id          TEXT PRIMARY KEY REFERENCES leads(lead_id),
    contact_quality  INTEGER DEFAULT 0,
    company_quality  INTEGER DEFAULT 0,
    intent_signal    INTEGER DEFAULT 0,
    decision_maker   INTEGER DEFAULT 0,
    reachability     INTEGER DEFAULT 0,
    total_score      INTEGER DEFAULT 0,
    tier             TEXT DEFAULT '',      -- HOT|STRONG|WARM|REJECTED
    score_breakdown  TEXT DEFAULT '{}',   -- JSON
    scored_at        TEXT
)
"""

CREATE_ENRICHMENT = """
CREATE TABLE IF NOT EXISTS enrichment (
    lead_id          TEXT PRIMARY KEY REFERENCES leads(lead_id),
    website_tech     TEXT DEFAULT '{}',   -- JSON: {cms, frameworks, analytics}
    pagespeed_mobile INTEGER DEFAULT -1,
    pagespeed_desktop INTEGER DEFAULT -1,
    core_web_vitals  TEXT DEFAULT '{}',   -- JSON: {lcp, cls, fid}
    site_issues      TEXT DEFAULT '[]',   -- JSON array: [missing_meta, broken_links, no_ssl]
    site_last_updated TEXT DEFAULT '',
    company_news     TEXT DEFAULT '',
    funding_news     TEXT DEFAULT '',
    proxycurl_data   TEXT DEFAULT '{}',   -- JSON: full LinkedIn profile
    recent_posts     TEXT DEFAULT '[]',   -- JSON: last 3 LinkedIn posts
    enriched_at      TEXT,
    enrichment_cost  REAL DEFAULT 0.0    -- $ spent tracking
)
"""

CREATE_PERSONALIZATION = """
CREATE TABLE IF NOT EXISTS personalization (
    lead_id          TEXT PRIMARY KEY REFERENCES leads(lead_id),
    hook_1           TEXT DEFAULT '',
    hook_2           TEXT DEFAULT '',
    hook_3           TEXT DEFAULT '',
    pain_points      TEXT DEFAULT '[]',   -- JSON: [{pain, evidence, solution}]
    value_prop       TEXT DEFAULT '',
    social_proof     TEXT DEFAULT '',
    best_channel     TEXT DEFAULT '',     -- cold_email|linkedin|instagram
    channel_reasoning TEXT DEFAULT '',
    personalized_at  TEXT
)
"""

CREATE_SEQUENCES = """
CREATE TABLE IF NOT EXISTS outreach_sequences (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id          TEXT NOT NULL REFERENCES leads(lead_id),
    platform         TEXT NOT NULL,       -- cold_email|linkedin|instagram
    sequence_json    TEXT DEFAULT '{}',
    generated_at     TEXT,
    UNIQUE(lead_id, platform)
)
"""

CREATE_EXPORTS = """
CREATE TABLE IF NOT EXISTS exports (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id          TEXT NOT NULL REFERENCES leads(lead_id),
    platform         TEXT NOT NULL,       -- cold_email|linkedin|instagram
    export_type      TEXT NOT NULL,       -- sheets|csv
    export_status    TEXT NOT NULL,       -- exported|skipped_tier|skipped_no_contact
    exported_at      TEXT NOT NULL,
    UNIQUE(lead_id, platform, export_type)
)
"""

CREATE_CONFIG = """
CREATE TABLE IF NOT EXISTS app_config (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
)
"""


def init_db():
    """Create all tables if they don't exist."""
    with db() as conn:
        conn.execute(CREATE_LEADS)
        conn.execute(CREATE_SCORES)
        conn.execute(CREATE_ENRICHMENT)
        conn.execute(CREATE_PERSONALIZATION)
        conn.execute(CREATE_SEQUENCES)
        conn.execute(CREATE_EXPORTS)
        conn.execute(CREATE_CONFIG)
    print(f"Database ready: {DB_PATH}")


# ---------------------------------------------------------------------------
# Lead ID generation
# ---------------------------------------------------------------------------

def generate_lead_id():
    """Generate a unique sequential lead ID: LG-YYYYMMDD-XXXX."""
    today = date.today().strftime("%Y%m%d")
    with db() as conn:
        row = conn.execute(
            "SELECT lead_id FROM leads WHERE lead_id LIKE ? ORDER BY id DESC LIMIT 1",
            (f"LG-{today}-%",)
        ).fetchone()
        if row:
            seq = int(row["lead_id"].split("-")[-1]) + 1
        else:
            seq = 1
    return f"LG-{today}-{seq:04d}"


# ---------------------------------------------------------------------------
# Lead CRUD
# ---------------------------------------------------------------------------

def insert_lead(lead: dict) -> str:
    """Insert a new lead. Returns lead_id. Skips if linkedin_url already exists."""
    lead_id = generate_lead_id()
    today = date.today().isoformat()

    with db() as conn:
        try:
            conn.execute("""
                INSERT INTO leads (
                    lead_id, source, first_name, last_name, full_name,
                    title, company, company_size, industry, company_website,
                    linkedin_url, company_linkedin, instagram_url, instagram_handle,
                    email, email_verified, location, pain_signal, pain_keywords,
                    recent_activity, funding_signal, date_discovered
                ) VALUES (
                    :lead_id, :source, :first_name, :last_name, :full_name,
                    :title, :company, :company_size, :industry, :company_website,
                    :linkedin_url, :company_linkedin, :instagram_url, :instagram_handle,
                    :email, :email_verified, :location, :pain_signal, :pain_keywords,
                    :recent_activity, :funding_signal, :date_discovered
                )
            """, {
                "lead_id": lead_id,
                "source": lead.get("source", ""),
                "first_name": lead.get("first_name", ""),
                "last_name": lead.get("last_name", ""),
                "full_name": lead.get("full_name", "") or f"{lead.get('first_name', '')} {lead.get('last_name', '')}".strip(),
                "title": lead.get("title", ""),
                "company": lead.get("company", ""),
                "company_size": lead.get("company_size", ""),
                "industry": lead.get("industry", ""),
                "company_website": lead.get("company_website", ""),
                "linkedin_url": lead.get("linkedin_url", ""),
                "company_linkedin": lead.get("company_linkedin", ""),
                "instagram_url": lead.get("instagram_url", ""),
                "instagram_handle": lead.get("instagram_handle", ""),
                "email": lead.get("email", ""),
                "email_verified": lead.get("email_verified", ""),
                "location": lead.get("location", ""),
                "pain_signal": lead.get("pain_signal", ""),
                "pain_keywords": lead.get("pain_keywords", ""),
                "recent_activity": lead.get("recent_activity", ""),
                "funding_signal": 1 if lead.get("funding_signal") else 0,
                "date_discovered": lead.get("date_discovered", today),
            })
            return lead_id
        except sqlite3.IntegrityError:
            return None  # duplicate (linkedin_url or lead_id collision)


def update_lead(lead_id: str, fields: dict):
    """Update specific fields on a lead."""
    if not fields:
        return
    set_clause = ", ".join(f"{k} = :{k}" for k in fields)
    with db() as conn:
        conn.execute(
            f"UPDATE leads SET {set_clause} WHERE lead_id = :lead_id",
            {**fields, "lead_id": lead_id}
        )


def get_lead(lead_id: str) -> dict | None:
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM leads WHERE lead_id = ?", (lead_id,)
        ).fetchone()
        return dict(row) if row else None


def get_leads(filters: dict = None, limit: int = None) -> list[dict]:
    """Get leads with optional filters. Returns list of dicts."""
    query = "SELECT l.*, s.total_score, s.tier FROM leads l LEFT JOIN scores s ON l.lead_id = s.lead_id"
    params = []

    if filters:
        conditions = []
        for key, val in filters.items():
            if key == "tier":
                conditions.append("s.tier = ?")
                params.append(val)
            elif key == "tier_in":
                placeholders = ",".join("?" * len(val))
                conditions.append(f"s.tier IN ({placeholders})")
                params.extend(val)
            elif key == "not_scored":
                conditions.append("s.lead_id IS NULL")
            elif key == "source":
                conditions.append("l.source = ?")
                params.append(val)
            else:
                conditions.append(f"l.{key} = ?")
                params.append(val)
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY l.id DESC"
    if limit:
        query += f" LIMIT {limit}"

    with db() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def check_duplicate(linkedin_url: str = None, company: str = None, first_name: str = None) -> bool:
    """Return True if a lead already exists with this linkedin_url or (company+first_name)."""
    with db() as conn:
        if linkedin_url:
            row = conn.execute(
                "SELECT 1 FROM leads WHERE linkedin_url = ? AND linkedin_url != ''",
                (linkedin_url,)
            ).fetchone()
            if row:
                return True
        if company and first_name:
            # Normalize: strip punctuation, lowercase
            norm_company = "".join(c for c in company.lower() if c.isalnum())
            norm_name = first_name.lower().strip()
            rows = conn.execute(
                "SELECT company, first_name FROM leads"
            ).fetchall()
            for r in rows:
                rc = "".join(c for c in (r["company"] or "").lower() if c.isalnum())
                rn = (r["first_name"] or "").lower().strip()
                if rc == norm_company and rn == norm_name:
                    return True
    return False


# ---------------------------------------------------------------------------
# Score CRUD
# ---------------------------------------------------------------------------

def upsert_score(lead_id: str, scores: dict):
    """Insert or replace score record."""
    with db() as conn:
        conn.execute("""
            INSERT INTO scores (
                lead_id, contact_quality, company_quality, intent_signal,
                decision_maker, reachability, total_score, tier, score_breakdown, scored_at
            ) VALUES (
                :lead_id, :contact_quality, :company_quality, :intent_signal,
                :decision_maker, :reachability, :total_score, :tier, :score_breakdown, :scored_at
            )
            ON CONFLICT(lead_id) DO UPDATE SET
                contact_quality = excluded.contact_quality,
                company_quality = excluded.company_quality,
                intent_signal = excluded.intent_signal,
                decision_maker = excluded.decision_maker,
                reachability = excluded.reachability,
                total_score = excluded.total_score,
                tier = excluded.tier,
                score_breakdown = excluded.score_breakdown,
                scored_at = excluded.scored_at
        """, {
            "lead_id": lead_id,
            "contact_quality": scores.get("contact_quality", 0),
            "company_quality": scores.get("company_quality", 0),
            "intent_signal": scores.get("intent_signal", 0),
            "decision_maker": scores.get("decision_maker", 0),
            "reachability": scores.get("reachability", 0),
            "total_score": scores.get("total_score", 0),
            "tier": scores.get("tier", ""),
            "score_breakdown": json.dumps(scores.get("breakdown", {})),
            "scored_at": datetime.now().isoformat(),
        })


def get_score(lead_id: str) -> dict | None:
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM scores WHERE lead_id = ?", (lead_id,)
        ).fetchone()
        return dict(row) if row else None


# ---------------------------------------------------------------------------
# Enrichment CRUD
# ---------------------------------------------------------------------------

def upsert_enrichment(lead_id: str, data: dict):
    with db() as conn:
        # Serialize dicts/lists to JSON strings
        def to_json(val):
            return json.dumps(val) if isinstance(val, (dict, list)) else (val or "")

        conn.execute("""
            INSERT INTO enrichment (
                lead_id, website_tech, pagespeed_mobile, pagespeed_desktop,
                core_web_vitals, site_issues, site_last_updated,
                company_news, funding_news, proxycurl_data, recent_posts,
                enriched_at, enrichment_cost
            ) VALUES (
                :lead_id, :website_tech, :pagespeed_mobile, :pagespeed_desktop,
                :core_web_vitals, :site_issues, :site_last_updated,
                :company_news, :funding_news, :proxycurl_data, :recent_posts,
                :enriched_at, :enrichment_cost
            )
            ON CONFLICT(lead_id) DO UPDATE SET
                website_tech = CASE WHEN excluded.website_tech != '{}' THEN excluded.website_tech ELSE website_tech END,
                pagespeed_mobile = CASE WHEN excluded.pagespeed_mobile >= 0 THEN excluded.pagespeed_mobile ELSE pagespeed_mobile END,
                pagespeed_desktop = CASE WHEN excluded.pagespeed_desktop >= 0 THEN excluded.pagespeed_desktop ELSE pagespeed_desktop END,
                core_web_vitals = CASE WHEN excluded.core_web_vitals != '{}' THEN excluded.core_web_vitals ELSE core_web_vitals END,
                site_issues = CASE WHEN excluded.site_issues != '[]' THEN excluded.site_issues ELSE site_issues END,
                site_last_updated = CASE WHEN excluded.site_last_updated != '' THEN excluded.site_last_updated ELSE site_last_updated END,
                company_news = CASE WHEN excluded.company_news != '' THEN excluded.company_news ELSE company_news END,
                funding_news = CASE WHEN excluded.funding_news != '' THEN excluded.funding_news ELSE funding_news END,
                proxycurl_data = CASE WHEN excluded.proxycurl_data != '{}' THEN excluded.proxycurl_data ELSE proxycurl_data END,
                recent_posts = CASE WHEN excluded.recent_posts != '[]' THEN excluded.recent_posts ELSE recent_posts END,
                enriched_at = excluded.enriched_at,
                enrichment_cost = enrichment_cost + excluded.enrichment_cost
        """, {
            "lead_id": lead_id,
            "website_tech": to_json(data.get("website_tech", {})),
            "pagespeed_mobile": data.get("pagespeed_mobile", -1),
            "pagespeed_desktop": data.get("pagespeed_desktop", -1),
            "core_web_vitals": to_json(data.get("core_web_vitals", {})),
            "site_issues": to_json(data.get("site_issues", [])),
            "site_last_updated": data.get("site_last_updated", ""),
            "company_news": data.get("company_news", ""),
            "funding_news": data.get("funding_news", ""),
            "proxycurl_data": to_json(data.get("proxycurl_data", {})),
            "recent_posts": to_json(data.get("recent_posts", [])),
            "enriched_at": datetime.now().isoformat(),
            "enrichment_cost": data.get("enrichment_cost", 0.0),
        })


def get_enrichment(lead_id: str) -> dict | None:
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM enrichment WHERE lead_id = ?", (lead_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        # Deserialize JSON fields
        for field in ["website_tech", "core_web_vitals", "site_issues", "proxycurl_data", "recent_posts"]:
            try:
                d[field] = json.loads(d[field])
            except (json.JSONDecodeError, TypeError):
                d[field] = {} if field not in ["site_issues", "recent_posts"] else []
        return d


# ---------------------------------------------------------------------------
# Personalization CRUD
# ---------------------------------------------------------------------------

def upsert_personalization(lead_id: str, data: dict):
    with db() as conn:
        conn.execute("""
            INSERT INTO personalization (
                lead_id, hook_1, hook_2, hook_3, pain_points,
                value_prop, social_proof, best_channel, channel_reasoning, personalized_at
            ) VALUES (
                :lead_id, :hook_1, :hook_2, :hook_3, :pain_points,
                :value_prop, :social_proof, :best_channel, :channel_reasoning, :personalized_at
            )
            ON CONFLICT(lead_id) DO UPDATE SET
                hook_1 = excluded.hook_1,
                hook_2 = excluded.hook_2,
                hook_3 = excluded.hook_3,
                pain_points = excluded.pain_points,
                value_prop = excluded.value_prop,
                social_proof = excluded.social_proof,
                best_channel = excluded.best_channel,
                channel_reasoning = excluded.channel_reasoning,
                personalized_at = excluded.personalized_at
        """, {
            "lead_id": lead_id,
            "hook_1": data.get("hook_1", ""),
            "hook_2": data.get("hook_2", ""),
            "hook_3": data.get("hook_3", ""),
            "pain_points": json.dumps(data.get("pain_points", [])),
            "value_prop": data.get("value_prop", ""),
            "social_proof": data.get("social_proof", ""),
            "best_channel": data.get("best_channel", ""),
            "channel_reasoning": data.get("channel_reasoning", ""),
            "personalized_at": datetime.now().isoformat(),
        })


def get_personalization(lead_id: str) -> dict | None:
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM personalization WHERE lead_id = ?", (lead_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["pain_points"] = json.loads(d["pain_points"])
        except (json.JSONDecodeError, TypeError):
            d["pain_points"] = []
        return d


# ---------------------------------------------------------------------------
# Sequence CRUD
# ---------------------------------------------------------------------------

def upsert_sequence(lead_id: str, platform: str, sequence: dict):
    with db() as conn:
        conn.execute("""
            INSERT INTO outreach_sequences (lead_id, platform, sequence_json, generated_at)
            VALUES (:lead_id, :platform, :sequence_json, :generated_at)
            ON CONFLICT(lead_id, platform) DO UPDATE SET
                sequence_json = excluded.sequence_json,
                generated_at = excluded.generated_at
        """, {
            "lead_id": lead_id,
            "platform": platform,
            "sequence_json": json.dumps(sequence),
            "generated_at": datetime.now().isoformat(),
        })


def get_sequence(lead_id: str, platform: str) -> dict | None:
    with db() as conn:
        row = conn.execute(
            "SELECT * FROM outreach_sequences WHERE lead_id = ? AND platform = ?",
            (lead_id, platform)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        try:
            d["sequence_json"] = json.loads(d["sequence_json"])
        except (json.JSONDecodeError, TypeError):
            d["sequence_json"] = {}
        return d


# ---------------------------------------------------------------------------
# Export tracking
# ---------------------------------------------------------------------------

def mark_exported(lead_id: str, platform: str, export_type: str, status: str):
    with db() as conn:
        conn.execute("""
            INSERT INTO exports (lead_id, platform, export_type, export_status, exported_at)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(lead_id, platform, export_type) DO NOTHING
        """, (lead_id, platform, export_type, status, datetime.now().isoformat()))


def already_exported(lead_id: str, platform: str, export_type: str) -> bool:
    with db() as conn:
        row = conn.execute(
            "SELECT 1 FROM exports WHERE lead_id = ? AND platform = ? AND export_type = ? AND export_status = 'exported'",
            (lead_id, platform, export_type)
        ).fetchone()
        return row is not None


# ---------------------------------------------------------------------------
# App config (key-value store)
# ---------------------------------------------------------------------------

def get_config(key: str, default=None):
    with db() as conn:
        row = conn.execute("SELECT value FROM app_config WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default


def set_config(key: str, value):
    with db() as conn:
        conn.execute(
            "INSERT INTO app_config (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, str(value))
        )


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------

def get_stats() -> dict:
    with db() as conn:
        total = conn.execute("SELECT COUNT(*) as n FROM leads").fetchone()["n"]
        by_source = conn.execute(
            "SELECT source, COUNT(*) as n FROM leads GROUP BY source"
        ).fetchall()
        by_tier = conn.execute(
            "SELECT tier, COUNT(*) as n FROM scores GROUP BY tier"
        ).fetchall()
        unscored = conn.execute(
            "SELECT COUNT(*) as n FROM leads l WHERE NOT EXISTS (SELECT 1 FROM scores s WHERE s.lead_id = l.lead_id)"
        ).fetchone()["n"]
        unenriched = conn.execute(
            "SELECT COUNT(*) as n FROM scores s WHERE s.tier IN ('HOT','STRONG','WARM') "
            "AND NOT EXISTS (SELECT 1 FROM enrichment e WHERE e.lead_id = s.lead_id)"
        ).fetchone()["n"]
        by_export = conn.execute(
            "SELECT platform, COUNT(*) as n FROM exports WHERE export_status = 'exported' GROUP BY platform"
        ).fetchall()

    return {
        "total": total,
        "unscored": unscored,
        "unenriched": unenriched,
        "by_source": {r["source"]: r["n"] for r in by_source},
        "by_tier": {r["tier"]: r["n"] for r in by_tier},
        "exported": {r["platform"]: r["n"] for r in by_export},
    }
