param(
  [switch]$Force
)

$ErrorActionPreference = 'Stop'

$SkillName = 'pitchbook-report-downloader'
$SrcDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Targets = @(
  Join-Path $HOME ".claude/skills/$SkillName",
  Join-Path ($env:CODEX_HOME ? $env:CODEX_HOME : (Join-Path $HOME '.codex')) "skills/$SkillName"
)

function Sync-ToTarget {
  param([string]$TargetDir)

  $targetRoot = Split-Path -Parent $TargetDir
  New-Item -ItemType Directory -Force -Path $targetRoot | Out-Null

  if (Test-Path $TargetDir) {
    if ($Force) {
      Remove-Item -Recurse -Force $TargetDir
      New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
    }
  } else {
    New-Item -ItemType Directory -Force -Path $TargetDir | Out-Null
  }

  Copy-Item -Path (Join-Path $SrcDir '*') -Destination $TargetDir -Recurse -Force

  Remove-Item -Recurse -Force (Join-Path $TargetDir '.git') -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force (Join-Path $TargetDir 'node_modules') -ErrorAction SilentlyContinue
  Remove-Item -Recurse -Force (Join-Path $TargetDir 'downloads') -ErrorAction SilentlyContinue

  Push-Location $TargetDir
  npm install
  npm run install:browsers
  if (-not (Test-Path '.env')) {
    Copy-Item 'references/.env.example' '.env'
  }
  Pop-Location
}

Write-Host "Installing skill: $SkillName"
Write-Host "Source: $SrcDir"

foreach ($t in $Targets) {
  Write-Host "Target: $t"
  Sync-ToTarget -TargetDir $t
}

Write-Host 'Install complete.'
Write-Host "Run: $HOME/.claude/skills/$SkillName/run.command"
