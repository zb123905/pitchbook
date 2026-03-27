"""
PitchBook Web Scraper
使用 Playwright + Stealth Mode 进行反爬虫检测的网页爬取
"""
import os
import asyncio
import logging
import random
from datetime import datetime, date
from typing import Dict, List, Optional
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from playwright_stealth import Stealth
from fake_useragent import UserAgent

import config

logger = logging.getLogger(__name__)


class PitchBookScraper:
    """
    PitchBook 网页爬虫

    特性：
    - Playwright Stealth 反检测
    - 随机 User-Agent 轮换
    - 真实的浏览器行为模拟
    - 智能错误处理和重试机制
    """

    # URL 白名单
    ALLOWED_DOMAINS = ['pitchbook.com', 'www.pitchbook.com']
    ALLOWED_PATHS = ['/news', '/news/reports', '/news/data-and-tools', '/profiles']

    # 浏览器配置
    VIEWPORT_SIZES = [
        {'width': 1920, 'height': 1080},
        {'width': 1366, 'height': 768},
        {'width': 1440, 'height': 900},
        {'width': 1536, 'height': 864},
    ]

    def __init__(self, headless: bool = True, max_retries: int = 3, fast_fail: bool = False):
        """
        初始化爬虫

        Args:
            headless: 是否使用无头模式
            max_retries: 最大重试次数
            fast_fail: 快速失败模式（403/400错误不重试）
        """
        self.headless = headless
        self.max_retries = max_retries
        self.fast_fail = fast_fail  # 快速失败模式
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.ua = UserAgent()

        # 统计信息
        self.stats = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'retries': 0,
        }

    def _is_valid_url(self, url: str) -> bool:
        """
        验证 URL 是否在白名单内

        Args:
            url: 要验证的 URL

        Returns:
            bool: 是否有效
        """
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            path = parsed.path.lower()

            # 检查域名
            if not any(allowed in domain for allowed in self.ALLOWED_DOMAINS):
                logger.warning(f"URL 不在白名单域名内: {url}")
                return False

            # 检查路径（可选）
            # if not any(path.startswith(allowed) for allowed in self.ALLOWED_PATHS):
            #     logger.warning(f"URL 路径不在白名单内: {url}")
            #     return False

            return True

        except Exception as e:
            logger.error(f"URL 验证失败: {e}")
            return False

    async def initialize(self) -> bool:
        """
        初始化浏览器

        Returns:
            bool: 是否成功
        """
        try:
            self.playwright = await async_playwright().start()

            # 启动 Chromium 浏览器
            self.browser = await self.playwright.chromium.launch(
                headless=self.headless,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-web-security',
                    '--disable-features=IsolateOrigins,site-per-process',
                ]
            )

            # 创建浏览器上下文
            viewport = random.choice(self.VIEWPORT_SIZES)
            self.context = await self.browser.new_context(
                viewport=viewport,
                user_agent=self.ua.random,
                locale='en-US',
                timezone_id='America/New_York',
            )

            # 创建页面
            self.page = await self.context.new_page()

            # 应用 stealth 模式
            stealth = Stealth()
            await stealth.apply_stealth_async(self.page)

            logger.info("浏览器初始化成功")
            return True

        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            return False

    async def _simulate_human_behavior(self):
        """
        模拟人类浏览行为
        """
        try:
            # 随机滚动
            await self.page.evaluate("""
                window.scrollTo({
                    top: Math.random() * 500,
                    behavior: 'smooth'
                });
            """)

            # 随机延迟
            await asyncio.sleep(random.uniform(0.5, 1.5))

        except Exception as e:
            logger.warning(f"行为模拟失败: {e}")

    async def _extract_content(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> Dict:
        """
        从页面提取内容（带日期验证）

        Args:
            start_date: 开始日期（用于过滤）
            end_date: 结束日期（用于过滤）

        Returns:
            包含标题、作者、日期、正文等信息的字典
            如果日期不在范围内，返回包含 skip_reason 的字典
        """
        try:
            # 等待主要内容加载
            await self.page.wait_for_selector('article, main, .content, .post', timeout=10000)

            # 提取标题
            title = await self.page.evaluate("""
                () => {
                    const selectors = [
                        'h1.article-title',
                        'h1.post-title',
                        'h1.entry-title',
                        'h1.title',
                        'h1'
                    ];
                    for (const selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el) return el.textContent.trim();
                    }
                    return document.title;
                }
            """)

            # 提取作者
            author = await self.page.evaluate("""
                () => {
                    const selectors = [
                        '.author-name',
                        '.post-author',
                        '.byline .author',
                        'meta[name="author"]'
                    ];
                    for (const selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el) {
                            return el.textContent ||
                                   el.getAttribute('content') ||
                                   '';
                        }
                    }
                    return '';
                }
            """)

            # 提取发布日期
            date = await self.page.evaluate("""
                () => {
                    const selectors = [
                        'time[datetime]',
                        '.publish-date',
                        '.post-date',
                        'meta[property="article:published_time"]'
                    ];
                    for (const selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el) {
                            return el.getAttribute('datetime') ||
                                   el.getAttribute('content') ||
                                   el.textContent ||
                                   '';
                        }
                    }
                    return '';
                }
            """)

            # 验证日期（如果提供了日期范围）
            if start_date and end_date and date:
                try:
                    # 尝试多种日期格式
                    date_obj = None
                    for fmt in ['%Y-%m-%d', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%SZ',
                                '%Y-%m-%d %H:%M:%S', '%a, %d %b %Y %H:%M:%S %z']:
                        try:
                            date_obj = datetime.strptime(date.strip(), fmt).date()
                            break
                        except ValueError:
                            continue

                    if date_obj and not (start_date <= date_obj <= end_date):
                        logger.info(f"跳过过期内容: 发布日期 {date_obj} 不在范围内 {start_date} - {end_date}")
                        return {
                            'skip_reason': 'out_of_date_range',
                            'pub_date': str(date_obj),
                            'title': '',
                            'content_html': ''
                        }
                except Exception as e:
                    logger.debug(f"日期解析失败，继续处理: {e}")
                    pass  # 日期解析失败，继续处理

            # 提取正文内容（HTML）
            content_html = await self.page.evaluate("""
                () => {
                    const selectors = [
                        'article .content',
                        'article .post-content',
                        'article .entry-content',
                        'main .content',
                        '.post-body'
                    ];
                    for (const selector of selectors) {
                        const el = document.querySelector(selector);
                        if (el) return el.innerHTML;
                    }
                    // 如果找不到具体区域，返回整个 article
                    const article = document.querySelector('article');
                    if (article) return article.innerHTML;
                    return '';
                }
            """)

            # 提取标签
            tags = await self.page.evaluate("""
                () => {
                    const selectors = [
                        '.tags a',
                        '.post-tags a',
                        '.categories a',
                        'meta[property="article:tag"]'
                    ];
                    const tags = [];
                    for (const selector of selectors) {
                        const elements = document.querySelectorAll(selector);
                        if (elements.length > 0) {
                            elements.forEach(el => {
                                const tag = el.textContent ||
                                           el.getAttribute('content') ||
                                           '';
                                if (tag) tags.push(tag.trim());
                            });
                            break;
                        }
                    }
                    return tags;
                }
            """)

            # 计算字数（粗略估计）
            word_count = len(content_html.split())

            return {
                'title': title.strip() if title else '',
                'author': author.strip() if author else '',
                'date': date.strip() if date else '',
                'content_html': content_html,
                'tags': tags if tags else [],
                'word_count': word_count,
                'url': self.page.url,
            }

        except Exception as e:
            logger.error(f"内容提取失败: {e}")
            return {}

    async def scrape_url(self, url: str, retry_count: int = 0,
                        start_date: Optional[date] = None, end_date: Optional[date] = None) -> Optional[Dict]:
        """
        爬取单个 URL（带日期过滤）

        Args:
            url: 要爬取的 URL
            retry_count: 当前重试次数
            start_date: 开始日期（用于过滤）
            end_date: 结束日期（用于过滤）

        Returns:
            包含爬取数据的字典，失败返回 None
            如果日期不在范围内，返回包含 skip_reason 的字典
        """
        # URL 验证
        if not self._is_valid_url(url):
            logger.error(f"无效的 URL: {url}")
            return None

        self.stats['total'] += 1

        try:
            logger.info(f"正在爬取: {url}")

            # 随机延迟模拟人类行为
            delay = random.uniform(3, 7)
            logger.debug(f"等待 {delay:.2f} 秒...")
            await asyncio.sleep(delay)

            # 导航到目标页面
            response = await self.page.goto(
                url,
                wait_until='networkidle',
                timeout=30000
            )

            # 检查 HTTP 状态码
            status = response.status
            logger.info(f"HTTP 状态码: {status}")

            # 快速失败模式：403/400错误不重试
            if self.fast_fail and status in [400, 403, 429]:
                logger.warning(f"快速失败模式：HTTP {status}，跳过该链接")
                self.stats['failed'] += 1
                return None

            if status == 403:
                # 被检测为机器人，切换 User-Agent
                logger.warning("检测到 403 Forbidden，切换 User-Agent")
                await self.context.set_extra_http_headers({
                    'User-Agent': self.ua.random
                })
                raise Exception("403 Forbidden")

            elif status == 429:
                # 速率限制
                wait_time = 60 * (2 ** retry_count)  # 指数退避
                logger.warning(f"检测到 429 Rate Limited，等待 {wait_time} 秒")
                await asyncio.sleep(wait_time)
                raise Exception("429 Rate Limited")

            elif status >= 400:
                raise Exception(f"HTTP {status}")

            # 检查是否有 CAPTCHA
            captcha_keywords = ['captcha', 'verify you are human', 'are you a robot']
            page_text = await self.page.text_content('body')
            if any(keyword in page_text.lower() for keyword in captcha_keywords):
                logger.warning("检测到 CAPTCHA，等待用户处理（最多 2 分钟）")
                print("\n⚠️ 检测到人机验证，请在浏览器中完成验证...")
                await asyncio.sleep(120)  # 等待 2 分钟

            # 模拟人类行为
            await self._simulate_human_behavior()

            # 提取内容（传入日期参数）
            content = await self._extract_content(start_date=start_date, end_date=end_date)

            # 检查是否被跳过（日期过滤）
            if content.get('skip_reason'):
                logger.info(f"⏭️ 跳过页面: {content.get('skip_reason')}")
                return content

            if not content or not content.get('content_html'):
                raise Exception("内容提取失败")

            # 添加爬取时间戳
            content['scraped_at'] = datetime.now().isoformat()
            content['scrape_success'] = True

            self.stats['success'] += 1
            logger.info(f"✅ 成功爬取: {content.get('title', url)[:50]}")

            return content

        except Exception as e:
            logger.error(f"爬取失败: {e}")

            # 重试逻辑
            if retry_count < self.max_retries:
                self.stats['retries'] += 1
                wait_time = random.uniform(5, 10)
                logger.info(f"等待 {wait_time:.2f} 秒后重试 ({retry_count + 1}/{self.max_retries})...")
                await asyncio.sleep(wait_time)
                return await self.scrape_url(url, retry_count + 1, start_date, end_date)

            self.stats['failed'] += 1
            return None

    async def scrape_batch(self, urls: List[str],
                          start_date: Optional[date] = None,
                          end_date: Optional[date] = None) -> List[Dict]:
        """
        批量爬取 URL

        Args:
            urls: URL 列表
            start_date: 开始日期（用于过滤）
            end_date: 结束日期（用于过滤）

        Returns:
            爬取结果列表
        """
        results = []

        for idx, url in enumerate(urls, 1):
            logger.info(f"[{idx}/{len(urls)}] 爬取: {url[:70]}...")

            try:
                result = await self.scrape_url(url, start_date=start_date, end_date=end_date)
                if result and not result.get('skip_reason'):
                    results.append(result)

            except Exception as e:
                logger.error(f"爬取出错: {e}")
                continue

        return results

    async def close(self):
        """清理资源"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()

            logger.info("浏览器资源已清理")

        except Exception as e:
            logger.error(f"资源清理失败: {e}")

    def get_stats(self) -> Dict:
        """获取统计信息"""
        return self.stats.copy()


# ================= 便捷函数 =================

async def scrape_single_url(url: str, headless: bool = True,
                            start_date: Optional[date] = None,
                            end_date: Optional[date] = None,
                            fast_fail: bool = False) -> Optional[Dict]:
    """
    爬取单个 URL 的便捷函数

    Args:
        url: 要爬取的 URL
        headless: 是否使用无头模式
        start_date: 开始日期（用于过滤）
        end_date: 结束日期（用于过滤）
        fast_fail: 快速失败模式（403/400错误不重试）

    Returns:
        爬取数据或 None
    """
    scraper = PitchBookScraper(headless=headless, fast_fail=fast_fail)

    try:
        if not await scraper.initialize():
            return None

        result = await scraper.scrape_url(url, start_date=start_date, end_date=end_date)
        return result

    finally:
        await scraper.close()


async def scrape_multiple_urls(urls: List[str], headless: bool = True,
                              start_date: Optional[date] = None,
                              end_date: Optional[date] = None,
                              fast_fail: bool = False) -> List[Dict]:
    """
    批量爬取 URL 的便捷函数

    Args:
        urls: URL 列表
        headless: 是否使用无头模式
        start_date: 开始日期（用于过滤）
        end_date: 结束日期（用于过滤）
        fast_fail: 快速失败模式（403/400错误不重试）

    Returns:
        爬取结果列表
    """
    scraper = PitchBookScraper(headless=headless, fast_fail=fast_fail)

    try:
        if not await scraper.initialize():
            return []

        results = await scraper.scrape_batch(urls, start_date=start_date, end_date=end_date)
        return results

    finally:
        await scraper.close()
