"""Shared gws CLI helpers.

Lifted from .claude/skills/proposal-generator/scripts/create_proposal_doc.py.
Handles the Windows cmd.exe 8191-char command line limit by invoking node + run-gws.js
directly (CreateProcess allows ~32K) when available, falling back to gws.cmd via shell.
"""

import json
import os
import shutil
import subprocess
from pathlib import Path


def find_gws():
    """Return (cmd_list, use_shell). Prefer direct node invocation on Windows."""
    npm_dir = Path(os.environ.get("APPDATA", "")) / "npm"
    gws_js = npm_dir / "node_modules" / "@googleworkspace" / "cli" / "run.js"

    if gws_js.exists():
        node_exe = None
        for candidate in [
            npm_dir / "node.exe",
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")) / "nodejs" / "node.exe",
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")) / "nodejs" / "node.exe",
        ]:
            if candidate.exists():
                node_exe = str(candidate)
                break
        if not node_exe:
            node_exe = shutil.which("node")
        if node_exe:
            return ([node_exe, str(gws_js)], False)

    gws_path = shutil.which("gws")
    if gws_path:
        return ([gws_path], True)
    gws_cmd = npm_dir / "gws.cmd"
    if gws_cmd.exists():
        return ([str(gws_cmd)], True)
    return (["gws"], True)


GWS_CMD, GWS_USE_SHELL = find_gws()


def run_gws(args, json_body=None, timeout=120):
    """Run a gws CLI command and return parsed JSON output. Raises RuntimeError on failure."""
    cmd = GWS_CMD + args
    if json_body is not None:
        cmd += ["--json", json.dumps(json_body)]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=GWS_USE_SHELL,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        stderr = result.stderr.strip() if result.stderr else "Unknown error"
        raise RuntimeError(f"gws command failed: {' '.join(args[:3])}... | {stderr}")

    stdout = result.stdout.strip()
    if not stdout:
        return {}
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        return {"raw": stdout}


def find_or_create_folder(name, parent_id=None, cache_path=None):
    """Find a Drive folder by name (optionally under parent_id), or create it.

    Returns the folder ID. If cache_path is provided, uses it as a stable cache for
    the resolved ID across runs.
    """
    if cache_path is not None and Path(cache_path).exists():
        cached_id = Path(cache_path).read_text().strip()
        if cached_id:
            try:
                q_parts = [
                    f"name='{name}'",
                    "mimeType='application/vnd.google-apps.folder'",
                    "trashed=false",
                ]
                if parent_id:
                    q_parts.append(f"'{parent_id}' in parents")
                result = run_gws([
                    "drive", "files", "list",
                    "--params", json.dumps({
                        "q": " and ".join(q_parts),
                        "fields": "files(id,name)",
                    }),
                ])
                for f in result.get("files", []):
                    if f.get("id") == cached_id:
                        return cached_id
            except RuntimeError:
                pass

    q_parts = [
        f"name='{name}'",
        "mimeType='application/vnd.google-apps.folder'",
        "trashed=false",
    ]
    if parent_id:
        q_parts.append(f"'{parent_id}' in parents")
    try:
        result = run_gws([
            "drive", "files", "list",
            "--params", json.dumps({
                "q": " and ".join(q_parts),
                "fields": "files(id,name)",
            }),
        ])
        files = result.get("files", [])
        if files:
            folder_id = files[0]["id"]
            if cache_path is not None:
                Path(cache_path).write_text(folder_id)
            return folder_id
    except RuntimeError:
        pass

    body = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        body["parents"] = [parent_id]
    result = run_gws(["drive", "files", "create"], json_body=body)
    folder_id = result.get("id")
    if not folder_id:
        raise RuntimeError(f"Failed to create folder '{name}'. Response: {result}")
    if cache_path is not None:
        Path(cache_path).write_text(folder_id)
    return folder_id


def move_to_folder(file_id, folder_id):
    """Move a Drive file into folder_id (clearing other parents)."""
    file_meta = run_gws([
        "drive", "files", "get",
        "--params", json.dumps({"fileId": file_id, "fields": "parents"}),
    ])
    current_parents = ",".join(file_meta.get("parents", []))
    params = {"fileId": file_id, "addParents": folder_id}
    if current_parents:
        params["removeParents"] = current_parents
    run_gws(
        ["drive", "files", "update", "--params", json.dumps(params)],
        json_body={},
    )
