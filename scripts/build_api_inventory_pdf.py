#!/usr/bin/env python3
"""Generate the Nexis Projects API & Integration Inventory PDF.

One-off report builder. Run with the Python 3.13 install that has reportlab:
    & "$env:LOCALAPPDATA\Programs\Python\Python313\python.exe" scripts/build_api_inventory_pdf.py
"""

from pathlib import Path
from datetime import date

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether,
)

OUT = Path(__file__).resolve().parents[1] / "Nexis-API-Inventory.pdf"

# ---------------------------------------------------------------------------
# Palette
# ---------------------------------------------------------------------------
INK      = colors.HexColor("#1a1a2e")
ACCENT   = colors.HexColor("#2d6cdf")
MUTED    = colors.HexColor("#5b6472")
HEAD_BG  = colors.HexColor("#2d6cdf")
ROW_ALT  = colors.HexColor("#f2f5fb")
LINE     = colors.HexColor("#d6dbe5")
PAID     = colors.HexColor("#b23a48")
FREE     = colors.HexColor("#1f7a4d")

# ---------------------------------------------------------------------------
# Styles
# ---------------------------------------------------------------------------
styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], textColor=INK, fontSize=22,
                    leading=26, spaceAfter=4, spaceBefore=0)
SUB = ParagraphStyle("SUB", parent=styles["Normal"], textColor=MUTED, fontSize=10.5,
                     leading=14, spaceAfter=2)
H2 = ParagraphStyle("H2", parent=styles["Heading2"], textColor=ACCENT, fontSize=14,
                    leading=18, spaceBefore=14, spaceAfter=6)
H3 = ParagraphStyle("H3", parent=styles["Heading3"], textColor=INK, fontSize=11.5,
                    leading=15, spaceBefore=8, spaceAfter=3)
BODY = ParagraphStyle("BODY", parent=styles["Normal"], textColor=INK, fontSize=9.5,
                      leading=13, spaceAfter=4, alignment=TA_LEFT)
SMALL = ParagraphStyle("SMALL", parent=styles["Normal"], textColor=MUTED, fontSize=8.5,
                       leading=11)
CELL = ParagraphStyle("CELL", parent=styles["Normal"], textColor=INK, fontSize=8.3,
                      leading=10.5)
CELL_H = ParagraphStyle("CELL_H", parent=styles["Normal"], textColor=colors.white,
                        fontSize=8.6, leading=11, fontName="Helvetica-Bold")

def hx(c):
    return "#" + c.hexval()[2:]

def cell(t):
    return Paragraph(t, CELL)

def tag(t, paid):
    c = PAID if paid else FREE
    return Paragraph(f'<font color="{hx(c)}"><b>{t}</b></font>', CELL)

# ---------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------
GENERATED = date.today().isoformat()

# Each project: (name, kind, blurb, rows)
# rows: [service, type(Paid/Free/Local/Manual), how used, model/detail, env/auth]
COL_W = [34*mm, 15*mm, 52*mm, 30*mm, 35*mm]

projects = [
    ("sales-playbook-dashboard", "Next.js web app",
     "Drafts LinkedIn / Instagram DMs from the sales-playbook skill.",
     [
        ["Anthropic Claude API", "Paid", "Primary DM/reply generation", "claude-sonnet-4-6", "ANTHROPIC_API_KEY"],
        ["OpenAI API", "Paid", "Fallback if Anthropic fails", "gpt-5.2", "OPENAI_API_KEY"],
     ]),
    ("content-engine-dashboard", "Next.js web app",
     "Ideates, researches, writes and logs content across IG / LinkedIn / blog.",
     [
        ["Anthropic Claude API", "Paid", "Primary content generation", "claude-sonnet-4-6", "ANTHROPIC_API_KEY"],
        ["OpenAI API", "Paid", "Fallback generation", "gpt-5.2", "OPENAI_API_KEY"],
        ["NotebookLM (CLI)", "Free", "Topic research + synthesis (research_notebooklm.py)", "web research", "Google login"],
        ["Google Workspace (gws)", "Free", "Sheets: schedule, log, YouTube bookmarks", "Sheets API", "gws / Google acct"],
        ["Generic URL fetch", "Free", "fetch-url route (no third party)", "plain fetch()", "none"],
     ]),
    ("upwork-proposal-dashboard", "Next.js web app",
     "Generates Upwork proposals + Loom scripts, saves to Drive.",
     [
        ["Anthropic Claude API", "Paid", "Proposal + Loom script gen (2 routes)", "claude-sonnet-4-6", "ANTHROPIC_API_KEY"],
        ["OpenAI API", "Paid", "Fallback for both routes", "gpt-4o", "OPENAI_API_KEY"],
        ["Google Drive API (googleapis)", "Free", "save-to-drive (OAuth)", "Drive v3", "GOOGLE_CLIENT_ID / _SECRET / _REFRESH_TOKEN"],
     ]),
    ("daily-news-brief", "Next.js + tsx cron",
     "Aggregates AI/tech news, summarizes, writes to a dashboard + Sheets.",
     [
        ["NewsAPI", "Paid", "Article source (6 category queries)", "newsapi.org/v2", "NEWSAPI_KEY"],
        ["Hacker News (Algolia)", "Free", "Story source", "no key", "none"],
        ["RSS feeds (rss-parser)", "Free", "ArXiv, TechCrunch, MIT TR, Verge, Ars", "no key", "none"],
        ["Firecrawl", "Paid", "Scrape AI tool directories", "api.firecrawl.dev/v1", "FIRECRAWL_API_KEY"],
        ["OpenAI API", "Paid", "Primary summarization / analysis", "gpt-4o, gpt-4o-mini", "OPENAI_API_KEY"],
        ["Anthropic Claude API", "Paid", "Fallback summarization", "claude-sonnet-4-6, claude-haiku-4-5", "ANTHROPIC_API_KEY"],
        ["Google Sheets (googleapis)", "Free", "Tool/article draft sheets", "Sheets API", "GOOGLE_SHEETS_SPREADSHEET_ID"],
     ]),
    ("lead-gen", "Python pipeline",
     "Discovers, scores, enriches prospects; exports to 3 CRM sheets.",
     [
        ["Apify", "Paid", "LinkedIn Jobs/Profile + Google Search scrapers", "api.apify.com/v2", "APIFY_API_KEY"],
        ["Proxycurl (nubela.co)", "Paid", "LinkedIn profile enrichment (HOT only, ~$0.01/call)", "proxycurl/api/v2", "PROXYCURL_API_KEY"],
        ["Hunter.io", "Paid", "Verified email finder (free tier 25/mo)", "api.hunter.io/v2", "HUNTER_API_KEY"],
        ["OpenAI API", "Paid", "Personalization + news intel (search-preview, replaces Perplexity)", "gpt-4o-mini, gpt-4o-mini-search-preview", "OPENAI_API_KEY"],
        ["Firecrawl", "Paid", "Website intel (falls back to requests)", "api.firecrawl.dev/v1", "FIRECRAWL_API_KEY"],
        ["Google Workspace (gws)", "Free", "Export to 3 CRM Google Sheets", "Sheets API", "gws / Google acct"],
        ["SMTP + DNS (dnspython)", "Free", "Email verification fallback", "no key", "none"],
        ["Playwright + HN Algolia", "Free", "Browser scrapers (HN, BuiltWith)", "no key", "none"],
     ]),
    ("website-quality-scorer", "FastAPI + Next.js",
     "Crawls a site, scores quality with a local ML model (XGBoost + SHAP).",
     [
        ["Firecrawl", "Paid", "Crawl page HTML / markdown", "api.firecrawl.dev/v1", "FIRECRAWL_API_KEY"],
        ["Google PageSpeed Insights", "Free", "Core Web Vitals (free 25k/day; works keyless, rate-limited)", "pagespeedonline v5", "PAGESPEED_API_KEY"],
        ["XGBoost + SHAP", "Local", "Scoring + explanations", "no API", "none"],
     ]),
    ("reel-engine", "Remotion",
     "Turns infographic posts into voice-synced motion-graphics reels.",
     [
        ["ElevenLabs", "Manual", "Voiceover (script pasted into ElevenLabs UI)", "no API key in code", "manual"],
        ["Whisper (whisper.cpp)", "Local", "Word-level transcription for sync", "@remotion/install-whisper-cpp", "none"],
     ]),
    ("browser-automation", "Playwright (Node)",
     "Stealth scraping of Upwork search results.",
     [
        ["Playwright + stealth", "Free", "Headful browser scraping", "playwright-extra", "none"],
     ]),
    ("upwork-job-scout", "Next.js web app",
     "Job sourcing UI (RSS-based; dummy data + bookmarks). No LLM wired yet.",
     [
        ["RSS feeds (fetch)", "Free", "Job sourcing", "no key", "none"],
     ]),
]

VENDORED = (
    "lightrag", "Vendored third-party RAG library (not a NexusPoint project). "
    "Ships pluggable bindings for OpenAI, Azure OpenAI, Anthropic, Gemini, Zhipu, NVIDIA, "
    "Ollama, vLLM, VoyageAI and more, all selected via its own .env. Only whatever you "
    "configure there is actually used; nothing is called by default."
)

ACADEMIC = [
    "fraud-detection-ccp", "ml-course-project", "kalman-filter-assignment",
    "robotics-maze-solver", "swarm-flocking",
    "data-science-case-studies-presentation", "responsible-data-scientist-presentation",
]

# Env / key appendix: (env var, where used, cost)
ENV_KEYS = [
    ["ANTHROPIC_API_KEY", "sales-playbook, content-engine, upwork-proposal, daily-news-brief", "Paid"],
    ["OPENAI_API_KEY", "all 3 dashboards, daily-news-brief, lead-gen", "Paid"],
    ["FIRECRAWL_API_KEY", "daily-news-brief, lead-gen, website-quality-scorer", "Paid"],
    ["APIFY_API_KEY", "lead-gen", "Paid"],
    ["PROXYCURL_API_KEY", "lead-gen", "Paid"],
    ["HUNTER_API_KEY", "lead-gen", "Paid (free tier)"],
    ["NEWSAPI_KEY", "daily-news-brief", "Paid (free tier)"],
    ["PAGESPEED_API_KEY", "website-quality-scorer", "Free (optional)"],
    ["GOOGLE_CLIENT_ID / _SECRET / _REFRESH_TOKEN", "upwork-proposal-dashboard", "Free (OAuth)"],
    ["GOOGLE_SHEETS_SPREADSHEET_ID", "daily-news-brief", "Free"],
    ["BRIEF_AUTH_TOKEN", "daily-news-brief (optional endpoint guard)", "Free"],
    ["gws CLI auth (hassanaleem86@gmail.com)", "content-engine, lead-gen", "Free"],
    ["NotebookLM login (Google)", "content-engine", "Free"],
]

# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------
flow = []

flow.append(Paragraph("Nexis Projects: API &amp; Integration Inventory", H1))
flow.append(Paragraph(f"Generated {GENERATED} &nbsp;|&nbsp; scan of <b>projects/</b> (node_modules excluded)", SUB))
flow.append(HRFlowable(width="100%", thickness=1.2, color=ACCENT, spaceBefore=6, spaceAfter=10))

flow.append(Paragraph("Summary", H2))
flow.append(Paragraph(
    "Nine NexusPoint projects make external calls. The recurring paid dependencies are the "
    "<b>Anthropic Claude API</b> (primary LLM) and <b>OpenAI API</b> (fallback LLM), plus "
    "<b>Firecrawl</b> for crawling. Google Workspace (via the <b>gws</b> CLI or the "
    "<b>googleapis</b> OAuth client) and <b>NotebookLM</b> are free on your own Google account. "
    "lead-gen is the most API-heavy project. The academic / coursework projects make no external "
    "calls. Color code below: ", BODY))
flow.append(Paragraph(
    f'<font color="{hx(PAID)}"><b>Paid</b></font> = billed external API &nbsp;&nbsp; '
    f'<font color="{hx(FREE)}"><b>Free</b></font> = free / your-account / keyless &nbsp;&nbsp; '
    "<b>Local</b> = runs on-machine &nbsp;&nbsp; <b>Manual</b> = human step, no API call.", SMALL))
flow.append(Spacer(1, 6))

# Per-project tables
flow.append(Paragraph("Per-project breakdown", H2))

for name, kind, blurb, rows in projects:
    block = []
    block.append(Paragraph(f"{name} &nbsp;<font size=8 color='{hx(MUTED)}'>({kind})</font>", H3))
    block.append(Paragraph(blurb, SMALL))
    block.append(Spacer(1, 3))

    data = [[Paragraph("Service", CELL_H), Paragraph("Type", CELL_H),
             Paragraph("How it is used", CELL_H), Paragraph("Model / detail", CELL_H),
             Paragraph("Auth / env", CELL_H)]]
    for r in rows:
        data.append([cell(r[0]), tag(r[1], r[1] == "Paid"), cell(r[2]), cell(r[3]), cell(r[4])])

    t = Table(data, colWidths=COL_W, repeatRows=1)
    ts = [
        ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), 0.4, LINE),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for i in range(1, len(data)):
        if i % 2 == 0:
            ts.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
    t.setStyle(TableStyle(ts))
    block.append(t)
    block.append(Spacer(1, 8))
    flow.append(KeepTogether(block))

# Vendored
flow.append(Paragraph("Vendored dependency (not a NexusPoint project)", H2))
flow.append(Paragraph(f"<b>{VENDORED[0]}</b> - {VENDORED[1]}", BODY))

# Academic
flow.append(Paragraph("Projects with no external APIs", H2))
flow.append(Paragraph(
    "Local computation / coursework only (no network calls): " + ", ".join(ACADEMIC) + ".", BODY))

# Env appendix
flow.append(Paragraph("Appendix: keys &amp; credentials by project", H2))
edata = [[Paragraph("Env var / credential", CELL_H), Paragraph("Used by", CELL_H), Paragraph("Cost", CELL_H)]]
for r in ENV_KEYS:
    edata.append([cell(f"<b>{r[0]}</b>"), cell(r[1]), tag(r[2], r[2].startswith("Paid"))])
et = Table(edata, colWidths=[58*mm, 78*mm, 24*mm], repeatRows=1)
ets = [
    ("BACKGROUND", (0, 0), (-1, 0), HEAD_BG),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("GRID", (0, 0), (-1, -1), 0.4, LINE),
    ("LEFTPADDING", (0, 0), (-1, -1), 4),
    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ("TOPPADDING", (0, 0), (-1, -1), 3),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
]
for i in range(1, len(edata)):
    if i % 2 == 0:
        ets.append(("BACKGROUND", (0, i), (-1, i), ROW_ALT))
et.setStyle(TableStyle(ets))
flow.append(et)
flow.append(Spacer(1, 8))
flow.append(Paragraph(
    "Note: the sales-playbook and content-engine dashboards use gpt-5.2 as the OpenAI fallback; "
    "upwork-proposal-dashboard and daily-news-brief still use gpt-4o. Verify gpt-5.2 params "
    "(max_tokens vs max_completion_tokens, temperature support) against the live OpenAI API.", SMALL))


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(18 * mm, 12 * mm, "NexusPoint - API & Integration Inventory (internal)")
    canvas.drawRightString(A4[0] - 18 * mm, 12 * mm, f"Page {doc.page}")
    canvas.setStrokeColor(LINE)
    canvas.line(18 * mm, 15 * mm, A4[0] - 18 * mm, 15 * mm)
    canvas.restoreState()


doc = SimpleDocTemplate(
    str(OUT), pagesize=A4,
    leftMargin=18 * mm, rightMargin=18 * mm, topMargin=16 * mm, bottomMargin=18 * mm,
    title="Nexis Projects - API & Integration Inventory", author="Nexis",
)
doc.build(flow, onFirstPage=_footer, onLaterPages=_footer)
print(f"Wrote {OUT}")
