#!/bin/sh
# Privacy guard: block committing private/sensitive paths even if force-added.
# Install: cp scripts/pre-commit-privacy-guard.sh .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
# Belt-and-suspenders over .gitignore (see .claude/rules/privacy.md).
#
# EDIT the regex below to match THIS OS's sensitive paths (keep in sync with .gitignore + privacy.md).

blocked=$(git diff --cached --name-only | grep -E '^(decisions/log\.md|\.env$|\.env\.[^e]|CLAUDE\.local\.md)' )
# Example additions: context/finances\.md|context/values\.md|reflections/|<private-folder>/

if [ -n "$blocked" ]; then
  echo "BLOCKED by privacy guard — these are Drive-only and must never be committed:"
  echo "$blocked" | sed 's/^/  - /'
  echo "If truly intentional, bypass with: git commit --no-verify"
  exit 1
fi
exit 0
