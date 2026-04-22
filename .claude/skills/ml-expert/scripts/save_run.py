"""
save_run.py — organizes ML task code and output into a timestamped run folder.

Usage (two-step pattern):
  # Step 1: Create run folder and save code
  python save_run.py --task-slug eda-images --code-file /tmp/ml_task.py --output-dir ml-runs

  # Step 2: Add output to existing run folder
  python save_run.py --run-dir ml-runs/20260422_143021_eda-images --output-file /tmp/ml_output.txt
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path


def create_run(task_slug: str, code_file: str, output_dir: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = task_slug.lower().replace(" ", "-").replace("_", "-")
    run_dir = Path(output_dir) / f"{timestamp}_{slug}"
    run_dir.mkdir(parents=True, exist_ok=True)

    src = Path(code_file)
    if not src.exists():
        print(f"ERROR: code file not found: {code_file}", file=sys.stderr)
        sys.exit(1)

    shutil.copy2(src, run_dir / "code.py")
    print(f"Run created: {run_dir}")
    print(f"Code saved:  {run_dir / 'code.py'}")
    return run_dir


def add_output(run_dir: str, output_file: str) -> None:
    rd = Path(run_dir)
    if not rd.exists():
        print(f"ERROR: run directory not found: {run_dir}", file=sys.stderr)
        sys.exit(1)

    src = Path(output_file)
    if not src.exists():
        print(f"ERROR: output file not found: {output_file}", file=sys.stderr)
        sys.exit(1)

    shutil.copy2(src, rd / "output.txt")
    print(f"Output saved: {rd / 'output.txt'}")


def main():
    parser = argparse.ArgumentParser(description="Save ML task run artifacts")
    parser.add_argument("--task-slug", help="Short name for the task (used in folder name)")
    parser.add_argument("--code-file", help="Path to the generated Python script")
    parser.add_argument("--output-dir", default="ml-runs", help="Parent directory for all runs")
    parser.add_argument("--run-dir", help="Existing run folder path (for adding output)")
    parser.add_argument("--output-file", help="Path to captured stdout/stderr output")
    args = parser.parse_args()

    if args.run_dir and args.output_file:
        add_output(args.run_dir, args.output_file)
    elif args.task_slug and args.code_file:
        run_dir = create_run(args.task_slug, args.code_file, args.output_dir)
        if args.output_file:
            add_output(str(run_dir), args.output_file)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
