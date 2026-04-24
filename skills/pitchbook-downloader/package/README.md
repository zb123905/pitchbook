# pitchbook-report-downloader-skill

Automate PitchBook report downloads by opening report pages, filling the lead form, and attempting direct file download with retries and diagnostics.

## Important

- Do not run `npx ...` inside Claude chat input.
- Run install/download commands in your system terminal.
- `/pitchbook-report-downloader` is not a built-in Claude slash command.

## Install (Git clone style)

Project-level:

```bash
mkdir -p .claude/skills
git clone <YOUR_REPO_URL> .claude/skills/pitchbook-report-downloader
bash .claude/skills/pitchbook-report-downloader/install.sh
```

Global:

```bash
git clone <YOUR_REPO_URL> ~/.claude/skills/pitchbook-report-downloader
bash ~/.claude/skills/pitchbook-report-downloader/install.sh
```

## Install / run with npm (npx)

Install skill files only:

```bash
npx pitchbook-report-downloader-skill install
```

Install and run interactive:

```bash
npx pitchbook-report-downloader-skill run
```

Install and run single URL:

```bash
npx pitchbook-report-downloader-skill run --url 'https://pitchbook.com/news/reports/2025-annual-global-m-a-report' --retries 3
```

Install and run listing URL:

```bash
npx pitchbook-report-downloader-skill run --listing-url 'https://pitchbook.com/news/reports?f0=0000018c-ee0d-d110-a9cf-ee5faa970000' --retries 3
```

## Local quick start

```bash
cd ~/.codex/skills/pitchbook-report-downloader
./bootstrap.sh
./run.command
```

## Output

Downloads/logs are written to:

```text
downloads/pitchbook-reports/
```
