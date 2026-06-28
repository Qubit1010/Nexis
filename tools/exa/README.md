# Exa.ai — Nexis web search & research tool

Canonical Exa client for Nexis. One entry point for high-quality web search, page contents, cited
answers, and agentic research, used by any skill or script.

Why Exa: neural search + category/domain/date filters return curated, citable sources (peer-reviewed
papers, specialist blogs, primary docs) instead of generic scraped pages.

## Setup (already done)

- **Key:** `EXA_API_KEY` lives in the repo-root `.env` (gitignored). The client auto-loads it; nothing
  to export.
- **SDK:** `exa-py` (>= 2.x) installed. Reinstall with `python -m pip install exa-py` if needed.
- **Python:** `C:\Users\Aleem\AppData\Local\Programs\Python\Python313\python.exe`.

## Usage — CLI

```bash
# Web search (deep = highest quality). --highlights pulls the exact citable snippets.
python tools/exa/exa_client.py search "retrieval practice spaced repetition effect size" \
    --num 8 --type deep --highlights

# Bias to a content category, return full text
python tools/exa/exa_client.py search "transformer tutorial" --category "research paper" --text

# Restrict to specific domains / a date window
python tools/exa/exa_client.py search "AI job market" --include-domains arxiv.org,nature.com \
    --start-date 2025-01-01

# Cited LLM answer over live search
python tools/exa/exa_client.py answer "how big is the testing effect on retention?"

# Fetch cleaned contents for URLs
python tools/exa/exa_client.py contents https://example.com/post --text

# Agentic multi-step research with a synthesized report (exa-research-fast | exa-research)
python tools/exa/exa_client.py research "Summarize the 2026 evidence on spaced repetition with sources" \
    --model exa-research -o report.json

# Save any command's JSON output
python tools/exa/exa_client.py search "..." -o results.json
```

## Usage — library

```python
from tools.exa.exa_client import search, answer, research, get_client

res = search("spaced repetition meta-analysis", num_results=10, category="research paper",
             highlights=True)
ans = answer("what is interleaving and does it help?", text=True)
rep = research("Best fully funded AI master's scholarships for 2026 with deadlines", model="exa-research")
```

## Notes / gotchas

- **Sandbox:** live network calls require the Bash/PowerShell tool to run with the sandbox disabled
  (`dangerouslyDisableSandbox: true`), otherwise DNS to `api.exa.ai` fails with `getaddrinfo failed`.
- **Search types:** `auto` (default), `fast` (low latency), `deep` (highest quality, slower).
- **Categories:** company, research paper, news, github, personal site, financial report, people,
  tweet, pdf.
- **UTF-8:** the CLI forces UTF-8 stdout so unicode/emoji in titles don't crash on Windows cp1252.
- **Cost:** `deep` search, `answer`, and `research` cost more than `fast`/`auto`. Prefer `--highlights`
  over full `--text` when you only need citable snippets.
```
