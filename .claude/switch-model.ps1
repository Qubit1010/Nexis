# Switch the active .claude/settings.local.json between saved model configs.
# Usage:
#   .claude/switch-model.ps1 glm          # use GLM (OpenRouter)
#   .claude/switch-model.ps1 open-models  # use free OpenRouter models
#   .claude/switch-model.ps1 default      # restore default Claude (no model overrides)
#   .claude/switch-model.ps1              # show current + available configs
#
# Merge strategy: only the env keys that appear in ANY stored config are managed by
# the switcher. All other top-level keys (permissions, additionalDirectories, etc.)
# and unrelated env vars (FIRECRAWL_API_KEY, ANTHROPIC_API_KEY, etc.) are always
# preserved exactly as-is. Safe to use in projects with existing settings.local.json.

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$Name
)

$ErrorActionPreference = 'Stop'
$claudeDir = $PSScriptRoot
$active = Join-Path $claudeDir 'settings.local.json'

# Discover available configs (subdirectories containing settings.local.json)
$configs = Get-ChildItem -Path $claudeDir -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName 'settings.local.json') } |
    Select-Object -ExpandProperty Name

function Show-Current {
    if (Test-Path $active) {
        try {
            $j = Get-Content $active -Raw | ConvertFrom-Json
            $model = $j.env.ANTHROPIC_MODEL
            if ($model) { Write-Host "Current active model: $model" }
            else         { Write-Host "Current active config: default (no model overrides)" }
        } catch {
            Write-Host "Current active config: (unparseable)"
        }
    } else {
        Write-Host "Current active config: none (no settings.local.json)"
    }
    Write-Host ""
    Write-Host "Available configs: $($configs -join ', ')"
}

if (-not $Name) {
    Show-Current
    Write-Host "Run: .claude/switch-model.ps1 <config-name>"
    exit 0
}

if ($Name -notin $configs) {
    Write-Host "Config '$Name' not found." -ForegroundColor Red
    Show-Current
    exit 1
}

# Build the set of env keys owned by the switcher: union of all stored config env keys.
# Only these keys are ever added/removed. Everything else in settings.local.json is untouched.
$managedKeys = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::Ordinal)
foreach ($cfg in $configs) {
    $cfgPath = Join-Path $claudeDir "$cfg/settings.local.json"
    $cfgJson  = Get-Content $cfgPath -Raw | ConvertFrom-Json
    if ($null -ne $cfgJson.env) {
        $cfgJson.env.PSObject.Properties.Name | ForEach-Object { [void]$managedKeys.Add($_) }
    }
}

# Read the current active settings (or start fresh if the file doesn't exist yet)
$current = if (Test-Path $active) {
    Get-Content $active -Raw | ConvertFrom-Json
} else {
    [PSCustomObject]@{}
}

# Ensure an env object exists at the top level
if (-not $current.PSObject.Properties['env']) {
    $current | Add-Member -MemberType NoteProperty -Name 'env' -Value ([PSCustomObject]@{})
}

# Remove all switcher-managed keys from the current env (clean slate for model vars)
foreach ($key in @($managedKeys)) {
    if ($null -ne $current.env.PSObject.Properties[$key]) {
        $current.env.PSObject.Properties.Remove($key)
    }
}

# Merge in the chosen config's env keys
$srcPath = Join-Path $claudeDir "$Name/settings.local.json"
$srcJson  = Get-Content $srcPath -Raw | ConvertFrom-Json
if ($null -ne $srcJson.env) {
    $srcJson.env.PSObject.Properties | ForEach-Object {
        $current.env | Add-Member -MemberType NoteProperty -Name $_.Name -Value $_.Value -Force
    }
}

# Drop the env key entirely if it ended up empty (happens for 'default' with no project vars)
if (@($current.env.PSObject.Properties).Count -eq 0) {
    $current.PSObject.Properties.Remove('env')
}

# Write back as UTF-8 without BOM
$json    = $current | ConvertTo-Json -Depth 10
$utf8    = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText($active, $json, $utf8)

Write-Host "Switched to '$Name' config." -ForegroundColor Green
Show-Current
Write-Host "Restart Claude Code for the change to take effect." -ForegroundColor Yellow
