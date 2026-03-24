"""
PDF Converter
将爬取的 HTML 内容转换为 PDF 格式
"""
import os
import re
import logging
from datetime import datetime
from typing import Dict, Optional

try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False
    logging.warning("pdfkit 未安装，PDF 转换功能将不可用")

import config

logger = logging.getLogger(__name__)


class PDFConverter:
    """
    PDF 转换器

    将爬取的 HTML 内容转换为格式化的 PDF 文档，
    包含专业的样式和元数据。
    """

    # PDF 配置选项
    PDF_OPTIONS = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': 'UTF-8',
        'no-outline': None,
        'enable-local-file-access': None,
    }

    # CSS 样式
    CSS_STYLES = """
    <style>
        body {
            font-family: 'Georgia', 'Times New Roman', serif;
            line-height: 1.6;
            color: #333;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }

        .metadata {
            background-color: #f5f5f5;
            padding: 15px;
            border-left: 4px solid #007acc;
            margin-bottom: 30px;
            font-size: 12px;
        }

        .metadata h2 {
            margin-top: 0;
            color: #007acc;
            font-size: 18px;
        }

        .metadata p {
            margin: 5px 0;
        }

        h1 {
            color: #222;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }

        h2 {
            color: #333;
            margin-top: 30px;
        }

        a {
            color: #007acc;
            text-decoration: none;
        }

        a:hover {
            text-decoration: underline;
        }

        code {
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }

        pre {
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }

        blockquote {
            border-left: 4px solid #ddd;
            padding-left: 20px;
            margin-left: 0;
            color: #666;
            font-style: italic;
        }

        table {
            border-collapse: collapse;
            width: 100%;
            margin: 20px 0;
        }

        table, th, td {
            border: 1px solid #ddd;
        }

        th {
            background-color: #007acc;
            color: white;
            padding: 12px;
            text-align: left;
        }

        td {
            padding: 10px;
        }

        .footer {
            margin-top: 50px;
            padding-top: 20px;
            border-top: 1px solid #ddd;
            font-size: 10px;
            color: #999;
            text-align: center;
        }

        img {
            max-width: 100%;
            height: auto;
        }
    </style>
    """

    def __init__(self, output_dir: Optional[str] = None):
        """
        初始化转换器

        Args:
            output_dir: 输出目录，默认使用配置中的 SCRAPER_PDF_DIR
        """
        self.output_dir = output_dir or config.SCRAPER_PDF_DIR
        os.makedirs(self.output_dir, exist_ok=True)

        if not PDFKIT_AVAILABLE:
            logger.error("pdfkit 未安装，无法生成 PDF")

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

    def _generate_html_document(self, data: Dict) -> str:
        """
        生成完整的 HTML 文档

        Args:
            data: 爬取的数据字典

        Returns:
            完整的 HTML 文档字符串
        """
        html_parts = []

        # HTML 头部
        html_parts.append("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>PitchBook Article</title>
        """)

        # 添加 CSS 样式
        html_parts.append(self.CSS_STYLES)

        html_parts.append("""
        </head>
        <body>
        """)

        # 元数据区块
        html_parts.append('<div class="metadata">')
        html_parts.append('<h2>Article Information</h2>')

        if data.get('title'):
            html_parts.append(f'<p><strong>Title:</strong> {data["title"]}</p>')

        if data.get('author'):
            html_parts.append(f'<p><strong>Author:</strong> {data["author"]}</p>')

        if data.get('date'):
            html_parts.append(f'<p><strong>Date:</strong> {data["date"]}</p>')

        if data.get('tags'):
            tags_str = ', '.join(data['tags'])
            html_parts.append(f'<p><strong>Tags:</strong> {tags_str}</p>')

        if data.get('word_count'):
            html_parts.append(f'<p><strong>Word Count:</strong> {data["word_count"]:,}</p>')

        html_parts.append('</div>')

        # 标题
        if data.get('title'):
            html_parts.append(f'<h1>{data["title"]}</h1>')

        # 正文内容
        html_parts.append(data.get('content_html', ''))

        # 页脚
        html_parts.append('<div class="footer">')
        html_parts.append('<p>--- Generated by VC/PE PitchBook Automation System ---</p>')

        if data.get('url'):
            html_parts.append(f'<p>Source: <a href="{data["url"]}">{data["url"]}</a></p>')

        if data.get('scraped_at'):
            scraped_at = data['scraped_at']
            try:
                dt = datetime.fromisoformat(scraped_at)
                formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                html_parts.append(f'<p>Scraped at: {formatted_time}</p>')
            except:
                html_parts.append(f'<p>Scraped at: {scraped_at}</p>')

        html_parts.append('</div>')

        # HTML 尾部
        html_parts.append("""
        </body>
        </html>
        """)

        return '\n'.join(html_parts)

    def convert(self, data: Dict, custom_filename: Optional[str] = None) -> Optional[str]:
        """
        转换爬取的数据为 PDF 文件

        Args:
            data: 包含爬取内容的字典
            custom_filename: 自定义文件名（不含扩展名）

        Returns:
            保存的文件路径，失败返回 None
        """
        if not PDFKIT_AVAILABLE:
            logger.error("pdfkit 不可用，无法生成 PDF")
            return None

        try:
            # 生成 HTML 文档
            html_content = self._generate_html_document(data)

            # 生成文件名
            if custom_filename:
                filename = self._sanitize_filename(custom_filename)
            else:
                # 使用标题生成文件名
                title = data.get('title', 'untitled')
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = self._sanitize_filename(f"{timestamp}_{title}")

            # 确保文件名以 .pdf 结尾
            if not filename.endswith('.pdf'):
                filename += '.pdf'

            # PDF 文件路径
            filepath = os.path.join(self.output_dir, filename)

            # 临时 HTML 文件路径
            temp_html_path = os.path.join(config.SCRAPER_CACHE_DIR, f"temp_{filename}.html")
            os.makedirs(os.path.dirname(temp_html_path), exist_ok=True)

            # 保存临时 HTML 文件
            with open(temp_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            # 转换为 PDF
            pdfkit.from_file(
                temp_html_path,
                filepath,
                options=self.PDF_OPTIONS
            )

            # 删除临时文件
            try:
                os.remove(temp_html_path)
            except:
                pass

            logger.info(f"PDF 文件已保存: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"PDF 转换失败: {e}")
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
            logger.info(f"[{idx}/{len(data_list)}] 转换为 PDF...")

            try:
                filepath = self.convert(data)
                if filepath:
                    results.append(filepath)

            except Exception as e:
                logger.error(f"转换失败: {e}")
                continue

        return results


# ================= 便捷函数 =================

def convert_to_pdf(data: Dict, output_dir: Optional[str] = None) -> Optional[str]:
    """
    转换单个数据为 PDF 的便捷函数

    Args:
        data: 爬取的数据
        output_dir: 输出目录

    Returns:
        文件路径或 None
    """
    converter = PDFConverter(output_dir)
    return converter.convert(data)


def convert_batch_to_pdf(data_list: list, output_dir: Optional[str] = None) -> list:
    """
    批量转换为 PDF 的便捷函数

    Args:
        data_list: 爬取的数据列表
        output_dir: 输出目录

    Returns:
        文件路径列表
    """
    converter = PDFConverter(output_dir)
    return converter.convert_batch(data_list)
