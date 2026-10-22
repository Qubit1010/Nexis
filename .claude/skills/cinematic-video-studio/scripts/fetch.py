"""Download finished Higgsfield results into a film folder.

    python -I fetch.py <film_dir> '<json>'      json: {"clips/s01.mp4": "<result_url>", "vo/line-01.mp3": "<url>"}
    python -I fetch.py <film_dir> @map.json     (same mapping, from a file)

Keys are paths relative to the film folder. Existing files are skipped unless --force,
so re-running after a partial failure is safe. Prints each file written.
"""
import json, sys, urllib.request
from pathlib import Path


def main():
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv
    if len(args) != 2:
        sys.exit(__doc__)
    film, spec = Path(args[0]), args[1]
    mapping = json.loads(Path(spec[1:]).read_text(encoding="utf-8") if spec.startswith("@") else spec)
    for rel, url in mapping.items():
        dest = film / rel
        if dest.exists() and not force:
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(url, dest)
        if dest.stat().st_size < 1000:
            sys.exit(f"Suspiciously small download ({dest.stat().st_size} B): {dest}")
        print(rel)


if __name__ == "__main__":
    main()
