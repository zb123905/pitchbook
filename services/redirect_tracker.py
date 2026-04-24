"""
URL Redirect Tracker for PitchBook Email Links

Tracks PitchBook tracking redirects (url6380.news.pitchbook.com/ls/click?)
to resolve final URLs and extract public content without authentication.
"""
import asyncio
import logging
from typing import Dict, Optional, Any
from urllib.parse import urlparse, urljoin
import re

try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

import config

logger = logging.getLogger(__name__)


class RedirectTracker:
    """
    Tracks URL redirects to resolve final destinations
    """

    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.user_agent = config.DOWNLOAD_USER_AGENT

    async def initialize(self):
        """Initialize Playwright browser"""
        if not PLAYWRIGHT_AVAILABLE:
            logger.warning("Playwright not available, redirect tracking will be limited")
            return False

        if self.browser is None:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage']
            )
            logger.info("RedirectTracker browser initialized")
        return True

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            self.browser = None
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None

    async def resolve_url(self, url: str, max_redirects: int = 10) -> Dict[str, Any]:
        """
        Track redirects and resolve final URL with content preview

        Args:
            url: The tracking URL to resolve
            max_redirects: Maximum number of redirects to follow

        Returns:
            Dictionary with:
                - success: bool
                - final_url: str (final resolved URL)
                - redirect_chain: list[str] (intermediate URLs)
                - status_code: int
                - content_type: str
                - is_file: bool (direct file link)
                - title: str (page title if HTML)
                - preview_text: str (content preview)
                - error: str (if failed)
        """
        result = {
            'success': False,
            'original_url': url,
            'final_url': url,
            'redirect_chain': [],
            'status_code': 0,
            'content_type': '',
            'is_file': False,
            'title': '',
            'preview_text': '',
            'error': ''
        }

        try:
            # Check if it's a direct file link
            if self._is_direct_file_link(url):
                result['is_file'] = True
                result['final_url'] = url
                result['success'] = True
                result['content_type'] = self._get_file_type(url)
                logger.info(f"Direct file link detected: {url[:80]}...")
                return result

            # Use browser to track redirects
            if self.browser:
                browser_result = await self._resolve_with_browser(url, max_redirects)
                result.update(browser_result)
            else:
                # Fallback to HTTP-based tracking
                http_result = await self._resolve_with_http(url, max_redirects)
                result.update(http_result)

        except Exception as e:
            result['error'] = str(e)
            logger.error(f"Error resolving URL {url[:80]}...: {e}")

        return result

    async def _resolve_with_browser(self, url: str, max_redirects: int) -> Dict[str, Any]:
        """Resolve URL using Playwright browser"""
        result = {
            'success': False,
            'final_url': url,
            'redirect_chain': [],
            'status_code': 0,
            'content_type': '',
            'title': '',
            'preview_text': '',
            'error': ''
        }

        try:
            context = await self.browser.new_context(
                user_agent=self.user_agent,
                viewport={'width': 1920, 'height': 1080}
            )
            page = await context.new_page()

            # Track redirects
            redirect_chain = []
            final_url = url

            def handle_response(response):
                nonlocal final_url
                if 300 <= response.status < 400:
                    redirect_chain.append(response.url)
                    final_url = response.headers.get('location', final_url)

            page.on('response', handle_response)

            # Navigate with redirect tracking
            response = await page.goto(
                url,
                wait_until='domcontentloaded',
                timeout=30000
            )

            if response:
                result['status_code'] = response.status
                result['content_type'] = response.headers.get('content-type', '')

            # Get final URL after all redirects
            final_url = page.url
            result['final_url'] = final_url
            result['redirect_chain'] = redirect_chain

            # Extract page content
            if response and response.ok:
                result['success'] = True

                # Check if it's a file download
                content_type = result['content_type'].lower()
                if any(ct in content_type for ct in ['application/pdf', 'application/vnd', 'application/octet-stream']):
                    result['is_file'] = True
                    result['content_type'] = content_type
                else:
                    # Extract page title and preview
                    try:
                        title = await page.title()
                        result['title'] = title

                        # Extract preview text from common selectors
                        preview = await self._extract_page_preview(page)
                        result['preview_text'] = preview

                    except Exception as e:
                        logger.debug(f"Could not extract page content: {e}")

            await context.close()

        except Exception as e:
            result['error'] = str(e)
            logger.debug(f"Browser resolution error: {e}")

        return result

    async def _resolve_with_http(self, url: str, max_redirects: int) -> Dict[str, Any]:
        """Resolve URL using HTTP requests (fallback)"""
        import requests

        result = {
            'success': False,
            'final_url': url,
            'redirect_chain': [],
            'status_code': 0,
            'content_type': '',
            'title': '',
            'preview_text': '',
            'error': ''
        }

        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            })

            response = session.get(url, allow_redirects=True, timeout=15, stream=True)

            result['status_code'] = response.status_code
            result['content_type'] = response.headers.get('content-type', '')
            result['final_url'] = response.url
            result['redirect_chain'] = response.history

            if response.ok:
                result['success'] = True

                content_type = result['content_type'].lower()
                if any(ct in content_type for ct in ['application/pdf', 'application/vnd', 'application/octet-stream']):
                    result['is_file'] = True
                elif 'text/html' in content_type:
                    # Extract title from HTML
                    try:
                        import re
                        title_match = re.search(r'<title[^>]*>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
                        if title_match:
                            result['title'] = title_match.group(1).strip()
                    except:
                        pass

        except Exception as e:
            result['error'] = str(e)

        return result

    async def _extract_page_preview(self, page: Page) -> str:
        """Extract preview text from page"""
        preview_parts = []

        try:
            # Try common article/content selectors
            selectors = [
                'article',
                '[role="article"]',
                '.article-content',
                '.post-content',
                '.entry-content',
                'main',
                '.content',
                'h1', 'h2'
            ]

            for selector in selectors:
                try:
                    elements = await page.query_selector_all(selector)
                    for el in elements[:3]:  # Limit to first 3 elements
                        text = await el.inner_text()
                        if text and len(text.strip()) > 20:
                            preview_parts.append(text.strip()[:500])
                            if len('\n'.join(preview_parts)) > 500:
                                break
                except:
                    continue

                if preview_parts:
                    break

        except Exception as e:
            logger.debug(f"Preview extraction error: {e}")

        return '\n\n'.join(preview_parts)[:1000] if preview_parts else ''

    @staticmethod
    def _is_direct_file_link(url: str) -> bool:
        """Check if URL is a direct file link"""
        url_lower = url.lower()
        file_extensions = ['.pdf', '.xlsx', '.xls', '.docx', '.doc', '.csv']
        return any(url_lower.endswith(ext) for ext in file_extensions)

    @staticmethod
    def _get_file_type(url: str) -> str:
        """Get file type from URL"""
        url_lower = url.lower()
        if '.pdf' in url_lower:
            return 'application/pdf'
        elif any(ext in url_lower for ext in ['.xlsx', '.xls']):
            return 'application/vnd.ms-excel'
        elif any(ext in url_lower for ext in ['.docx', '.doc']):
            return 'application/vnd.ms-word'
        elif '.csv' in url_lower:
            return 'text/csv'
        return 'application/octet-stream'

    async def batch_resolve(self, urls: list[str]) -> list[Dict[str, Any]]:
        """
        Resolve multiple URLs in batch

        Args:
            urls: List of URLs to resolve

        Returns:
            List of resolution results
        """
        results = []

        await self.initialize()

        for i, url in enumerate(urls):
            logger.info(f"Resolving URL [{i+1}/{len(urls)}]: {url[:80]}...")
            result = await self.resolve_url(url)
            results.append(result)

        await self.close()

        # Summary statistics
        successful = sum(1 for r in results if r['success'])
        files = sum(1 for r in results if r['is_file'])
        pages = successful - files

        logger.info(f"Redirect tracking complete: {successful}/{len(urls)} successful ({files} files, {pages} pages)")

        return results


class PitchBookLinkResolver:
    """
    Specialized resolver for PitchBook email tracking links
    """

    # PitchBook tracking domain patterns
    TRACKING_PATTERNS = [
        r'url\d+\.news\.pitchbook\.com/ls/click',
        r'news\.pitchbook\.com/ls/click',
        r'pitchbook\.com/.*url=',
    ]

    @classmethod
    def is_pitchbook_tracking_link(cls, url: str) -> bool:
        """Check if URL is a PitchBook tracking link"""
        url_lower = url.lower()
        return any(re.search(pattern, url_lower) for pattern in cls.TRACKING_PATTERNS)

    @classmethod
    def extract_direct_links(cls, url: str) -> list[str]:
        """
        Try to extract direct links from tracking URL parameters

        Args:
            url: Tracking URL

        Returns:
            List of potential direct URLs found
        """
        direct_links = []

        try:
            from urllib.parse import parse_qs, urlparse

            parsed = urlparse(url)
            params = parse_qs(parsed.query)

            # Common parameter names that might contain URLs
            url_params = ['url', 'link', 'redirect', 'target', 'u', 'goto']

            for param in url_params:
                if param in params:
                    for value in params[param]:
                        if value.startswith('http'):
                            direct_links.append(value)

        except Exception as e:
            logger.debug(f"Could not extract direct links: {e}")

        return direct_links


# Singleton instance
_tracker_instance: Optional[RedirectTracker] = None


async def get_tracker() -> RedirectTracker:
    """Get or create singleton tracker instance"""
    global _tracker_instance
    if _tracker_instance is None:
        _tracker_instance = RedirectTracker()
    return _tracker_instance
