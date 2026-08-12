#!/usr/bin/env python3
"""Run every check in references/checks.md against a live page or a markdown draft.

This is the core of the skill. It is deliberately all local parsing - bs4, lxml, textstat,
stdlib - because there is no free API for any of it (verified against all four scout
catalogs) and local means deterministic, offline-testable, rate-limit-free and free.

The contract with checks.md is one-directional: that file owns the thresholds, this file
implements them, and every emitted row names its source so a reader can go check. If a
threshold moves in seo-advisor's corpus, it moves in checks.md and then here.

The four verdicts matter more than the checks:

    pass    - measured, clears the threshold
    fail    - measured, does not clear it
    review  - measured, but the verdict needs judgment; evidence attached
    unknown - not measurable from anything available here; reason and manual method attached

`review` and `unknown` are the honest half of this script and the reason it is worth
running. A script can count the words in the opening paragraph. It cannot tell you whether
those words answer the query, and pretending otherwise - emitting `pass` because nothing
looked broken - is how an audit hands a client a confidently wrong document.

Draft mode exists so blog-writer can validate a post before it is ever published. The
checks that need a live response (Lighthouse, orphans, real image bytes) are skipped and
reported as skipped, never as passing.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Thresholds. Every one of these is sourced in references/checks.md - do not edit here
# without editing there, or the report will cite a number the reference does not carry.
TITLE_MIN, TITLE_MAX = 50, 60
TITLE_FRONTLOAD = 40
META_MIN, META_MAX = 105, 155
META_FRONTLOAD = 120
SECTION_WORDS_REVIEW, SECTION_WORDS_FAIL = 200, 250
QUESTION_RATIO_LO, QUESTION_RATIO_HI = 0.20, 0.50
LINKS_PER_2000_LO, LINKS_PER_2000_HI = 8, 15
URL_MAX_CHARS, URL_MAX_DEPTH = 60, 3
HERO_MAX_BYTES = 150_000
PARA_SENTENCES_LO, PARA_SENTENCES_HI = 1.5, 5.0

BANNED_ANCHORS = {"click here", "read more", "learn more", "this article", "here",
                  "more", "link", "this page", "find out more", "see more"}
BACKREF_OPENERS = ("this ", "these ", "those ", "as mentioned", "as noted", "as discussed",
                   "the above", "therefore", "thus,", "it is ", "they are ")
BOILERPLATE_META = ("welcome to", "we offer a wide range", "your one stop", "your one-stop",
                    "the best in the business", "lorem ipsum")
CAMERA_FILENAME = re.compile(r"^(img|dsc|dscn|photo|image|untitled|screenshot)[-_]?\d+", re.I)
STOCK_HOSTS = ("shutterstock", "istockphoto", "gettyimages", "unsplash", "pexels", "pixabay",
               "stock.adobe", "depositphotos", "freepik")
# Rough per-character pixel widths at ~20px Arial. Directional only - nothing here renders
# a font, so title.pixels always reports `unknown` and attaches this as an estimate.
_NARROW = set("ijltfr.,;:'!|[]()I ")
_WIDE = set("mwMW@%")


def _px_estimate(text: str) -> int:
    return round(sum(5 if c in _NARROW else 13 if c in _WIDE else 9 for c in text))


def _words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9']+", text or "")


def _sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", (text or "").strip()) if s]


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", " ", (s or "").lower())


def _keyword_hit(haystack: str, keyword: str) -> str:
    """'full' if the whole phrase is present, 'partial' if most content words are, else 'none'."""
    if not keyword:
        return "none"
    h, k = _norm(haystack), _norm(keyword)
    if k.strip() and k.strip() in h:
        return "full"
    terms = [t for t in k.split() if len(t) > 2]
    if terms and sum(1 for t in terms if t in h) >= max(1, len(terms) - 1):
        return "partial"
    return "none"


_BOILERPLATE_ATTR = re.compile(
    r"(^|[-_ ])(nav|navbar|menu|header|footer|sidebar|widget|breadcrumb|cookie|banner|"
    r"popup|modal|newsletter|subscribe|social|share|related|comment|pagination|skip|"
    r"offcanvas|search)([-_ ]|$)", re.I)


def _main_content_text(body) -> str:
    """The article text, with navigation and footer chrome removed.

    Reading the whole <body> for content analysis puts the nav and footer into the term
    counts, and on the first live run of terms.py that produced a "missing concepts" list
    reading: search, news, download, website, list, open. Those are menu items. They are the
    same on every page of the site and they say nothing about topical coverage.

    Prefers a semantic <main> or <article> container when the page has one, and otherwise
    strips the usual chrome elements and any container whose class or id names itself as
    chrome. Falls back to the full body if stripping removed almost everything, because an
    over-aggressive strip that silently empties the document is worse than some chrome.
    """
    import copy

    node = body.find("main") or body.find("article") or body
    node = copy.copy(node)

    for tag in node.find_all(["nav", "header", "footer", "aside", "form", "iframe", "svg"]):
        tag.decompose()
    for tag in node.find_all(attrs={"class": _BOILERPLATE_ATTR}):
        tag.decompose()
    for tag in node.find_all(attrs={"id": _BOILERPLATE_ATTR}):
        tag.decompose()
    for tag in node.find_all(attrs={"role": re.compile(r"navigation|banner|contentinfo|search", re.I)}):
        tag.decompose()

    text = node.get_text(" ", strip=True)
    full = body.get_text(" ", strip=True)
    if len(text) < 0.15 * len(full) and len(text) < 400:
        return full  # the strip ate the article; better some chrome than no content
    return text


# --------------------------------------------------------------------------- document model

class Doc:
    """One page, normalized, so live HTML and a markdown draft take the same code path."""

    def __init__(self, *, url: str = "", title: str = "", meta_description: str | None = None,
                 canonical: str = "", headings: list[tuple[int, str]] | None = None,
                 body_text: str = "", paragraphs: list[str] | None = None,
                 images: list[dict] | None = None, links: list[dict] | None = None,
                 jsonld: list | None = None, html: str = "", is_draft: bool = False,
                 author: str = "", nav_items: list[str] | None = None,
                 raw_meta_present: bool = True, main_text: str = ""):
        self.url = url
        # main_text excludes nav/footer chrome; body_text is everything. Content and term
        # analysis use main_text, structural checks use body_text.
        self._main_text = main_text
        self.title = title
        self.meta_description = meta_description
        self.canonical = canonical
        self.headings = headings or []
        self.body_text = body_text
        self.paragraphs = paragraphs or []
        self.images = images or []
        self.links = links or []
        self.jsonld = jsonld or []
        self.html = html
        self.is_draft = is_draft
        self.author = author
        self.nav_items = nav_items or []
        self.raw_meta_present = raw_meta_present

    @property
    def h1s(self) -> list[str]:
        return [t for lvl, t in self.headings if lvl == 1]

    @property
    def main_text(self) -> str:
        return self._main_text or self.body_text

    @property
    def word_count(self) -> int:
        """Words of article text. Excludes nav and footer, so it is comparable across sites."""
        return len(_words(self.main_text))

    def sections(self) -> list[dict]:
        """Text between each heading and the next, so section length is measurable."""
        if not self.headings:
            return [{"heading": "(no headings)", "level": 0, "text": self.main_text,
                     "words": self.word_count}]
        out, text = [], self.main_text
        positions = []
        for lvl, h in self.headings:
            idx = text.find(h)
            positions.append((idx if idx >= 0 else None, lvl, h))
        known = [p for p in positions if p[0] is not None]
        for i, (start, lvl, h) in enumerate(known):
            end = known[i + 1][0] if i + 1 < len(known) else len(text)
            body = text[start + len(h):end]
            out.append({"heading": h, "level": lvl, "text": body.strip(),
                        "words": len(_words(body))})
        return out


def doc_from_html(html: str, url: str) -> Doc:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    head_title = soup.find("title")
    meta_el = soup.find("meta", attrs={"name": re.compile(r"^description$", re.I)})
    canonical_el = soup.find("link", attrs={"rel": re.compile(r"canonical", re.I)})

    # Extract JSON-LD BEFORE stripping scripts. `soup.body` is the same tree as `soup`, so
    # decomposing scripts through it removes them from both, and every page would report
    # "no JSON-LD found" while carrying perfectly good schema.
    jsonld = []
    for s in soup.find_all("script", attrs={"type": re.compile(r"ld\+json", re.I)}):
        raw = s.string or s.get_text() or ""
        try:
            jsonld.append({"ok": True, "data": json.loads(raw)})
        except (json.JSONDecodeError, TypeError) as exc:
            jsonld.append({"ok": False, "error": str(exc), "snippet": raw[:200]})

    body = soup.body or soup
    for tag in body(["script", "style", "noscript", "template"]):
        tag.decompose()

    # Strip zero-width and non-breaking characters before deciding a heading has text.
    # Page builders emit <h2>&#8203;</h2> as spacing, and counted as real those inflate the
    # heading tree, poison the question ratio and attribute a whole section's words to a
    # heading nobody can see.
    headings = []
    for h in body.find_all(re.compile(r"^h[1-6]$")):
        text = h.get_text(" ", strip=True)
        if re.sub(r"[​-‏⁠﻿\xa0\s]+", "", text):
            headings.append((int(h.name[1]), text))
    paragraphs = [p.get_text(" ", strip=True) for p in body.find_all("p")
                  if len(p.get_text(strip=True)) > 30]

    images = []
    for img in body.find_all("img"):
        src = img.get("src") or img.get("data-src") or ""
        images.append({
            "src": urljoin(url, src) if src else "",
            "alt": img.get("alt"),  # None means the attribute is absent; "" means decorative
            "width": img.get("width"), "height": img.get("height"),
            "loading": (img.get("loading") or "").lower(),
            "fetchpriority": (img.get("fetchpriority") or "").lower(),
            "srcset": bool(img.get("srcset")),
        })

    host = urlparse(url).hostname or ""
    links = []
    for a in body.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue
        absolute = urljoin(url, href)
        links.append({
            "href": absolute,
            "anchor": a.get_text(" ", strip=True),
            "internal": (urlparse(absolute).hostname or "") == host,
            "in_nav": bool(a.find_parent(["nav", "header", "footer"])),
        })

    main_text = _main_content_text(body)

    nav = soup.find("nav")
    nav_items = [a.get_text(" ", strip=True) for a in nav.find_all("a")] if nav else []

    author = ""
    for sel in ({"name": "author"}, {"property": "article:author"}):
        m = soup.find("meta", attrs=sel)
        if m and m.get("content"):
            author = m["content"].strip()
            break
    if not author:
        el = body.find(attrs={"class": re.compile(r"author|byline", re.I)})
        if el:
            author = el.get_text(" ", strip=True)[:120]

    return Doc(
        url=url,
        title=head_title.get_text(strip=True) if head_title else "",
        meta_description=(meta_el.get("content") or "").strip() if meta_el else None,
        canonical=canonical_el.get("href", "") if canonical_el else "",
        headings=headings,
        body_text=body.get_text(" ", strip=True), main_text=main_text,
        paragraphs=paragraphs, images=images, links=links, jsonld=jsonld,
        html=html, author=author, nav_items=nav_items,
        raw_meta_present=meta_el is not None,
    )


def doc_from_markdown(md: str, url: str = "") -> Doc:
    """A blog-writer draft. Reads the `## SEO Metadata` block when the draft carries one."""
    title, meta_desc, slug = "", None, ""
    meta_block = re.search(r"^##\s+SEO Metadata\s*$(.*?)(?=^##\s|\Z)", md,
                           re.M | re.S | re.I)
    if meta_block:
        blob = meta_block.group(1)
        for key, pat in (("title", r"(?:SEO\s+)?title[^:\n]*:\s*(.+)"),
                         ("meta", r"meta\s+description[^:\n]*:\s*(.+)"),
                         ("slug", r"(?:URL\s+)?slug[^:\n]*:\s*(.+)")):
            m = re.search(pat, blob, re.I)
            if not m:
                continue
            val = m.group(1).strip().strip("`*_\"' ")
            if key == "title":
                title = val
            elif key == "meta":
                meta_desc = val
            else:
                slug = val
        md = md[:meta_block.start()]  # the metadata block is not body content

    body_md = re.sub(r"^---\s*$.*?^---\s*$", "", md, count=1, flags=re.M | re.S)  # frontmatter
    body_md = re.sub(r"```.*?```", " ", body_md, flags=re.S)

    headings = [(len(h.group(1)), h.group(2).strip())
                for h in re.finditer(r"^(#{1,6})\s+(.+?)\s*$", body_md, re.M)]
    if not title and headings and headings[0][0] == 1:
        title = headings[0][1]

    images = [{"src": m.group(2), "alt": m.group(1), "width": None, "height": None,
               "loading": "", "fetchpriority": "", "srcset": False}
              for m in re.finditer(r"!\[(.*?)\]\((.*?)\)", body_md)]

    links = []
    for m in re.finditer(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)", body_md):
        href = m.group(2).split()[0]
        links.append({"href": href, "anchor": m.group(1),
                      "internal": not href.startswith(("http://", "https://")),
                      "in_nav": False})

    plain = re.sub(r"^#{1,6}\s+", "", body_md, flags=re.M)
    plain = re.sub(r"!\[.*?\]\(.*?\)", " ", plain)
    plain = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", plain)
    plain = re.sub(r"[*_`>]+", "", plain)
    paragraphs = [p.strip().replace("\n", " ") for p in re.split(r"\n\s*\n", plain)
                  if len(p.strip()) > 30 and not p.strip().startswith(("-", "|", "*", "1."))]

    return Doc(url=url or slug, title=title, meta_description=meta_desc,
               headings=headings, body_text=" ".join(paragraphs),
               paragraphs=paragraphs, images=images, links=links,
               is_draft=True, raw_meta_present=meta_desc is not None)


# --------------------------------------------------------------------------- checks

def _row(cid, area, observed, threshold, verdict, source, evidence="") -> dict:
    return {"check_id": cid, "area": area, "observed": observed, "threshold": threshold,
            "verdict": verdict, "source": source, "evidence": evidence}


def check_titles(doc: Doc, kw: str) -> list[dict]:
    A, out = "Titles and metas", []
    t = doc.title or ""
    out.append(_row("title.present", A, "present" if t else "missing", "must exist",
                    "pass" if t else "fail", "course/11", t[:120]))
    if t:
        n = len(t)
        out.append(_row("title.length", A, f"{n} chars", f"{TITLE_MIN}-{TITLE_MAX} chars",
                        "pass" if TITLE_MIN <= n <= TITLE_MAX else "fail", "course/11 [s296]", t))
        out.append(_row("title.pixels", A, f"~{_px_estimate(t)}px estimated", "~600px",
                        "unknown", "course/11",
                        "Google truncates on pixel width, not characters. Nothing here renders a "
                        "font, so this is a directional estimate. Check the live SERP snippet."))
        hit = _keyword_hit(t[:TITLE_FRONTLOAD], kw)
        out.append(_row("title.frontload", A,
                        f"keyword {hit} in first {TITLE_FRONTLOAD} chars",
                        f"primary keyword within first {TITLE_FRONTLOAD} chars",
                        {"full": "pass", "partial": "review", "none": "fail"}[hit]
                        if kw else "review",
                        "course/11 [s296, s207]", t[:TITLE_FRONTLOAD]))
        first_para = doc.paragraphs[0] if doc.paragraphs else ""
        out.append(_row("title.agreement", A, "needs a read", "title, H1 and opening agree",
                        "review", "course/11",
                        f"TITLE: {t}\nH1: {doc.h1s[0] if doc.h1s else '(none)'}\n"
                        f"OPENING: {first_para[:220]}"))

    md = doc.meta_description
    out.append(_row("meta.present", A, "present" if md else "missing", "must exist",
                    "pass" if md else "fail", "course/11",
                    "A blank meta description beats a generic auto-generated one. If the fix is "
                    "a site-wide template, do not ship the template."))
    if md:
        n = len(md)
        out.append(_row("meta.length", A, f"{n} chars", f"{META_MIN}-{META_MAX} chars",
                        "pass" if META_MIN <= n <= META_MAX else "fail", "course/11 [s207]", md))
        out.append(_row("meta.frontload", A, f"first {META_FRONTLOAD} chars shown below",
                        f"key information within first {META_FRONTLOAD} chars",
                        "review", "course/11 [s207]", md[:META_FRONTLOAD]))
        low = md.lower()
        boiler = [b for b in BOILERPLATE_META if b in low]
        out.append(_row("meta.specificity", A,
                        f"boilerplate phrase found: {boiler[0]}" if boiler else "no boilerplate matched",
                        "specific to this page", "review", "course/11", md))
    return out


def check_headings(doc: Doc, kw: str) -> list[dict]:
    A, out = "Headings and structure", []
    h1 = doc.h1s
    out.append(_row("h1.count", A, f"{len(h1)} H1", "exactly 1",
                    "pass" if len(h1) == 1 else "fail", "course/12 [s296, s294]",
                    " | ".join(h1)[:200]))
    if h1:
        hit = _keyword_hit(h1[0], kw)
        out.append(_row("h1.keyword", A, f"keyword {hit}",
                        "primary keyword present, close to but not identical to the title",
                        "review" if not kw or hit != "full" else "pass",
                        "course/12", h1[0]))

    levels = [lvl for lvl, _ in doc.headings]
    skips = [(levels[i], levels[i + 1]) for i in range(len(levels) - 1)
             if levels[i + 1] - levels[i] > 1]
    out.append(_row("heading.hierarchy", A,
                    f"{len(skips)} skipped level(s)", "no skipped levels",
                    "pass" if not skips else "fail", "course/12",
                    "; ".join(f"H{a} -> H{b}" for a, b in skips[:6]) +
                    (" | Fix in CSS. If a heading looks wrong, style it, do not demote it."
                     if skips else "")))

    subs = [t for lvl, t in doc.headings if lvl in (2, 3)]
    if subs:
        qs = [t for t in subs if t.strip().endswith("?") or
              re.match(r"^(how|what|why|when|where|who|which|can|should|do|does|is|are)\b", t.strip(), re.I)]
        ratio = len(qs) / len(subs)
        out.append(_row("heading.question_ratio", A, f"{len(qs)}/{len(subs)} = {ratio:.0%}",
                        f"~1/3 ({QUESTION_RATIO_LO:.0%}-{QUESTION_RATIO_HI:.0%})",
                        "pass" if QUESTION_RATIO_LO <= ratio <= QUESTION_RATIO_HI else "review",
                        "course/12 [s181, s294]",
                        "Source questions from People Also Ask via seo-foundation. A target, not "
                        "a quota - do not bolt questions onto a page that has none."))
        bare = [t for t in subs if len(_words(t)) <= 3 and not t.strip().endswith("?")]
        out.append(_row("heading.descriptive", A, f"{len(bare)} category-style heading(s)",
                        "headings should answer, not label", "review", "course/12",
                        "; ".join(bare[:8])))
        out.append(_row("heading.story", A, "needs a read",
                        "H2s in order should narrate the page", "review", "course/12",
                        " -> ".join(t for lvl, t in doc.headings if lvl == 2)[:600]))

    long_secs, backrefs = [], []
    for s in doc.sections():
        if s["words"] > SECTION_WORDS_REVIEW:
            long_secs.append(f"{s['heading']} ({s['words']}w)")
        opener = s["text"].strip().lower()
        if opener.startswith(BACKREF_OPENERS):
            backrefs.append(f"{s['heading']}: \"{s['text'].strip()[:70]}...\"")
    worst = max((s["words"] for s in doc.sections()), default=0)
    out.append(_row("section.length", A, f"{len(long_secs)} section(s) over {SECTION_WORDS_REVIEW}w, "
                    f"longest {worst}w", f"split much over {SECTION_WORDS_REVIEW} words",
                    "fail" if worst > SECTION_WORDS_FAIL else
                    ("review" if long_secs else "pass"), "course/12 [s110]",
                    "; ".join(long_secs[:8]) +
                    " | An extractable unit runs 134-167 words. A 400-word section is two units glued together."))
    out.append(_row("section.backward_dep", A, f"{len(backrefs)} section(s) open with a back-reference",
                    "each section standalone", "fail" if backrefs else "pass", "course/12",
                    "; ".join(backrefs[:6])))
    return out


def check_content(doc: Doc, kw: str) -> list[dict]:
    A, out = "Content quality", []
    opening = " ".join(_words(doc.paragraphs[0])[:60]) if doc.paragraphs else ""
    out.append(_row("content.answer_first", A, "needs a read",
                    "the primary question answered in the first 40-60 words",
                    "review", "course/14 [s220, s273]",
                    f"QUERY: {kw or '(not supplied)'}\nFIRST 60 WORDS: {opening}"))
    out.append(_row("content.word_count", A, f"{doc.word_count} words",
                    "no target - length is not a ranking factor", "pass", "course/14",
                    "Reported so you can see thin against the competitor set. Never a verdict: "
                    "padding to hit a number is the pattern the helpful-content system catches."))

    if doc.paragraphs:
        counts = sorted(len(_sentences(p)) for p in doc.paragraphs)
        median = counts[len(counts) // 2]
        out.append(_row("content.paragraph_length", A, f"median {median} sentences",
                        "2-4 sentences",
                        "pass" if PARA_SENTENCES_LO <= median <= PARA_SENTENCES_HI else "review",
                        "course/12", f"distribution: {counts[:20]}"))

    numbers = re.findall(r"(?<![\w/])\d[\d,.]*\s*(?:%|percent|x\b|k\b|m\b|bn\b|seconds?|ms\b|kb\b|mb\b)?",
                         doc.main_text)
    stats = [n for n in numbers if len(n.strip()) > 1]
    out.append(_row("content.statistics", A, f"{len(stats)} concrete number(s)", "at least 1",
                    "pass" if stats else "fail", "course/14 [s220, s179]",
                    "Princeton GEO measured statistics at +30% citation lift "
                    "[practitioner, peer-reviewed method]. Sample: " + ", ".join(stats[:8])))

    ext = [l for l in doc.links if not l["internal"] and not l["in_nav"]]
    out.append(_row("content.citations", A, f"{len(ext)} outbound citation(s)", "at least 1",
                    "pass" if ext else "fail", "course/14 [s220, s179]",
                    "Inline citations +30% [practitioner]. " +
                    "; ".join(f"{l['anchor'][:40]} -> {urlparse(l['href']).hostname}" for l in ext[:6])))

    quotes = re.findall(r"[\"“]([^\"”]{40,300})[\"”]", doc.main_text)
    out.append(_row("content.expert_quote", A, f"{len(quotes)} quoted passage(s)", "at least 1",
                    "review", "course/14 [s220, s179]",
                    "Expert quotes are the strongest single lever measured at +41%, but the script "
                    "cannot verify the person is real or relevant. Sample: " +
                    (quotes[0][:160] if quotes else "(none found)")))

    fh = [m for m in ("we tested", "we ran", "i tested", "i ran", "in our", "our own",
                      "what broke", "i would do differently", "we measured", "screenshot",
                      "when we", "after we", "in practice")
          if m in doc.main_text.lower()]
    out.append(_row("content.firsthand", A, f"{len(fh)} first-hand marker(s)", "at least 1",
                    "review", "course/14 + course/18",
                    "Experience is the first E and the thing most sites fail. Markers found: "
                    + (", ".join(fh) if fh else "none - check manually, the phrasing varies")))

    heads = [t.lower() for _, t in doc.headings]
    dupes = [h for h in set(heads) if heads.count(h) > 1]
    out.append(_row("content.padding", A, "needs a read", "no restated or filler sections",
                    "review", "course/14",
                    "Tells: a section restating the previous one, a definition of something "
                    "obvious, three examples where one would do, a summarizing conclusion. "
                    + (f"Repeated headings: {dupes}" if dupes else "")))

    try:
        import textstat
        grade = textstat.flesch_kincaid_grade(doc.main_text)
        ease = textstat.flesch_reading_ease(doc.main_text)
        obs = f"Flesch-Kincaid grade {grade:.1f}, reading ease {ease:.0f}"
    except Exception as exc:  # noqa: BLE001
        obs = f"not measured ({type(exc).__name__})"
    out.append(_row("content.readability", A, obs, "no corpus threshold", "review",
                    "measured here",
                    "The 320-source corpus sets no readability target. The aruntastic method "
                    "suggests roughly 10th grade [practitioner, aruntastic]. Report it, never "
                    "gate on it - a technical B2B page at grade 14 may be correct for its reader."))

    out.append(_row("content.satisfaction", A, "needs a read",
                    "would the reader stop searching after this page",
                    "review", "course/14",
                    "The single predictive test. The other checks in this area serve it. If the "
                    "answer is no, nothing else on this page matters."))
    return out


def check_urls(doc: Doc) -> list[dict]:
    A, out = "URLs and navigation", []
    if not doc.url:
        return out
    p = urlparse(doc.url if "://" in doc.url else "https://x/" + doc.url.lstrip("/"))
    path = p.path or "/"
    # Live URLs are note-only: the switching cost is every inbound link. A draft slug has not
    # shipped, so there it is a real fail and free to fix.
    v = "fail" if doc.is_draft else "review"
    note = "" if doc.is_draft else "Note only. Do not change a live URL without one of the four exceptions in checks.md."

    n = len(doc.url)
    out.append(_row("url.length", A, f"{n} chars", f"under {URL_MAX_CHARS}",
                    "pass" if n < URL_MAX_CHARS else v, "course/13 [s299, s303]", note))
    out.append(_row("url.case", A, "has uppercase" if path != path.lower() else "lowercase",
                    "lowercase", "pass" if path == path.lower() else v, "course/13", note))
    out.append(_row("url.separators", A, "underscores present" if "_" in path else "hyphens only",
                    "hyphens, not underscores", "pass" if "_" not in path else v, "course/13",
                    (note + " Underscores join words, hyphens separate them.").strip()))
    depth = len([s for s in path.split("/") if s])
    out.append(_row("url.depth", A, f"{depth} segment(s)", f"{URL_MAX_DEPTH} maximum",
                    "pass" if depth <= URL_MAX_DEPTH else v, "course/13", note))
    has_date = bool(re.search(r"/(19|20)\d{2}(/\d{1,2})?/", path))
    out.append(_row("url.dates", A, "date in path" if has_date else "no date", "no dates on evergreen content",
                    v if has_date else "pass", "course/13", note))

    if doc.nav_items:
        out.append(_row("nav.item_count", A, f"{len(doc.nav_items)} nav item(s)", "about 7",
                        "pass" if 3 <= len(doc.nav_items) <= 9 else "review", "course/13",
                        "; ".join(doc.nav_items[:12])))
        out.append(_row("nav.vocabulary", A, "needs a read", "customer vocabulary, not internal",
                        "review", "course/13",
                        "Cross-check against 08-audience-persona.md verbatim vocabulary. Items: "
                        + "; ".join(doc.nav_items[:12])))
    return out


def check_links(doc: Doc) -> list[dict]:
    A, out = "Internal linking", []
    body_links = [l for l in doc.links if not l["in_nav"]]
    internal = [l for l in body_links if l["internal"]]
    per2k = (len(internal) / max(doc.word_count, 1)) * 2000
    out.append(_row("links.density", A,
                    f"{len(internal)} internal body link(s), {per2k:.1f} per 2,000 words",
                    f"{LINKS_PER_2000_LO}-{LINKS_PER_2000_HI} per 2,000 words",
                    "pass" if LINKS_PER_2000_LO <= per2k <= LINKS_PER_2000_HI else "review",
                    "course/16 [s128]",
                    "A sanity range, not a quota. Hitting 12 by bolting a link block onto the "
                    "footer satisfies the number and none of the intent."))

    bad = [l for l in doc.links if l["anchor"].strip().lower() in BANNED_ANCHORS]
    out.append(_row("links.anchor_quality", A, f"{len(bad)} non-descriptive anchor(s)",
                    "specific, descriptive anchors", "fail" if bad else "pass", "course/16",
                    "; ".join(f"\"{l['anchor']}\" -> {l['href'][:60]}" for l in bad[:8])))

    pairs: dict[tuple[str, str], int] = {}
    for l in internal:
        key = (l["anchor"].strip().lower(), l["href"])
        pairs[key] = pairs.get(key, 0) + 1
    repeated = {k: c for k, c in pairs.items() if c > 3 and k[0]}
    out.append(_row("links.anchor_variety", A, f"{len(repeated)} over-repeated anchor(s)",
                    "vary naturally, no exact-match at scale",
                    "review" if repeated else "pass", "course/16",
                    "; ".join(f"\"{a}\" x{c}" for (a, _), c in list(repeated.items())[:5])))

    for cid, obs in (("links.orphan", "orphans"), ("links.depth", "click depth"),
                     ("links.opportunities", "internal link opportunities")):
        if doc.is_draft:
            out.append(_row(cid, A, "not run in draft mode", "-", "unknown", "course/16",
                            "Needs a live site crawl. Run links.py --site once published."))
        else:
            out.append(_row(cid, A, f"run links.py --site for {obs}", "-", "unknown", "course/16",
                            f"Site-level check. `python scripts/links.py --site <domain>` "
                            f"computes {obs}; a single page cannot see them."))
    return out


def check_media(doc: Doc) -> list[dict]:
    A, out = "Media", []
    imgs = doc.images
    if not imgs:
        out.append(_row("media.alt_present", A, "no images on the page", "-", "pass", "course/17", ""))
        return out

    missing = [i for i in imgs if i["alt"] is None]
    decorative = [i for i in imgs if i["alt"] == ""]
    out.append(_row("media.alt_present", A,
                    f"{len(missing)} of {len(imgs)} image(s) missing the alt attribute",
                    "alt attribute on every image",
                    "fail" if missing else "pass", "course/17 [s296, s166]",
                    "alt=\"\" on a decorative image is correct and passes; omitting the attribute "
                    f"entirely is the failure. {len(decorative)} marked decorative. "
                    + "; ".join(i["src"][:70] for i in missing[:6])))

    stuffed = [i for i in imgs if i["alt"] and len(_words(i["alt"])) > 15]
    out.append(_row("media.alt_quality", A, f"{len(stuffed)} over-long alt text(s)",
                    "descriptive and in context", "review", "course/17",
                    "Test: how would you describe this to someone over the phone. "
                    + "; ".join(f"\"{i['alt'][:60]}\"" for i in stuffed[:5])))

    nosize = [i for i in imgs if not (i["width"] and i["height"])]
    out.append(_row("media.explicit_size", A, f"{len(nosize)} of {len(imgs)} without width/height",
                    "width and height on every image",
                    "fail" if nosize else "pass", "course/17",
                    "One attribute pair per image removes an entire category of layout shift."))

    if not doc.is_draft:
        hero = imgs[0]
        out.append(_row("media.hero_lazy", A,
                        f"loading={hero['loading'] or 'default'}, fetchpriority={hero['fetchpriority'] or 'unset'}",
                        "hero eager with fetchpriority=high",
                        "fail" if hero["loading"] == "lazy" else
                        ("review" if hero["fetchpriority"] != "high" else "pass"),
                        "course/17", f"first image: {hero['src'][:100]}"))

    camera = [i for i in imgs if CAMERA_FILENAME.match(Path(urlparse(i["src"]).path).stem or "")]
    out.append(_row("media.filename", A, f"{len(camera)} camera-style filename(s)",
                    "descriptive filenames", "review", "course/17",
                    "Going forward only. Bulk-renaming existing images is a URL change and "
                    "carries the same cost as section 4. "
                    + "; ".join(Path(urlparse(i["src"]).path).name for i in camera[:6])))

    stock = [i for i in imgs if any(h in i["src"].lower() for h in STOCK_HOSTS)]
    out.append(_row("media.stock", A, f"{len(stock)} likely stock image(s)",
                    "original media earns citations", "review", "course/17",
                    "Original diagrams, screenshots with real numbers and comparison tables earn "
                    "citations. Stock photography does none of that."))

    out.append(_row("media.hero_weight", A, "run media.py", f"under {HERO_MAX_BYTES // 1000}KB",
                    "unknown", "course/17 [s295, s292]",
                    "Byte weight needs the actual file. `python scripts/media.py --url <url>` "
                    "fetches each image and computes the measured WebP saving."))

    if not doc.is_draft:
        vids = re.findall(r"<video[\s>]|youtube\.com/embed|player\.vimeo\.com", doc.html, re.I)
        if vids:
            has_transcript = bool(re.search(r"transcript", doc.body_text, re.I))
            out.append(_row("media.transcript", A,
                            "transcript found" if has_transcript else "no transcript found",
                            "publish the transcript on the page",
                            "pass" if has_transcript else "fail", "course/17",
                            "The highest-value and most-skipped video action, because models "
                            "train on transcripts."))
            self_hosted = bool(re.search(r"<video[\s>]", doc.html, re.I))
            out.append(_row("media.video_host", A,
                            "self-hosted <video>" if self_hosted else "embedded platform player",
                            "host on YouTube",
                            "fail" if self_hosted else "pass", "course/17", ""))
    return out


def check_eeat(doc: Doc) -> list[dict]:
    A, out = "E-E-A-T", []
    generic = {"admin", "administrator", "the team", "staff", "editor", "marketing team", ""}
    a = (doc.author or "").strip()
    out.append(_row("eeat.author_named", A, a or "none found",
                    "a named author, not Admin or The Team",
                    "fail" if a.lower() in generic else "pass", "course/18", ""))
    if not doc.is_draft:
        bio = bool(re.search(r"/author/|/team/|/about/|rel=[\"']author[\"']", doc.html, re.I))
        out.append(_row("eeat.author_bio", A, "bio link found" if bio else "no bio link",
                        "author name links to a real bio",
                        "pass" if bio else "fail", "course/18", ""))
        types = _schema_types(doc)
        out.append(_row("eeat.author_schema", A,
                        "Person schema present" if "Person" in types else "no Person schema",
                        "Person/Author schema with sameAs", "review", "course/18",
                        "sameAs feeds entity consolidation. Same name, photo and bio across "
                        "LinkedIn and industry sites is what makes it work."))
        scheme = urlparse(doc.url).scheme
        mixed = len(re.findall(r'src=["\']http://', doc.html))
        out.append(_row("eeat.https", A,
                        f"{scheme}, {mixed} mixed-content reference(s)", "HTTPS, no mixed content",
                        "fail" if scheme != "https" or mixed else "pass", "course/18 [confirmed]",
                        "A confirmed ranking factor and non-negotiable."))
        for cid, pat, label in (("eeat.about", r"/about", "About page link"),
                                ("eeat.contact", r"/contact|tel:|mailto:", "contact details")):
            found = bool(re.search(pat, doc.html, re.I))
            out.append(_row(cid, A, f"{label} {'found' if found else 'not found'}",
                            "present and real", "review" if found else "fail", "course/18",
                            "Working contact details means address, phone and email, not only a form."
                            if cid == "eeat.contact" else ""))
    hedges = [h for h in ("however", "the downside", "not a good fit", "limitation", "trade-off",
                          "tradeoff", "won't work", "does not work well", "drawback")
              if h in doc.main_text.lower()]
    out.append(_row("eeat.limitations", A, f"{len(hedges)} limitation marker(s)",
                    "acknowledges at least one honest limitation", "review", "course/18",
                    "Balanced coverage including the limits of what you sell. Cheap, rare, and "
                    "it is what trust concretely looks like on a commercial page."))
    out.append(_row("eeat.six_questions", A, "needs a read", "most pages fail three or more",
                    "review", "course/18",
                    "1 Who wrote this and can I tell? 2 Evidence they have done it? 3 Claims "
                    "sourced? 4 Can I verify the organization is real? 5 Does it acknowledge "
                    "limitations? 6 If it were wrong, would there be any way to tell?"))
    return out


def _schema_types(doc: Doc) -> list[str]:
    types = []
    for block in doc.jsonld:
        if not block.get("ok"):
            continue
        items = block["data"] if isinstance(block["data"], list) else [block["data"]]
        for item in items:
            if not isinstance(item, dict):
                continue
            for node in ([item] + (item.get("@graph") or []) if isinstance(item.get("@graph"), list) else [item]):
                if isinstance(node, dict) and node.get("@type"):
                    t = node["@type"]
                    types.extend(t if isinstance(t, list) else [t])
    return types


# Required properties per on-page type. Site-level types (Organization, LocalBusiness,
# Product, Service) are deliberately absent - they belong to the technical skill.
SCHEMA_REQUIRED = {
    "Article": ["headline", "author"], "BlogPosting": ["headline", "author"],
    "FAQPage": ["mainEntity"], "HowTo": ["name", "step"],
    "BreadcrumbList": ["itemListElement"], "Person": ["name"],
}


def check_schema(doc: Doc) -> list[dict]:
    A, out = "Schema", []
    if not doc.jsonld:
        out.append(_row("schema.parses", A, "no JSON-LD found", "at least Article/BlogPosting",
                        "fail" if not doc.is_draft else "review", "course/18",
                        "In draft mode the stub may be added at publish time."))
        return out

    broken = [b for b in doc.jsonld if not b.get("ok")]
    out.append(_row("schema.parses", A, f"{len(broken)} of {len(doc.jsonld)} block(s) failed to parse",
                    "all blocks valid JSON", "fail" if broken else "pass", "measured here",
                    "; ".join(b.get("error", "")[:80] for b in broken[:3])))

    types = _schema_types(doc)
    out.append(_row("schema.types", A, ", ".join(sorted(set(types))) or "none", "reported",
                    "pass", "measured here", ""))

    problems = []
    for block in doc.jsonld:
        if not block.get("ok"):
            continue
        items = block["data"] if isinstance(block["data"], list) else [block["data"]]
        for item in items:
            if not isinstance(item, dict):
                continue
            t = item.get("@type")
            t = t[0] if isinstance(t, list) and t else t
            for field in SCHEMA_REQUIRED.get(t, []):
                if field not in item:
                    problems.append(f"{t} missing required '{field}'")
    out.append(_row("schema.required_fields", A, f"{len(problems)} missing required field(s)",
                    "every required property present",
                    "fail" if problems else "pass", "measured here",
                    "; ".join(problems[:8]) +
                    " | When generating schema, instruct the model to ask rather than invent: a "
                    "fabricated field does not error, it just quietly fails to do anything."))

    faq_qs = []
    for block in doc.jsonld:
        if not block.get("ok"):
            continue
        items = block["data"] if isinstance(block["data"], list) else [block["data"]]
        for item in items:
            if isinstance(item, dict) and item.get("@type") == "FAQPage":
                for q in item.get("mainEntity") or []:
                    if isinstance(q, dict) and q.get("name"):
                        faq_qs.append(q["name"])
    if faq_qs:
        body_low = doc.body_text.lower()
        orphaned = [q for q in faq_qs if q.lower()[:40] not in body_low]
        out.append(_row("schema.faq_matches", A,
                        f"{len(orphaned)} of {len(faq_qs)} FAQ question(s) not visible on the page",
                        "schema content must exist in the visible page",
                        "fail" if orphaned else "pass", "course/18",
                        "Marking up content that is not on the page is a guidelines violation. "
                        + "; ".join(orphaned[:4])))
    return out


def analyze(doc: Doc, primary_keyword: str = "") -> dict:
    rows: list[dict] = []
    for fn in (check_titles, check_headings, check_content):
        rows += fn(doc, primary_keyword)
    for fn in (check_urls, check_links, check_media, check_eeat, check_schema):
        rows += fn(doc)

    counts = {v: sum(1 for r in rows if r["verdict"] == v)
              for v in ("pass", "fail", "review", "unknown")}
    return {
        "url": doc.url,
        "mode": "draft" if doc.is_draft else "live",
        "primary_keyword": primary_keyword or None,
        "word_count": doc.word_count,
        "counts": counts,
        "checks": rows,
        "not_connected": [
            "Search Console: CTR, impressions, position and decay are unavailable. gws has no "
            "Search Console service and no credential exists. Export Performance manually and "
            "pass it to inventory.py --gsc-csv.",
            "AI Overview presence: not returned by any data source here. Check the query in "
            "incognito and record the result by hand.",
        ],
        "reading_note": ("Read the verdict distribution before individual rows. Many `fail` is a "
                         "metadata problem and cheap. Many `review` is a content problem and no "
                         "script can help with it."),
    }


# --------------------------------------------------------------------------- cli

def _selftest() -> int:
    """Fixture-based. No network. Proves the verdict logic, not the parser plumbing."""
    ok = True
    bad_html = """<html><head>
      <title>Home</title>
    </head><body>
      <h1>Welcome</h1><h1>Also Welcome</h1>
      <h2>Services</h2><h4>Deep</h4>
      <p>This is the thing we mentioned. It continues without ever saying what it is about,
         at some length, in a way that does not answer anything a reader came for.</p>
      <img src="/IMG_4471.jpg">
      <a href="/x">click here</a>
      <script type="application/ld+json">{ broken json </script>
    </body></html>"""

    print("1. a deliberately broken page fails the checks it should")
    d = doc_from_html(bad_html, "https://acme.com/Some_Very_Long_Path/With/Extra/Depth/Here/Page")
    res = analyze(d, "garden landscaping")
    by = {r["check_id"]: r for r in res["checks"]}
    expect_fail = ["title.length", "h1.count", "heading.hierarchy", "meta.present",
                   "links.anchor_quality", "media.alt_present", "media.explicit_size",
                   "schema.parses", "content.citations", "section.backward_dep"]
    for cid in expect_fail:
        if by.get(cid, {}).get("verdict") != "fail":
            print(f"   FAIL: {cid} = {by.get(cid, {}).get('verdict')} (expected fail)")
            ok = False
    if ok:
        print(f"   PASS: all {len(expect_fail)} expected failures fired")

    print("2. judgment checks return review, never a fabricated pass")
    for cid in ("content.answer_first", "content.satisfaction", "title.agreement",
                "eeat.six_questions", "content.readability"):
        if by.get(cid, {}).get("verdict") != "review":
            print(f"   FAIL: {cid} = {by.get(cid, {}).get('verdict')} (expected review)")
            ok = False
    else:
        print("   PASS: the five judgment checks all returned review")

    print("3. word count reports but never fails - length is not a ranking factor")
    if by["content.word_count"]["verdict"] == "pass" and "no target" in by["content.word_count"]["threshold"]:
        print("   PASS: reported as an observation")
    else:
        print("   FAIL: word count produced a verdict")
        ok = False

    print("4. title pixel width is unknown, not estimated-as-fact")
    if by["title.pixels"]["verdict"] == "unknown":
        print("   PASS: unknown with the estimate attached")
    else:
        print(f"   FAIL: {by['title.pixels']['verdict']}")
        ok = False

    print("5. a live URL is note-only; the same slug in a draft is a real fail")
    live_url = [r for r in res["checks"] if r["check_id"] == "url.depth"][0]
    draft = doc_from_markdown("# T\n\ntext " * 40, "/a/b/c/d/e/f")
    draft_url = [r for r in analyze(draft)["checks"] if r["check_id"] == "url.depth"][0]
    if live_url["verdict"] == "review" and draft_url["verdict"] == "fail":
        print("   PASS: live=review (switching cost), draft=fail (free to fix)")
    else:
        print(f"   FAIL: live={live_url['verdict']} draft={draft_url['verdict']}")
        ok = False

    print("6. a good page passes the checks it should")
    good_html = """<html><head>
      <title>Garden Landscaping Services That Transform Small Yards</title>
      <meta name="description" content="Garden landscaping for small urban yards. Design, planting and drainage, with real costs and timelines from 40 completed projects.">
      <link rel="canonical" href="https://acme.com/services/garden-landscaping">
      <meta name="author" content="Dana Whitfield">
    </head><body>
      <nav><a href="/">Home</a><a href="/services">Services</a><a href="/about">About</a></nav>
      <h1>Garden Landscaping for Small Urban Yards</h1>
      <p>Garden landscaping for a small urban yard costs between 2,400 and 6,800 dollars and
         takes 3 to 5 weeks. We ran 40 of these projects in 2025 and the drainage work is
         what moves the number most.</p>
      <h2>What does garden landscaping cost?</h2>
      <p>Across our own 40 jobs the median was 4,100 dollars. However, sloped sites run 30%
         higher because of drainage. Published figures from the trade body agree.</p>
      <h2>How long does the work take?</h2>
      <p>Three to five weeks. When we tested compressing that to two weeks the planting
         suffered, so we stopped offering it.</p>
      <img src="/small-urban-garden-after-planting.webp" alt="A small urban garden after planting"
           width="1200" height="800" fetchpriority="high">
      <a href="/services/drainage">how drainage changes the price</a>
      <a href="https://tradebody.org/report">the trade body's 2025 report</a>
      <script type="application/ld+json">
      {"@type":"Article","headline":"Garden Landscaping","author":{"@type":"Person","name":"Dana Whitfield"}}
      </script>
    </body></html>"""
    g = analyze(doc_from_html(good_html, "https://acme.com/services/garden-landscaping"),
                "garden landscaping")
    gby = {r["check_id"]: r["verdict"] for r in g["checks"]}
    expect_pass = ["h1.count", "heading.hierarchy", "meta.present", "meta.length",
                   "media.alt_present", "media.explicit_size", "schema.parses",
                   "content.statistics", "content.citations", "links.anchor_quality",
                   "url.length", "url.depth", "eeat.https", "eeat.author_named"]
    missed = [c for c in expect_pass if gby.get(c) != "pass"]
    if missed:
        print(f"   FAIL: expected pass but got {[(c, gby.get(c)) for c in missed]}")
        ok = False
    else:
        print(f"   PASS: all {len(expect_pass)} expected passes fired")

    print("7. Search Console is reported as not connected, never inferred")
    if any("Search Console" in n for n in g["not_connected"]):
        print("   PASS: named in not_connected")
    else:
        print("   FAIL: the GSC gap is not surfaced")
        ok = False

    print("\nRESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Run the on-page check registry against a page or draft.")
    ap.add_argument("--url", help="live page URL")
    ap.add_argument("--draft", help="path to a markdown draft")
    ap.add_argument("--primary-keyword", default="", help="the query this page targets")
    ap.add_argument("--refresh", action="store_true", help="bypass the page cache")
    ap.add_argument("--out", help="write the full result to this JSON file")
    ap.add_argument("--fails-only", action="store_true", help="print only fail and review rows")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not (args.url or args.draft):
        ap.error("--url or --draft required (or use --selftest)")
    if not args.primary_keyword:
        print("[onpage] no --primary-keyword: relevance checks will degrade to `review`. "
              "Structure is still measured, but not whether it is about the right thing.",
              file=sys.stderr)

    if args.draft:
        doc = doc_from_markdown(Path(args.draft).read_text(encoding="utf-8"))
    else:
        import fetch_page
        rec = fetch_page.fetch(args.url, refresh=args.refresh)
        if not rec.get("html"):
            print(f"[onpage] empty body for {args.url} (status {rec.get('status')}). That is a "
                  "rendering finding, not a check result. Report it and hand off to a technical "
                  "pass rather than auditing an empty document.", file=sys.stderr)
            return 1
        doc = doc_from_html(rec["html"], rec.get("final_url") or args.url)
        print(fetch_page.cost_report(), file=sys.stderr)

    res = analyze(doc, args.primary_keyword)

    if args.out:
        Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        c = res["counts"]
        print(f"{res['url'] or args.draft}: {c['fail']} fail, {c['review']} review, "
              f"{c['pass']} pass, {c['unknown']} unknown -> {args.out}")
    else:
        rows = res["checks"]
        if args.fails_only:
            rows = [r for r in rows if r["verdict"] in ("fail", "review")]
        area = None
        for r in rows:
            if r["area"] != area:
                area = r["area"]
                print(f"\n## {area}")
            print(f"  [{r['verdict'].upper():7}] {r['check_id']:26} {r['observed']}")
            if r["verdict"] in ("fail", "review", "unknown") and r["evidence"]:
                print(f"            {r['evidence'][:300]}")
        c = res["counts"]
        print(f"\n{c['fail']} fail | {c['review']} review | {c['pass']} pass | {c['unknown']} unknown")
        for n in res["not_connected"]:
            print(f"NOT CONNECTED: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
