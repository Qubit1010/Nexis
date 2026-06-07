# Convenience wrapper — runs the cross-platform Node sync script.
# Usage:  .\scripts\sync-playbook.ps1   (or:  npm run sync-playbook)
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
node (Join-Path $here "sync-playbook.mjs")
