#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

function usage() {
  console.log(`Usage:
  node scripts/retry_failed_from_run.mjs --run <run-json> [--out <urls-file>]
`);
}

const args = process.argv.slice(2);
let runPath = '';
let outPath = '';

for (let i = 0; i < args.length; i += 1) {
  if (args[i] === '--run' && args[i + 1]) {
    runPath = args[i + 1];
    i += 1;
  } else if (args[i] === '--out' && args[i + 1]) {
    outPath = args[i + 1];
    i += 1;
  } else if (args[i] === '--help' || args[i] === '-h') {
    usage();
    process.exit(0);
  }
}

if (!runPath) {
  usage();
  process.exit(1);
}

const fullRun = path.resolve(runPath);
const raw = fs.readFileSync(fullRun, 'utf8');
const data = JSON.parse(raw);
if (!Array.isArray(data)) {
  throw new Error('Run JSON must be an array');
}

const failed = data
  .filter((item) => item && item.ok === false && typeof item.url === 'string' && item.url)
  .map((item) => item.url);

const unique = Array.from(new Set(failed));
if (!outPath) {
  const baseDir = path.dirname(fullRun);
  outPath = path.join(baseDir, `failed-${Date.now()}.txt`);
}

fs.writeFileSync(path.resolve(outPath), `${unique.join('\n')}\n`, 'utf8');
console.log(`Failed URL count: ${unique.length}`);
console.log(`Output file: ${path.resolve(outPath)}`);
