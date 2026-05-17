#!/usr/bin/env python3
"""
Playwright section-by-section + full-page screenshots.

Uses bounding-box clustering to deduplicate the nested-section problem that
plagued the reference implementation (77 dupes → ~10 real sections).

Usage:
    python screenshot_sections.py <url> <output-dir>

Writes:
    <output-dir>/extraction/full-desktop.png
    <output-dir>/extraction/full-mobile.png
    <output-dir>/extraction/sections/desktop/NN-<label>.png
    <output-dir>/extraction/sections/mobile/NN-<label>.png
"""

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright, Page


DESKTOP_VIEWPORT = {"width": 1440, "height": 900}
MOBILE_VIEWPORT = {"width": 390, "height": 844}

# Heuristic labels applied in order (first 9). Beyond that, "section10", "section11", etc.
SECTION_LABELS = [
    "hero", "logos", "services", "work", "process",
    "testimonials", "about", "cta", "footer",
]

MAX_SECTIONS = 14


def slow_scroll(page: Page, steps: int = 10) -> None:
    """Scroll to trigger Framer/lazy animations, then return to top."""
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.3)
    total = page.evaluate("document.body.scrollHeight")
    step = max(total // steps, 200)
    for i in range(1, steps + 1):
        page.evaluate(f"window.scrollTo(0, {step * i})")
        time.sleep(0.2)
    page.evaluate("window.scrollTo(0, 0)")
    time.sleep(0.8)


def get_clustered_sections(page: Page, viewport_w: int) -> list:
    """
    Bounding-box clustering. Strategy:
    1. Try direct children of <main>. Else <body> direct children.
    2. Filter: height > 240, width > 0.6 * viewport
    3. Dedupe by Y-bin (round y/30) — same band = same logical section
    4. Cap at MAX_SECTIONS
    """
    # Walk down the tree taking the deepest level where we get a useful count
    candidates_js = """
    (() => {
        const minWidth = arguments[0];
        const probes = [
            'main > *',
            'main > * > *',
            'body > div > *',
            'body > div > div > *',
            'section',
        ];
        for (const sel of probes) {
            const els = Array.from(document.querySelectorAll(sel));
            const valid = [];
            const seen = new Set();
            for (const el of els) {
                const r = el.getBoundingClientRect();
                if (r.height < 240 || r.width < minWidth) continue;
                const key = Math.round((r.top + window.scrollY) / 30) + ':' + Math.round(r.height / 30);
                if (seen.has(key)) continue;
                seen.add(key);
                valid.push({
                    selector: sel,
                    y: r.top + window.scrollY,
                    height: r.height,
                    width: r.width,
                });
            }
            if (valid.length >= 4 && valid.length <= 20) {
                return valid.sort((a, b) => a.y - b.y);
            }
        }
        return [];
    })
    """
    # Playwright doesn't pass `arguments` cleanly via .evaluate for IIFE — use a fn form
    boxes = page.evaluate(
        """(minWidth) => {
            const probes = ['main > *', 'main > * > *', 'body > div > *', 'body > div > div > *', 'section'];
            for (const sel of probes) {
                const els = Array.from(document.querySelectorAll(sel));
                const valid = [];
                const seen = new Set();
                for (const el of els) {
                    const r = el.getBoundingClientRect();
                    if (r.height < 240 || r.width < minWidth) continue;
                    const key = Math.round((r.top + window.scrollY) / 30) + ':' + Math.round(r.height / 30);
                    if (seen.has(key)) continue;
                    seen.add(key);
                    valid.push({
                        selector: sel,
                        y: r.top + window.scrollY,
                        height: r.height,
                        width: r.width,
                    });
                }
                if (valid.length >= 4 && valid.length <= 20) {
                    return valid.sort((a, b) => a.y - b.y);
                }
            }
            return [];
        }""",
        viewport_w * 0.6,
    )
    return boxes[:MAX_SECTIONS]


def screenshot_section(page: Page, box: dict, save_path: Path) -> bool:
    """Scroll to a section by its Y coordinate and screenshot a viewport-aligned slice."""
    try:
        page.evaluate(f"window.scrollTo(0, {max(0, box['y'] - 20)})")
        time.sleep(0.4)
        # Take a clipped screenshot from current viewport
        clip_height = min(box["height"], 1200)  # cap so we don't blow file sizes
        page.screenshot(
            path=str(save_path),
            clip={"x": 0, "y": 20, "width": box["width"], "height": clip_height},
        )
        return True
    except Exception as e:
        print(f"    section screenshot failed: {e}")
        return False


def run_viewport(page: Page, url: str, viewport: dict, label: str, out_root: Path) -> None:
    page.set_viewport_size(viewport)
    page.goto(url, wait_until="networkidle", timeout=90_000)
    time.sleep(2)
    slow_scroll(page)

    # Full-page screenshot
    full_path = out_root / f"full-{label}.png"
    page.screenshot(path=str(full_path), full_page=True)
    print(f"  full-{label}.png saved")

    # Section detection
    boxes = get_clustered_sections(page, viewport["width"])
    print(f"  {len(boxes)} sections detected ({label})")

    sect_dir = out_root / "sections" / label
    sect_dir.mkdir(parents=True, exist_ok=True)

    for idx, box in enumerate(boxes):
        name = SECTION_LABELS[idx] if idx < len(SECTION_LABELS) else f"section{idx + 1}"
        path = sect_dir / f"{idx + 1:02d}-{name}.png"
        if screenshot_section(page, box, path):
            print(f"    {path.name}")


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: screenshot_sections.py <url> <output-dir>")

    url = sys.argv[1]
    out_root = Path(sys.argv[2]) / "extraction"
    out_root.mkdir(parents=True, exist_ok=True)

    print(f"Screenshotting {url}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        print("\n[Desktop 1440x900]")
        ctx = browser.new_context(viewport=DESKTOP_VIEWPORT)
        run_viewport(ctx.new_page(), url, DESKTOP_VIEWPORT, "desktop", out_root)
        ctx.close()

        print("\n[Mobile 390x844]")
        ctx = browser.new_context(
            viewport=MOBILE_VIEWPORT,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0) AppleWebKit/605.1.15",
            is_mobile=True,
            has_touch=True,
        )
        run_viewport(ctx.new_page(), url, MOBILE_VIEWPORT, "mobile", out_root)
        ctx.close()

        browser.close()

    print("\nScreenshots complete.")


if __name__ == "__main__":
    main()
