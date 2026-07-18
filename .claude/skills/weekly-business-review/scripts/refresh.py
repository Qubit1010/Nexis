"""One-command refresh: regenerate the week's snapshot, then redeploy the dashboard.

    python refresh.py                  # current week -> deploy
    python refresh.py --week 2026-07-13  # any week -> deploy

Runs entirely on this machine (gws/Supabase auth lives here, not on Vercel) --
this is the "click a button" step for a human, just a single command instead
of two.
"""
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
DASHBOARD_DIR = SCRIPTS_DIR.parents[3] / "projects" / "weekly-business-review"


def main():
    week_args = sys.argv[1:]  # forwarded as-is to wbr.py, e.g. --week 2026-07-13

    print("== 1/2  wbr.py: pulling fresh data ==")
    subprocess.run([sys.executable, str(SCRIPTS_DIR / "wbr.py"), *week_args], check=True)

    print("\n== 2/2  vercel deploy --prod ==")
    subprocess.run("npx vercel deploy --prod --yes", cwd=DASHBOARD_DIR, shell=True, check=True)

    print("\nDone -- the live dashboard now reflects this week's data.")


if __name__ == "__main__":
    main()
