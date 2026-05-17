#!/usr/bin/env python3
"""
Pixel-precise design tokens via Playwright's getComputedStyle().

Reads CSS at runtime — supplements the regex-based parse_design.py
which only sees inline styles.

Usage:
    python measure_computed.py <url> <output-dir>

Writes:
    <output-dir>/extraction/computed-tokens.json
"""

import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


PROBE_SELECTORS = [
    "h1", "h2", "h3", "h4", "h5",
    "p",
    "button",
    "a",
    "nav",
    "header",
    "footer",
    "main",
    "section",
    "article",
    "[class*='card']",
    "[class*='Card']",
    "[class*='btn']",
    "[class*='Button']",
    "[data-framer-name]",
    "input",
    "blockquote",
]

PROPERTIES = [
    "font-family",
    "font-size",
    "font-weight",
    "line-height",
    "letter-spacing",
    "color",
    "background-color",
    "padding-top",
    "padding-right",
    "padding-bottom",
    "padding-left",
    "margin-top",
    "margin-bottom",
    "border-radius",
    "border-width",
    "border-color",
    "border-style",
    "box-shadow",
    "text-transform",
]

VIEWPORT = {"width": 1440, "height": 900}


def measure(page, url: str) -> dict:
    page.set_viewport_size(VIEWPORT)
    page.goto(url, wait_until="networkidle", timeout=90_000)
    time.sleep(2)

    js = """
    (config) => {
        const { selectors, properties } = config;
        const out = {};
        for (const sel of selectors) {
            const els = Array.from(document.querySelectorAll(sel)).slice(0, 5);
            const samples = [];
            for (const el of els) {
                const r = el.getBoundingClientRect();
                if (r.width === 0 || r.height === 0) continue;
                const cs = window.getComputedStyle(el);
                const sample = { _text: (el.innerText || '').slice(0, 60) };
                for (const p of properties) {
                    sample[p] = cs.getPropertyValue(p);
                }
                samples.push(sample);
            }
            if (samples.length > 0) out[sel] = samples;
        }
        // Body-level page background
        out._body = [{
            'background-color': window.getComputedStyle(document.body).getPropertyValue('background-color'),
            'color': window.getComputedStyle(document.body).getPropertyValue('color'),
            'font-family': window.getComputedStyle(document.body).getPropertyValue('font-family'),
        }];
        return out;
    }
    """
    return page.evaluate(js, {"selectors": PROBE_SELECTORS, "properties": PROPERTIES})


def main():
    if len(sys.argv) < 3:
        sys.exit("Usage: measure_computed.py <url> <output-dir>")

    url = sys.argv[1]
    out = Path(sys.argv[2]) / "extraction"
    out.mkdir(parents=True, exist_ok=True)

    print(f"Measuring computed styles on {url} ...", flush=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport=VIEWPORT)
        data = measure(page, url)
        browser.close()

    out_file = out / "computed-tokens.json"
    out_file.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Saved {out_file}")
    print(f"  matched {len([k for k in data if not k.startswith('_')])} selector groups")
    if "h1" in data:
        h1 = data["h1"][0]
        print(f"  h1: {h1.get('font-size')} / {h1.get('font-weight')} / line-height {h1.get('line-height')}")
    if "p" in data:
        p_ = data["p"][0]
        print(f"  p:  {p_.get('font-size')} / line-height {p_.get('line-height')}")


if __name__ == "__main__":
    main()
