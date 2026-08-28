"""Manage the local Expensify clone and generate the permalinks a winning proposal is built from.

The proposal that won issue 98426 was a causal chain across four files, each step cited as a
permalink pinned to a full commit SHA with a line range:

    https://github.com/Expensify/App/blob/79bca1613e.../src/.../RateField.tsx#L95-L97

That format is doing real work. A reviewer can click it and land on exactly the lines you mean, and
because the SHA is pinned rather than `main`, it still lands there weeks later when the file has
moved. A proposal citing `main` rots the moment someone merges, and a proposal citing no lines at
all reads as a description of the symptom rather than a diagnosis of the cause.

Every permalink this script emits is verified before it is returned: the file must exist at that SHA
and the line range must be inside the file. An unverified permalink is worse than no permalink,
because it looks authoritative while pointing at the wrong code, and a reviewer who clicks one and
finds nothing has learned something about your proposal that you did not intend to teach them.

Usage:
  python repo.py --ensure
  python repo.py --permalink src/components/MenuItem/MenuItem.tsx 810 818
  python repo.py --blame src/components/MenuItem/MenuItem.tsx 814
  python repo.py --selftest
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO_URL = "https://github.com/Expensify/App.git"

# Deliberately outside OneDrive. A React Native checkout plus node_modules under a syncing folder
# produces constant upload churn and occasional file locks mid-build, and the repo alone is 2.8GB.
DEFAULT_PATH = Path(os.environ.get("EXPENSIFY_REPO_PATH", r"C:\dev\expensify-app"))


class RepoError(RuntimeError):
    pass


def _git(args, cwd=None, check=True):
    proc = subprocess.run(["git"] + args, cwd=str(cwd or DEFAULT_PATH),
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and proc.returncode != 0:
        raise RepoError("git %s failed:\n%s" % (" ".join(args), (proc.stderr or "").strip()))
    return (proc.stdout or "").strip()


def exists():
    return (DEFAULT_PATH / ".git").is_dir()


def ensure(update=True):
    """Clone if missing, otherwise fetch the latest main."""
    if not exists():
        DEFAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
        if "onedrive" in str(DEFAULT_PATH).lower():
            raise RepoError(
                "Refusing to clone into a OneDrive path (%s). A 2.8GB React Native checkout plus\n"
                "node_modules under a syncing folder causes upload churn and file locks during builds.\n"
                "Set EXPENSIFY_REPO_PATH to somewhere outside OneDrive." % DEFAULT_PATH)
        print("Cloning Expensify/App into %s" % DEFAULT_PATH)
        print("Using --filter=blob:none: full history for root-cause archaeology, without")
        print("downloading every historical blob. Expect a few minutes and a few hundred MB.")
        proc = subprocess.run(
            ["git", "clone", "--filter=blob:none", REPO_URL, str(DEFAULT_PATH)],
            text=True)
        if proc.returncode != 0:
            raise RepoError("clone failed with exit %d" % proc.returncode)
    elif update:
        _git(["fetch", "origin", "main", "--quiet"])
    return DEFAULT_PATH


def head_sha(ref="origin/main"):
    return _git(["rev-parse", ref])


def _line_count(path, sha):
    blob = _git(["show", "%s:%s" % (sha, path)])
    return blob.count("\n") + 1 if blob else 0


def permalink(path, start, end=None, sha=None):
    """Build and verify a SHA-pinned permalink. Raises if the file or lines do not exist."""
    if not exists():
        raise RepoError("No local clone at %s. Run --ensure first." % DEFAULT_PATH)
    path = path.replace("\\", "/").lstrip("./")
    sha = sha or head_sha()

    try:
        _git(["cat-file", "-e", "%s:%s" % (sha, path)])
    except RepoError:
        raise RepoError("%s does not exist at %s. Check the path against the current tree." % (path, sha[:10]))

    total = _line_count(path, sha)
    if start < 1 or start > total:
        raise RepoError("line %d is outside %s, which has %d lines at %s" % (start, path, total, sha[:10]))
    if end is not None:
        if end < start:
            raise RepoError("end line %d is before start line %d" % (end, start))
        if end > total:
            raise RepoError("end line %d is past the end of %s (%d lines)" % (end, path, total))

    anchor = "#L%d-L%d" % (start, end) if end and end != start else "#L%d" % start
    url = "https://github.com/Expensify/App/blob/%s/%s%s" % (sha, path, anchor)
    snippet = _git(["show", "%s:%s" % (sha, path)]).splitlines()[start - 1:(end or start)]
    return {"url": url, "sha": sha, "path": path, "start": start, "end": end or start,
            "total_lines": total, "snippet": snippet}


BLAME_QUERY = """
query($owner:String!,$repo:String!,$ref:String!,$path:String!){
  repository(owner:$owner,name:$repo){
    object(expression:$ref){
      ... on Commit {
        blame(path:$path){
          ranges { startingLine endingLine
            commit { oid messageHeadline committedDate author{name}
              associatedPullRequests(first:1){nodes{number url title}} } }
        }
      }
    }
  }
}
"""


def blame(path, line, ref="main", timeout=45):
    """Find the pull request that introduced a line, via the GitHub GraphQL blame API.

    Naming the offending PR is a strong quality signal in a proposal, and Expensify asks for it at
    the post-merge checklist stage anyway, so finding it early costs nothing and pays twice.

    This deliberately does not use local `git blame`. On a `--filter=blob:none` clone, blame has to
    lazily fetch a historical blob per candidate commit over the network, which on a file with
    thousands of revisions takes minutes rather than seconds. The GraphQL API does the same work
    server-side and returns the associated pull request directly, which local blame cannot do at all
    (it can only parse a number out of the commit subject, which is guesswork on squashed history).

    The API itself gives up on very large, heavily edited files, returning an HTML error page after
    ten seconds or so. When that happens this raises rather than returning something plausible: a
    fabricated "introduced by PR #x" in a proposal is worse than no attribution, because a reviewer
    who checks it and finds it wrong now doubts the rest of your analysis.
    """
    path = path.replace("\\", "/").lstrip("./")
    proc = subprocess.run(
        ["gh", "api", "graphql", "-F", "owner=Expensify", "-F", "repo=App",
         "-F", "ref=%s" % ref, "-F", "path=%s" % path, "-f", "query=%s" % BLAME_QUERY],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
    raw = (proc.stdout or "").strip()
    if proc.returncode != 0 or not raw.startswith("{"):
        raise RepoError(
            "GitHub's blame API did not answer for %s. This happens on very large, heavily edited "
            "files. Read it by hand instead:\n"
            "  https://github.com/Expensify/App/blame/%s/%s#L%d" % (path, ref, path, line))
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        raise RepoError("could not parse the blame response for %s" % path)

    obj = ((data.get("data") or {}).get("repository") or {}).get("object") or {}
    ranges = ((obj.get("blame") or {}).get("ranges")) or []
    if not ranges:
        raise RepoError(
            "No blame data returned for %s at %s. Check the path: files move often in this repo, "
            "which is exactly why proposals pin a SHA rather than linking to main." % (path, ref))

    for r in ranges:
        if r["startingLine"] <= line <= r["endingLine"]:
            c = r["commit"]
            prs = (c.get("associatedPullRequests") or {}).get("nodes") or []
            pr = prs[0] if prs else None
            return {
                "commit": c["oid"],
                "subject": c["messageHeadline"],
                "author": (c.get("author") or {}).get("name"),
                "date": c.get("committedDate"),
                "line_range": "%d-%d" % (r["startingLine"], r["endingLine"]),
                "pr": pr["number"] if pr else None,
                "pr_url": pr["url"] if pr else None,
                "pr_title": pr["title"] if pr else None,
                "commit_url": "https://github.com/Expensify/App/commit/%s" % c["oid"],
            }
    raise RepoError("line %d is outside every blame range returned for %s" % (line, path))


def selftest():
    """Verify permalink construction and its guard rails.

    If no clone exists the clone-dependent checks are reported as SKIPPED rather than passed. A
    selftest that quietly passes because it never ran is worse than one that fails, since it teaches
    you to trust a check that is not happening.
    """
    failures, skipped = [], []

    if not exists():
        skipped.append("no clone at %s, so permalink and blame checks could not run" % DEFAULT_PATH)
    else:
        # A real file at a real SHA should produce a link whose snippet is non-empty.
        try:
            pl = permalink("package.json", 2, 4)
            if not re.match(r"^https://github\.com/Expensify/App/blob/[0-9a-f]{40}/package\.json#L2-L4$", pl["url"]):
                failures.append("permalink shape wrong: %s" % pl["url"])
            if len(pl["snippet"]) != 3:
                failures.append("expected a 3-line snippet, got %d" % len(pl["snippet"]))
        except RepoError as exc:
            failures.append("permalink on package.json failed: %s" % exc)

        # The guards matter more than the happy path, because they are what stop a confidently
        # wrong citation reaching a reviewer.
        for bad, why in [
            (lambda: permalink("src/does/not/exist.tsx", 1), "missing file"),
            (lambda: permalink("package.json", 999999), "line past end of file"),
            (lambda: permalink("package.json", 10, 2), "end before start"),
        ]:
            try:
                bad()
                failures.append("permalink accepted a %s, it should have raised" % why)
            except RepoError:
                pass

        # Blame runs against the API, not the clone, so it is checked on a small stable file.
        # A failure here is reported as a skip rather than a failure, because the API genuinely
        # gives up on large files and that is a documented limitation, not a broken script.
        try:
            b = blame("babel.config.js", 1)
            if not re.match(r"^[0-9a-f]{40}$", b["commit"] or ""):
                failures.append("blame returned a malformed commit: %r" % b["commit"])
            elif b["pr"] is None:
                skipped.append("blame resolved a commit but no associated PR, which happens on direct pushes")
        except RepoError as exc:
            skipped.append("blame could not run (%s)" % str(exc).split(chr(10))[0])
        except subprocess.TimeoutExpired:
            skipped.append("blame timed out, which the API does on large files")

    if failures:
        print("SELFTEST FAILED")
        for f in failures:
            print("  - %s" % f)
        return 1
    print("SELFTEST PASSED" if not skipped else "SELFTEST PASSED WITH SKIPS")
    for s in skipped:
        print("  SKIPPED: %s" % s)
    if skipped:
        print("  Run --ensure to clone, then re-run this to exercise the permalink guards.")
    else:
        print("  permalink verified, and correctly rejects missing files, out-of-range and inverted ranges")
        print("  blame resolves a real commit and its pull request")
    return 0


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--ensure", action="store_true", help="clone the repo if missing, else fetch main")
    p.add_argument("--permalink", nargs="+", metavar=("PATH", "START"), help="PATH START [END]")
    p.add_argument("--blame", nargs=2, metavar=("PATH", "LINE"), help="find the PR that introduced a line")
    p.add_argument("--sha", help="pin to a specific SHA instead of current origin/main")
    p.add_argument("--selftest", action="store_true")
    a = p.parse_args()

    try:
        if a.selftest:
            return selftest()
        if a.ensure:
            path = ensure()
            print("Repo ready at %s" % path)
            print("origin/main is at %s" % head_sha())
            return 0
        if a.permalink:
            path = a.permalink[0]
            start = int(a.permalink[1])
            end = int(a.permalink[2]) if len(a.permalink) > 2 else None
            pl = permalink(path, start, end, sha=a.sha)
            print(pl["url"])
            print("")
            for i, line in enumerate(pl["snippet"], start=pl["start"]):
                print("  %5d  %s" % (i, line))
            return 0
        if a.blame:
            b = blame(a.blame[0], int(a.blame[1]), ref=a.sha or "main")
            print("commit  %s  (%s, %s)" % (b["commit"][:12], b["author"], (b["date"] or "")[:10]))
            print("lines   %s" % b["line_range"])
            print("subject %s" % b["subject"])
            if b["pr_url"]:
                print("PR      %s" % b["pr_url"])
                print("")
                print("Naming this PR in the proposal shows you found where the behaviour came from,")
                print("and Expensify asks for it at the post-merge checklist stage regardless.")
            else:
                print("No PR number in the commit subject; check the commit page for the merge context.")
            return 0
        p.print_help()
        return 0
    except RepoError as exc:
        print("Repo error: %s" % exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
