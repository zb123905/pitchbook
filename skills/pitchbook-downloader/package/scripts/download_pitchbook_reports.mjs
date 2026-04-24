#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { chromium } from 'playwright';

const DEFAULT_LISTING_URL = 'https://pitchbook.com/news/reports?f0=0000018c-ee0d-d110-a9cf-ee5faa970000';
const DEFAULT_TIMEOUT_MS = 90000;
const DEFAULT_RETRIES = 3;

function parseArgs(argv) {
  const args = {
    urls: [],
    listingUrl: null,
    urlsFile: null,
    outputDir: path.resolve(os.homedir(), 'Downloads', 'pitchbook-reports'),
    profileDir: path.resolve(os.homedir(), '.cache', 'pitchbook-playwright-profile'),
    retries: DEFAULT_RETRIES,
    timeoutMs: DEFAULT_TIMEOUT_MS,
    headless: false,
    maxFromListing: 0,
  };

  for (let i = 0; i < argv.length; i += 1) {
    const k = argv[i];
    const v = argv[i + 1];
    if (k === '--url' && v) {
      args.urls.push(v);
      i += 1;
    } else if (k === '--listing-url' && v) {
      args.listingUrl = v;
      i += 1;
    } else if (k === '--urls-file' && v) {
      args.urlsFile = v;
      i += 1;
    } else if (k === '--output-dir' && v) {
      args.outputDir = path.resolve(v);
      i += 1;
    } else if (k === '--profile-dir' && v) {
      args.profileDir = path.resolve(v);
      i += 1;
    } else if (k === '--retries' && v) {
      args.retries = Math.max(1, Number.parseInt(v, 10) || DEFAULT_RETRIES);
      i += 1;
    } else if (k === '--timeout-ms' && v) {
      args.timeoutMs = Math.max(10000, Number.parseInt(v, 10) || DEFAULT_TIMEOUT_MS);
      i += 1;
    } else if (k === '--headless') {
      args.headless = true;
    } else if (k === '--max-from-listing' && v) {
      args.maxFromListing = Math.max(0, Number.parseInt(v, 10) || 0);
      i += 1;
    } else if (k === '--help' || k === '-h') {
      printHelp();
      process.exit(0);
    }
  }

  return args;
}

function printHelp() {
  console.log(`PitchBook 报告下载器

用法:
  node scripts/download_pitchbook_reports.mjs [options]

参数:
  --url <url>               添加单个报告 URL（可重复）
  --urls-file <path>        从文件读取 URL（每行一个）
  --listing-url <url>       从报告列表页抓取链接
  --max-from-listing <n>    限制抓取数量（0 表示不限制）
  --output-dir <path>       下载目录
  --profile-dir <path>      持久化浏览器目录
  --retries <n>             每个报告最大重试次数
  --timeout-ms <ms>         超时时间（毫秒）
  --headless                无头模式运行（默认否）
  --help, -h                显示帮助

环境变量（表单自动填写）:
  PB_FIRST_NAME（必填）
  PB_LAST_NAME（必填）
  PB_EMAIL（必填）
  PB_COMPANY（必填）
  PB_TITLE（必填）
  PB_PHONE（可选）
  PB_COUNTRY（可选）
`);
}

function requireEnv(name) {
  const value = process.env[name]?.trim();
  if (!value) {
    throw new Error(`缺少必填环境变量：${name}`);
  }
  return value;
}

function buildProfile() {
  return {
    firstName: requireEnv('PB_FIRST_NAME'),
    lastName: requireEnv('PB_LAST_NAME'),
    email: requireEnv('PB_EMAIL'),
    company: requireEnv('PB_COMPANY'),
    title: requireEnv('PB_TITLE'),
    phone: process.env.PB_PHONE?.trim() || '',
    country: process.env.PB_COUNTRY?.trim() || '',
  };
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function jitter(min = 250, max = 900) {
  const ms = Math.floor(Math.random() * (max - min + 1)) + min;
  await sleep(ms);
}

function normalizeUrl(url) {
  try {
    const u = new URL(url.trim());
    u.hash = '';
    return u.toString();
  } catch {
    return null;
  }
}

function loadUrlsFromFile(filePath) {
  const full = path.resolve(filePath);
  const raw = fs.readFileSync(full, 'utf8');
  return raw
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line && !line.startsWith('#'));
}

async function waitForCloudflareToSettle(page, timeoutMs) {
  const started = Date.now();
  while (Date.now() - started < timeoutMs) {
    const title = await page.title().catch(() => '');
    const bodyText = await page.locator('body').innerText().catch(() => '');
    const blocked =
      /just a moment/i.test(title) ||
      /enable javascript and cookies to continue/i.test(bodyText) ||
      /verify you are human/i.test(bodyText);

    if (!blocked) return;
    await sleep(1500);
  }
  throw new Error('Cloudflare 验证在超时时间内未通过');
}

async function extractReportLinksFromListing(page, listingUrl, timeoutMs, maxFromListing) {
  await page.goto(listingUrl, { waitUntil: 'domcontentloaded', timeout: timeoutMs });
  await waitForCloudflareToSettle(page, Math.min(timeoutMs, 60000));

  await page.waitForTimeout(1800);

  const links = await page.$$eval('a[href]', (anchors) => {
    const base = 'https://pitchbook.com';
    const out = [];
    for (const a of anchors) {
      const href = a.getAttribute('href');
      if (!href) continue;
      let abs;
      try {
        abs = new URL(href, base).toString();
      } catch {
        continue;
      }
      if (!abs.includes('/news/reports/')) continue;
      if (/\/news\/reports\/?($|\?)/.test(abs)) continue;
      out.push(abs);
    }
    return out;
  });

  const unique = Array.from(new Set(links));
  if (maxFromListing > 0) {
    return unique.slice(0, maxFromListing);
  }
  return unique;
}

async function maybeClickDownloadTrigger(page) {
  const candidates = [
    () => page.getByRole('button', { name: /download|get report|access report|request report/i }).first(),
    () => page.getByRole('link', { name: /download|get report|access report|request report/i }).first(),
    () => page.locator('button:has-text("Download")').first(),
    () => page.locator('a:has-text("Download")').first(),
    () => page.locator('[data-testid*="download" i]').first(),
    () => page.locator('[class*="download" i]').first(),
  ];

  for (const pick of candidates) {
    const locator = pick();
    try {
      if (await locator.count()) {
        const visible = await locator.isVisible().catch(() => false);
        if (!visible) continue;
        await locator.click({ timeout: 5000 });
        await jitter(300, 900);
        return true;
      }
    } catch {
      // keep trying
    }
  }
  return false;
}

async function fillFirstMatched(page, selectors, value) {
  if (!value) return false;
  for (const selector of selectors) {
    const locator = page.locator(selector).first();
    try {
      if (!(await locator.count())) continue;
      if (!(await locator.isVisible().catch(() => false))) continue;
      await locator.click({ timeout: 4000 });
      await locator.fill(value, { timeout: 4000 });
      await jitter(120, 300);
      return true;
    } catch {
      // try next selector
    }
  }
  return false;
}

async function selectCountryIfPossible(page, country) {
  if (!country) return false;
  const selectors = [
    'select[name*="country" i]',
    'select[id*="country" i]',
  ];

  for (const selector of selectors) {
    const el = page.locator(selector).first();
    try {
      if (!(await el.count())) continue;
      if (!(await el.isVisible().catch(() => false))) continue;
      await el.selectOption({ label: country }).catch(async () => {
        await el.selectOption({ value: country });
      });
      await jitter(120, 300);
      return true;
    } catch {
      // continue
    }
  }
  return false;
}

async function checkConsentBoxes(page) {
  const boxes = page.locator('input[type="checkbox"]');
  const count = await boxes.count();
  for (let i = 0; i < count; i += 1) {
    const cb = boxes.nth(i);
    try {
      if (!(await cb.isVisible().catch(() => false))) continue;
      if (!(await cb.isChecked().catch(() => true))) {
        await cb.check({ timeout: 2500 }).catch(async () => {
          await cb.click({ timeout: 2500 });
        });
      }
    } catch {
      // ignore optional boxes
    }
  }
}

async function clickSubmit(page) {
  const candidates = [
    () => page.getByRole('button', { name: /download|submit|get report|access report|request/i }).first(),
    () => page.locator('button[type="submit"]').first(),
    () => page.locator('input[type="submit"]').first(),
    () => page.locator('button:has-text("Submit")').first(),
    () => page.locator('button:has-text("Download")').first(),
  ];

  for (const pick of candidates) {
    const locator = pick();
    try {
      if (!(await locator.count())) continue;
      if (!(await locator.isVisible().catch(() => false))) continue;
      await locator.click({ timeout: 5000 });
      return true;
    } catch {
      // try next
    }
  }
  return false;
}

async function savePdfUrlWithSession(page, pdfUrl, outputDir, base) {
  try {
    const res = await page.context().request.get(pdfUrl, { timeout: 30000 });
    if (!res.ok()) return null;
    const bytes = await res.body();
    const dest = path.join(outputDir, `${base}.pdf`);
    fs.writeFileSync(dest, bytes);
    return dest;
  } catch {
    return null;
  }
}

async function tryDirectDownload(page, outputDir, base) {
  const candidates = [
    () => page.getByRole('button', { name: /download pdf|download data|download/i }).first(),
    () => page.getByRole('link', { name: /download pdf|download data|download/i }).first(),
    () => page.locator('button:has-text("Download PDF")').first(),
    () => page.locator('a:has-text("Download PDF")').first(),
    () => page.locator('button:has-text("Download Data")').first(),
    () => page.locator('a:has-text("Download Data")').first(),
  ];

  for (const pick of candidates) {
    const locator = pick();
    try {
      if (!(await locator.count())) continue;
      if (!(await locator.isVisible().catch(() => false))) continue;
      const downloadPromise = page.waitForEvent('download', { timeout: 12000 }).catch(() => null);
      const popupPromise = page.context().waitForEvent('page', { timeout: 12000 }).catch(() => null);
      const samePagePdfPromise = page
        .waitForURL(/\.pdf(\?|$)/i, { timeout: 12000 })
        .then(() => page.url())
        .catch(() => null);
      await locator.click({ timeout: 4000 });

      const dl = await downloadPromise;
      if (dl) {
        const suggested = dl.suggestedFilename() || `${base}.pdf`;
        const ext = path.extname(suggested) || '.pdf';
        const dest = path.join(outputDir, `${base}${ext}`);
        await dl.saveAs(dest);
        return dest;
      }

      const samePagePdfUrl = await samePagePdfPromise;
      if (samePagePdfUrl) {
        const saved = await savePdfUrlWithSession(page, samePagePdfUrl, outputDir, base);
        if (saved) return saved;
      }

      const popup = await popupPromise;
      if (popup) {
        await popup.waitForLoadState('domcontentloaded', { timeout: 15000 }).catch(() => undefined);
        const popupUrl = popup.url();
        if (/\.pdf(\?|$)/i.test(popupUrl)) {
          const saved = await savePdfUrlWithSession(popup, popupUrl, outputDir, base);
          if (saved) {
            await popup.close().catch(() => undefined);
            return saved;
          }
        }
      }

      // No downloadable artifact found from this clickable target.
      continue;
    } catch {
      // continue
    }
  }
  return null;
}

function safeFileBaseFromUrl(url) {
  const u = new URL(url);
  const slug = u.pathname.split('/').filter(Boolean).pop() || 'report';
  return slug.replace(/[^a-zA-Z0-9._-]/g, '_');
}

async function runOneReport(context, reportUrl, profile, args) {
  const page = await context.newPage();
  const base = safeFileBaseFromUrl(reportUrl);

  for (let attempt = 1; attempt <= args.retries; attempt += 1) {
    const attemptTag = `${base}.attempt-${attempt}`;
    const shotPath = path.join(args.outputDir, `${attemptTag}.png`);

    try {
      console.log(`\n[${base}] 第 ${attempt}/${args.retries} 次尝试`);
      await page.goto(reportUrl, { waitUntil: 'domcontentloaded', timeout: args.timeoutMs });
      await waitForCloudflareToSettle(page, Math.min(args.timeoutMs, 75000));
      await jitter(600, 1200);

      const directBefore = await tryDirectDownload(page, args.outputDir, base);
      if (directBefore) {
        console.log(`[成功] 直接下载完成：${directBefore}`);
        await page.close();
        return { ok: true, url: reportUrl, file: directBefore, attempts: attempt };
      }

      await maybeClickDownloadTrigger(page);

      const firstFilled = await fillFirstMatched(page, [
        'input[name*="first" i]',
        'input[id*="first" i]',
        'input[placeholder*="first" i]',
      ], profile.firstName);

      const lastFilled = await fillFirstMatched(page, [
        'input[name*="last" i]',
        'input[id*="last" i]',
        'input[placeholder*="last" i]',
      ], profile.lastName);

      const emailFilled = await fillFirstMatched(page, [
        'input[type="email"]',
        'input[name*="email" i]',
        'input[id*="email" i]',
      ], profile.email);

      const companyFilled = await fillFirstMatched(page, [
        'input[name*="company" i]',
        'input[id*="company" i]',
        'input[placeholder*="company" i]',
      ], profile.company);

      const titleFilled = await fillFirstMatched(page, [
        'input[name*="title" i]',
        'input[id*="title" i]',
        'input[placeholder*="title" i]',
        'input[name*="job" i]',
      ], profile.title);

      await fillFirstMatched(page, [
        'input[type="tel"]',
        'input[name*="phone" i]',
        'input[id*="phone" i]',
      ], profile.phone);

      await selectCountryIfPossible(page, profile.country);
      await checkConsentBoxes(page);

      const downloadPromise = page.waitForEvent('download', { timeout: 45000 }).catch(() => null);
      const submitted = await clickSubmit(page);
      if (!submitted) {
        throw new Error('填写后未找到可点击的提交/下载按钮');
      }

      const dl = await downloadPromise;
      if (dl) {
        const ext = path.extname(dl.suggestedFilename() || '.pdf') || '.pdf';
        const dest = path.join(args.outputDir, `${base}${ext}`);
        await dl.saveAs(dest);
        console.log(`[成功] 已下载：${dest}`);
        await page.close();
        return { ok: true, url: reportUrl, file: dest, attempts: attempt };
      }

      const directAfter = await tryDirectDownload(page, args.outputDir, base);
      if (directAfter) {
        console.log(`[成功] 提交后直接下载完成：${directAfter}`);
        await page.close();
        return { ok: true, url: reportUrl, file: directAfter, attempts: attempt };
      }

      const body = await page.locator('body').innerText().catch(() => '');
      if (/thank you|check your email|download should begin/i.test(body)) {
        console.log(`[提示] 已提交表单，但未捕获直接下载事件：${reportUrl}`);
        await page.screenshot({ path: shotPath, fullPage: true });
        await page.close();
        return {
          ok: true,
          url: reportUrl,
          file: null,
          attempts: attempt,
          note: '已提交，但未捕获直接下载事件，请查看截图。',
          screenshot: shotPath,
        };
      }

      // Some PitchBook flows submit without a direct download event or explicit success text.
      // If no clear validation error appears and we filled most required fields, mark uncertain success.
      const filledRequiredCount = [firstFilled, lastFilled, emailFilled, companyFilled, titleFilled]
        .filter(Boolean).length;
      const hasValidationError = /required|invalid|please enter|error/i.test(body);
      if (!hasValidationError && filledRequiredCount >= 4) {
        await page.screenshot({ path: shotPath, fullPage: true });
        console.log(`[提示] 已提交，但无明确下载信号；标记为可能成功：${reportUrl}`);
        await page.close();
        return {
          ok: true,
          url: reportUrl,
          file: null,
          attempts: attempt,
          note: '表单已提交，但下载信号不明确，请查看截图或检查邮箱。',
          screenshot: shotPath,
        };
      }

      throw new Error('已点击提交，但未检测到下载事件或明确成功信号');
    } catch (err) {
      const message = err instanceof Error ? err.message : String(err);
      console.error(`[重试] ${message}`);
      await page.screenshot({ path: shotPath, fullPage: true }).catch(() => undefined);
      if (attempt === args.retries) {
        await page.close();
        return { ok: false, url: reportUrl, error: message, screenshot: shotPath, attempts: attempt };
      }
      await page.goto('about:blank').catch(() => undefined);
      await sleep(1300 * attempt);
    }
  }

  await page.close();
  return { ok: false, url: reportUrl, error: 'Unknown error' };
}

function dedupe(arr) {
  return Array.from(new Set(arr));
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const profile = buildProfile();

  ensureDir(args.outputDir);
  ensureDir(args.profileDir);

  const allUrls = [...args.urls];
  if (args.urlsFile) {
    allUrls.push(...loadUrlsFromFile(args.urlsFile));
  }

  const normalized = dedupe(allUrls.map(normalizeUrl).filter(Boolean));
  const needsListing = normalized.length === 0;
  const listingUrl = args.listingUrl || DEFAULT_LISTING_URL;

  const context = await chromium.launchPersistentContext(args.profileDir, {
    headless: args.headless,
    acceptDownloads: true,
    viewport: { width: 1366, height: 960 },
    userAgent:
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
    locale: 'en-US',
  });

  const urls = [...normalized];

  if (needsListing || args.listingUrl) {
    const crawlPage = await context.newPage();
    try {
      const listingUrls = await extractReportLinksFromListing(
        crawlPage,
        listingUrl,
        args.timeoutMs,
        args.maxFromListing,
      );
      urls.push(...listingUrls);
      console.log(`[信息] 列表页抓取到 ${listingUrls.length} 个报告链接`);
    } finally {
      await crawlPage.close();
    }
  }

  const finalUrls = dedupe(urls.map(normalizeUrl).filter(Boolean));
  if (!finalUrls.length) {
    throw new Error('未找到可处理的报告 URL，请提供 --url / --urls-file 或有效 --listing-url。');
  }

  console.log(`[信息] 本次待处理报告数：${finalUrls.length}`);

  const results = [];
  for (const reportUrl of finalUrls) {
    const result = await runOneReport(context, reportUrl, profile, args);
    results.push(result);
  }

  await context.close();

  const okCount = results.filter((r) => r.ok).length;
  const failCount = results.length - okCount;
  const reportPath = path.join(args.outputDir, `run-${Date.now()}.json`);
  fs.writeFileSync(reportPath, JSON.stringify(results, null, 2), 'utf8');

  console.log('\n=== 运行总结 ===');
  console.log(`成功：${okCount}`);
  console.log(`失败：${failCount}`);
  console.log(`结果日志：${reportPath}`);

  if (failCount > 0) {
    process.exitCode = 2;
  }
}

main().catch((err) => {
  console.error('[致命错误]', err instanceof Error ? err.message : err);
  process.exit(1);
});
