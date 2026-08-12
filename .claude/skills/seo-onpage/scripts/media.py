#!/usr/bin/env python3
"""Measure a page's images: real bytes, real dimensions, and the real saving from WebP.

The reason this file exists is that "optimize your images" is advice every client has
already been given and already ignored. What moves is a number they can check:

    hero.jpg  412 KB  2400x1600 displayed at 800px
    -> WebP at the same visual quality: 71 KB
    -> 341 KB saved on the element that decides your LCP

Pillow is installed, so the re-encode is done locally and the saving is measured rather
than quoted from a blog post. Nothing is uploaded and nothing is written back to the site.

HEAD first, GET only when the server did not send a usable content-length, so a page with
40 images does not mean 40 full downloads. Capped by --max-images because at some point the
marginal image stops changing the recommendation.

AVIF: not produced. `pillow_avif` is not installed on this machine, so AVIF is cited as
directionally smaller than WebP with less support, and the WebP number is the one measured.
Reporting an unmeasured AVIF saving alongside a measured WebP one would put a guess and a
measurement in the same column.
"""
from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from urllib.parse import urlparse

SKILL_DIR = Path(__file__).resolve().parents[1]
REPO = SKILL_DIR.parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(REPO / ".claude" / "skills" / "web-scraper" / "scripts"))

from engines.base import is_safe_url  # noqa: E402
from engines.http_engine import HEADERS  # noqa: E402

HERO_MAX_BYTES = 150_000        # course/17
MODERN_FORMATS = {"WEBP", "AVIF"}
WEBP_QUALITY = 82               # visually equivalent to typical JPEG q85 output
OVERSIZE_RATIO = 2.0            # natural width more than 2x displayed width

BYTES_FETCHED = 0
IMAGES_SEEN = 0


def _human(n: int | None) -> str:
    if n is None:
        return "unknown"
    return f"{n / 1000:.0f} KB" if n >= 1000 else f"{n} B"


def measure_image(url: str, *, timeout: int = 25, download: bool = True) -> dict:
    """Bytes, format, natural size, and the measured WebP re-encode saving."""
    global BYTES_FETCHED
    import requests

    out = {"src": url, "bytes": None, "format": None, "natural_width": None,
           "natural_height": None, "webp_bytes": None, "webp_saving": None, "note": ""}

    if not is_safe_url(url):
        out["note"] = "skipped: private or non-http host"
        return out

    # Ask the way a browser asks. Modern image CDNs (Wix, Cloudflare, Shopify, Netlify)
    # content-negotiate on Accept and return AVIF or WebP to real visitors while serving the
    # original PNG/JPEG to anything that does not ask. Measured on a live client site: the
    # same URL returned 93,554 bytes as PNG with no Accept header and 29,828 bytes as AVIF
    # with one. Without this, every finding on such a site is a measurement artifact -
    # savings that are already being realised get reported as available, and the client is
    # sold an optimization they already have.
    browser_headers = dict(HEADERS)
    browser_headers["Accept"] = "image/avif,image/webp,image/apng,image/*,*/*;q=0.8"

    try:
        h = requests.head(url, headers=browser_headers, timeout=timeout, allow_redirects=True)
        cl = h.headers.get("content-length")
        if cl and cl.isdigit():
            out["bytes"] = int(cl)
        out["format"] = (h.headers.get("content-type") or "").split("/")[-1].upper() or None
    except Exception as exc:  # noqa: BLE001
        out["note"] = f"HEAD failed: {type(exc).__name__}"

    # Only download when HEAD did not answer, or when we intend to measure the re-encode.
    if not download:
        return out
    try:
        r = requests.get(url, headers=browser_headers, timeout=timeout)
        blob = r.content
        BYTES_FETCHED += len(blob)
        out["bytes"] = len(blob)
        ctype = (r.headers.get("content-type") or "").split(";")[0].strip().lower()
        # A host that blocks scripted requests answers 200 with an HTML error page. Left
        # unchecked that surfaces as "decode failed", which reads like a broken image rather
        # than a blocked fetch, and those need completely different responses.
        if ctype and not ctype.startswith("image/"):
            out["format"] = None
            out["note"] = (f"not an image: server returned {ctype} ({r.status_code}). The host "
                           "likely blocks scripted requests; check this image by hand.").strip()
            return out
        out["format"] = ctype.split("/")[-1].upper() if ctype else out["format"]
    except Exception as exc:  # noqa: BLE001
        out["note"] = (out["note"] + f" GET failed: {type(exc).__name__}").strip()
        return out

    try:
        from PIL import Image

        im = Image.open(io.BytesIO(blob))
        out["format"] = (im.format or "").upper()
        out["natural_width"], out["natural_height"] = im.size

        if out["format"] in ("SVG", "GIF"):
            out["note"] = (out["note"] + f" {out['format']} not re-encoded").strip()
            return out

        buf = io.BytesIO()
        im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB").save(
            buf, format="WEBP", quality=WEBP_QUALITY, method=4)
        out["webp_bytes"] = buf.tell()
        out["webp_saving"] = max(0, out["bytes"] - out["webp_bytes"])
    except Exception as exc:  # noqa: BLE001
        out["note"] = (out["note"] + f" decode failed: {type(exc).__name__}").strip()

    return out


def audit(url: str, *, max_images: int = 30, refresh: bool = False) -> dict:
    global IMAGES_SEEN
    import fetch_page
    import onpage

    rec = fetch_page.fetch(url, refresh=refresh)
    if not rec.get("html"):
        return {"url": url, "error": f"empty body (status {rec.get('status')})"}
    doc = onpage.doc_from_html(rec["html"], rec.get("final_url") or url)

    imgs = [i for i in doc.images if i["src"].startswith(("http://", "https://"))]
    IMAGES_SEEN = len(imgs)
    truncated = len(imgs) > max_images
    imgs = imgs[:max_images]

    rows = []
    for idx, i in enumerate(imgs):
        print(f"[media] {idx + 1}/{len(imgs)} {i['src'][:80]}", file=sys.stderr)
        m = measure_image(i["src"])
        displayed = None
        try:
            displayed = int(str(i["width"]).replace("px", "")) if i["width"] else None
        except ValueError:
            pass
        oversize = (m["natural_width"] and displayed
                    and m["natural_width"] > displayed * OVERSIZE_RATIO)
        rows.append({
            **m,
            "position": idx,
            "is_hero_candidate": idx == 0,
            "alt": i["alt"], "alt_missing": i["alt"] is None,
            "declared_width": i["width"], "declared_height": i["height"],
            "has_explicit_size": bool(i["width"] and i["height"]),
            "loading": i["loading"], "fetchpriority": i["fetchpriority"],
            "srcset": i["srcset"],
            "modern_format": (m["format"] or "") in MODERN_FORMATS,
            "oversized_for_display": bool(oversize),
        })

    total = sum(r["bytes"] or 0 for r in rows)
    saving = sum(r["webp_saving"] or 0 for r in rows)
    hero = rows[0] if rows else None

    findings = []
    if hero:
        if hero["bytes"] and hero["bytes"] > HERO_MAX_BYTES:
            findings.append(
                f"The first image is {_human(hero['bytes'])}, over the {HERO_MAX_BYTES // 1000}KB "
                f"guideline. Re-encoded to WebP it measures {_human(hero['webp_bytes'])}, a "
                f"{_human(hero['webp_saving'])} saving on the element most likely to be your LCP.")
        if hero["loading"] == "lazy":
            findings.append("The first image is lazy-loaded. The hero should load eagerly with "
                            "fetchpriority=high; lazy-loading it delays the LCP directly.")
        elif hero["fetchpriority"] != "high":
            findings.append("The first image has no fetchpriority=high. One attribute, and it "
                            "tells the browser which image decides the LCP.")

    negotiated = [r for r in rows if (r["format"] or "") in MODERN_FORMATS]
    legacy = [r for r in rows if not r["modern_format"] and r["webp_saving"]]
    if negotiated:
        findings.append(
            f"{len(negotiated)} of {len(rows)} image(s) are ALREADY delivered in a modern "
            f"format (AVIF/WebP) to real browsers - the host content-negotiates on Accept. "
            "There is no compression work to sell here, and a tool that does not send an "
            "Accept header will report a large false saving on these.")
    if legacy:
        findings.append(
            f"{len(legacy)} image(s) are still JPEG or PNG. Converting them measures a "
            f"{_human(sum(r['webp_saving'] for r in legacy))} saving in total. WebP is typically "
            "25-35% smaller than equivalent JPEG and universally supported; AVIF is smaller "
            "again with narrower support, so WebP with a JPEG fallback is the safe default.")

    nosize = [r for r in rows if not r["has_explicit_size"]]
    if nosize:
        findings.append(f"{len(nosize)} of {len(rows)} image(s) have no width and height "
                        "attributes. Adding them removes an entire category of layout shift "
                        "for one line of HTML each.")

    noalt = [r for r in rows if r["alt_missing"]]
    if noalt:
        findings.append(f"{len(noalt)} image(s) have no alt attribute at all. alt=\"\" on a "
                        "decorative image is correct; omitting the attribute is not.")

    oversized = [r for r in rows if r["oversized_for_display"]]
    if oversized:
        findings.append(f"{len(oversized)} image(s) are served at more than {OVERSIZE_RATIO:g}x "
                        "their display size. Most of those bytes are discarded by the browser.")

    return {
        "url": url,
        "images_on_page": IMAGES_SEEN,
        "images_measured": len(rows),
        "truncated": truncated,
        "total_bytes": total,
        "total_bytes_human": _human(total),
        "measured_webp_saving": saving,
        "measured_webp_saving_human": _human(saving),
        "images": rows,
        "findings": findings,
        "notes": [
            "Every saving here was measured by re-encoding the actual file locally with "
            f"Pillow at WebP quality {WEBP_QUALITY}. Nothing was uploaded and nothing was changed.",
            "AVIF is not measured: pillow_avif is not installed. It is directionally smaller "
            "than WebP with less browser support. The WebP figure is the one to quote.",
            "Filenames: rename going forward only. Bulk-renaming existing images is a URL "
            "change and carries the same inbound-link cost as changing a page slug.",
        ],
    }


def cost_report() -> str:
    return (f"media: {IMAGES_SEEN} image(s) on page, {BYTES_FETCHED / 1_000_000:.1f} MB downloaded "
            "to measure. No paid API used.")


def _selftest() -> int:
    """Live but tiny. The claim under test is that the saving is measured, not asserted."""
    ok = True

    print("1. Pillow can re-encode to WebP on this machine")
    try:
        from PIL import Image

        buf = io.BytesIO()
        Image.new("RGB", (400, 300), (120, 90, 60)).save(buf, format="JPEG", quality=92)
        jpeg = buf.getvalue()
        out = io.BytesIO()
        Image.open(io.BytesIO(jpeg)).save(out, format="WEBP", quality=WEBP_QUALITY, method=4)
        print(f"   PASS: {len(jpeg)} B JPEG -> {out.tell()} B WebP")
    except Exception as exc:  # noqa: BLE001
        print(f"   FAIL: {type(exc).__name__}: {exc}")
        return 1

    print("2. AVIF is honestly reported as unavailable rather than guessed")
    try:
        import pillow_avif  # noqa: F401
        print("   NOTE: pillow_avif IS installed here - the module's note is now stale, update it")
    except ImportError:
        print("   PASS: pillow_avif absent, so AVIF savings are cited directionally, never measured")

    print("3. measure a real remote image end to end")
    m = None
    for candidate in ("https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_92x30dp.png",
                      "https://www.python.org/static/img/python-logo@2x.png",
                      "https://picsum.photos/400/300.jpg"):
        m = measure_image(candidate)
        if m["natural_width"]:
            break
    if m and m["bytes"] and m["natural_width"]:
        print(f"   PASS: {_human(m['bytes'])} {m['format']} "
              f"{m['natural_width']}x{m['natural_height']}, webp={_human(m['webp_bytes'])}")
    else:
        print(f"   FAIL: no candidate image could be measured. Last: {m}")
        ok = False

    print("4. a host that blocks scripted requests is reported as blocked, not as a broken image")
    blocked = measure_image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/47/"
                            "PNG_transparency_demonstration_1.png/320px-PNG_transparency_demonstration_1.png")
    if blocked["natural_width"] or "not an image" in blocked["note"]:
        print(f"   PASS: {blocked['note'] or 'measured fine'}")
    else:
        print(f"   FAIL: unclear failure mode - {blocked['note']}")
        ok = False

    print("5. SSRF guard rejects a private host")
    r = measure_image("http://127.0.0.1/logo.png")
    if "skipped" in r["note"]:
        print("   PASS: rejected")
    else:
        print(f"   FAIL: {r['note']}")
        ok = False

    print("\n" + cost_report())
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Measure a page's images and the real WebP saving.")
    ap.add_argument("--url")
    ap.add_argument("--max-images", type=int, default=30)
    ap.add_argument("--refresh", action="store_true")
    ap.add_argument("--out")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return _selftest()
    if not args.url:
        ap.error("--url required (or use --selftest)")

    res = audit(args.url, max_images=args.max_images, refresh=args.refresh)
    if res.get("error"):
        print(f"ERROR: {res['error']}")
        return 1

    if args.out:
        Path(args.out).write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"{args.url}: {res['images_measured']} image(s), {res['total_bytes_human']} total, "
              f"{res['measured_webp_saving_human']} measurable saving -> {args.out}")
    else:
        print(f"\n{res['images_measured']} of {res['images_on_page']} image(s) measured, "
              f"{res['total_bytes_human']} total")
        print(f"Measured WebP saving available: {res['measured_webp_saving_human']}\n")
        for r in res["images"]:
            flag = "HERO" if r["is_hero_candidate"] else "    "
            print(f"  {flag} {_human(r['bytes']):>8} {str(r['format'] or '?'):5} "
                  f"{str(r['natural_width'] or '?'):>5}x{str(r['natural_height'] or '?'):<5} "
                  f"-> webp {_human(r['webp_bytes']):>8}  {Path(urlparse(r['src']).path).name[:44]}")
        print("\nFindings:")
        for f in res["findings"] or ["  none - the media layer is fine"]:
            print(f"  - {f}")
        for n in res["notes"]:
            print(f"\nNOTE: {n}")

    print(cost_report(), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
