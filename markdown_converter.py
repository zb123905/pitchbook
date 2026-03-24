"""
Markdown Converter
将爬取的 HTML 内容转换为 Markdown 格式
"""
import os
import re
import logging
from datetime import datetime
from typing import Dict, Optional
from markdownify import markdownify as md

import config

logger = logging.getLogger(__name__)


class MarkdownConverter:
    """
    Markdown 转换器

    将爬取的 HTML 内容转换为结构化的 Markdown 文档，
    包含元数据头部和格式化的内容。
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化转换器

        Args:
            output_dir: 输出目录，默认使用配置中的 SCRAPER_MARKDOWN_DIR
        """
        self.output_dir = output_dir or config.SCRAPER_MARKDOWN_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    def _sanitize_filename(self, filename: str, max_length: int = 100) -> str:
        """
        清理文件名，移除非法字符

        Args:
            filename: 原始文件名
            max_length: 最大长度

        Returns:
            安全的文件名
        """
        # 移除或替换非法字符
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = filename.strip()

        # 限制长度
        if len(filename) > max_length:
            filename = filename[:max_length]

        # 如果为空，使用时间戳
        if not filename:
            filename = datetime.now().strftime('%Y%m%d_%H%M%S')

        return filename

    def _generate_metadata_header(self, data: Dict) -> str:
        """
        生成元数据头部

        Args:
            data: 爬取的数据字典

        Returns:
            Markdown 格式的元数据头部
        """
        lines = []

        # 标题
        title = data.get('title', 'Untitled')
        lines.append(f"# {title}\n")

        # 元数据
        metadata = []

        if data.get('author'):
            metadata.append(f"**Author:** {data['author']}")

        if data.get('date'):
            metadata.append(f"**Date:** {data['date']}")

        if data.get('tags'):
            tags_str = ', '.join(data['tags'])
            metadata.append(f"**Tags:** {tags_str}")

        if data.get('word_count'):
            metadata.append(f"**Word Count:** {data['word_count']:,}")

        if metadata:
            lines.append('\n'.join(metadata))
            lines.append('')

        lines.append('---\n')

        return '\n'.join(lines)

    def _generate_footer(self, data: Dict) -> str:
        """
        生成页脚

        Args:
            data: 爬取的数据字典

        Returns:
            Markdown 格式的页脚
        """
        lines = ['\n---']

        if data.get('url'):
            lines.append(f"\n*Source: {data['url']}*")

        if data.get('scraped_at'):
            scraped_at = data['scraped_at']
            # 格式化时间戳
            try:
                dt = datetime.fromisoformat(scraped_at)
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                lines.append(f"*Scraped at: {formatted_time}*")
            except:
                lines.append(f"*Scraped at: {scraped_at}*")

        return '\n'.join(lines)

    def convert(self, data: Dict, custom_filename: Optional[str] = None) -> Optional[str]:
        """
        转换爬取的数据为 Markdown 文件

        Args:
            data: 包含爬取内容的字典
            custom_filename: 自定义文件名（不含扩展名）

        Returns:
            保存的文件路径，失败返回 None
        """
        try:
            # 提取 HTML 内容
            html_content = data.get('content_html', '')

            if not html_content:
                logger.error("没有可转换的 HTML 内容")
                return None

            # 转换为 Markdown
            markdown_content = md(html_content)

            # 生成完整的 Markdown 文档
            full_document = []

            # 添加元数据头部
            full_document.append(self._generate_metadata_header(data))

            # 添加正文内容
            full_document.append(markdown_content)

            # 添加页脚
            full_document.append(self._generate_footer(data))

            final_content = '\n'.join(full_document)

            # 生成文件名
            if custom_filename:
                filename = self._sanitize_filename(custom_filename)
            else:
                # 使用标题生成文件名
                title = data.get('title', 'untitled')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = self._sanitize_filename(f"{timestamp}_{title}")

            # 确保文件名以 .md 结尾
            if not filename.endswith('.md'):
                filename += '.md'

            # 保存文件
            filepath = os.path.join(self.output_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(final_content)

            logger.info(f"Markdown 文件已保存: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Markdown 转换失败: {e}")
            return None

    def convert_batch(self, data_list: list) -> list:
        """
        批量转换

        Args:
            data_list: 包含爬取数据的字典列表

        Returns:
            成功保存的文件路径列表
        """
        results = []

        for idx, data in enumerate(data_list, 1):
            logger.info(f"[{idx}/{len(data_list)}] 转换为 Markdown...")

            try:
                filepath = self.convert(data)
                if filepath:
                    results.append(filepath)

            except Exception as e:
                logger.error(f"转换失败: {e}")
                continue

        return results


# ================= 便捷函数 =================

def convert_to_markdown(data: Dict, output_dir: Optional[str] = None) -> Optional[str]:
    """
    转换单个数据为 Markdown 的便捷函数

    Args:
        data: 爬取的数据
        output_dir: 输出目录

    Returns:
        文件路径或 None
    """
    converter = MarkdownConverter(output_dir)
    return converter.convert(data)


def convert_batch_to_markdown(data_list: list, output_dir: Optional[str] = None) -> list:
    """
    批量转换为 Markdown 的便捷函数

    Args:
        data_list: 爬取的数据列表
        output_dir: 输出目录

    Returns:
        文件路径列表
    """
    converter = MarkdownConverter(output_dir)
    return converter.convert_batch(data_list)
