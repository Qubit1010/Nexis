"""Load API keys from the repo-root .env (the standard Nexis location).

Mirrors tools/exa/exa_client.py key-loading so every client here reads the same .env
without anything needing to be exported by hand.
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
    return here.parents[3]  # .claude/skills/research/scripts -> repo root fallback


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
    """Return an API key by env var name, loading the .env first."""
    load_env()
    val = os.environ.get(name)
    if val:
        return val.strip()
    if required:
        raise SystemExit(f"{name} not found in environment or repo .env.")
    return None
