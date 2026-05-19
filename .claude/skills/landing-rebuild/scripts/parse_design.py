#!/usr/bin/env python3
"""
CSS regex + base64 font token extraction.

Usage:
    python parse_design.py <output-dir>

Reads <output-dir>/extraction/page.html and writes:
  <output-dir>/extraction/design-tokens.json
"""

import base64
import json
import re
import sys
from pathlib import Path


def extract_css_blocks(html: str) -> list[str]:
    blocks = []
    for m in re.finditer(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE):
        blocks.append(m.group(1))
    for m in re.finditer(r'style="([^"]*)"', html):
        blocks.append(m.group(1))
    return blocks


def extract_colors(text: str) -> list[str]:
    patterns = [
        r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b",
        r"rgba?\(\s*[\d.]+\s*,\s*[\d.]+\s*,\s*[\d.]+(?:\s*,\s*[\d.]+)?\s*\)",
        r"hsla?\(\s*[\d.]+(?:deg)?\s*,?\s*[\d.%]+\s*,?\s*[\d.%]+(?:\s*,\s*[\d.]+)?\s*\)",
    ]
    found = set()
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            found.add(m.group(0).lower())
    return sorted(found)


def extract_font_families(text: str) -> list[str]:
    """Regex-based extraction. Often returns garbage (e.g. &quot for HTML-encoded values).
    The base64 decoder below is more reliable for Framer pages."""
    found = set()
    for m in re.finditer(r"font-family\s*:\s*([^;\"{}]+)", text, re.IGNORECASE):
        raw = m.group(1).strip().rstrip(",")
        for family in raw.split(","):
            f = family.strip().strip("'\"")
            if not f or f.lower() in ("inherit", "initial", "unset"):
                continue
            if f.startswith("&"):  # HTML-encoded artifact
                continue
            if len(f) > 60:  # likely garbage
                continue
            found.add(f)
    return sorted(found)


def decode_framer_fonts(text: str) -> list[dict]:
    """
    Framer encodes font choices like:
        --font-selector: Q1VTVE9NO1NhdG9zaGkgUmVndWxhcg==
    which base64-decodes to: CUSTOM;Satoshi Regular

    Decode every --font-selector occurrence, dedupe.
    """
    results = []
    seen = set()
    for m in re.finditer(r"--font-selector\s*:\s*([A-Za-z0-9+/=]+)", text):
        b64 = m.group(1).strip()
        try:
            decoded = base64.b64decode(b64).decode("utf-8", errors="replace")
        except Exception:
            continue
        if decoded in seen:
            continue
        seen.add(decoded)
        # Format is usually "SOURCE;Font Family Variant"
        parts = decoded.split(";", 1)
        source = parts[0] if len(parts) > 1 else ""
        family_full = parts[-1].strip()
        # Split "Satoshi Regular" → family + weight hint
        family_words = family_full.split()
        # Heuristic: last word is weight if it matches known weights
        weight_words = {"thin", "extralight", "light", "regular", "medium", "semibold",
                        "bold", "extrabold", "black", "heavy", "italic"}
        weight_hint = None
        if family_words and family_words[-1].lower() in weight_words:
            weight_hint = family_words[-1]
            family_name = " ".join(family_words[:-1])
        else:
            family_name = family_full
        results.append({
            "raw": decoded,
            "source": source,
            "family": family_name,
            "weight_hint": weight_hint,
        })
    return results


def extract_font_sizes(text: str) -> list[str]:
    found = set()
    for m in re.finditer(r"font-size\s*:\s*([\d.]+(?:px|rem|em|vw|vh|%|pt))", text, re.IGNORECASE):
        found.add(m.group(1).lower())
    return sorted(found, key=lambda x: float(re.search(r"[\d.]+", x).group()))


def extract_font_weights(text: str) -> list[str]:
    found = set()
    for m in re.finditer(r"font-weight\s*:\s*([\w]+)", text, re.IGNORECASE):
        v = m.group(1)
        if v.lower() not in ("inherit", "initial", "unset"):
            found.add(v)
    return sorted(found)


def extract_border_radii(text: str) -> list[str]:
    found = set()
    for m in re.finditer(r"border-radius\s*:\s*([\d.]+(?:px|rem|em|%))", text, re.IGNORECASE):
        found.add(m.group(1))
    return sorted(found, key=lambda x: float(re.search(r"[\d.]+", x).group()))


def extract_css_vars(text: str) -> dict:
    found = {}
    for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;}\n]+)", text):
        key = m.group(1).strip()
        val = m.group(2).strip()
        if key not in found:
            found[key] = val
    return found


def extract_letter_spacing(text: str) -> list[str]:
    found = set()
    for m in re.finditer(r"letter-spacing\s*:\s*([-\d.]+(?:px|em|rem))", text, re.IGNORECASE):
        found.add(m.group(1))
    return sorted(found)


def extract_box_shadows(text: str) -> list[str]:
    found = set()
    for m in re.finditer(r"box-shadow\s*:\s*([^;\"{}]{8,120})", text, re.IGNORECASE):
        found.add(m.group(1).strip())
    return sorted(found)[:15]


def extract_image_urls(html: str) -> list[str]:
    """Extract all images from common CDNs and inline img tags."""
    found = set()
    for m in re.finditer(r'src="(https?://[^"]+\.(?:png|jpg|jpeg|webp|svg|gif|avif)(?:\?[^"]*)?)"',
                         html, re.IGNORECASE):
        found.add(m.group(1).replace("&amp;", "&"))
    for m in re.finditer(r"url\(['\"]?(https?://[^'\")]+\.(?:png|jpg|jpeg|webp|svg|gif|avif)[^'\")]*)['\"]?\)",
                         html, re.IGNORECASE):
        found.add(m.group(1).replace("&amp;", "&"))
    return sorted(found)


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: parse_design.py <output-dir>")

    out_root = Path(sys.argv[1])
    extraction = out_root / "extraction"
    html_file = extraction / "page.html"

    if not html_file.exists():
        sys.exit(f"Missing {html_file} — run extract.py first")

    html = html_file.read_text(encoding="utf-8")
    css_blocks = extract_css_blocks(html)
    all_css = "\n".join(css_blocks)

    tokens = {
        "colors": extract_colors(all_css),
        "font_families_regex": extract_font_families(all_css),
        "framer_fonts_decoded": decode_framer_fonts(all_css),
        "font_sizes": extract_font_sizes(all_css),
        "font_weights": extract_font_weights(all_css),
        "border_radii": extract_border_radii(all_css),
        "letter_spacing": extract_letter_spacing(all_css),
        "box_shadows": extract_box_shadows(all_css),
        "css_variables": extract_css_vars(all_css),
        "image_urls": extract_image_urls(html),
    }

    out_path = extraction / "design-tokens.json"
    out_path.write_text(json.dumps(tokens, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Design tokens saved to {out_path}")
    print(f"  colors:          {len(tokens['colors'])}")
    print(f"  framer fonts:    {[f['family'] for f in tokens['framer_fonts_decoded']]}")
    print(f"  regex fonts:     {tokens['font_families_regex'][:5]}")
    print(f"  font sizes:      {len(tokens['font_sizes'])}")
    print(f"  border radii:    {tokens['border_radii']}")
    print(f"  image urls:      {len(tokens['image_urls'])}")


if __name__ == "__main__":
    main()
