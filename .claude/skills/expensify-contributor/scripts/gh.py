"""Thin wrapper over the authenticated `gh` CLI.

Every other script in this skill talks to GitHub through here for one reason: a failed API call and
an empty result must never look the same. If `gh` errors out (rate limit, expired auth, network),
callers get an exception. If the query genuinely returns nothing, callers get an empty list. Code
that cannot tell those apart will happily report "no competition on this issue" when what actually
happened is that the token expired, and you will find out at the worst possible moment.
"""

import json
import shutil
import subprocess

REPO = "Expensify/App"


class GhError(RuntimeError):
    """The gh CLI failed. This is not the same as 'the query returned nothing'."""


def _require_gh() -> str:
    path = shutil.which("gh")
    if not path:
        raise GhError(
            "The GitHub CLI (gh) is not on PATH. Install it from https://cli.github.com and run "
            "`gh auth login`. This skill reads the Expensify repo through gh so it inherits your "
            "existing authentication instead of managing a token of its own."
        )
    return path


def api(path: str, jq: str | None = None, paginate: bool = False):
    """Call `gh api <path>`, optionally with a --jq filter. Raises GhError on failure."""
    cmd = [_require_gh(), "api", path]
    if paginate:
        cmd.append("--paginate")
    if jq:
        cmd += ["--jq", jq]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()
        if "rate limit" in stderr.lower():
            raise GhError(f"GitHub rate limit hit. Wait and retry.\n{stderr}")
        if "authentication" in stderr.lower() or "HTTP 401" in stderr:
            raise GhError(f"gh is not authenticated. Run `gh auth login`.\n{stderr}")
        raise GhError(f"gh api {path} failed (exit {proc.returncode}):\n{stderr}")
    out = (proc.stdout or "").strip()
    if not out:
        return [] if jq else None
    if jq:
        # --jq streams one JSON value per line when the filter yields multiple results.
        lines = [ln for ln in out.splitlines() if ln.strip()]
        parsed = []
        for ln in lines:
            try:
                parsed.append(json.loads(ln))
            except json.JSONDecodeError:
                parsed.append(ln)
        return parsed[0] if len(parsed) == 1 and not path.startswith("search") else parsed
    return json.loads(out)


def issue(number: int) -> dict:
    return api(f"repos/{REPO}/issues/{number}")


def comments(number: int) -> list:
    out = api(f"repos/{REPO}/issues/{number}/comments?per_page=100")
    return out if isinstance(out, list) else []


def timeline(number: int) -> list:
    out = api(f"repos/{REPO}/issues/{number}/timeline?per_page=100")
    return out if isinstance(out, list) else []


def search_issues(query: str, per_page: int = 30) -> list:
    q = query.replace(" ", "+")
    out = api(f"search/issues?q={q}&per_page={per_page}")
    if isinstance(out, dict):
        return out.get("items", [])
    return []


def labels_of(iss: dict) -> set:
    return {lbl["name"] for lbl in iss.get("labels", [])}


def help_wanted_at(number: int) -> str | None:
    """Timestamp the Help Wanted label was applied, or None if it has not been."""
    for ev in timeline(number):
        if ev.get("event") == "labeled" and (ev.get("label") or {}).get("name") == "Help Wanted":
            return ev.get("created_at")
    return None
