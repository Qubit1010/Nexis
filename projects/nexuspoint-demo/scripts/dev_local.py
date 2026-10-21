"""Run `npm run dev` with the repo .env loaded (Supabase and LLM keys), without copying secrets into the app folder."""
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
env = dict(os.environ)
for line in (ROOT.parents[1] / ".env").read_text(encoding="utf-8").splitlines():
    if "=" in line and not line.strip().startswith("#"):
        k, v = line.strip().split("=", 1)
        env.setdefault(k, v.strip().strip('"').strip("'"))
raise SystemExit(subprocess.call("npm run dev", cwd=ROOT, env=env, shell=True))
