"""
gdrive-sync — Two-way sync between Nexis private folders and Google Drive.

Modes:
  python sync.py --setup              First-time: create Drive folder structure
  python sync.py --push               Upload new/changed local files (default)
  python sync.py --push --folder ctx  Push one folder only
  python sync.py --check              Scan Drive for missing/newer files locally
  python sync.py --push --check       Full two-way sync
  python sync.py --push --dry-run     Preview without uploading
  python sync.py --schedule-weekly    Register Windows Task Scheduler job
  python sync.py --unschedule         Remove scheduled job

Drive is a permanent backup: files are never deleted from Drive.
"""

import os
import sys
import json
import time
import hashlib
import argparse
import mimetypes
import subprocess
from pathlib import Path
from datetime import datetime, timezone

# ── optional deps ─────────────────────────────────────────────────────────────
try:
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    from googleapiclient.errors import HttpError
except ImportError:
    print("Missing deps. Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parents[3] / ".env")
except ImportError:
    pass

# ── config ────────────────────────────────────────────────────────────────────
SCRIPTS_DIR = Path(__file__).parent
REPO_ROOT   = SCRIPTS_DIR.parents[3]

SYNC_FOLDERS = [
    "archives",
    "catalog",
    "client-projects",
    "context",
    "decisions",
    "logs",
    "references",
]

WORK_FOLDER_NAME = "Work"
SYNC_ROOT_NAME   = "Nexis Business Context"
IDS_FILE         = SCRIPTS_DIR / "folder_ids.json"
SCOPES           = ["https://www.googleapis.com/auth/drive"]

TASK_NAME        = "NexisGDriveSync"
TASK_SCRIPT      = str(Path(__file__).resolve())

# ── auth ──────────────────────────────────────────────────────────────────────
def _load_token(path: Path) -> Credentials | None:
    try:
        creds = Credentials.from_authorized_user_file(str(path), SCOPES)
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds
    except Exception:
        pass
    return None


GWS_CLIENT_SECRET = Path.home() / ".config" / "gws" / "client_secret.json"
STANDALONE_TOKEN  = SCRIPTS_DIR / "gdrive_token.json"


def get_drive_service():
    # Try cached token files first
    token_locations = [
        Path(os.environ.get("APPDATA", "")) / "gws" / "token.json",
        Path.home() / ".gws"    / "token.json",
        Path.home() / ".config" / "gws" / "token.json",
        STANDALONE_TOKEN,
    ]
    for loc in token_locations:
        if loc.exists():
            creds = _load_token(loc)
            if creds:
                return build("drive", "v3", credentials=creds, cache_discovery=False)

    # Fall back to interactive OAuth using GWS client_secret.json
    if GWS_CLIENT_SECRET.exists():
        print("Opening browser for Google Drive authorisation...")
        flow = InstalledAppFlow.from_client_secrets_file(str(GWS_CLIENT_SECRET), SCOPES)
        creds = flow.run_local_server(port=0)
        STANDALONE_TOKEN.write_text(creds.to_json())
        print(f"Token saved to {STANDALONE_TOKEN}")
        return build("drive", "v3", credentials=creds, cache_discovery=False)

    print("ERROR: No GWS token or client_secret.json found.")
    print("Run: gws auth login")
    sys.exit(1)


# ── drive helpers ─────────────────────────────────────────────────────────────
def find_folder(svc, name: str, parent_id: str | None = None) -> str | None:
    q = f'name="{name}" and mimeType="application/vnd.google-apps.folder" and trashed=false'
    if parent_id:
        q += f' and "{parent_id}" in parents'
    r = svc.files().list(q=q, fields="files(id)").execute()
    files = r.get("files", [])
    return files[0]["id"] if files else None


def get_or_create_folder(svc, name: str, parent_id: str | None = None) -> tuple[str, bool]:
    fid = find_folder(svc, name, parent_id)
    if fid:
        return fid, False
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        meta["parents"] = [parent_id]
    f = svc.files().create(body=meta, fields="id").execute()
    return f["id"], True


def list_drive_folder(svc, folder_id: str) -> dict[str, dict]:
    """
    Returns a flat map of relative-path → {id, md5, modifiedTime}
    for every non-folder file under folder_id (recursive via BFS).
    """
    result = {}

    def _recurse(fid: str, prefix: str):
        page_token = None
        while True:
            resp = svc.files().list(
                q=f'"{fid}" in parents and trashed=false',
                fields="nextPageToken, files(id, name, mimeType, md5Checksum, modifiedTime)",
                pageToken=page_token,
            ).execute()
            for f in resp.get("files", []):
                rel = f"{prefix}/{f['name']}" if prefix else f["name"]
                if f["mimeType"] == "application/vnd.google-apps.folder":
                    _recurse(f["id"], rel)
                else:
                    result[rel] = {
                        "id":           f["id"],
                        "md5":          f.get("md5Checksum", ""),
                        "modifiedTime": f.get("modifiedTime", ""),
                    }
            page_token = resp.get("nextPageToken")
            if not page_token:
                break

    _recurse(folder_id, "")
    return result


def file_md5(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_parent_folder(svc, rel_parts: tuple[str, ...], root_id: str) -> str:
    """Walk/create the subfolder chain for a nested file path."""
    current = root_id
    for part in rel_parts:
        current, _ = get_or_create_folder(svc, part, current)
    return current


def upload_file(svc, local_path: Path, parent_id: str, existing_id: str | None = None) -> str:
    mime = mimetypes.guess_type(str(local_path))[0] or "application/octet-stream"
    media = MediaFileUpload(str(local_path), mimetype=mime, resumable=len(local_path.read_bytes()) > 5_000_000)
    for attempt in range(3):
        try:
            if existing_id:
                svc.files().update(fileId=existing_id, media_body=media).execute()
                return "updated"
            else:
                svc.files().create(
                    body={"name": local_path.name, "parents": [parent_id]},
                    media_body=media, fields="id",
                ).execute()
                return "uploaded"
        except (TimeoutError, OSError) as e:
            if attempt == 2:
                raise
            time.sleep(2 ** attempt)  # 1s, 2s


def download_file(svc, file_id: str, dest: Path):
    dest.parent.mkdir(parents=True, exist_ok=True)
    request = svc.files().get_media(fileId=file_id)
    with open(dest, "wb") as fh:
        fh.write(request.execute())


# ── IDs cache ─────────────────────────────────────────────────────────────────
def load_ids() -> dict:
    return json.loads(IDS_FILE.read_text()) if IDS_FILE.exists() else {}


def save_ids(ids: dict):
    IDS_FILE.write_text(json.dumps(ids, indent=2))


# ── setup ─────────────────────────────────────────────────────────────────────
def cmd_setup(svc):
    print(f"Setting up Drive folder structure...")

    work_id = find_folder(svc, WORK_FOLDER_NAME)
    if not work_id:
        print(f"  '{WORK_FOLDER_NAME}' not found — creating at Drive root")
        work_id, _ = get_or_create_folder(svc, WORK_FOLDER_NAME)
    else:
        print(f"  Found '{WORK_FOLDER_NAME}' ({work_id})")

    root_id, created = get_or_create_folder(svc, SYNC_ROOT_NAME, work_id)
    print(f"  '{SYNC_ROOT_NAME}': {'created' if created else 'exists'} ({root_id})")

    ids = {"root": root_id, "subfolders": {}}
    for folder in SYNC_FOLDERS:
        fid, created = get_or_create_folder(svc, folder, root_id)
        ids["subfolders"][folder] = fid
        print(f"    /{folder}: {'created' if created else 'exists'} ({fid})")

    save_ids(ids)
    print(f"\nSetup complete. IDs saved to {IDS_FILE.name}")
    return ids


# ── push ──────────────────────────────────────────────────────────────────────
def cmd_push(svc, ids: dict, folders: list[str], dry_run: bool):
    stats = {"uploaded": 0, "updated": 0, "skipped": 0, "errors": 0}

    for folder in folders:
        if folder not in ids["subfolders"]:
            print(f"Unknown folder '{folder}'. Known: {', '.join(ids['subfolders'])}")
            continue

        local_root  = REPO_ROOT / folder
        drive_root  = ids["subfolders"][folder]

        if not local_root.exists():
            print(f"  /{folder}: local folder does not exist, skipping")
            continue

        print(f"\nPushing /{folder} → Drive/{SYNC_ROOT_NAME}/{folder}/")
        drive_files = list_drive_folder(svc, drive_root)

        for item in sorted(local_root.rglob("*")):
            if item.is_dir():
                continue
            rel      = item.relative_to(local_root)
            rel_str  = rel.as_posix()
            existing = drive_files.get(rel_str)

            if existing:
                local_hash = file_md5(item)
                if local_hash == existing["md5"]:
                    stats["skipped"] += 1
                    continue

            if dry_run:
                action = "would update" if existing else "would upload"
                print(f"    {action}: {rel_str}")
                stats["uploaded"] += 1
                continue

            try:
                parent_id = ensure_parent_folder(svc, rel.parts[:-1], drive_root)
                action    = upload_file(svc, item, parent_id, existing["id"] if existing else None)
                stats[action] += 1
                print(f"    {action}: {rel_str}")
            except HttpError as e:
                print(f"    ERROR {rel_str}: {e}")
                stats["errors"] += 1

    prefix = "[DRY RUN] " if dry_run else ""
    print(f"\n{prefix}Push complete — uploaded: {stats['uploaded']}, updated: {stats['updated']}, "
          f"skipped: {stats['skipped']}, errors: {stats['errors']}")


# ── check (two-way awareness) ─────────────────────────────────────────────────
def cmd_check(svc, ids: dict, folders: list[str]):
    """
    Scan Drive for:
    1. Files that exist on Drive but not locally (may have been deleted — Drive keeps them)
    2. Files where Drive's modifiedTime is newer than the local file
    """
    drive_only   = []
    drive_newer  = []

    for folder in folders:
        if folder not in ids["subfolders"]:
            continue

        local_root = REPO_ROOT / folder
        drive_root = ids["subfolders"][folder]

        print(f"\nChecking /{folder}...")
        drive_files = list_drive_folder(svc, drive_root)

        for rel_str, dfile in drive_files.items():
            local_path = local_root / rel_str.replace("/", os.sep)

            if not local_path.exists():
                drive_only.append((folder, rel_str, dfile["id"]))
                continue

            # Compare modification times
            if dfile["modifiedTime"]:
                drive_mtime = datetime.fromisoformat(dfile["modifiedTime"].replace("Z", "+00:00"))
                local_mtime = datetime.fromtimestamp(local_path.stat().st_mtime, tz=timezone.utc)
                if drive_mtime > local_mtime:
                    # Also confirm MD5 differs (mtime alone can be misleading)
                    if dfile["md5"] and file_md5(local_path) != dfile["md5"]:
                        drive_newer.append((folder, rel_str, dfile["id"], drive_mtime))

    # Report
    print()
    if not drive_only and not drive_newer:
        print("All good — Drive matches local files.")
        return [], []

    if drive_only:
        print(f"Drive-only files ({len(drive_only)}) — exist on Drive but not locally:")
        for folder, rel, _ in drive_only:
            print(f"  {folder}/{rel}")

    if drive_newer:
        print(f"\nDrive-newer files ({len(drive_newer)}) — Drive version is more recent:")
        for folder, rel, _, mtime in drive_newer:
            print(f"  {folder}/{rel}  (Drive: {mtime.strftime('%Y-%m-%d %H:%M')})")

    return drive_only, drive_newer


# ── pull ──────────────────────────────────────────────────────────────────────
def cmd_pull(svc, ids: dict, files: list[tuple[str, str, str]]):
    """Download specified files from Drive to local."""
    for folder, rel_str, file_id in files:
        local_path = REPO_ROOT / folder / rel_str.replace("/", os.sep)
        print(f"  pulling: {folder}/{rel_str}")
        download_file(svc, file_id, local_path)
    print(f"\nPulled {len(files)} file(s).")


# ── schedule ──────────────────────────────────────────────────────────────────
def cmd_schedule_weekly():
    """Register a Windows Task Scheduler job for weekly push."""
    python_exe = sys.executable
    script     = TASK_SCRIPT
    xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <WeeklyTrigger>
      <StartBoundary>2026-01-04T09:00:00</StartBoundary>
      <DaysOfWeek><Sunday /></DaysOfWeek>
      <WeeksInterval>1</WeeksInterval>
    </WeeklyTrigger>
  </Triggers>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>"{script}" --push</Arguments>
      <WorkingDirectory>{SCRIPTS_DIR}</WorkingDirectory>
    </Exec>
  </Actions>
  <Settings>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
  </Settings>
</Task>"""

    xml_path = SCRIPTS_DIR / "task.xml"
    xml_path.write_text(xml, encoding="utf-16")
    result = subprocess.run(
        ["schtasks", "/Create", "/TN", TASK_NAME, "/XML", str(xml_path), "/F"],
        capture_output=True, text=True
    )
    xml_path.unlink(missing_ok=True)

    if result.returncode == 0:
        print(f"Scheduled weekly sync every Sunday at 9am (Task: {TASK_NAME})")
        print("To remove: python sync.py --unschedule")
    else:
        print(f"ERROR scheduling task: {result.stderr}")


def cmd_unschedule():
    result = subprocess.run(
        ["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"Removed scheduled task '{TASK_NAME}'")
    else:
        print(f"Task not found or error: {result.stderr}")


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Nexis GDrive two-way sync")
    parser.add_argument("--setup",           action="store_true", help="Create Drive folder structure")
    parser.add_argument("--push",            action="store_true", help="Upload new/changed local files")
    parser.add_argument("--check",           action="store_true", help="Scan Drive for missing/newer files")
    parser.add_argument("--pull",            action="store_true", help="Pull files listed in --files")
    parser.add_argument("--folder",          help="Target a single folder (e.g. context)")
    parser.add_argument("--files",           help="Comma-separated 'folder/rel/path' entries for --pull")
    parser.add_argument("--dry-run",         action="store_true", help="Preview without uploading")
    parser.add_argument("--schedule-weekly", action="store_true", help="Register weekly Task Scheduler job")
    parser.add_argument("--unschedule",      action="store_true", help="Remove scheduled job")
    args = parser.parse_args()

    if args.schedule_weekly:
        cmd_schedule_weekly(); return
    if args.unschedule:
        cmd_unschedule(); return

    print("Connecting to Google Drive...")
    svc = get_drive_service()

    if args.setup:
        cmd_setup(svc); return

    ids = load_ids()
    if not ids:
        print("No folder IDs found. Run: python sync.py --setup")
        sys.exit(1)

    folders = [args.folder] if args.folder else SYNC_FOLDERS

    if args.push:
        cmd_push(svc, ids, folders, args.dry_run)

    if args.check:
        drive_only, drive_newer = cmd_check(svc, ids, folders)
        if drive_only or drive_newer:
            print("\nRun with --pull to download flagged files, or ask Claude to pull them.")

    if args.pull and args.files:
        pull_list = []
        for entry in args.files.split(","):
            parts = entry.strip().split("/", 1)
            if len(parts) == 2:
                folder, rel = parts
                drive_files = list_drive_folder(svc, ids["subfolders"].get(folder, ""))
                if rel in drive_files:
                    pull_list.append((folder, rel, drive_files[rel]["id"]))
        if pull_list:
            cmd_pull(svc, ids, pull_list)
        else:
            print("No matching files found on Drive for the given paths.")


if __name__ == "__main__":
    main()
