"""
brain-sync — Two-way mirror between this OS repo and its second-brain Obsidian vault.

Setup: set OBSIDIAN_VAULT_PATH (env / .claude/settings.local.json) to the vault's
absolute path. The repo root is derived from this file's location — no other config.

Scope (the shared-subset contract, see both CLAUDE.md files):
  context/**/*.md      two-way, last-writer-wins, .bak before overwrite
  decisions/log.md     two-way, append-only UNION MERGE (lossless, converges both sides)
Everything else (wiki/, raw/, clients/, live data, .env) never syncs.

Modes:
  python sync_vault.py --check              Drift report, both directions, no writes
  python sync_vault.py --push               Repo -> vault (+ decisions union merge)
  python sync_vault.py --pull               Vault -> repo (+ decisions union merge)
  python sync_vault.py --push --dry-run     Preview
  python sync_vault.py --maintain           Unattended weekly heartbeat: lossless converge
                                            (decisions merge + copy-missing both ways, never
                                            overwrite), then auto-commit the vault so the
                                            graphify post-commit hook rebuilds the graph.
                                            Logs to logs/brain-sync.log.
  python sync_vault.py --schedule-weekly    Register Windows Task Scheduler job (Sun 9am)
  python sync_vault.py --unschedule         Remove the scheduled job
  python sync_vault.py --ingest-status      Wiki staleness report (exit 1 = ingest overdue);
                                            --json for the machine-readable form
  python sync_vault.py --mark-ingested      Reset the staleness baseline (wiki/.ingest-state.json)
  python sync_vault.py --selftest           Run the built-in convergence check

Engine adapted from gdrive-sync/scripts/sync.py (MD5 skip-on-equal + mtime-newer
confirmed-by-md5), with the Drive API layer swapped for the local filesystem.
Deletions are reported, never propagated.
"""

import os
import re
import sys
import json
import shutil
import hashlib
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# NEXIS = the OS repo root (this file lives at .claude/skills/brain-sync/scripts/).
NEXIS = Path(__file__).resolve().parents[4]
# No default vault path: OBSIDIAN_VAULT_PATH must be set. The sentinel fails the
# existing "Vault not found" guard with a clear message instead of syncing into cwd.
VAULT = Path(os.environ.get("OBSIDIAN_VAULT_PATH") or "__OBSIDIAN_VAULT_PATH_NOT_SET__")

DECISIONS_KEY = "decisions/log.md"


def file_md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def scoped_files(root: Path) -> dict[str, Path]:
    """Relative-posix-path -> absolute path for every in-scope file under root."""
    out = {}
    ctx = root / "context"
    if ctx.exists():
        for p in sorted(ctx.rglob("*.md")):
            if p.name == "index.md":  # per-side navigation furniture, not shared knowledge
                continue
            out[p.relative_to(root).as_posix()] = p
    dec = root / "decisions" / "log.md"
    if dec.exists():
        out[DECISIONS_KEY] = dec
    return out


def fmt_mtime(path: Path) -> str:
    return datetime.fromtimestamp(path.stat().st_mtime).strftime("%Y-%m-%d %H:%M")


# ── decisions union merge ─────────────────────────────────────────────────────
def parse_log(text: str) -> tuple[str, list[str]]:
    """Split a decision log into (header, [entries]). Entries start with '['.
    Continuation lines (not starting with '[') attach to the previous entry."""
    if "---" in text:
        head, _, body = text.partition("---")
        header = head + "---"
    else:
        header, body = "", text
    entries = []
    for line in body.splitlines():
        if not line.strip():
            continue
        if line.lstrip().startswith("[") or not entries:
            entries.append(line.rstrip())
        else:
            entries[-1] += "\n" + line.rstrip()
    return header, entries


def merged_log(text_a: str, text_b: str) -> str:
    """Union of entries from both logs, stable-sorted by [YYYY-MM-DD] prefix.
    Lossless: every entry from either side survives."""
    header_a, entries_a = parse_log(text_a)
    header_b, entries_b = parse_log(text_b)
    header = header_a or header_b
    seen, union = set(), []
    for e in entries_a + entries_b:
        key = " ".join(e.split())  # whitespace-insensitive identity
        if key not in seen:
            seen.add(key)
            union.append(e)
    union.sort(key=lambda e: e[:12])  # stable: same-date entries keep insertion order
    return header.rstrip() + "\n\n" + "\n\n".join(union) + "\n"


def backup(path: Path):
    shutil.copy2(path, path.with_suffix(path.suffix + ".bak"))


def sync_decisions(dry: bool) -> str:
    """Converge decisions/log.md on BOTH sides to the union. Returns action taken."""
    a, b = NEXIS / DECISIONS_KEY, VAULT / DECISIONS_KEY
    if not a.exists() and not b.exists():
        return "missing on both sides"
    if not a.exists() or not b.exists():
        src, dst = (b, a) if not a.exists() else (a, b)
        if not dry:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
        return f"copied to {'repo' if dst == a else 'vault'} (missing there)"
    ta, tb = a.read_text(encoding="utf-8"), b.read_text(encoding="utf-8")
    merged = merged_log(ta, tb)
    changed = []
    for path, original in ((a, ta), (b, tb)):
        if merged != original:
            changed.append("repo" if path == a else "vault")
            if not dry:
                backup(path)
                path.write_text(merged, encoding="utf-8", newline="\n")
    return f"union-merged, updated: {', '.join(changed)}" if changed else "already converged"


# ── ingest staleness detector ─────────────────────────────────────────────────
# The mirror half (context/ + decisions/) is automated; the knowledge half
# (wiki/ + CRITICAL_FACTS.md) is Claude-driven and used to idle silently.
# Baseline = wiki/.ingest-state.json, written by --mark-ingested at each ingest.

def current_skills() -> list[str]:
    return sorted(p.parent.name for p in (NEXIS / ".claude" / "skills").glob("*/SKILL.md"))


def decision_dates() -> list[str]:
    dec = NEXIS / DECISIONS_KEY
    if not dec.exists():
        return []
    return re.findall(r"^\[(\d{4}-\d{2}-\d{2})\]", dec.read_text(encoding="utf-8"), re.M)


def ingest_status() -> dict:
    """How far the vault wiki lags behind the repo's knowledge. Falls back to
    wiki/log.md's newest date when no state file exists (then skill drift
    can't be measured, only decisions and age)."""
    baseline_skills, last_ingest, last_decision_seen = None, None, None
    state_path = VAULT / "wiki" / ".ingest-state.json"
    if state_path.exists():
        try:
            st = json.loads(state_path.read_text(encoding="utf-8"))
            last_ingest = st.get("date")
            baseline_skills = st.get("skill_folders")
            last_decision_seen = st.get("last_decision_date")
        except (json.JSONDecodeError, OSError):
            pass
    if last_ingest is None:
        log = VAULT / "wiki" / "log.md"
        if log.exists():
            dates = re.findall(r"^- \[(\d{4}-\d{2}-\d{2})\]", log.read_text(encoding="utf-8"), re.M)
            last_ingest = max(dates) if dates else None
        last_decision_seen = last_decision_seen or last_ingest

    skills = current_skills()
    new_skills = sorted(set(skills) - set(baseline_skills)) if baseline_skills is not None else []
    dates = decision_dates()
    new_decisions = (sum(1 for d in dates if d > last_decision_seen)
                     if last_decision_seen else len(dates))
    days = ((datetime.now().date() - datetime.strptime(last_ingest, "%Y-%m-%d").date()).days
            if last_ingest else None)
    # Stale = real knowledge drift, not one stray decision: any new skill,
    # a burst of decisions, or the 14-day hard backstop.
    stale = bool(new_skills) or new_decisions > 5 or days is None or days > 14
    return {"last_ingest": last_ingest, "days_since": days, "stale": stale,
            "new_skills": new_skills, "new_decisions": new_decisions}


def cmd_ingest_status(as_json: bool) -> int:
    s = ingest_status()
    if as_json:
        print(json.dumps(s))
        return 1 if s["stale"] else 0
    if s["stale"]:
        print(f"INGEST OVERDUE: {len(s['new_skills'])} new skill(s), {s['new_decisions']} new "
              f"decision(s) since last ingest {s['last_ingest']} ({s['days_since']}d ago)")
        for name in s["new_skills"]:
            print(f"  new skill: {name}")
        print("Run the brain-sync Ingest workflow (SKILL.md): distill into wiki/ + refresh "
              "CRITICAL_FACTS.md, then --mark-ingested.")
        return 1
    print(f"Ingest current — last {s['last_ingest']} ({s['days_since']}d ago), "
          f"{s['new_decisions']} decision(s) since.")
    return 0


def cmd_mark_ingested():
    """Reset the staleness baseline. Run as the last step of every ingest."""
    state = {"date": datetime.now().strftime("%Y-%m-%d"),
             "skill_folders": current_skills(),
             "last_decision_date": max(decision_dates(), default="")}
    p = VAULT / "wiki" / ".ingest-state.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(state, indent=1), encoding="utf-8")
    print(f"{p} updated: {len(state['skill_folders'])} skills, "
          f"last decision {state['last_decision_date']}")


# ── check ─────────────────────────────────────────────────────────────────────
def cmd_check(as_json: bool = False) -> int:
    nexis, vault = scoped_files(NEXIS), scoped_files(VAULT)
    nexis_only  = sorted(set(nexis) - set(vault))
    vault_only  = sorted(set(vault) - set(nexis))
    differ = []
    for rel in sorted(set(nexis) & set(vault)):
        if file_md5(nexis[rel]) != file_md5(vault[rel]):
            newer = "repo" if nexis[rel].stat().st_mtime > vault[rel].stat().st_mtime else "vault"
            differ.append((rel, newer))

    if as_json:
        in_sync = not (nexis_only or vault_only or differ)
        print(json.dumps({"in_sync": in_sync, "nexis_only": nexis_only, "vault_only": vault_only,
                          "differ": [{"file": rel, "newer": newer} for rel, newer in differ]}))
        return 0 if in_sync else 1

    if not (nexis_only or vault_only or differ):
        print("In sync — vault matches the repo for the scoped subset.")
        return 0
    if nexis_only:
        print(f"Repo-only ({len(nexis_only)}) — missing in vault (push to copy):")
        for rel in nexis_only:
            print(f"  {rel}")
    if vault_only:
        print(f"Vault-only ({len(vault_only)}) — missing in repo (pull to copy):")
        for rel in vault_only:
            print(f"  {rel}")
    if differ:
        print(f"Differ ({len(differ)}):")
        for rel, newer in differ:
            side = nexis if newer == "repo" else vault
            print(f"  {rel}  (newer: {newer}, {fmt_mtime(side[rel])})"
                  + ("  [union merge on push/pull]" if rel == DECISIONS_KEY else ""))
    print("\nRun --push (repo -> vault) or --pull (vault -> repo). decisions/log.md always union-merges.")
    return 1


# ── mirror ────────────────────────────────────────────────────────────────────
def cmd_mirror(direction: str, dry: bool):
    src_root, dst_root = (NEXIS, VAULT) if direction == "push" else (VAULT, NEXIS)
    src, dst = scoped_files(src_root), scoped_files(dst_root)
    stats = {"copied": 0, "updated": 0, "skipped": 0}
    prefix = "[DRY RUN] " if dry else ""

    print(f"{prefix}{direction}: {src_root.name} -> {dst_root.name}")
    print(f"  decisions/log.md: {sync_decisions(dry)}")

    for rel, spath in src.items():
        if rel == DECISIONS_KEY:
            continue
        dpath = dst_root / rel
        if dpath.exists():
            if file_md5(spath) == file_md5(dpath):
                stats["skipped"] += 1
                continue
            if not dry:
                backup(dpath)
                shutil.copy2(spath, dpath)
            stats["updated"] += 1
            print(f"  updated: {rel} (.bak written)")
        else:
            if not dry:
                dpath.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(spath, dpath)
            stats["copied"] += 1
            print(f"  copied: {rel}")

    orphans = sorted(set(dst) - set(src) - {DECISIONS_KEY})
    if orphans:
        print(f"  NOT deleted ({len(orphans)}) — exist only on target, remove by hand if intended:")
        for rel in orphans:
            print(f"    {rel}")
    print(f"{prefix}Done — copied: {stats['copied']}, updated: {stats['updated']}, skipped: {stats['skipped']}")
    if direction == "push" and (stats["copied"] or stats["updated"]) and not dry:
        print("Reminder: if evergreen knowledge changed, run the ingest step "
              "(distill into wiki/ + refresh CRITICAL_FACTS.md — see SKILL.md).")


# ── maintain (unattended weekly heartbeat) ────────────────────────────────────
def cmd_maintain():
    """Safe unattended converge + vault auto-commit (fires the graphify rebuild hook).
    Never overwrites a differing file — that judgment call stays with Claude/Aleem."""
    log_path = NEXIS / "logs" / "brain-sync.log"
    log_path.parent.mkdir(exist_ok=True)
    log = open(log_path, "a", encoding="utf-8")

    class Tee:
        def write(self, s):
            sys.__stdout__.write(s)
            log.write(s)
        def flush(self):
            sys.__stdout__.flush()
            log.flush()

    sys.stdout = Tee()
    print(f"\n===== brain-sync --maintain {datetime.now():%Y-%m-%d %H:%M} =====")

    print(f"decisions/log.md: {sync_decisions(dry=False)}")

    nexis, vault = scoped_files(NEXIS), scoped_files(VAULT)
    for rel in sorted(set(nexis) - set(vault) - {DECISIONS_KEY}):
        dst = VAULT / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(nexis[rel], dst)
        print(f"copied to vault: {rel}")
    for rel in sorted(set(vault) - set(nexis) - {DECISIONS_KEY}):
        dst = NEXIS / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(vault[rel], dst)
        print(f"copied to repo: {rel}")
    conflicts = [rel for rel in sorted(set(nexis) & set(vault))
                 if rel != DECISIONS_KEY and file_md5(nexis[rel]) != file_md5(vault[rel])]
    for rel in conflicts:
        print(f"CONFLICT (not touched): {rel} — run --check then --push/--pull from a session")

    # Knowledge-half heartbeat: the wiki can't be ingested unattended, but its
    # staleness must never be silent again (the 2026-06-20..07-11 idle).
    ing = ingest_status()
    if ing["stale"]:
        print(f"INGEST OVERDUE: {len(ing['new_skills'])} new skill(s), {ing['new_decisions']} "
              f"new decision(s) since {ing['last_ingest']} — run the ingest from a session")
    else:
        print(f"Ingest current (last {ing['last_ingest']})")

    git = ["git", "-C", str(VAULT)]
    dirty = subprocess.run(git + ["status", "--porcelain"], capture_output=True, text=True).stdout.strip()
    if dirty:
        subprocess.run(git + ["add", "-A"], capture_output=True, text=True)
        r = subprocess.run(git + ["commit", "-m", f"brain-sync weekly snapshot {datetime.now():%Y-%m-%d}"],
                           capture_output=True, text=True)
        print(r.stdout.strip() or r.stderr.strip())
        print("Vault committed — graphify post-commit hook is rebuilding the graph in the background.")
    else:
        print("Vault clean — nothing to commit, graph already current.")
    print(f"===== done ({'%d conflict(s)' % len(conflicts) if conflicts else 'ok'}) =====")


# ── schedule (adapted from gdrive-sync) ───────────────────────────────────────
# Per-repo task name so two OSes on one machine don't clobber each other's schedule.
TASK_NAME = f"{NEXIS.name}-BrainSync"

def cmd_schedule_weekly():
    # ponytail: plain /SC WEEKLY beats Task XML — gdrive-sync's WeeklyTrigger XML
    # is rejected by the Task Scheduler schema (never actually registered).
    tr = f'"{sys.executable}" "{Path(__file__).resolve()}" --maintain'
    result = subprocess.run(
        ["schtasks", "/Create", "/SC", "WEEKLY", "/D", "SUN", "/ST", "09:30",
         "/TN", TASK_NAME, "/TR", tr, "/F"],
        capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Scheduled weekly brain maintenance every Sunday 9:30am (Task: {TASK_NAME})")
    else:
        print(f"ERROR scheduling task: {result.stderr}")


def cmd_unschedule():
    result = subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
                            capture_output=True, text=True)
    print(f"Removed task '{TASK_NAME}'" if result.returncode == 0
          else f"Task not found or error: {result.stderr}")


# ── selftest ──────────────────────────────────────────────────────────────────
def selftest():
    import tempfile
    global NEXIS, VAULT
    real_n, real_v = NEXIS, VAULT
    tmp = Path(tempfile.mkdtemp(prefix="brainsync_"))
    try:
        NEXIS, VAULT = tmp / "nexis", tmp / "vault"
        for root in (NEXIS, VAULT):
            (root / "context").mkdir(parents=True)
            (root / "decisions").mkdir()
        hdr = "# Decision Log\n\n---\n"
        (NEXIS / DECISIONS_KEY).write_text(hdr + "\n[2026-01-01] DECISION: shared | R | C\n\n[2026-07-01] DECISION: nexis-only | R | C\n", encoding="utf-8")
        (VAULT / DECISIONS_KEY).write_text(hdr + "\n[2026-01-01] DECISION: shared | R | C\n\n[2026-06-01] DECISION: vault-only | R | C\n", encoding="utf-8")
        (NEXIS / "context/a.md").write_text("new version", encoding="utf-8")
        (VAULT / "context/a.md").write_text("old version", encoding="utf-8")
        (VAULT / "context/vault-note.md").write_text("vault only", encoding="utf-8")

        assert cmd_check() == 1, "drift must be detected"
        cmd_mirror("push", dry=False)

        merged = (NEXIS / DECISIONS_KEY).read_text(encoding="utf-8")
        assert merged == (VAULT / DECISIONS_KEY).read_text(encoding="utf-8"), "decisions must converge"
        for frag in ("shared", "nexis-only", "vault-only"):
            assert frag in merged, f"lost entry: {frag}"
        assert merged.index("2026-06-01") < merged.index("2026-07-01"), "entries must be date-sorted"
        assert (VAULT / "context/a.md").read_text(encoding="utf-8") == "new version"
        assert (VAULT / "context/a.md.bak").read_text(encoding="utf-8") == "old version", ".bak must hold old"
        assert (VAULT / "context/vault-note.md").exists(), "orphan must not be deleted"

        cmd_mirror("pull", dry=False)
        assert (NEXIS / "context/vault-note.md").read_text(encoding="utf-8") == "vault only"
        assert cmd_check() == 0, "must be in sync after push+pull"

        # ingest staleness detector: fresh baseline, then a new skill flips it
        (NEXIS / ".claude" / "skills" / "a").mkdir(parents=True)
        (NEXIS / ".claude" / "skills" / "a" / "SKILL.md").write_text("x", encoding="utf-8")
        cmd_mark_ingested()
        assert not ingest_status()["stale"], "fresh baseline must not be stale"
        (NEXIS / ".claude" / "skills" / "b").mkdir()
        (NEXIS / ".claude" / "skills" / "b" / "SKILL.md").write_text("x", encoding="utf-8")
        s = ingest_status()
        assert s["stale"] and s["new_skills"] == ["b"], "new skill folder must flip stale"
        print("\nSELFTEST PASS")
    finally:
        NEXIS, VAULT = real_n, real_v
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    ap = argparse.ArgumentParser(description="OS repo <-> second-brain vault sync")
    ap.add_argument("--check", action="store_true", help="Drift report, no writes")
    ap.add_argument("--push", action="store_true", help="repo -> vault")
    ap.add_argument("--pull", action="store_true", help="vault -> repo")
    ap.add_argument("--dry-run", action="store_true", help="Preview without writing")
    ap.add_argument("--maintain", action="store_true", help="Unattended converge + vault auto-commit")
    ap.add_argument("--schedule-weekly", action="store_true", help="Register weekly Task Scheduler job")
    ap.add_argument("--unschedule", action="store_true", help="Remove scheduled job")
    ap.add_argument("--ingest-status", action="store_true", help="Wiki staleness report (exit 1 = overdue)")
    ap.add_argument("--json", action="store_true", help="With --ingest-status/--check: machine-readable output")
    ap.add_argument("--mark-ingested", action="store_true", help="Reset the staleness baseline (last ingest step)")
    ap.add_argument("--selftest", action="store_true", help="Run built-in convergence check")
    args = ap.parse_args()

    if args.selftest:
        selftest(); return
    if args.schedule_weekly:
        cmd_schedule_weekly(); return
    if args.unschedule:
        cmd_unschedule(); return
    if not VAULT.exists():
        sys.exit(f"Vault not found: {VAULT} (set OBSIDIAN_VAULT_PATH)")
    if args.ingest_status:
        sys.exit(cmd_ingest_status(args.json))
    if args.mark_ingested:
        cmd_mark_ingested(); return
    if args.maintain:
        cmd_maintain(); return
    if args.push and args.pull:
        sys.exit("Pick one direction; decisions/log.md converges both sides either way.")
    if args.push:
        cmd_mirror("push", args.dry_run)
    elif args.pull:
        cmd_mirror("pull", args.dry_run)
    else:
        sys.exit(cmd_check(args.json))


if __name__ == "__main__":
    main()
