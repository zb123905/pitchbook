"""
CloudScraper Service - 使用 CloudScraper 库绕过 403 Forbidden 错误

参考: https://github.com/VenomouS/cloudscraper

特性:
- 自动绕过 Cloudflare 保护
- 自动处理 403 Forbidden 错误
- 智能会话管理
- 支持 JavaScript 挑战
"""
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional
from urllib.parse import urlparse, unquote
import hashlib
import re

try:
    import cloudscraper
except ImportError:
    cloudscraper = None
    logging.warning("CloudScraper 未安装，请运行: pip install cloudscraper")

import config

logger = logging.getLogger(__name__)


class CloudScraperService:
    """
    CloudScraper 服务封装

    使用 CloudScraper 库绕过常见的反爬虫保护，包括：
    - Cloudflare
    - 403 Forbidden
    - JavaScript 挑战
    """

    def __init__(
        self,
        browser: str = 'chrome',
        delay: Optional[int] = None,
        proxy: Optional[Dict[str, str]] = None
    ):
        """
        初始化 CloudScraper 服务

        Args:
            browser: 模拟的浏览器类型 ('chrome', 'firefox', 'opera')
            delay: 请求延迟（秒），None 使用默认值
            proxy: 代理配置 {'http': 'http://proxy', 'https': 'https://proxy'}
        """
        if cloudscraper is None:
            raise ImportError("CloudScraper 未安装，请运行: pip install cloudscraper")

        self.browser = browser
        self.delay = delay
        self.proxy = proxy

        # 创建 CloudScraper 实例
        self.scraper = self._create_scraper()

        # 统计信息
        self.stats = {
            'total_requests': 0,
            'success': 0,
            'failed': 0,
            'forbidden': 0,  # 403
            'cloudflare_challenges': 0,
        }

        logger.info(f"CloudScraper 服务已初始化 (browser={browser})")

    def _create_scraper(self):
        """创建 CloudScraper 实例"""
        try:
            scraper = cloudscraper.create_scraper(
                browser=self.browser,
                delay=self.delay,
                # CloudScraper 会自动处理以下情况：
                # - Cloudflare 保护
                # - 403 Forbidden
                # - JavaScript 挑战
                # - User-Agent 检测
            )

            # 设置代理（如果提供）
            if self.proxy:
                scraper.proxies = self.proxy
                logger.info(f"CloudScraper 使用代理: {self.proxy.get('http', 'N/A')}")

            return scraper
        except Exception as e:
            logger.error(f"创建 CloudScraper 失败: {e}")
            raise

    def download_report(
        self,
        url: str,
        save_dir: Optional[str] = None
    ) -> Dict[str, any]:
        """
        下载报告文件

        Args:
            url: 报告 URL
            save_dir: 保存目录

        Returns:
            包含下载结果的字典
        """
        if save_dir is None:
            save_dir = config.FILE_DOWNLOAD_DIR

        self.stats['total_requests'] += 1

        result = {
            'success': False,
            'url': url,
            'method': 'cloudscraper',
            'error': None,
            'filepath': None,
            'filename': None,
            'file_size_bytes': 0,
            'started_at': datetime.now().isoformat()
        }

        try:
            logger.info(f"[CloudScraper] 下载报告: {url[:100]}...")

            # 使用 CloudScraper 请求
            response = self.scraper.get(
                url,
                timeout=config.DOWNLOAD_TIMEOUT,
                stream=True
            )

            # 检查状态码
            if response.status_code == 403:
                self.stats['forbidden'] += 1
                self.stats['failed'] += 1
                result['error'] = '403 Forbidden - CloudScraper 无法绕过'
                result['status_code'] = 403
                logger.warning(f"[CloudScraper] 403 Forbidden: {url[:100]}...")
                return result

            elif response.status_code != 200:
                self.stats['failed'] += 1
                result['error'] = f'HTTP {response.status_code}'
                result['status_code'] = response.status_code
                logger.warning(f"[CloudScraper] HTTP {response.status_code}: {url[:100]}...")
                return result

            # 下载内容
            content = response.content

            # 验证内容
            if len(content) < 100:
                self.stats['failed'] += 1
                result['error'] = '内容太小，可能不是有效文件'
                logger.warning(f"[CloudScraper] 内容太小: {len(content)} bytes")
                return result

            # 生成文件名
            filename = self._generate_filename(url, response)
            filepath = os.path.join(save_dir, filename)

            # 保存文件
            with open(filepath, 'wb') as f:
                f.write(content)

            self.stats['success'] += 1
            result.update({
                'success': True,
                'filepath': filepath,
                'filename': filename,
                'file_size_bytes': len(content),
                'content_type': response.headers.get('Content-Type', 'unknown'),
                'status_code': response.status_code,
                'completed_at': datetime.now().isoformat()
            })

            logger.info(f"[CloudScraper] 下载成功: {filename} ({len(content)} bytes)")
            return result

        except Exception as e:
            self.stats['failed'] += 1
            result['error'] = str(e)
            logger.error(f"[CloudScraper] 下载失败: {e}")
            return result

    def scrape_content(self, url: str) -> Dict[str, any]:
        """
        抓取网页内容

        Args:
            url: 要抓取的 URL

        Returns:
            包含抓取结果的字典
        """
        self.stats['total_requests'] += 1

        result = {
            'success': False,
            'url': url,
            'method': 'cloudscraper',
            'error': None,
            'title': None,
            'content': None,
            'status_code': None
        }

        try:
            logger.info(f"[CloudScraper] 抓取内容: {url[:100]}...")

            response = self.scraper.get(
                url,
                timeout=config.DOWNLOAD_TIMEOUT
            )

            # 检查状态码
            if response.status_code == 403:
                self.stats['forbidden'] += 1
                self.stats['failed'] += 1
                result['error'] = '403 Forbidden'
                result['status_code'] = 403
                return result

            elif response.status_code != 200:
                self.stats['failed'] += 1
                result['error'] = f'HTTP {response.status_code}'
                result['status_code'] = response.status_code
                return result

            # 使用 BeautifulSoup 解析
            try:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')

                # 提取标题
                title_tag = soup.find('title')
                title = title_tag.get_text(strip=True) if title_tag else ""

                # 提取主要内容
                content_selectors = [
                    'article',
                    '[class*="content"]',
                    '[class*="article"]',
                    'main'
                ]

                content = ""
                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        # 移除脚本和样式
                        for script in element(['script', 'style', 'nav', 'footer']):
                            script.decompose()
                        content = element.get_text(separator='\n', strip=True)
                        if len(content) > 100:
                            break

                self.stats['success'] += 1
                result.update({
                    'success': True,
                    'title': title,
                    'content': content,
                    'status_code': response.status_code,
                    'word_count': len(content.split()) if content else 0
                })

                logger.info(f"[CloudScraper] 抓取成功: {title[:50]}... ({result['word_count']} words)")
                return result

            except ImportError:
                # 如果没有 BeautifulSoup，返回原始 HTML
                self.stats['success'] += 1
                result.update({
                    'success': True,
                    'content': response.text,
                    'status_code': response.status_code
                })
                return result

        except Exception as e:
            self.stats['failed'] += 1
            result['error'] = str(e)
            logger.error(f"[CloudScraper] 抓取失败: {e}")
            return result

    def download_batch(
        self,
        urls: List[str],
        save_dir: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """
        批量下载报告

        Args:
            urls: URL 列表
            save_dir: 保存目录

        Returns:
            下载结果列表
        """
        results = []

        for url in urls:
            result = self.download_report(url, save_dir)
            results.append(result)

        success_count = sum(1 for r in results if r['success'])
        logger.info(f"[CloudScraper] 批量下载完成: {success_count}/{len(urls)} 成功")

        return results

    def scrape_batch(self, urls: List[str]) -> List[Dict[str, any]]:
        """
        批量抓取内容

        Args:
            urls: URL 列表

        Returns:
            抓取结果列表
        """
        results = []

        for url in urls:
            result = self.scrape_content(url)
            results.append(result)

        success_count = sum(1 for r in results if r['success'])
        logger.info(f"[CloudScraper] 批量抓取完成: {success_count}/{len(urls)} 成功")

        return results

    def _generate_filename(self, url: str, response) -> str:
        """从 URL 或响应头生成文件名"""
        # 尝试 Content-Disposition
        content_disposition = response.headers.get('Content-Disposition', '')
        if content_disposition:
            filename_match = re.search(r'filename[*]?=["\']?([^"\';\r\n]+)', content_disposition)
            if filename_match:
                filename = unquote(filename_match.group(1))
                if filename and len(filename) > 3:
                    return filename

        # 从 URL 提取
        url_path = urlparse(url).path
        filename = os.path.basename(url_path)

        if filename and len(filename) > 3:
            return unquote(filename)

        # 生成哈希文件名
        url_hash = hashlib.md5(url.encode()).hexdigest()[:8]

        # 检测文件类型
        url_lower = url.lower()
        if '.pdf' in url_lower:
            return f"cloudscraper_report_{url_hash}.pdf"
        elif any(ext in url_lower for ext in ['.xlsx', '.xls']):
            return f"cloudscraper_report_{url_hash}.xlsx"
        else:
            return f"cloudscraper_report_{url_hash}.bin"

    def get_stats(self) -> Dict[str, int]:
        """获取统计信息"""
        return self.stats.copy()

    def reset_stats(self):
        """重置统计信息"""
        self.stats = {
            'total_requests': 0,
            'success': 0,
            'failed': 0,
            'forbidden': 0,
            'cloudflare_challenges': 0,
        }

    def close(self):
        """关闭会话"""
        if self.scraper:
            self.scraper.close()
            logger.info("CloudScraper 会话已关闭")


# 便捷函数
def create_cloudscraper_service(
    browser: str = 'chrome',
    proxy: Optional[Dict[str, str]] = None
) -> CloudScraperService:
    """
    创建 CloudScraper 服务

    Args:
        browser: 浏览器类型
        proxy: 代理配置

    Returns:
        CloudScraperService 实例
    """
    return CloudScraperService(browser=browser, proxy=proxy)


def test_cloudscraper():
    """测试 CloudScraper 是否工作"""
    logging.basicConfig(level=logging.INFO)

    try:
        service = create_cloudscraper_service()

        # 测试简单的请求
        result = service.scrape_content("https://pitchbook.com")

        if result['success']:
            print("CloudScraper 测试成功！")
            print(f"标题: {result.get('title', 'N/A')[:100]}...")
        else:
            print(f"CloudScraper 测试失败: {result.get('error', 'Unknown')}")

        service.close()
        return result

    except Exception as e:
        print(f"CloudScraper 测试异常: {e}")
        return {'success': False, 'error': str(e)}


if __name__ == "__main__":
    test_cloudscraper()
