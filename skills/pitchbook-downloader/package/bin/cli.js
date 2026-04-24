#!/usr/bin/env node
const path = require('path');
const { spawnSync } = require('child_process');

const repoRoot = path.resolve(__dirname, '..');
const installScript = path.join(repoRoot, 'install.sh');
const installScriptPs1 = path.join(repoRoot, 'install.ps1');

function run(cmd, args, opts = {}) {
  const ret = spawnSync(cmd, args, { stdio: 'inherit', ...opts });
  if (ret.error) process.exit(1);
  if (ret.status !== 0) process.exit(ret.status || 1);
}

function isWindows() {
  return process.platform === 'win32';
}

function runInstall() {
  if (isWindows()) {
    run('powershell', ['-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', installScriptPs1, '-Force'], { cwd: repoRoot });
    return;
  }
  run('bash', [installScript], { cwd: repoRoot });
}

function argValue(name) {
  const args = process.argv.slice(2);
  const i = args.indexOf(name);
  if (i >= 0 && i + 1 < args.length) return args[i + 1];
  return null;
}

function hasArg(name) {
  return process.argv.slice(2).includes(name);
}

function printHelp() {
  console.log('pitchbook-report-downloader-skill');
  console.log('');
  console.log('Install skill only:');
  console.log('  npx pitchbook-report-downloader-skill install');
  console.log('');
  console.log('Install and run interactive:');
  console.log('  npx pitchbook-report-downloader-skill run');
  console.log('');
  console.log('Install and run single URL:');
  console.log('  npx pitchbook-report-downloader-skill run --url <report-url> --retries 3');
  console.log('');
  console.log('Install and run listing URL:');
  console.log('  npx pitchbook-report-downloader-skill run --listing-url <reports-url> --retries 3');
}

const cmd = process.argv[2];
if (!cmd || cmd === '--help' || cmd === '-h') {
  printHelp();
  process.exit(0);
}

if (cmd === 'install') {
  runInstall();
  process.exit(0);
}

if (cmd === 'run') {
  runInstall();

  const home = process.env.USERPROFILE || process.env.HOME || '';
  const base = isWindows()
    ? path.join(home, '.claude', 'skills', 'pitchbook-report-downloader')
    : path.join(home, '.claude', 'skills', 'pitchbook-report-downloader');

  const interactiveScript = path.join(base, 'scripts', 'interactive_download.mjs');
  const downloaderScript = path.join(base, 'scripts', 'download_pitchbook_reports.mjs');

  const retries = argValue('--retries');
  const url = argValue('--url');
  const listingUrl = argValue('--listing-url');

  if (url || listingUrl) {
    const args = [downloaderScript];
    if (url) args.push('--url', url);
    if (listingUrl) args.push('--listing-url', listingUrl);
    if (retries) args.push('--retries', retries);
    run('node', args, { cwd: base });
  } else {
    run('node', [interactiveScript], { cwd: base });
  }
  process.exit(0);
}

printHelp();
process.exit(1);
