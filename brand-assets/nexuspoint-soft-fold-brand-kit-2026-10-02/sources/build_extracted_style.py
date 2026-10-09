"""Build provenance-rich CSS extraction from saved live portfolio snapshots."""
from pathlib import Path
import hashlib
import json
import re
from fontTools.ttLib import TTFont

KIT = Path(__file__).resolve().parent.parent
SOURCES = KIT / "sources"
FONTS = KIT / "fonts"
ROOT_URL = "https://www.aleemuh.com"
SNAPSHOTS = {
    "portfolio-live.html": ROOT_URL + "/",
    "about.D7EEYB4O.css": ROOT_URL + "/_astro/about.D7EEYB4O.css",
    "index.DcaP5fwH.css": ROOT_URL + "/_astro/index.DcaP5fwH.css",
    "inter-official.css": "https://rsms.me/inter/inter.css",
    "typodermic-license.html": "https://typodermicfonts.com/license/",
    "mokoto-official.html": "https://drizyfont.com/fonts/mokoto-glitch-typeface-font/",
    "fontshare-licenses.html": "https://www.fontshare.com/licenses",
}
css = (SOURCES / "about.D7EEYB4O.css").read_text(encoding="utf-8-sig")
home_css = (SOURCES / "index.DcaP5fwH.css").read_text(encoding="utf-8-sig")
all_css = css + "\n" + home_css
tokens = {}
for key, value in re.findall(r"(--(?:color|font|text|radius|spacing|ease|container)[^:;{}]*):([^;{}]+)", css):
    tokens[key] = value.strip()

assets = []
for block in re.findall(r"@font-face\{([^}]+)\}", css):
    props = dict(re.findall(r"([\w-]+):([^;]+)", block))
    path = re.search(r"url\(([^)]+)\)", props.get("src", ""))
    assets.append({
        "family": props.get("font-family", "").strip('"\''),
        "css_weight": props.get("font-weight"),
        "style": props.get("font-style"),
        "display": props.get("font-display"),
        "source_asset_url": ROOT_URL + path.group(1).strip('"\'') if path else None,
        "evidence": "about.D7EEYB4O.css @font-face",
        "binary_downloaded": bool(path and ((FONTS / Path(path.group(1).strip('\"\'')).name).is_file() or (FONTS / "portfolio-local-use" / Path(path.group(1).strip('\"\'')).name).is_file())),
    })

def rules_matching(pattern):
    return [m.group(0) for m in re.finditer(r"[^{}]+\{[^{}]*\}", all_css)
            if re.search(pattern, m.group(0))]

def font_metadata(path):
    font = TTFont(path)
    names = {}
    for record in font["name"].names:
        if record.nameID in (0, 1, 2, 5, 6, 13, 14):
            try:
                value = record.toUnicode()
            except Exception:
                continue
            names.setdefault(str(record.nameID), [])
            if value not in names[str(record.nameID)]:
                names[str(record.nameID)].append(value)
    font.close()
    return names

def luminance(hex_color):
    v = [int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5)]
    linear = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in v]
    return sum(x * y for x, y in zip(linear, (0.2126, 0.7152, 0.0722)))

def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)))
    return round((lb + 0.05) / (la + 0.05), 3)

licenses = {
    "Inter": {
        "publisher": "Rasmus Andersson / The Inter Project Authors",
        "official_source": "https://rsms.me/inter/",
        "official_download": "https://github.com/rsms/inter/releases/download/v4.1/Inter-4.1.zip",
        "license_url": "https://raw.githubusercontent.com/rsms/inter/v4.1/LICENSE.txt",
        "license": "SIL Open Font License 1.1",
        "bundled": True,
        "note": "OFL font files and copyright/license are included. Exact portfolio WOFF2 300/400/500 are included; official 4.1 desktop files and variable webfonts are an additional handoff resource.",
    },
    "Gambetta": {
        "publisher": "Indian Type Foundry / Fontshare",
        "official_source": "https://www.fontshare.com/fonts/gambetta",
        "official_download": "https://api.fontshare.com/v2/fonts/download/gambetta",
        "license_url": "https://www.fontshare.com/licenses",
        "license": "ITF Free Font License 2.0, 17 Aug 2026",
        "bundled": False,
        "note": "Free commercial and self-hosted use. Third-party font redistribution is prohibited. Contractors must download their own copy from Fontshare. A direct download obtained for Aleem is preserved under sources/private-font-reference and must be excluded from shared archives.",
    },
    "Ethnocentric": {
        "publisher": "Typodermic Fonts / Ray Larabie",
        "official_source": "https://typodermicfonts.com/ethnocentric/",
        "license_url": "https://typodermicfonts.com/license/",
        "license": "Exact file's original agreement controls; current desktop and embedding routes differ",
        "bundled": False,
        "note": "Portfolio CSS declares normal 400. Do not assume its existing license or substitute a current font package. Obtain the matching desktop/web/PDF rights from the foundry when needed.",
    },
    "Conthrax": {
        "publisher": "Typodermic Fonts / Ray Larabie",
        "official_source": "https://typodermicfonts.com/conthrax/",
        "license_url": "https://typodermicfonts.com/license/",
        "license": "Exact file's original agreement controls; current desktop and embedding routes differ",
        "bundled": False,
        "note": "The site's CSS declares 400 and its H3/H4 rule requests 300. Inspection of the user-requested local copy identifies Conthrax-SemiBold, version 3.000. The local portfolio binary is excluded from shared archives.",
    },
    "Nasalization": {
        "publisher": "Typodermic Fonts / Ray Larabie",
        "official_source": "https://typodermicfonts.com/nasalization/",
        "license_url": "https://typodermicfonts.com/license/",
        "license": "Exact file's original agreement controls; current desktop and embedding routes differ",
        "bundled": False,
        "note": "Portfolio CSS declares normal 400. Current foundry desktop permission does not establish web embedding or redistribution permission for the portfolio asset.",
    },
    "Mokoto": {
        "publisher": "Drizy Font / Drizy Studio",
        "official_source": "https://drizyfont.com/fonts/mokoto-glitch-typeface-font/",
        "license_url": "https://drizyfont.com/fonts/mokoto-glitch-typeface-font/",
        "license": "Commercial license required for commercial use; desktop/web/document routes depend on license",
        "bundled": False,
        "note": "Portfolio CSS declares normal 400. Record as extracted identity; purchase or confirm the existing project's relevant commercial license before reuse.",
    },
}

result = {
    "project": "NexusPoint Wrapped Nexus brand kit",
    "verified_date_local": "2026-10-02",
    "timezone": "Asia/Karachi",
    "method": "Public live HTML and referenced CSS fetched over HTTPS. Values are CSS declarations, not screenshot estimates. Font licenses checked against current official foundry sources and included agreements.",
    "portfolio": ROOT_URL + "/",
    "canonical": "https://aleemuh.com/",
    "snapshots": [{"file": "sources/" + filename, "url": url,
                   "sha256": hashlib.sha256((SOURCES / filename).read_bytes()).hexdigest(),
                   "bytes": (SOURCES / filename).stat().st_size}
                  for filename, url in SNAPSHOTS.items() if (SOURCES / filename).exists()],
    "colors": {
        "accent": {"hex": "#02A1E1", "rgb": [2, 161, 225], "css_token": "--color-accent", "use": "Centre point, highlighted heading words, focus outlines, selection and highlights"},
        "accent_hover": {"hex": "#0289BF", "rgb": [2, 137, 191], "css_token": "--color-accent-hover"},
        "ink": {"hex": "#000000", "rgb": [0, 0, 0], "css_token": "--color-ink"},
        "ink_soft": {"hex": "#101010", "rgb": [16, 16, 16], "css_token": "--color-ink-soft"},
        "ink_line": {"hex": "#1D1E1F", "rgb": [29, 30, 31], "css_token": "--color-ink-line"},
        "white": {"hex": "#FFFFFF", "rgb": [255, 255, 255], "css_token": "--color-white"},
        "band_deep": {"hex": "#060607", "rgb": [6, 6, 7], "css_token": "--band-ground"},
        "logo_mark_existing_site": {"hex": "#EEF1F4", "rgb": [238, 241, 244], "css_selector": ".cta-mark-n"},
    },
    "font_roles": [
        {"role": "H1 / hero primary", "family": "Ethnocentric", "css_weight": 400, "token": "--font-heavy", "evidence": "h1 and .hero-headline"},
        {"role": "H2 / section headings", "family": "Mokoto", "css_weight": 400, "token": "--font-h2", "evidence": "h2"},
        {"role": "H3-H4 / display labels", "family": "Conthrax", "css_weight": 300, "token": "--font-display", "evidence": "h1,h2,h3,h4 base rule; h1/h2 overridden; available @font-face is declared 400, so 300 resolves to that face"},
        {"role": "Heading accent words / navigation / footer links", "family": "Nasalization", "css_weight": 400, "token": "--font-tech", "evidence": "h1 em,h2 em,h3 em; .nav-link; .footer-link"},
        {"role": "Body / interface / CTA labels", "family": "Inter", "css_weights_available": [300, 400, 500], "token": "--font-sans", "evidence": "body; .rule-link", "default": "16px, line-height 1.6"},
        {"role": "Editorial italic / quotes", "family": "Gambetta", "css_weight": 300, "style": "italic", "token": "--font-serif", "evidence": "em outside H1-H3; .prose-article blockquote"},
    ],
    "font_assets": assets,
    "licenses": licenses,
    "font_binary_metadata": {p.relative_to(FONTS).as_posix(): font_metadata(p) for p in sorted(FONTS.rglob("*")) if p.suffix.lower() in (".woff2", ".otf", ".ttf")},
    "local_font_copy_policy": "fonts/portfolio-local-use contains exact additional portfolio files for Aleem's local previews at his request. Those files are excluded from external handoff archives.",
    "raw_theme_tokens": tokens,
    "layout": {
        "spacing_unit": "4px (.25rem)",
        "responsive_breakpoints_px": [640, 768, 1024, 1280, 1536],
        "content_max_width": "1280px (80rem / --container-7xl)",
        "radii": {"sharp": "2px", "card": "10px", "pill": "500px"},
        "hero_grid": {"size": "76px × 76px", "line": "#FFFFFF0B, approximately 4.3% white"},
        "hero_glow": "13% accent, ellipse 70% × 55% at 78% -8%, fading to transparent at 70%",
        "card_surface": "5% white fill, 10% white inset edge",
        "cta_rule": "1px white at 22%; hover at 55%",
        "focus": "2px accent outline, 3px offset",
    },
    "typography": {
        "hero_actual": {"font_size": "clamp(2.75rem,.5rem + 6.9vw,6.5rem)", "font_size_px": "44px to 104px", "line_height": 1.08, "letter_spacing": "-.01em"},
        "hero_emphasis": {"family": "Nasalization", "letter_spacing": ".02em"},
        "eyebrow": {"font_size": "13px", "line_height": 1.5, "letter_spacing": ".115em"},
        "cta": {"family": "Inter", "weight": 500, "font_size": "13px", "letter_spacing": ".14em", "case": "uppercase"},
        "article_body": {"line_height": 1.75, "opacity": 0.85},
    },
    "motion": {
        "standard_easing": "cubic-bezier(.25,1,.5,1)",
        "reveal": "rise .54s, opacity 0 to 1, blur 6px to 0, translateY 20px to 0",
        "stagger": "75ms increments for initial reveal",
        "interaction": "300-500ms transitions for cards and links",
        "reduced_motion": "CSS disables decorative canvas effects and reveal animations when prefers-reduced-motion is reduce",
    },
    "contrast_srgb": {
        "accent_on_black": contrast("#02A1E1", "#000000"),
        "white_on_accent": contrast("#FFFFFF", "#02A1E1"),
        "accent_on_white": contrast("#02A1E1", "#FFFFFF"),
        "black_on_accent": contrast("#000000", "#02A1E1"),
        "hover_on_white": contrast("#0289BF", "#FFFFFF"),
        "note": "Computed sRGB ratios. Logo color is exempt from text contrast requirements; normal live text should follow appropriate WCAG contrast levels. For a blue-filled button, black copy gives stronger contrast than white.",
    },
    "evidence_rules": {
        "heading_roles": rules_matching(r"(?:^|\})(?:h1|h2|h1,h2,h3,h4|em|h1 em)|hero-headline"),
        "navigation": rules_matching(r"nav-link|footer-link"),
        "grid_and_surface": rules_matching(r"hero-field|card-surface|band-deep|rule-link\["),
    },
    "limitations": [
        "Fonts were identified from the current live @font-face and element CSS rules. This does not identify the generated logo's wordmark font.",
        "The screenshot's hero rotator shows pipeline; the fetched live initial word shows revenue. The identity tokens remain consistent.",
        "The existing display-font licenses on Aleem's portfolio were not provided. No inference of unauthorized use is made; existing agreements may differ from current downloads.",
        "sources/private-font-reference is Aleem's directly downloaded private Fontshare reference, excluded from external handoff archives.",
    ],
}
(SOURCES / "extracted-style.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"accent": result["colors"]["accent"], "contrast": result["contrast_srgb"], "font_count": len(assets), "font_binaries_inspected_locally": len(result["font_binary_metadata"])}, indent=2))
