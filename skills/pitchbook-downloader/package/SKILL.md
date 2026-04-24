---
name: pitchbook-report-downloader
description: Automate PitchBook report downloads by opening report pages, filling the lead form, handling Cloudflare/intermittent page states, and saving downloadable files with retries and diagnostics.
---

# PitchBook Report Downloader

Use this skill when you need to download one or many PitchBook reports from `/news/reports` pages where a form must be filled before download.

## Why This Helps

PitchBook pages can be flaky because of:
- Cloudflare challenge pages (`Just a moment...`)
- delayed or changing download/form selectors
- occasional form submit without direct browser download event

This skill uses:
- persistent browser profile (improves Cloudflare pass rate)
- multi-selector fallback for form and buttons
- retry per report
- screenshot + JSON log for every failed attempt

## Setup (first time)

```bash
cd ~/.claude/skills/pitchbook-report-downloader
npm install
npm run install:browsers
```

## Claude Code Simple Install

```bash
mkdir -p ~/.claude/skills
git clone https://github.com/<your-org>/<your-repo>.git ~/.claude/skills/pitchbook-report-downloader
cd ~/.claude/skills/pitchbook-report-downloader
./bootstrap.sh
```

Then edit `.env`, and run:

```bash
bash ~/.claude/skills/pitchbook-report-downloader/install.sh
~/.claude/skills/pitchbook-report-downloader/run.command
```

## Codex One-Click Install From GitHub

After you push this folder to GitHub, install with:

```bash
python3 /Users/a1111/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py \
  --repo <your-org>/<your-repo> \
  --path <path-in-repo>/pitchbook-report-downloader
```

Then restart Codex.

## Required Form Fields

Create a `.env` based on example:

```bash
cp ~/.claude/skills/pitchbook-report-downloader/references/.env.example \
  ~/.claude/skills/pitchbook-report-downloader/.env
```

Set values:
- `PB_FIRST_NAME`
- `PB_LAST_NAME`
- `PB_EMAIL`
- `PB_COMPANY`
- `PB_TITLE`
- optional: `PB_PHONE`, `PB_COUNTRY`

## Run Examples

Fastest local one-click run:
```bash
~/.claude/skills/pitchbook-report-downloader/run.command
```

Interactive CLI (will prompt for URL):
```bash
cd ~/.claude/skills/pitchbook-report-downloader
npm run interactive
```

1. From report listing page (your main use case):
```bash
cd ~/.claude/skills/pitchbook-report-downloader
set -a; source .env; set +a
npm run download:reports -- \
  --listing-url 'https://pitchbook.com/news/reports?f0=0000018c-ee0d-d110-a9cf-ee5faa970000' \
  --retries 3
```

2. From explicit URLs file:
```bash
cd ~/.claude/skills/pitchbook-report-downloader
set -a; source .env; set +a
npm run download:reports -- \
  --urls-file references/urls.example.txt \
  --retries 3
```

3. Single URL quick test:
```bash
cd ~/.claude/skills/pitchbook-report-downloader
set -a; source .env; set +a
npm run download:reports -- \
  --url 'https://pitchbook.com/news/reports/2025-annual-global-m-a-report' \
  --retries 2
```

## Outputs

Default output folder:
- `./downloads/pitchbook-reports/`

Generated artifacts:
- downloaded report files (`.pdf` or suggested extension)
- failure screenshots (`*.attempt-N.png`)
- run summary JSON (`run-<timestamp>.json`)

## Retry Only Failed URLs

```bash
cd ~/.claude/skills/pitchbook-report-downloader
npm run retry:failed -- --run downloads/pitchbook-reports/run-<timestamp>.json --out failed.txt
set -a; source .env; set +a
npm run download:reports -- --urls-file failed.txt --retries 3
```

## Stability Tips

- Use non-headless mode by default (already default here).
- Keep the same `--profile-dir` for repeat runs so Cloudflare clearance can persist.
- If a run fails, inspect screenshot and JSON log first; then rerun only failed URLs.
- Some pages may submit form but send link via email instead of direct browser download; script will mark this as success-with-note.

## Script Path

- `~/.claude/skills/pitchbook-report-downloader/scripts/download_pitchbook_reports.mjs`
