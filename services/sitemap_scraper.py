"""
Sitemap 抓取器 - 无需认证

从 PitchBook sitemap.xml 发现公开内容 URL
参考: jakobgreenfeld/fun_and_profit
"""
import requests
import gzip
from io import BytesIO
from typing import List
import xml.etree.ElementTree as ET
import logging

logger = logging.getLogger(__name__)


class SitemapScraper:
    """Sitemap 抓取器 - 无需认证

    注意：PitchBook 可能会阻止对 sitemap 的访问（403 Forbidden）
    这是他们的反爬措施，绕过需要账号认证。
    """

    SITEMAP_URL = "https://pitchbook.com/sitemap.xml"
    SITEMAP_NS = {'sitemap': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    def __init__(self, timeout: int = 10):
        """
        初始化 sitemap 抓取器

        Args:
            timeout: HTTP 请求超时时间（秒）
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def scrape_sitemap(self, sitemap_url: str = None, retry_count: int = 2) -> List[str]:
        """
        从 sitemap.xml 提取所有 URL

        Args:
            sitemap_url: Sitemap URL，默认使用 PitchBook 主 sitemap
            retry_count: 失败重试次数

        Returns:
            URL 列表
        """
        if sitemap_url is None:
            sitemap_url = self.SITEMAP_URL

        for attempt in range(retry_count + 1):
            try:
                logger.info(f"正在抓取 sitemap: {sitemap_url} (尝试 {attempt + 1}/{retry_count + 1})")
                response = self.session.get(sitemap_url, timeout=self.timeout)

                if response.status_code == 403:
                    logger.warning(f"403 Forbidden: {sitemap_url}")
                    if attempt < retry_count:
                        logger.info(f"等待后重试...")
                        import time
                        time.sleep(5)
                        continue
                    return []

                response.raise_for_status()

                root = ET.fromstring(response.content)
                urls = []

                # 尝试使用命名空间
                for elem in root.findall('.//sitemap:loc', self.SITEMAP_NS):
                    urls.append(elem.text)

                # 如果没有找到，尝试不带命名空间
                if not urls:
                    for elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                        urls.append(elem.text)

                # 如果还是没找到，尝试简单的 loc 标签
                if not urls:
                    for elem in root.findall('.//loc'):
                        urls.append(elem.text)

                logger.info(f"从 sitemap 找到 {len(urls)} 个 URL")
                return urls

            except requests.RequestException as e:
                logger.error(f"抓取 sitemap 失败: {e}")
                if attempt < retry_count:
                    logger.info(f"重试...")
                    import time
                    time.sleep(5)
                    continue
                return []
            except ET.ParseError as e:
                logger.error(f"解析 sitemap XML 失败: {e}")
                return []

        return []

    def download_and_extract_gz_file(self, url: str) -> List[str]:
        """
        下载并解压 .gz 压缩的 sitemap

        Args:
            url: 压缩 sitemap 的 URL

        Returns:
            URL 列表
        """
        try:
            logger.info(f"正在下载压缩 sitemap: {url}")
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            # 解压内容
            content = gzip.decompress(response.content)

            root = ET.fromstring(content)
            urls = []

            # 尝试使用命名空间
            for elem in root.findall('.//sitemap:loc', self.SITEMAP_NS):
                urls.append(elem.text)

            # 如果没有找到，尝试不带命名空间
            if not urls:
                for elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                    urls.append(elem.text)

            # 如果还是没找到，尝试简单的 loc 标签
            if not urls:
                for elem in root.findall('.//loc'):
                    urls.append(elem.text)

            logger.info(f"从压缩 sitemap 提取 {len(urls)} 个 URL")
            return urls

        except requests.RequestException as e:
            logger.error(f"下载压缩 sitemap 失败: {e}")
            return []
        except gzip.BadGzipFile:
            logger.error(f"文件不是有效的 gzip 格式: {url}")
            return []
        except ET.ParseError as e:
            logger.error(f"解析压缩 sitemap XML 失败: {e}")
            return []

    def get_public_content_urls(self, keywords: List[str] = None) -> List[str]:
        """
        获取所有公开内容 URL

        Args:
            keywords: URL 关键词过滤器，默认查找 public-profiles 和 news

        Returns:
            公开内容 URL 列表
        """
        if keywords is None:
            keywords = ['public-profiles', 'news', 'reports']

        sitemap_urls = self.scrape_sitemap()
        public_urls = []

        for url in sitemap_urls:
            # 检查 URL 是否包含关键词
            if any(keyword in url for keyword in keywords):
                logger.info(f"找到匹配的 sitemap: {url}")
                extracted_urls = self.download_and_extract_gz_file(url)
                public_urls.extend(extracted_urls)

        logger.info(f"总共找到 {len(public_urls)} 个公开内容 URL")
        return public_urls

    def filter_by_date(self, urls: List[str], max_urls: int = 100) -> List[str]:
        """
        过滤 URL（按数量限制）

        Args:
            urls: URL 列表
            max_urls: 最大返回数量

        Returns:
            过滤后的 URL 列表
        """
        return urls[:max_urls]


# 便捷函数
def get_pitchbook_public_urls(max_urls: int = 50) -> List[str]:
    """
    获取 PitchBook 公开内容 URL

    Args:
        max_urls: 最大返回数量

    Returns:
        公开内容 URL 列表
    """
    scraper = SitemapScraper()
    urls = scraper.get_public_content_urls()
    return scraper.filter_by_date(urls, max_urls)


if __name__ == "__main__":
    # 测试
    logging.basicConfig(level=logging.INFO)
    urls = get_pitchbook_public_urls(10)
    print(f"找到 {len(urls)} 个公开 URL:")
    for url in urls:
        print(f"  - {url}")
