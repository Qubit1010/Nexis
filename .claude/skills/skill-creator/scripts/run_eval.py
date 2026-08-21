#!/usr/bin/env python3
"""Run trigger evaluation for a skill description.

Tests whether a skill's description causes Claude to trigger (read the skill)
for a set of queries. Outputs results as JSON.
"""

import argparse
import json
import os
import queue
import shutil
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scripts.utils import parse_skill_md


def _claude_exe() -> str:
    """Absolute path to a WORKING claude CLI.

    Two separate Windows failures both end up scoring every query as "not
    triggered", and the resulting report looks like a real measurement rather
    than a broken harness (every should-trigger query fails, every should-not
    query passes, summary reads ~50%):

    1. `claude` resolves to a .CMD shim, and CreateProcess will not resolve a
       bare name to a .CMD the way a shell does, so Popen(["claude", ...]) dies
       with WinError 2. shutil.which() applies PATHEXT and fixes this.
    2. The shim that wins on PATH can be a dead redirect. On this machine
       ~/.local/bin/claude.CMD forwards to an Antigravity path that no longer
       exists, so it launches fine and immediately exits with "The system cannot
       find the path specified." which() cannot detect that, since the shim is a
       real file.

    So prefer the actual packaged binary, then fall back to PATH. Set
    CLAUDE_CLI to override if the install lives somewhere else.
    """
    override = os.environ.get("CLAUDE_CLI", "").strip()
    if override and Path(override).exists():
        return override

    appdata = os.environ.get("APPDATA", "")
    candidates = [
        Path(appdata) / "npm/node_modules/@anthropic-ai/claude-code/bin/claude.exe",
        Path.home() / "AppData/Roaming/npm/node_modules/@anthropic-ai/claude-code/bin/claude.exe",
        Path.home() / ".claude/local/node_modules/@anthropic-ai/claude-code/bin/claude.exe",
    ]
    for c in candidates:
        if c.exists():
            return str(c)

    # 3. The Claude Desktop packaged install, which none of the paths above reach.
    #    On this machine (2026-08-21) it is the ONLY working CLI: ~/.local/bin/claude
    #    is a bash shim hard-coded to version 2.1.74, which no longer exists, while
    #    the real binary is 2.1.229 under LocalCache. The shim is what wins on PATH,
    #    so shutil.which() finds it, it launches, prints "No such file or directory"
    #    to stderr and exits 0 - which is invisible once stderr is DEVNULL.
    #    Version directories sort naturally, so take the highest rather than the
    #    first, or a stale 2.1.74 beats a live 2.1.229 on string order.
    def _vkey(path):
        try:
            return tuple(int(x) for x in path.parent.name.split("."))
        except ValueError:
            return (0,)

    packaged = sorted(
        Path.home().glob(
            "AppData/Local/Packages/Claude_*/LocalCache/Roaming/Claude/"
            "claude-code/*/claude.exe"
        ),
        key=_vkey,
    )
    if packaged:
        return str(packaged[-1])

    return shutil.which("claude") or "claude"


def find_project_root() -> Path:
    """Find the project root by walking up from cwd looking for .claude/.

    Mimics how Claude Code discovers its project root, so the command file
    we create ends up where claude -p will look for it.
    """
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
) -> bool:
    """Run a single query and return whether the skill was triggered.

    Creates a command file in .claude/commands/ so it appears in Claude's
    available_skills list, then runs `claude -p` with the raw query.
    Uses --include-partial-messages to detect triggering early from
    stream events (content_block_start) rather than waiting for the
    full assistant message, which only arrives after tool execution.
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    project_commands_dir = Path(project_root) / ".claude" / "commands"
    command_file = project_commands_dir / f"{clean_name}.md"

    try:
        project_commands_dir.mkdir(parents=True, exist_ok=True)
        # Use YAML block scalar to avoid breaking on quotes in description
        indented_desc = "\n  ".join(skill_description.split("\n"))
        command_content = (
            f"---\n"
            f"description: |\n"
            f"  {indented_desc}\n"
            f"---\n\n"
            f"# {skill_name}\n\n"
            f"This skill handles: {skill_description}\n"
        )
        command_file.write_text(command_content)

        cmd = [
            _claude_exe(),
            "-p", query,
            "--output-format", "stream-json",
            "--verbose",
            "--include-partial-messages",
        ]
        if model:
            cmd.extend(["--model", model])

        # Remove CLAUDECODE env var to allow nesting claude -p inside a
        # Claude Code session. The guard is for interactive terminal conflicts;
        # programmatic subprocess usage is safe.
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=project_root,
            env=env,
        )

        triggered = False
        start_time = time.time()
        buffer = ""
        # A launch failure that EXITS CLEANLY is invisible to the error path below,
        # because run_single_query returns False rather than raising. That is how a dead
        # PATH shim (see _claude_exe) produced a full 26-query report reading 13/26 with
        # every should-trigger query "failing" - a plausible-looking measurement of
        # nothing. Track whether the child ever wrote a byte; no output at all means the
        # check never ran, which is a different fact from "the skill did not trigger"
        # and must not be scored as one.
        got_output = False
        # Track state for stream event detection
        pending_tool_name = None
        accumulated_json = ""

        def _is_match(text: str) -> bool:
            """Did Claude reach for this skill?

            The harness registers a throwaway command named <skill>-skill-<uuid> so a
            description can be tested before the skill exists. But once the skill is
            actually installed, Claude invokes the REAL name instead, and matching only
            the throwaway name reports 0% for a skill that triggers perfectly. Accept
            either, so the harness works pre- and post-install.
            """
            return clean_name in text or skill_name in text

        # select() only works on sockets on Windows, not pipes, so polling the
        # child's stdout with it raises WinError 10093 and every query silently
        # reports "not triggered". Pump the pipe from a thread instead, which
        # behaves the same on both platforms. os.read (not stream.read) so we get
        # data as soon as it arrives and keep early trigger detection.
        chunk_q: queue.Queue = queue.Queue()

        def _pump(fd: int, q: queue.Queue) -> None:
            try:
                while True:
                    data = os.read(fd, 8192)
                    if not data:
                        break
                    q.put(data)
            except OSError:
                pass
            finally:
                q.put(None)  # sentinel: EOF

        threading.Thread(
            target=_pump, args=(process.stdout.fileno(), chunk_q), daemon=True
        ).start()

        try:
            while time.time() - start_time < timeout:
                try:
                    chunk = chunk_q.get(timeout=1.0)
                except queue.Empty:
                    if process.poll() is not None:
                        break
                    continue

                if chunk is None:  # EOF
                    break
                got_output = True
                buffer += chunk.decode("utf-8", errors="replace")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Early detection via stream events
                    if event.get("type") == "stream_event":
                        se = event.get("event", {})
                        se_type = se.get("type", "")

                        if se_type == "content_block_start":
                            cb = se.get("content_block", {})
                            if cb.get("type") == "tool_use":
                                tool_name = cb.get("name", "")
                                if tool_name in ("Skill", "Read"):
                                    pending_tool_name = tool_name
                                    accumulated_json = ""
                                else:
                                    return False

                        elif se_type == "content_block_delta" and pending_tool_name:
                            delta = se.get("delta", {})
                            if delta.get("type") == "input_json_delta":
                                accumulated_json += delta.get("partial_json", "")
                                if _is_match(accumulated_json):
                                    return True

                        elif se_type in ("content_block_stop", "message_stop"):
                            if pending_tool_name:
                                return _is_match(accumulated_json)
                            if se_type == "message_stop":
                                return False

                    # Fallback: full assistant message
                    elif event.get("type") == "assistant":
                        message = event.get("message", {})
                        for content_item in message.get("content", []):
                            if content_item.get("type") != "tool_use":
                                continue
                            tool_name = content_item.get("name", "")
                            tool_input = content_item.get("input", {})
                            if tool_name == "Skill" and _is_match(tool_input.get("skill", "")):
                                triggered = True
                            elif tool_name == "Read" and _is_match(tool_input.get("file_path", "")):
                                triggered = True
                            return triggered

                    elif event.get("type") == "result":
                        return triggered
        finally:
            # Clean up process on any exit path (return, exception, timeout)
            if process.poll() is None:
                process.kill()
                process.wait()

        if not got_output:
            raise RuntimeError(
                f"claude CLI produced no output (exit={process.poll()}). "
                f"The query never ran, so this is not a trigger result. "
                f"Binary: {cmd[0]}"
            )
        return triggered
    finally:
        if command_file.exists():
            command_file.unlink()


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
) -> dict:
    """Run the full eval set and return results."""
    results = []
    errors: list[Exception] = []

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        future_to_info = {}
        for item in eval_set:
            for run_idx in range(runs_per_query):
                future = executor.submit(
                    run_single_query,
                    item["query"],
                    skill_name,
                    description,
                    timeout,
                    str(project_root),
                    model,
                )
                future_to_info[future] = (item, run_idx)

        query_triggers: dict[str, list[bool]] = {}
        query_items: dict[str, dict] = {}
        for future in as_completed(future_to_info):
            item, _ = future_to_info[future]
            query = item["query"]
            query_items[query] = item
            if query not in query_triggers:
                query_triggers[query] = []
            try:
                query_triggers[query].append(future.result())
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                query_triggers[query].append(False)
                errors.append(e)

    # A query that never launched is not the same as a skill that did not trigger, but scoring
    # both as False makes them indistinguishable, and the resulting report looks like a real
    # measurement: every should-trigger query "fails", every should-not query "passes", and the
    # summary reads as a plausible ~50%. Surfacing it is the difference between rewriting a
    # description for no reason and fixing the harness.
    if errors and len(errors) == sum(len(v) for v in query_triggers.values()):
        print(
            f"\nERROR: all {len(errors)} runs failed to execute, so these results measure nothing.\n"
            f"       First error: {type(errors[0]).__name__}: {errors[0]}\n"
            f"       If this is WinError 2, the claude CLI could not be launched.",
            file=sys.stderr,
        )

    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", default=None, help="Model to use for claude -p (default: user's configured model)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, content = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root()

    if args.verbose:
        print(f"Evaluating: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        project_root=project_root,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
