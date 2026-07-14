# Recipe: ML / LLM Training-Data Gathering

Build a clean, provenance-tagged corpus from papers, forums, and open-source repos for model training,
RAG, or fine-tuning. Output is **JSONL** (one record per line) so it streams into a data pipeline.

## Sources and how to reach them
| Source | Engine | Notes |
|---|---|---|
| arXiv abstracts / listings | `http` (free) | Server-rendered. `arxiv.org/abs/<id>`, `arxiv.org/list/cs.AI/recent`. Full PDFs: fetch the `/pdf/` URL or use the scientific skills. |
| GitHub READMEs / docs | `http` (free) | Use `raw.githubusercontent.com/<owner>/<repo>/<branch>/README.md` — raw is clean markdown, no render needed. |
| Hacker News threads | `crawl4ai` (free) | `news.ycombinator.com/item?id=<id>`. http often 403s -> auto-escalates to crawl4ai. |
| Reddit threads | `crawl4ai` / `firecrawl` | Old-reddit (`old.reddit.com`) is lighter. Respect Reddit's API terms (Q7). |
| StackExchange | `http` (free) | Server-rendered Q&A. |
| Docs sites (deep) | `--depth crawl` (crawl4ai BFS) | Whole-site markdown corpus in one command. |

## Commands (validated)
Multi-source corpus, raw markdown + provenance (url + engine on every line):
```
# targets.txt: one URL per line
python scripts/scrape.py --urls targets.txt --extract raw --out jsonl \
  --workers 3 --save --outfile corpus.jsonl
```
Live test: arXiv 1706.03762 + crawl4ai README + a HN item -> 3 JSONL lines, HN auto-escalated http->crawl4ai.

Deep-crawl a whole docs site into a corpus:
```
python scripts/scrape.py --url "https://docs.example.com" --depth crawl --pages 40 --max-depth 2 \
  --extract raw --out jsonl --save --outfile docs_corpus.jsonl
```

Structured fields instead of raw text (e.g. paper title/abstract/authors) — write a small llm schema:
```
# paper_schema.json: {"many": false, "fields":[{"name":"title",...},{"name":"abstract",...},{"name":"authors",...}]}
python scripts/scrape.py --urls arxiv_urls.txt --extract llm --schema paper_schema.json --out jsonl
```

## Provenance (non-negotiable for training data — Q5)
Every `raw` record already carries `url` + `engine` + `note`. Keep them. For a training set add the
fetch date and license yourself (a post-step), so each row is: `{url, engine, fetched, license, text}`.
A corpus without provenance is unusable for a defensible model.

## Cleaning + dedup (Q3, Q5)
- Markdown (what these engines emit) is already ~67% fewer tokens than raw HTML — keep markdown, not HTML.
- Dedup near-identical documents before training: `formats.dedup` on `url`, then a content hash for
  mirror pages. Heavy semantic dedup (MinHash/embeddings) is out of scope here — do it in the data pipeline.
- Three cleaning layers: raw (as fetched) -> normalized (whitespace, boilerplate stripped — the markdown
  already does most) -> curated (the fields you actually train on). Retain raw so you can re-derive.

## Licensing + ethics (Q5, Q7 — read `legal-and-ethics.md`)
- Public != unlicensed. arXiv papers, GitHub repos, forum posts each carry a license / ToS.
- Reddit and many forums now restrict AI-training use (Reddit v. Anthropic/Perplexity). Prefer sources
  with a clear license (arXiv, permissively-licensed repos, Common Crawl, HF datasets).
- Minimize personal data. Strip usernames/PII from forum content unless the license clearly permits it.
- The EDPB has specific guidance on scraping for generative-AI training — respect robots.txt and ToS.

## Hand off
- For *finding* which papers/threads to scrape, use the `research` skill (scientific mode finds papers;
  general mode finds threads/repos), then feed its URLs here as `targets.txt`.
- For paper-specific parsing (equations, figures, citations), the `scientific-agent-skills` router has
  dedicated PDF/literature skills — this skill gets you the raw text, those structure it.
