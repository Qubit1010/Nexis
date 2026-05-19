#!/usr/bin/env python3
"""
Single full-page screenshot of a running dev server. Used for visual diff
against the original site's full-desktop.png.

Usage:
    python render_screenshot.py <url> <output-path> [--mobile]
"""

import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: render_screenshot.py <url> <output-path> [--mobile]")

    url = sys.argv[1]
    out = Path(sys.argv[2])
    out.parent.mkdir(parents=True, exist_ok=True)
    mobile = "--mobile" in sys.argv

    viewport = {"width": 390, "height": 844} if mobile else {"width": 1440, "height": 900}

    print(f"Rendering {url} → {out} ({'mobile' if mobile else 'desktop'})")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx_kwargs = {"viewport": viewport}
        if mobile:
            ctx_kwargs.update(
                user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_0) AppleWebKit/605.1.15",
                is_mobile=True,
                has_touch=True,
            )
        ctx = browser.new_context(**ctx_kwargs)
        page = ctx.new_page()
        try:
            page.goto(url, wait_until="networkidle", timeout=60_000)
        except Exception:
            # dev server might not reach 'networkidle' (HMR keeps a socket open)
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
        time.sleep(3)

        # scroll to trigger any reveal animations, then return to top
        total = page.evaluate("document.body.scrollHeight")
        for y in range(0, total, max(total // 6, 200)):
            page.evaluate(f"window.scrollTo(0, {y})")
            time.sleep(0.2)
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(1)

        page.screenshot(path=str(out), full_page=True)
        browser.close()
    print(f"Saved {out}")


if __name__ == "__main__":
    main()
