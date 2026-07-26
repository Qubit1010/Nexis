"""Re-authenticate the NotebookLM CLI.

Two modes, run in this order:

    python relogin.py open      # opens the browser, blocks until you kill it
    python relogin.py capture   # reopens the profile and saves the session

Why two commands instead of one: the sign-in lives in the persistent browser profile
on disk (`~/.notebooklm/browser_profile`), and `storage_state` can be read back from
it in a completely separate run. So there is no need to coordinate "user has finished
signing in" inside a single process. The old flow tried to, via a polled signal file,
and failed twice over: the browser process was reaped as soon as the launching shell
returned, and the sign-in check missed because NotebookLM redirects through several
hostnames before settling.

IMPORTANT: run `open` as a BACKGROUND task (`run_in_background: true`). A foreground
call gets torn down when it returns and takes the browser with it.
"""
import json
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

STORAGE = Path.home() / ".notebooklm" / "profiles" / "default" / "storage_state.json"
PROFILE = Path.home() / ".notebooklm" / "browser_profile"
URL = "https://notebooklm.google.com/"


def _context(p):
    return p.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE),
        headless=False,
        no_viewport=True,
        args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
    )


def open_browser():
    """Hold a signed-in-able window open until the caller kills this process."""
    STORAGE.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = _context(p)
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        page.bring_to_front()
        print("BROWSER OPEN. Sign in, then run: relogin.py capture", flush=True)
        print("Window title is 'Google Chrome for Testing' - NOT your normal Chrome.",
              flush=True)
        while True:                            # caller kills us once sign-in is done
            time.sleep(5)


def capture():
    """Reopen the profile and persist its cookies as storage_state.json."""
    STORAGE.parent.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = _context(p)
        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(URL, wait_until="domcontentloaded", timeout=60000)
        try:
            page.wait_for_load_state("networkidle", timeout=25000)
        except Exception:
            pass                               # best-effort; the URL check decides
        url = page.url
        print(f"landed on: {url}")
        if "accounts.google.com" in url or "/signin" in url.lower():
            print("NOT SIGNED IN - profile bounced to the Google login page")
            browser.close()
            return 1
        state = browser.storage_state()
        STORAGE.write_text(json.dumps(state), encoding="utf-8")
        print(f"saved {len(state.get('cookies', []))} cookies -> {STORAGE}")
        browser.close()
        return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "open":
        open_browser()
    elif cmd == "capture":
        sys.exit(capture())
    else:
        sys.exit(__doc__)
