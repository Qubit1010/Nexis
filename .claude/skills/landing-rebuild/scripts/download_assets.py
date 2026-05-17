#!/usr/bin/env python3
"""
Role-aware image downloader. Reads extracted HTML, infers each image's
likely role (hero portrait / work card / avatar / logo / generic asset),
downloads with a sensible filename, and writes an asset-manifest.json.

Usage:
    python download_assets.py <output-dir>

Reads <output-dir>/extraction/page.html and writes:
    <output-dir>/extraction/public-images/<role>-N.<ext>
    <output-dir>/extraction/asset-manifest.json
"""

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

import requests


HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def ext_from_url(url: str) -> str:
    path = urlparse(url).path.lower()
    for e in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".avif"):
        if path.endswith(e):
            return e
    return ".png"


def find_images_with_context(html: str) -> list[dict]:
    """
    Walk the HTML and for each <img src="..."> capture:
      - the src URL
      - ~400 chars of surrounding markup (for role inference)
      - any width/height attributes
    """
    results = []
    for m in re.finditer(r'<img\b[^>]*\bsrc="([^"]+)"[^>]*>', html, re.IGNORECASE):
        src = m.group(1).replace("&amp;", "&")
        if not src.startswith("http"):
            continue
        start = max(0, m.start() - 200)
        end = min(len(html), m.end() + 200)
        context = html[start:end].lower()

        tag = m.group(0).lower()
        width = None
        height = None
        wmatch = re.search(r'width="(\d+)"', tag)
        hmatch = re.search(r'height="(\d+)"', tag)
        if wmatch:
            width = int(wmatch.group(1))
        if hmatch:
            height = int(hmatch.group(1))

        # Also look at width in querystring (Framer puts ?width=1200&height=...)
        url_w = re.search(r"[?&]width=(\d+)", src)
        if url_w and not width:
            width = int(url_w.group(1))
        url_h = re.search(r"[?&]height=(\d+)", src)
        if url_h and not height:
            height = int(url_h.group(1))

        results.append({"src": src, "context": context, "width": width, "height": height,
                        "pos": m.start()})
    return results


def infer_roles(images: list[dict]) -> list[dict]:
    """
    Heuristic role assignment.
      - First large landscape image (width >= 1000, ratio > 1.2) → hero
      - Small square images near "testimonial"/"client" keywords → avatar
      - Small repeating-position images → logo
      - 16:9 / 4:3 landscape images → work card
      - Everything else → asset
    """
    counts = {"hero": 0, "about": 0, "work": 0, "avatar": 0, "logo": 0, "asset": 0}

    # Map URL → first-seen index for dedup (Framer repeats logos in marquees)
    seen_urls = {}
    for i, img in enumerate(images):
        if img["src"] not in seen_urls:
            seen_urls[img["src"]] = i

    for i, img in enumerate(images):
        if seen_urls[img["src"]] != i:
            img["role"] = "duplicate"
            img["filename"] = None
            continue

        ctx = img["context"]
        w = img["width"] or 0
        h = img["height"] or 0
        ratio = (w / h) if h else 1.0

        # 1) About portrait: large near "about"/"founder"/"bio" keywords
        if (w >= 1000 and h >= 1000 and 0.85 < ratio < 1.2 and
            any(k in ctx for k in ("about", "founder", "bio", "myself", " i am ", "i'm"))):
            role = "about"
        # 2) Hero portrait: very large square-ish, first occurrence
        elif w >= 1200 and 0.85 < ratio < 1.2 and counts["hero"] == 0:
            role = "hero"
        # 3) Avatar: small square (typically 120x120 from Framer)
        elif w and w <= 250 and h and h <= 250 and 0.9 < ratio < 1.1:
            role = "avatar"
        # 4) Logo: small landscape near logo keywords or small (under 500w)
        elif w and w < 500 and (
            any(k in ctx for k in ("logo", "trusted", "client")) or counts["logo"] < 6
        ):
            role = "logo"
        # 5) Work card: landscape 16:9 / 4:3 / wider, decent size
        elif w >= 800 and ratio >= 1.3:
            role = "work"
        else:
            role = "asset"

        counts[role] = counts.get(role, 0) + 1
        n = counts[role]
        img["role"] = role
        img["filename"] = f"{role}-{n}{ext_from_url(img['src'])}" if role != "hero" else f"hero-portrait{ext_from_url(img['src'])}"

    return images


def main():
    if len(sys.argv) < 2:
        sys.exit("Usage: download_assets.py <output-dir>")

    out_root = Path(sys.argv[1])
    extraction = out_root / "extraction"
    html_file = extraction / "page.html"
    if not html_file.exists():
        sys.exit(f"Missing {html_file} — run extract.py first")

    images_dir = extraction / "public-images"
    images_dir.mkdir(parents=True, exist_ok=True)

    html = html_file.read_text(encoding="utf-8")
    images = find_images_with_context(html)
    print(f"Found {len(images)} img tags; deduplicating + inferring roles...")
    images = infer_roles(images)

    manifest = []
    downloaded = 0
    skipped = 0
    for img in images:
        if img["role"] == "duplicate":
            skipped += 1
            continue
        try:
            r = requests.get(img["src"], headers=HEADERS, timeout=25)
            r.raise_for_status()
            dest = images_dir / img["filename"]
            dest.write_bytes(r.content)
            manifest.append({
                "src": img["src"],
                "local": str(dest.relative_to(extraction)),
                "role": img["role"],
                "width": img["width"],
                "height": img["height"],
                "bytes": len(r.content),
            })
            print(f"  {img['role']:>8}  {img['filename']:30}  {len(r.content):>10,} bytes")
            downloaded += 1
        except Exception as e:
            print(f"  ERR  {img['src']}: {e}")

    manifest_path = extraction / "asset-manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nDownloaded {downloaded} images (skipped {skipped} dupes). Manifest: {manifest_path}")


if __name__ == "__main__":
    main()
