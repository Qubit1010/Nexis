#!/usr/bin/env python3
"""Export a lean, private team clone of Nexis (the `nexis-team` repo).

Copies an allowlist of skills, shared tools, company docs and projects from this repo (and from
gitignored folders on disk) into a staging tree, applies mechanical scrubs for Aleem-specific
paths/emails, applies a few exact-string patches, and reports anything personal that is left.

It only ever writes inside the destination. Team-authored files (CLAUDE.md, rules, guides,
setup scripts, templates) are NOT managed here and are never overwritten, except the skill and
project folders below, which are re-copied on every run. Edits made by hand inside an exported
skill are lost when that skill is re-exported (use --skills NAME to limit the blast radius).

    python scripts/build_team_repo.py --dest ../nexis-team --dry-run
    python scripts/build_team_repo.py --dest ../nexis-team
    python scripts/build_team_repo.py --dest ../nexis-team --skills seo-onpage research
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VAULT_SRC = Path(r"C:\Users\qubit\OneDrive\Documents\agency-brain")

ROSTER = {
    "core": """seo-advisor seo-foundation seo-onpage seo-technical seo-authority-ai meeting-insights
        content-advisor content-engine content-strategy content-production copy-conversion
        copywriting-advisor social-media-advisor client-content-creator blog-writer blog-images
        linkedin-infographic-studio instagram-carousel-studio image-prompt-generator
        strategic-foundation to-markdown skill-creator claude-advisor brain-sync session-closeout
        playwright-cli notebooklm""",
    "sales": "upwork-proposal-studio upwork-reply-drafter upwork-advisor sales-playbook discovery-call-prep",
    "leadgen": """research web-scraper lead-generator leads-to-crm website-audit-system
        facebook-lead-nav free-tool-scout free-for-dev-scout selfhosted-scout api-scout""",
    # proposal-generator is deliberately absent: it deploys to Aleem's Vercel/Supabase and takes
    # payment through his Payoneer, so it needs a team-ized redesign before anyone else uses it.
    "delivery": """client-onboarding-workflow case-study-generator brand-strategy
        brand-voice brand-visual branding-advisor""",
    "dev": "developer-advisor senior-architect senior-backend senior-frontend code-reviewer ui-ux-pro-max canvas-design",
    # Open-source bounty work (Expensify/App). Added 2026-10-10 at the founder's request.
    "extras": "expensify-contributor",
}
SKILLS = [s for group in ROSTER.values() for s in group.split()]

SKIP_PARTS = {".impeccable", "__pycache__", "node_modules", ".cache", "results", ".folder_id", ".git",
              "portfolio-local-use"}  # licensed webfont binaries; the brand kit says keep them out of shared archives
SKIP_SUFFIX = {".pyc", ".log", ".err"}
CATALOG_SKILLS = {"free-tool-scout", "free-for-dev-scout", "selfhosted-scout", "api-scout"}
KEEP_EVALS = {"skill-creator"}
# _research files a skill reads at runtime or cites (everything else under _research is dropped,
# except sources.json for every skill).
KEEP_RESEARCH = {"expensify-contributor": {"measurements.json", "queries.md"}}
# SKILL.md rewritten by hand for the team repo; a re-export keeps the team's copy.
TEAM_REWRITTEN = {"brain-sync", "session-closeout"}
NO_PDF = {"claude-advisor"}
MAX_BYTES = 5 * 1024 * 1024

TOOLS = ["tools/exa", "tools/gdocs"]

AGENCY_FILES = (
    [f"agency/{n}" for n in (
        "08-audience-persona.md", "09-seo-foundation.md",
        "10-seo-onpage.md", "11-seo-technical.md", "12-seo-authority-ai.md", "13-brand-strategy.md",
        "14-brand-voice.md", "15-brand-visual-identity.md", "16-brand-guidelines.md",
        "17-conversion-copy.md", "18-content-strategy.md", "19-social-media-strategy.md",
        "20-website-copy-audit.md", "22-content-engine.md",   # 07 (founder self-assessment) and 21 (personal blog) are withheld
        "icp-agencies.md", "icp-geography.md", "icp-individuals.md", "nexuspoint-positioning.md",
        "pricing-and-packages.md", "white-label-partnership-model.md")]
)

# Identity files only (the full kit is 74 MB of print applications, QA renders and a font zip).
KIT = "brand-assets/nexuspoint-soft-fold-brand-kit-2026-10-02"
BRAND_FILES = [f"{KIT}/{n}" for n in ("README.md", "brand-guide.md", "brand-guide.pdf",
                                      "brand-tokens.css", "brand-tokens.json")]
BRAND_DIRS = [f"{KIT}/logos", f"{KIT}/fonts", f"{KIT}/templates", "brand-assets/Old/logos"]
# Outside this repo: the white logo the landing build reads. Lands inside brand-assets/Old/logos.
EXTRA_COPIES = [(Path(r"C:\Users\qubit\OneDrive\Documents\Automations\Website-Creator\Projects\nexuspoint\public\White-Logo-T.png"),
                 "brand-assets/Old/logos/White-Logo-T.png")]

BRAIN_SOP = [("references/sops/nexis-blueprint/build-a-second-brain.md",
              "brain-template/skills/build-a-second-brain.md")]

# Copied only when the destination file is missing (team-owned afterwards).
SEED_ONCE = [("scripts/sync_agents_mirror.py", "scripts/sync_agents_mirror.py")]

TEXT_SUFFIX = {".md", ".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".sh", ".json", ".yaml", ".yml",
               ".txt", ".html", ".j2", ".css", ".toml", ".csv", ".sql", ".ps1", ".cmd", ".bat", ".example"}

# ── mechanical scrubs ─────────────────────────────────────────────────────────
SEP = r"[\\/]+"
NEXIS_RE = re.compile(
    r"(?:[A-Za-z]:|/[a-z])" + SEP + r"Users" + SEP + r"qubit" + SEP + r"OneDrive" + SEP + r"Documents"
    + SEP + r"Automations" + SEP + r"Nexis(" + SEP + r")?", re.I)
VAULT_RE = re.compile(
    r"(?:[A-Za-z]:|/[a-z])" + SEP + r"Users" + SEP + r"qubit" + SEP + r"OneDrive" + SEP + r"Documents"
    + SEP + r"agency-brain", re.I)
PYEXE_RE = re.compile(r"[A-Za-z]:" + SEP + r"Users" + SEP + r"qubit" + SEP + r"AppData" + SEP + r"Local" + SEP
                      + r"Programs" + SEP + r"Python" + SEP + r"Python\d+" + SEP + r"python\.exe", re.I)
NLM_RE = re.compile(r"[A-Za-z]:" + SEP + r"Users" + SEP + r"qubit" + SEP + r"AppData" + SEP + r"Local" + SEP
                    + r"Programs" + SEP + r"Python" + SEP + r"Python\d+" + SEP + r"Scripts" + SEP
                    + r"notebooklm\.exe", re.I)
HOME_RE = re.compile(r"[A-Za-z]:" + SEP + r"Users" + SEP + r"qubit(?=[\\/]|\b)", re.I)
LITERALS = [
    ("tell Aleem rather than editing it", "fix the key name in your .env"),
    ("Worth telling Aleem.", "Fix the key name in your .env."),
    ("tell Aleem", "tell the project owner"),
    ("hassanaleem86@gmail.com", "<your-google-account>"),
    ("hkaleem609@gmail.com", "<your-google-account>"),
    ("gmail-mcp-483215", "<your-gcp-project>"),
]


NOTEBOOK_BANNER = (
    "> **Team repo note.** The notebook IDs and CLI paths in this file belong to the founder's NotebookLM "
    "account and are not reachable from yours. Treat the file as the recipe: build your own notebook with "
    "`.claude/skills/notebooklm/references/research-corpus-pipeline.md`, substitute your IDs, or skip the "
    "live query and answer from the local `references/`.\n\n"
)


def scrub_text(text: str) -> str:
    text = NEXIS_RE.sub(lambda m: "" if m.group(1) else ".", text)
    text = VAULT_RE.sub("$OBSIDIAN_VAULT_PATH", text)
    text = PYEXE_RE.sub("python", text)
    text = NLM_RE.sub("notebooklm", text)
    text = HOME_RE.sub("~", text)
    for old, new in LITERALS:
        text = text.replace(old, new)
    return text


# ── exact-string patches (path relative to dest, old, new) ────────────────────
PATCHES = [
    (".claude/skills/brain-sync/scripts/sync_vault.py",
     'VAULT = Path(os.environ.get("OBSIDIAN_VAULT_PATH")\n             or r"$OBSIDIAN_VAULT_PATH")',
     'VAULT = Path(os.environ.get("OBSIDIAN_VAULT_PATH") or (NEXIS / "brain"))'),
    (".claude/skills/brain-sync/scripts/sync_vault.py",
     '            if p.name == "index.md":  # per-side navigation furniture, not shared knowledge\n                continue',
     '            if p.name == "index.md":  # per-side navigation furniture, not shared knowledge\n                continue\n'
     '            if any(part.startswith("_") for part in p.relative_to(ctx).parts):  # _templates etc.\n                continue'),
    (".claude/skills/brain-sync/scripts/sync_vault.py",
     "def cmd_schedule_weekly():\n",
     "def cmd_schedule_weekly():\n"
     "    if os.name != \"nt\":\n"
     "        print(f'Scheduling is Windows-only here. Add this to cron (crontab -e) or launchd instead:\\n"
     "30 9 * * 0 \"{sys.executable}\" \"{Path(__file__).resolve()}\" --maintain')\n"
     "        return\n"),
    # Descriptions must not route to skills that are not in the team repo.
    (".claude/skills/content-production/SKILL.md", "rendered video to reel-creator, landing pages", "landing pages"),
    (".claude/skills/developer-advisor/SKILL.md", "use senior-frontend, senior-backend or nexis-builder.",
     "use senior-frontend or senior-backend."),
    (".claude/skills/image-prompt-generator/SKILL.md",
     "Instagram carousels to instagram-carousel-studio, 9:16 frames to shorts-creator, SVG diagrams",
     "Instagram carousels to instagram-carousel-studio, SVG diagrams"),
    (".claude/skills/instagram-carousel-studio/SKILL.md", "asks every run for Aleem's brand palette",
     "asks every run for the brand palette"),
    (".claude/skills/instagram-carousel-studio/SKILL.md",
     " A named template goes to carousel, a single image to image-prompt-generator.",
     " A single image goes to image-prompt-generator."),
    (".claude/skills/linkedin-infographic-studio/SKILL.md", "asks every run for Aleem's brand palette",
     "asks every run for the brand palette"),
    (".claude/skills/linkedin-infographic-studio/SKILL.md",
     " A named template goes to linkedin-infographics, a non-infographic image to image-prompt-generator.",
     " A non-infographic image goes to image-prompt-generator."),
    (".claude/skills/social-media-advisor/SKILL.md", "for Aleem's own posting, content-engine or post-creator.",
     "for the posting copy itself, content-engine."),
    (".claude/skills/upwork-proposal-studio/SKILL.md",
     "; a signable proposal for a direct (non-Upwork) client goes to proposal-generator.", "."),
    (".claude/skills/client-content-creator/SKILL.md", "Use this skill whenever Aleem:", "Use this skill whenever the user:"),
    (".claude/skills/facebook-lead-nav/scripts/preflight.mjs",
     '--profile "C:\\\\Users\\\\Aleem\\\\fb-automation-profile"', '--profile "~/fb-automation-profile"'),
    # expensify-contributor: per-person settings instead of the founder's machine.
    (".claude/skills/expensify-contributor/scripts/repo.py",
     'os.environ.get("EXPENSIFY_REPO_PATH", r"C:\\dev\\expensify-app")',
     'os.environ.get("EXPENSIFY_REPO_PATH", str(Path.home() / "dev" / "expensify-app"))'),
    (".claude/skills/expensify-contributor/references/environment-setup.md",
     "Clones to `C:\\dev\\expensify-app` by default", "Clones to `~/dev/expensify-app` by default"),
    (".claude/skills/expensify-contributor/scripts/triage.py", "import json\nimport re\n", "import json\nimport os\nimport re\n"),
    (".claude/skills/expensify-contributor/scripts/triage.py",
     "    # 5. Can it be reproduced without a Mac? This is an Aleem-specific constraint until Mac access\n"
     "    #    is arranged, and it is a hard practical limit rather than a preference.\n"
     "    m = PLATFORM_ONLY.match(title)\n"
     "    if m and m.group(1).lower().replace(\" \", \"\") in (\"ios\", \"macos\", \"desktop\"):",
     "    # 5. Can it be reproduced without a Mac? A hard practical limit, not a preference. Set\n"
     "    #    EXPENSIFY_HAS_MAC=1 in .env if you have Mac access and iOS/macOS/desktop issues are in scope.\n"
     "    m = PLATFORM_ONLY.match(title)\n"
     "    has_mac = os.environ.get(\"EXPENSIFY_HAS_MAC\", \"\").lower() in (\"1\", \"true\", \"yes\")\n"
     "    if m and not has_mac and m.group(1).lower().replace(\" \", \"\") in (\"ios\", \"macos\", \"desktop\"):"),
    (".claude/skills/expensify-contributor/scripts/watchlist.py",
     "the tester has and Aleem does not.", "the tester has and you may not."),
    (".claude/skills/expensify-contributor/scripts/watchlist.py",
     "reduced to what Aleem can actually test on Windows.", "reduced to what can be tested without a Mac."),
    # Outreach must not be written, or signed, as Aleem when a teammate runs it.
    (".claude/skills/leads-to-crm/scripts/messages.py",
     "You write the opening outreach message for Aleem Ul Hassan, founder of an AI \\\nautomation studio.",
     "You write the opening outreach message for the sender, a member of an AI \\\nautomation studio."),
    (".claude/skills/leads-to-crm/scripts/messages.py",
     "This is a DRAFT for Aleem to review", "This is a DRAFT for the sender to review"),
    (".claude/skills/leads-to-crm/scripts/messages.py",
     "lead in Aleem's own CRM", "lead in the sender's own CRM"),
    (".claude/skills/website-audit-system/scripts/generate_hook_email.py",
     "cold outreach hook email for NexusPoint (Aleem's agency).",
     "cold outreach hook email for NexusPoint (an AI automation and web agency)."),
    (".claude/skills/website-audit-system/scripts/generate_hook_email.py",
     'Close with exactly: "- Aleem, NexusPoint"',
     "Close with exactly: \"- {os.environ.get('OUTREACH_SENDER_NAME', 'Your Name')}, NexusPoint\""),
    (".claude/skills/sales-playbook/scripts/convo.py",
     '_SELF_NAMES = {"aleem", "aleem ul hassan", "aleem hassan"}',
     '# Set SELF_NAMES="your name,your handle" so your own turns are not counted as the prospect\'s.\n'
     '_SELF_NAMES = {n.strip().lower() for n in\n'
     '               os.environ.get("SELF_NAMES", "aleem,aleem ul hassan,aleem hassan").split(",") if n.strip()}'),
    (".claude/skills/facebook-lead-nav/scripts/preflight.mjs",
     "import { existsSync } from 'node:fs';",
     "import { existsSync } from 'node:fs';\nimport { homedir } from 'node:os';\nimport { join } from 'node:path';"),
    (".claude/skills/facebook-lead-nav/scripts/preflight.mjs",
     "process.env.FB_AUTOMATION_PROFILE || 'C:\\\\Users\\\\Aleem\\\\fb-automation-profile'",
     "process.env.FB_AUTOMATION_PROFILE || join(homedir(), 'fb-automation-profile')"),
    (".claude/skills/content-engine/scripts/log_post.py",
     'SHEET_ID = "1TwAuLDKak3hpPWqlojpNL_OTsUyCOBaAVjRRncOpb9Q"',
     'def _load_dotenv():\n'
     '    for base in Path(__file__).resolve().parents:\n'
     '        env = base / ".env"\n'
     '        if env.is_file():\n'
     '            for line in env.read_text(encoding="utf-8").splitlines():\n'
     '                k, sep, v = line.partition("=")\n'
     '                if sep and k.strip() and not k.lstrip().startswith("#"):\n'
     '                    os.environ.setdefault(k.strip(), v.strip().strip("\\"\'"))\n'
     '            return\n\n\n'
     '_load_dotenv()\n'
     'SHEET_ID = os.environ.get("CONTENT_LOG_SHEET_ID", "")\n'
     'if not SHEET_ID:\n'
     '    sys.exit("CONTENT_LOG_SHEET_ID is not set. Put the Google Sheet ID of your content log in .env "\n'
     '             "(see .env.example) before using log_post.py.")'),
]

# (path relative to dest, regex, replacement) for lines whose scrubbed form is awkward to match exactly
REGEX_PATCHES = [
    ("projects/nexuspoint-quetta-landing/build.py",
     r'LOGO_WHITE = Path\(r"[^"]*White-Logo-T\.png"\)',
     'LOGO_WHITE = REPO / "brand-assets" / "Old" / "logos" / "White-Logo-T.png"'),
]

LEFTOVER_RE = re.compile(r"qubit|OneDrive|hassanaleem|hkaleem|gmail-mcp|1TwAuL|13RiOJ", re.I)
ALEEM_RE = re.compile(r"aleem", re.I)


def git_files(rel: str) -> list[str]:
    out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "-z", "--", rel],
                         cwd=ROOT, capture_output=True, check=True).stdout
    return [p for p in out.decode("utf-8").split("\0") if p]


class Exporter:
    def __init__(self, dest: Path, dry: bool):
        self.dest, self.dry = dest, dry
        self.written: list[Path] = []
        self.skipped_big: list[str] = []
        self.bytes = 0

    def put(self, src: Path, rel: str) -> None:
        dst = self.dest / rel
        if src.name.startswith(".env") and src.name != ".env.example":
            return  # secrets never travel
        size = src.stat().st_size
        if size > MAX_BYTES:
            self.skipped_big.append(f"{rel} ({size / 1048576:.1f} MB)")
            return
        self.bytes += size
        self.written.append(dst)
        if self.dry:
            return
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix.lower() in TEXT_SUFFIX or src.name.startswith(".env"):
            try:
                text = src.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                shutil.copy2(src, dst)
                return
            dst.write_text(scrub_text(text), encoding="utf-8", newline="")
        else:
            shutil.copy2(src, dst)

    # skills ---------------------------------------------------------------
    def skill(self, name: str) -> None:
        base = f".claude/skills/{name}"
        if not (ROOT / base).is_dir():
            print(f"  ! missing skill: {name}")
            return
        target = self.dest / base
        kept = None
        if name in TEAM_REWRITTEN and (target / "SKILL.md").is_file():
            kept = (target / "SKILL.md").read_bytes()
        if not self.dry and target.exists():
            shutil.rmtree(target)
        files = set(git_files(base))
        if name in CATALOG_SKILLS:
            for p in (ROOT / base / "catalog").glob("*"):
                if p.is_file():
                    files.add(f"{base}/catalog/{p.name}")
        for f in sorted(files):
            rel = f[len(base) + 1:]
            parts = Path(rel).parts
            if any(part in SKIP_PARTS for part in parts):
                continue
            if Path(rel).suffix.lower() in SKIP_SUFFIX:
                continue
            if parts[0] == "_research" and rel != "_research/sources.json" \
                    and Path(rel).name not in KEEP_RESEARCH.get(name, ()):
                continue
            if parts[0] == "evals" and name not in KEEP_EVALS:
                continue
            if parts[0].endswith("-workspace"):
                continue
            if Path(rel).suffix.lower() == ".pdf" and (name in NO_PDF or parts[0] == "catalog"):
                continue
            src = ROOT / f
            if src.is_file():
                self.put(src, f)
        if kept is not None and not self.dry:
            (target / "SKILL.md").write_bytes(kept)
        nb = target / "references" / "notebook-live-query.md"
        if nb.is_file() and not self.dry:
            text = nb.read_text(encoding="utf-8")
            if "Team repo note" not in text:
                head, sep, rest = text.partition("\n")
                nb.write_text(head + sep + "\n" + NOTEBOOK_BANNER + rest, encoding="utf-8", newline="")

    def tree(self, rel: str) -> None:
        for f in sorted(git_files(rel)):
            if any(part in SKIP_PARTS for part in Path(f).parts):
                continue
            src = ROOT / f
            if src.is_file():
                self.put(src, f)

    def files(self, rels: list[str]) -> None:
        for rel in rels:
            src = ROOT / rel
            if src.is_file():
                self.put(src, rel)
            else:
                print(f"  ! missing: {rel}")

    def walk_project(self, name: str, skip_dirs: set[str], skip_files: set[str] = frozenset(),
                     skip_suffix: set[str] = frozenset(), skip_rel: tuple[str, ...] = ()) -> None:
        base = ROOT / "projects" / name
        for p in sorted(base.rglob("*")):
            if not p.is_file():
                continue
            rel = p.relative_to(base).as_posix()
            if any(part in skip_dirs for part in p.relative_to(base).parts):
                continue
            if p.name in skip_files or p.suffix.lower() in skip_suffix:
                continue
            if any(rel == s or rel.startswith(s.rstrip("/") + "/") for s in skip_rel):
                continue
            if (self.dest / "projects" / name / rel).exists():
                continue  # project files are copy-once: the team repo owns them after the first export
            self.put(p, f"projects/{name}/{rel}")

    def brand(self) -> None:
        self.files(BRAND_FILES)
        for rel in BRAND_DIRS:
            # git-visible files only: the kit keeps licensed font binaries untracked on purpose
            for f in sorted(git_files(rel)):
                if any(part in SKIP_PARTS for part in Path(f).parts):
                    continue
                src = ROOT / f
                if src.is_file():
                    self.put(src, f)
        for src, rel in EXTRA_COPIES:
            if src.is_file():
                self.put(src, rel)
            else:
                print(f"  ! missing extra copy: {src}")

    def projects(self) -> None:
        common = {"node_modules", ".next", ".vercel", "__pycache__", ".impeccable", "dist", "qa", ".git"}
        self.walk_project(
            "quetta-local-market", common | {"build", "deliverables"},
            skip_suffix={".log", ".xlsx", ".pptx", ".docx", ".pdf"}, skip_rel=())
        self.walk_project("nexuspoint-quetta-landing", common)
        self.walk_project(
            "nexuspoint-demo", common | {"snapshots"},
            skip_files={".env.local", "next-env.d.ts", "tsconfig.tsbuildinfo"}, skip_rel=("tests/qa",))

    def patches(self) -> None:
        if self.dry:
            return
        for rel, old, new in PATCHES:
            path = self.dest / rel
            if not path.is_file():
                print(f"  ! patch target missing: {rel}")
                continue
            text = path.read_text(encoding="utf-8")
            if new in text:
                continue  # already applied (matters when `old` is a prefix of `new`, e.g. inserted imports)
            if old not in text:
                print(f"  ! patch no longer matches (already applied or source changed): {rel}")
                continue
            path.write_text(text.replace(old, new, 1), encoding="utf-8", newline="")
            print(f"  patched {rel}")
        for rel, pattern, new in REGEX_PATCHES:
            path = self.dest / rel
            if not path.is_file():
                print(f"  ! regex patch target missing: {rel}")
                continue
            text = path.read_text(encoding="utf-8")
            text2, n = re.subn(pattern, lambda m: new, text, count=1)
            if n:
                path.write_text(text2, encoding="utf-8", newline="")
                print(f"  regex-patched {rel}")
            else:
                print(f"  ! regex patch no longer matches: {rel}")

    def report(self) -> None:
        leftovers: dict[str, int] = {}
        aleem: dict[str, int] = {}
        if not self.dry:
            for p in self.written:
                if not p.is_file() or p.suffix.lower() not in TEXT_SUFFIX:
                    continue
                try:
                    t = p.read_text(encoding="utf-8")
                except UnicodeDecodeError:
                    continue
                n = len(LEFTOVER_RE.findall(t))
                a = len(ALEEM_RE.findall(t))
                rel = p.relative_to(self.dest).as_posix()
                if n:
                    leftovers[rel] = n
                if a:
                    aleem[rel] = a
        report = {
            "files": len(self.written), "mb": round(self.bytes / 1048576, 1),
            "skipped_over_5mb": self.skipped_big,
            "hard_leftovers (paths/emails/ids)": leftovers,
            "files_mentioning_aleem": len(aleem),
            "aleem_in_skill_md_or_scripts": {k: v for k, v in aleem.items()
                                             if k.endswith("SKILL.md") or "/scripts/" in k},
        }
        out = self.dest.parent / "nexis-team.export-report.json"
        if not self.dry:
            out.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(json.dumps({k: v for k, v in report.items() if k != "aleem_in_skill_md_or_scripts"}, indent=2))
        print(f"aleem mentions in SKILL.md/scripts: {len(report['aleem_in_skill_md_or_scripts'])} files")
        if not self.dry:
            print(f"full report: {out}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", default=str(ROOT.parent / "nexis-team"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skills", nargs="*", help="Re-export only these skills (skips tools/agency/projects).")
    args = ap.parse_args()

    dest = Path(args.dest).resolve()
    if dest == ROOT or ROOT in dest.parents:
        sys.exit("Refusing to write inside the source repo.")
    ex = Exporter(dest, args.dry_run)

    if args.skills:
        for s in args.skills:
            ex.skill(s)
    else:
        for s in SKILLS:
            ex.skill(s)
        for t in TOOLS:
            ex.tree(t)
        ex.files(AGENCY_FILES)
        ex.files([src for src, _ in BRAIN_SOP])
        ex.brand()
        ex.projects()
        for src, dst in SEED_ONCE:
            if not (dest / dst).exists():
                ex.put(ROOT / src, dst)
    ex.patches()
    # relocate the brain SOP copy (put() mirrors the source path)
    if not args.dry_run and not args.skills:
        for src, dst in BRAIN_SOP:
            moved = dest / src
            if moved.is_file():
                (dest / dst).parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(moved), str(dest / dst))
        refs = dest / "references"
        for d in sorted((p for p in refs.rglob("*") if p.is_dir()), reverse=True):
            if not any(d.iterdir()):
                d.rmdir()
        if refs.is_dir() and not any(refs.iterdir()):
            refs.rmdir()
    ex.report()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
