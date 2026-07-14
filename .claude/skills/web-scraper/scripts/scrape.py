"""web-scraper orchestrator / CLI.

Ties the five engines + router + extract + formats into one command. Walks the escalation ladder on
a BlockedError, rotates numbered API keys inside each engine on a QuotaError, extracts (raw/links/css/
llm), then renders (json/csv/jsonl/md), optionally saving.

Examples:
  python scrape.py --url https://example.com --extract raw
  python scrape.py --url <directory> --extract llm --schema templates/leadgen_schema.json --out csv --save
  python scrape.py --urls targets.txt --extract llm --schema s.json --out jsonl --save --outfile corpus.jsonl
  python scrape.py --url <zillow search> --engine apify --out json   # router picks the zillow actor
  python scrape.py --url <site> --depth crawl --pages 25 --extract raw --out md

Runs UNSANDBOXED (needs DNS + a real browser for crawl4ai). Parallel over --urls via ThreadPoolExecutor.
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import extract as extract_mod  # noqa: E402
import formats  # noqa: E402
import router  # noqa: E402
from engines import (  # noqa: E402
    apify_engine, crawl4ai_engine, firecrawl_engine, http_engine, scrapingant_engine,
)
from engines.base import BlockedError, EngineError, QuotaError  # noqa: E402

ENGINES = {
    "http": http_engine, "crawl4ai": crawl4ai_engine, "firecrawl": firecrawl_engine,
    "apify": apify_engine, "scrapingant": scrapingant_engine,
}


def _fetch_one(engine_name: str, url: str, actor: str | None) -> dict:
    """One engine attempt. apify with a specialized actor routes through its actor() path."""
    eng = ENGINES[engine_name]
    if engine_name == "apify" and actor:
        # specialized actor: most take a startUrls list; the recipes override run_input when needed
        return apify_engine.actor(actor, {"startUrls": [{"url": url}]}, max_items=200)
    return eng.fetch(url)


def scrape_url(url: str, *, engine: str = "auto", depth: str = "page", pages: int = 20,
               max_depth: int = 2) -> dict:
    """Fetch one URL, escalating up the ladder on BlockedError. Returns the engine result dict."""
    plan = router.classify(url)
    actor = plan.get("actor")
    if depth == "crawl":  # deep crawl uses the free self-hosted engine directly
        pages_out = crawl4ai_engine.crawl(url, max_pages=pages, max_depth=max_depth)
        md = "\n\n---\n\n".join(p.get("markdown", "") for p in pages_out)
        return {"url": url, "markdown": md, "rows": pages_out, "engine": "crawl4ai",
                "links": [], "html": "", "metadata": {}, "note": f"crawl {len(pages_out)} pages"}

    start = plan["engine"] if engine == "auto" else engine
    tried, last = [], None
    for eng_name in router.escalation_from(start):
        tried.append(eng_name)
        try:
            res = _fetch_one(eng_name, url, actor if eng_name == "apify" else None)
            res["note"] = (res.get("note", "") + f" | tried={'>'.join(tried)}").strip(" |")
            return res
        except BlockedError as e:
            last = e
            print(f"[scrape] {eng_name} blocked on {url} ({e}); escalating", file=sys.stderr)
        except QuotaError as e:
            last = e
            print(f"[scrape] {eng_name} out of quota on {url} ({e}); escalating", file=sys.stderr)
        except EngineError as e:
            last = e
            print(f"[scrape] {eng_name} error on {url} ({e}); escalating", file=sys.stderr)
    raise EngineError(f"all engines failed for {url} (tried {tried}): {last}")


def process(url: str, *, engine: str, extract: str, schema: dict | None, instructions: str,
            depth: str, pages: int, max_depth: int) -> dict:
    res = scrape_url(url, engine=engine, depth=depth, pages=pages, max_depth=max_depth)
    return extract_mod.extract(res, extract, schema=schema, instructions=instructions)


def _rows_from(res: dict, extract: str) -> list[dict]:
    """Reduce an extracted result to output rows for csv/jsonl/md rendering."""
    if extract in ("css", "llm"):
        return res.get("rows") or []
    if extract == "links":
        return [{"url": u} for u in (res.get("links") or [])]
    # raw
    return [{"url": res.get("url", ""), "engine": res.get("engine", ""),
             "markdown": res.get("markdown", ""), "note": res.get("note", "")}]


def main() -> int:
    ap = argparse.ArgumentParser(description="Multi-engine web scraper + structured extraction.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", help="single target URL")
    src.add_argument("--urls", help="file with one URL per line")
    ap.add_argument("--engine", default="auto", choices=["auto", *ENGINES.keys()])
    ap.add_argument("--extract", default="raw", choices=["raw", "links", "css", "llm"])
    ap.add_argument("--schema", help="path to a css/llm schema JSON")
    ap.add_argument("--instructions", default="", help="extra guidance for --extract llm")
    ap.add_argument("--depth", default="page", choices=["page", "crawl"])
    ap.add_argument("--pages", type=int, default=20, help="max pages for --depth crawl")
    ap.add_argument("--max-depth", type=int, default=2, help="max depth for --depth crawl")
    ap.add_argument("--out", default="json", choices=["json", "jsonl", "csv", "md"])
    ap.add_argument("--dedup", help="field(s) to dedup rows on, comma-separated")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--save", action="store_true", help="write to --outfile (or an auto name)")
    ap.add_argument("--outfile", help="explicit output path")
    args = ap.parse_args()

    schema = json.loads(Path(args.schema).read_text(encoding="utf-8")) if args.schema else None
    urls = ([args.url] if args.url
            else [u.strip() for u in Path(args.urls).read_text(encoding="utf-8").splitlines() if u.strip()])

    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(process, u, engine=args.engine, extract=args.extract, schema=schema,
                          instructions=args.instructions, depth=args.depth, pages=args.pages,
                          max_depth=args.max_depth): u for u in urls}
        for fut in as_completed(futs):
            u = futs[fut]
            try:
                results.append(fut.result())
            except Exception as e:  # noqa: BLE001 - one bad URL shouldn't kill the batch
                print(f"[scrape] FAILED {u}: {e}", file=sys.stderr)

    rows: list[dict] = []
    for res in results:
        rows.extend(_rows_from(res, args.extract))
    if args.dedup:
        rows = formats.dedup(rows, key=[k.strip() for k in args.dedup.split(",")])

    out = formats.render(rows, args.out)
    if args.save:
        ext = {"json": "json", "jsonl": "jsonl", "csv": "csv", "md": "md"}[args.out]
        path = Path(args.outfile) if args.outfile else Path(f"scrape_output.{ext}")
        path.write_text(out, encoding="utf-8")
        print(f"Saved {len(rows)} row(s) -> {path}", file=sys.stderr)
    else:
        print(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
