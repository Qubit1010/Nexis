"""Tiny stdlib HTTP helpers so the service clients carry zero extra dependencies."""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


class HttpError(RuntimeError):
    pass


# Some endpoints (Jina via Cloudflare) 403 the default python-urllib agent (error 1010).
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"


def _read(resp) -> str:
    return resp.read().decode("utf-8", "replace")


def post_json(url: str, payload: dict, headers: dict | None = None, timeout: int = 25) -> Any:
    data = json.dumps(payload).encode("utf-8")
    hdrs = {"Content-Type": "application/json", "Accept": "application/json",
            "User-Agent": UA, **(headers or {})}
    req = urllib.request.Request(url, data=data, headers=hdrs, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(_read(resp))
    except urllib.error.HTTPError as e:
        raise HttpError(f"POST {url} -> {e.code}: {_read(e)[:300]}") from e
    except urllib.error.URLError as e:
        raise HttpError(f"POST {url} failed: {e.reason}") from e


# A key that is out of credit/quota, vs a genuinely bad request. Serper says 400 "Not enough credits",
# Tavily says 432 "exceeds your plan's set usage limit"; 401/403/429 cover revoked + rate-limited keys.
_EXHAUSTED = ("not enough credits", "usage limit", "quota", "exceeded", "-> 401", "-> 403", "-> 429", "-> 432")


def with_key_rotation(keys: list[str], call):
    """Run call(key) over numbered keys, advancing only when one is exhausted. Raises the LAST error
    if every key is spent, so the caller still sees a real reason. Mirrors web-scraper's engine rotation.
    """
    last: Exception | None = None
    for i, key in enumerate(keys):
        try:
            return call(key)
        except HttpError as e:
            if not any(m in str(e).lower() for m in _EXHAUSTED):
                raise                      # a real error (bad query, malformed payload) -- don't burn keys
            last = e
            if i + 1 < len(keys):
                import sys
                print(f"[rotate] key {i + 1} exhausted, trying key {i + 2}", file=sys.stderr)
    raise last if last else HttpError("no API keys configured")


def get_text(url: str, headers: dict | None = None, timeout: int = 25) -> str:
    hdrs = {"User-Agent": UA, **(headers or {})}
    req = urllib.request.Request(url, headers=hdrs, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return _read(resp)
    except urllib.error.HTTPError as e:
        raise HttpError(f"GET {url} -> {e.code}: {_read(e)[:300]}") from e
    except urllib.error.URLError as e:
        raise HttpError(f"GET {url} failed: {e.reason}") from e


def get_json(url: str, headers: dict | None = None, timeout: int = 25) -> Any:
    hdrs = {"Accept": "application/json", **(headers or {})}
    return json.loads(get_text(url, hdrs, timeout))


def quote(value: str) -> str:
    return urllib.parse.quote(value, safe="")
