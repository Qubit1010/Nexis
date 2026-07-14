"""Load API keys from the repo-root .env (the standard Nexis location).

Mirrors research/scripts/_env.py, plus get_keys() for numbered-key rotation:
Apify has APIFY_API_KEY(+_2/_3/_4) and Firecrawl has FIRECRAWL_API_KEY(+_2). Engines try keys in
order and rotate to the next on a quota/limit error, so one exhausted key doesn't sink the job.
"""
from __future__ import annotations

import os
from pathlib import Path

_LOADED = False


def repo_root() -> Path:
    """Walk up from this file to the first dir containing a .env."""
    here = Path(__file__).resolve()
    for parent in [here.parent, *here.parents]:
        if (parent / ".env").exists():
            return parent
    return here.parents[4]  # .claude/skills/web-scraper/scripts -> repo root fallback


def load_env() -> None:
    """Parse repo .env into os.environ (setdefault, so real env vars win)."""
    global _LOADED
    if _LOADED:
        return
    env_path = repo_root() / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))
    _LOADED = True


def get_key(name: str, *, required: bool = True) -> str | None:
    """Return a single API key by env var name, loading the .env first."""
    load_env()
    val = os.environ.get(name)
    if val:
        return val.strip()
    if required:
        raise SystemExit(f"{name} not found in environment or repo .env.")
    return None


def get_keys(name: str, *, required: bool = True) -> list[str]:
    """Return all numbered keys for a service: name, name_2, name_3, ... in order.

    E.g. get_keys("APIFY_API_KEY") -> [APIFY_API_KEY, APIFY_API_KEY_2, APIFY_API_KEY_3, APIFY_API_KEY_4].
    De-duplicated, blanks skipped. Engines iterate this and rotate on quota/limit errors.
    """
    load_env()
    keys: list[str] = []
    for suffix in ["", "_2", "_3", "_4", "_5"]:
        val = os.environ.get(f"{name}{suffix}")
        if val:
            val = val.strip()
            if val and val not in keys:
                keys.append(val)
    if not keys and required:
        raise SystemExit(f"{name} (or {name}_2 ...) not found in environment or repo .env.")
    return keys


if __name__ == "__main__":  # smoke: show which services have keys, never print the keys
    for svc in ["APIFY_API_KEY", "FIRECRAWL_API_KEY", "SCRAPING_ANT_API_KEY", "OPENAI_API_KEY", "EXA_API_KEY"]:
        n = len(get_keys(svc, required=False))
        print(f"{svc}: {n} key(s)")
