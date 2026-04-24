#!/usr/bin/env node
import path from 'node:path';
import readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SKILL_DIR = path.resolve(__dirname, '..');
const DEFAULT_LISTING = 'https://pitchbook.com/news/reports?f0=0000018c-ee0d-d110-a9cf-ee5faa970000';

async function ask() {
  const rl = readline.createInterface({ input, output });
  try {
    console.log('PitchBook 下载器（交互模式）');
    console.log('1) 单个报告 URL');
    console.log('2) 报告列表 URL（自动抓取并批量下载）');
    const mode = (await rl.question('请选择模式 [1/2，默认 2]：')).trim() || '2';

    let target = '';
    if (mode === '1') {
      target = (await rl.question('请输入报告 URL：')).trim();
      if (!target) throw new Error('报告 URL 不能为空');
    } else {
      target = (await rl.question(`请输入列表 URL（默认：${DEFAULT_LISTING}）：`)).trim() || DEFAULT_LISTING;
    }

    const retriesRaw = (await rl.question('每个报告最大重试次数（默认 3）：')).trim();
    const retries = retriesRaw ? Number.parseInt(retriesRaw, 10) : 3;
    if (!Number.isFinite(retries) || retries < 1) throw new Error('重试次数必须 >= 1');

    return { mode, target, retries };
  } finally {
    rl.close();
  }
}

function runDownloader({ mode, target, retries }) {
  const script = path.join(SKILL_DIR, 'scripts', 'download_pitchbook_reports.mjs');
  const args = [script, '--retries', String(retries)];

  if (mode === '1') {
    args.push('--url', target);
  } else {
    args.push('--listing-url', target);
  }

  const child = spawn('node', args, {
    cwd: SKILL_DIR,
    stdio: 'inherit',
    env: process.env,
  });

  child.on('exit', (code) => {
    process.exit(code ?? 1);
  });
}

(async () => {
  try {
    const cfg = await ask();
    runDownloader(cfg);
  } catch (err) {
    console.error('[interactive-error]', err instanceof Error ? err.message : String(err));
    process.exit(1);
  }
})();
