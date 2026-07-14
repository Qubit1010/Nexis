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
