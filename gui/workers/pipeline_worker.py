"""
后台工作线程

执行完整的 7 步流程，通过回调通知进度更新
"""
import os
import sys
import asyncio
import logging
from datetime import datetime
from typing import Callable, Optional, Dict, Any

# 添加项目根目录到路径（使用 path_utils 支持打包环境）
from path_utils import get_app_dir, get_user_data_path, ensure_directory
project_root = get_app_dir()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import config
import email_credentials
from mcp_client import MCPClient
from email_processor import EmailProcessor
from report_content_extractor import ReportContentExtractor
from content_analyzer import VCPEContentAnalyzer
from report_generator import WeeklyReportGenerator
from pitchbook_scraper import PitchBookScraper
from markdown_converter import MarkdownConverter
from pdf_converter import PDFConverter


class PipelineWorker:
    """
    后台工作线程 - 执行完整的 VC/PE 分析流程

    使用方法:
        worker = PipelineWorker(config, progress_callback, log_callback)
        results = worker.run()
    """

    # 步骤定义
    STEPS = [
        "连接MCP服务器",
        "读取PitchBook邮件",
        "提取邮件内容和链接",
        "自动下载报告",
        "Web爬取内容",
        "提取报告内容",
        "综合分析",
        "生成报告"
    ]

    def __init__(
        self,
        config_obj: Any,
        progress_callback: Callable[[int, str, str], None],
        log_callback: Callable[[str, str], None],
        stats_callback: Callable[[Dict], None],
        stop_check: Callable[[], bool] = None
    ):
        """
        初始化工作线程

        Args:
            config_obj: PipelineConfig 配置对象
            progress_callback: 进度回调 (step_index, status, message)
            log_callback: 日志回调 (level, message)
            stats_callback: 统计回调 (stats_dict)
            stop_check: 停止检查函数，返回 True 应停止
        """
        self.config = config_obj
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.stats_callback = stats_callback
        self.stop_check = stop_check or (lambda: False)

        self._running = False
        self._results = {}
        self._start_time = None

        # 配置日志（使用 get_user_data_path 确保日志目录正确）
        logs_dir = get_user_data_path('data/logs')
        ensure_directory = os.path.exists(logs_dir) or os.makedirs(logs_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(logs_dir, 'gui_system.log'), encoding='utf-8'),
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _update_progress(self, step: int, status: str, message: str):
        """更新进度"""
        self.progress_callback(step, status, message)

    def _log(self, level: str, message: str):
        """记录日志"""
        self.log_callback(level, message)
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        elif level == "INFO":
            self.logger.info(message)
        else:
            self.logger.debug(message)

    def _update_stats(self, stats: Dict):
        """更新统计信息"""
        if self._start_time:
            stats['elapsed_time'] = (datetime.now() - self._start_time).total_seconds()
        self.stats_callback(stats)

    def _check_stop(self) -> bool:
        """检查是否应停止"""
        return self.stop_check()

    def run(self) -> Dict[str, Any]:
        """
        执行完整流程

        Returns:
            结果字典，包含 success, results, error
        """
        self._running = True
        self._start_time = datetime.now()

        try:
            # 应用配置到 email_credentials
            self._apply_config()

            # 运行异步流程
            results = asyncio.run(self._run_pipeline())

            self._running = False
            return {
                'success': True,
                'results': results,
                'error': None
            }

        except Exception as e:
            self._running = False
            error_msg = str(e)
            self._log("ERROR", f"流程执行失败: {error_msg}")
            return {
                'success': False,
                'results': self._results,
                'error': error_msg
            }

    def _apply_config(self):
        """应用 GUI 配置到 email_credentials"""
        email_credentials.IMAP_CONFIG['email_address'] = self.config.email.email_address
        email_credentials.IMAP_CONFIG['password'] = self.config.email.password
        email_credentials.IMAP_CONFIG['fetch_days'] = self.config.email.fetch_days
        email_credentials.IMAP_CONFIG['max_emails'] = self.config.email.max_emails
        email_credentials.IMAP_CONFIG['enable_scraper'] = self.config.scraper.enable_scraper
        email_credentials.IMAP_CONFIG['fast_fail'] = self.config.scraper.fast_fail
        email_credentials.IMAP_CONFIG['max_scrape_links'] = self.config.scraper.max_scrape_links
        email_credentials.IMAP_CONFIG['scrape_delay_min'] = self.config.scraper.scrape_delay_min
        email_credentials.IMAP_CONFIG['scrape_delay_max'] = self.config.scraper.scrape_delay_max
        email_credentials.IMAP_CONFIG['date_filter_days'] = self.config.scraper.date_filter_days
        email_credentials.IMAP_CONFIG['generate_pdf'] = self.config.analysis.generate_pdf

    async def _run_pipeline(self) -> Dict[str, Any]:
        """执行完整的 7 步流程"""
        results = {
            'emails_count': 0,
            'links_count': 0,
            'pitchbook_links_count': 0,
            'downloaded_count': 0,
            'scraped_count': 0,
            'analyzed_count': 0,
            'output_file': None,
            'report_type': 'Word'
        }

        # ================= 步骤1：连接MCP服务器 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        self._update_progress(0, "running", "正在连接 MCP 邮件服务器...")
        self._log("INFO", f"使用邮箱: {self.config.email.email_address}")

        mcp_client = MCPClient()
        if not mcp_client.connect():
            self._update_progress(0, "error", "MCP 连接失败")
            raise Exception("MCP 连接失败，请检查邮箱配置和 MCP 服务器状态")

        self._update_progress(0, "success", "MCP 服务器连接成功")
        self._log("INFO", "✅ MCP 服务器连接成功")

        # ================= 步骤2：读取PitchBook邮件 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        self._update_progress(1, "running", "正在搜索 PitchBook 邮件...")

        fetch_days = self.config.email.fetch_days
        max_emails = self.config.email.max_emails
        start_date, end_date = email_credentials.get_date_range(fetch_days)

        self._log("INFO", f"📅 邮件日期范围: {start_date} 至 {end_date}")
        self._log("INFO", f"🔍 搜索参数：最近 {fetch_days} 天，最多 {max_emails} 封邮件")

        emails = mcp_client.search_emails(query="PitchBook", limit=max_emails)
        mcp_client.disconnect()

        if not emails:
            self._update_progress(1, "error", "未找到 PitchBook 邮件")
            raise Exception("未找到 PitchBook 邮件，请检查收件箱")

        # 按日期过滤
        filtered_emails = []
        for email in emails:
            email_date = email.get('date', '')
            if email_date and email_credentials.is_within_date_range(email_date, start_date, end_date):
                filtered_emails.append(email)

        results['emails_count'] = len(filtered_emails)
        self._update_progress(1, "success", f"找到 {len(filtered_emails)} 封邮件")
        self._log("INFO", f"✅ 找到 {len(emails)} 封邮件，符合日期范围: {len(filtered_emails)} 封")
        self._update_stats(results)

        emails = filtered_emails

        # ================= 步骤3：提取邮件内容和链接 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        self._update_progress(2, "running", "正在提取邮件内容和链接...")

        processor = EmailProcessor()
        processed_emails = []

        for idx, email in enumerate(emails, 1):
            if self._check_stop():
                raise Exception("用户取消操作")

            email.setdefault('links', [])
            email.setdefault('attachments', [])
            email.setdefault('body', '')
            email.setdefault('html_body', '')
            email.setdefault('source_file', email.get('source_file', f"MCP_{email.get('id', '')}"))
            processed_emails.append(email)

        saved_emails_path = processor.save_processed_emails(processed_emails)
        if saved_emails_path:
            self._log("INFO", f"💾 邮件数据已保存: {saved_emails_path}")

        # 统计链接
        all_links = []
        for email in processed_emails:
            email_date = email.get('date', '')
            for link in email.get('links', []):
                link_with_date = link.copy()
                link_with_date['email_date'] = email_date
                all_links.append(link_with_date)

        pitchbook_links = [link for link in all_links if 'pitchbook.com' in link.get('url', '').lower()]

        results['links_count'] = len(all_links)
        results['pitchbook_links_count'] = len(pitchbook_links)

        self._update_progress(2, "success", f"提取 {len(all_links)} 个链接，其中 {len(pitchbook_links)} 个 PitchBook 链接")
        self._log("INFO", f"🔗 提取链接总数: {len(all_links)}")
        self._log("INFO", f"🔗 PitchBook 链接: {len(pitchbook_links)}")
        self._update_stats(results)

        # ================= 步骤4：自动下载报告 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        self._update_progress(3, "running", "正在尝试下载报告...")

        downloaded_reports = []
        if not pitchbook_links:
            self._update_progress(3, "skipped", "无 PitchBook 链接，跳过下载")
        else:
            self._log("INFO", f"📥 开始下载 {len(pitchbook_links)} 个报告...")

            for idx, link in enumerate(pitchbook_links, 1):
                if self._check_stop():
                    raise Exception("用户取消操作")

                url = link['url']
                try:
                    result = processor.download_report_from_link(url)
                    if result.get('success'):
                        downloaded_reports.append(result)
                        self._log("INFO", f"   ✅ {result['filename']}")
                    else:
                        self._log("DEBUG", f"   ❌ 失败: {result.get('error', '未知错误')}")
                except Exception as e:
                    self._log("DEBUG", f"下载失败: {e}")

            results['downloaded_count'] = len(downloaded_reports)
            self._update_progress(3, "success", f"下载 {len(downloaded_reports)} 个报告")
            self._log("INFO", f"✅ 成功下载 {len(downloaded_reports)} 个报告")
            self._update_stats(results)

        # ================= 步骤5：Web爬取内容 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        self._update_progress(4, "running", "正在爬取网页内容...")

        scraped_results = []

        # 检查是否启用爬虫
        if not self.config.scraper.enable_scraper:
            self._update_progress(4, "skipped", "爬虫功能已禁用")
            self._log("INFO", "⏭️ 爬虫功能已禁用，跳过网页爬取")
        elif pitchbook_links:
            max_scrape = self.config.scraper.max_scrape_links
            date_filter_days = self.config.scraper.date_filter_days
            start_date, end_date = email_credentials.get_date_range(date_filter_days)

            # 按日期过滤链接
            links_to_scrape = []
            for link in pitchbook_links:
                email_date = link.get('email_date', '')
                if email_date and email_credentials.is_within_date_range(email_date, start_date, end_date):
                    links_to_scrape.append(link)

            if max_scrape > 0 and len(links_to_scrape) > max_scrape:
                links_to_scrape = links_to_scrape[:max_scrape]

            delay_avg = (self.config.scraper.scrape_delay_min + self.config.scraper.scrape_delay_max) / 2
            estimated_time = len(links_to_scrape) * delay_avg / 60

            self._log("INFO", f"🕷️ 准备爬取 {len(links_to_scrape)} 个网页...")
            self._log("INFO", f"⏱️ 预计需要 {estimated_time:.1f} 分钟")

            if self.config.scraper.fast_fail:
                self._log("INFO", f"⚡ 快速失败模式已启用（反爬虫页面将跳过）")

            try:
                scraper = PitchBookScraper(headless=True, fast_fail=self.config.scraper.fast_fail)
                if not await scraper.initialize():
                    self._update_progress(4, "error", "爬虫初始化失败")
                else:
                    md_converter = MarkdownConverter()
                    pdf_converter = PDFConverter()

                    for idx, link in enumerate(links_to_scrape, 1):
                        if self._check_stop():
                            await scraper.close()
                            raise Exception("用户取消操作")

                        url = link['url']
                        self._log("INFO", f"[{idx}/{len(links_to_scrape)}] 爬取: {url[:70]}...")

                        try:
                            scraped_data = await scraper.scrape_url(
                                url,
                                start_date=start_date,
                                end_date=end_date
                            )

                            if scraped_data:
                                if scraped_data.get('skip_reason'):
                                    self._log("DEBUG", f"   ⏭️ 跳过: {scraped_data.get('skip_reason')}")
                                    continue

                                md_path = md_converter.convert(scraped_data)
                                pdf_path = pdf_converter.convert(scraped_data)

                                scraped_results.append({
                                    'url': url,
                                    'title': scraped_data.get('title', ''),
                                    'markdown_path': md_path,
                                    'pdf_path': pdf_path,
                                    'word_count': scraped_data.get('word_count', 0),
                                })

                                self._log("INFO", f"   ✅ {scraped_data.get('title', 'N/A')[:50]}")

                        except Exception as e:
                            self._log("DEBUG", f"   ❌ 错误: {e}")
                            continue

                    await scraper.close()

                    results['scraped_count'] = len(scraped_results)
                    self._update_progress(4, "success", f"爬取 {len(scraped_results)} 个页面")
                    self._log("INFO", f"✅ 成功爬取 {len(scraped_results)} 个页面")
                    self._update_stats(results)

            except Exception as e:
                if "用户取消" not in str(e):
                    self._update_progress(4, "error", f"爬取出错: {e}")
                    self._log("WARNING", f"Web 爬取出错: {e}")
        else:
            self._update_progress(4, "skipped", "无 PitchBook 链接")

        # ================= 步骤6：提取报告内容 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        self._update_progress(5, "running", "正在提取报告内容...")

        if downloaded_reports:
            extractor = ReportContentExtractor()
            for report in downloaded_reports:
                if self._check_stop():
                    raise Exception("用户取消操作")
                try:
                    content = extractor.extract_content(report['filepath'])
                    report['extracted_content'] = content
                except Exception as e:
                    report['extracted_content'] = ""

            extracted_count = sum(1 for r in downloaded_reports if r.get('extracted_content'))
            self._update_progress(5, "success", f"提取 {extracted_count} 个报告内容")
            self._log("INFO", f"✅ 成功提取 {extracted_count}/{len(downloaded_reports)} 个报告内容")
        else:
            self._update_progress(5, "skipped", "无下载报告")

        # ================= 步骤6：综合分析 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        self._update_progress(6, "running", "正在进行综合分析...")

        analyzer = VCPEContentAnalyzer(use_llm=self.config.analysis.enable_llm)

        # Analyze emails with progress updates
        email_count = len(processed_emails)
        self._log("INFO", f"🔍 开始分析 {email_count} 封邮件...")

        email_analyses = []
        for idx, email in enumerate(processed_emails, 1):
            if self._check_stop():
                raise Exception("用户取消操作")

            subject = email.get('subject', 'Unknown')[:30]
            self._update_progress(
                6, "running",
                f"正在分析邮件 {idx}/{email_count}: {subject}..."
            )

            try:
                analysis = analyzer.analyze_email(email)
                if analysis:
                    email_analyses.append(analysis)
                    self._log("DEBUG", f"   ✅ [{idx}/{email_count}] {subject}")
            except Exception as e:
                self._log("DEBUG", f"   ❌ [{idx}/{email_count}] 分析失败: {e}")

        self._log("INFO", f"✅ 邮件分析: {len(email_analyses)} 封")

        report_analyses = []
        if downloaded_reports:
            report_analyses = analyzer.analyze_downloaded_reports(downloaded_reports)
            self._log("INFO", f"✅ 报告分析: {len(report_analyses)} 份")

        scraped_analyses = []
        if scraped_results:
            scraped_analyses = analyzer.analyze_scraped_content(scraped_results)
            self._log("INFO", f"✅ 网页内容分析: {len(scraped_analyses)} 篇")

        all_analyses = email_analyses + report_analyses + scraped_analyses
        market_overview = analyzer.generate_market_overview(all_analyses) or {}

        analysis_save_path = analyzer.save_analysis_results(all_analyses)
        if analysis_save_path:
            self._log("INFO", f"💾 分析结果已保存: {analysis_save_path}")

        results['analyzed_count'] = len(all_analyses)
        self._update_progress(6, "success", f"分析 {len(all_analyses)} 个项目")
        self._update_stats(results)

        # ================= 步骤7：生成报告 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        generate_pdf = self.config.analysis.generate_pdf
        report_type = "PDF" if generate_pdf else "Word"

        self._update_progress(7, "running", f"正在生成 {report_type} 报告...")

        try:
            if generate_pdf:
                try:
                    from pdf.pdf_report_generator import PDFReportGenerator
                    generator = PDFReportGenerator(enable_charts=self.config.analysis.enable_charts)
                    output_dir = config.PDF_REPORT_DIR
                    file_ext = 'pdf'
                except ImportError:
                    self._log("WARNING", "PDF 报告生成器不可用，回退到 Word")
                    generate_pdf = False

            if not generate_pdf:
                generator = WeeklyReportGenerator()
                output_dir = config.SUMMARY_REPORT_DIR
                file_ext = 'docx'
                report_type = "Word"

            output_path = os.path.join(
                output_dir,
                f'VC_PE_Weekly_AI分析_{datetime.now().strftime("%Y%m%d_%H%M%S")}.{file_ext}'
            )

            generator.generate_weekly_report(all_analyses, output_path, market_overview)

            results['output_file'] = output_path
            results['report_type'] = report_type

            file_size = os.path.getsize(output_path)
            size_kb = file_size / 1024

            self._update_progress(7, "success", f"{report_type} 报告已生成 ({size_kb:.1f} KB)")
            self._log("INFO", f"✅ {report_type} 报告已生成: {output_path}")
            self._log("INFO", f"   文件大小: {size_kb:.1f} KB")
            self._update_stats(results)

        except Exception as e:
            self._update_progress(7, "error", f"报告生成失败: {e}")
            raise

        self._results = results
        return results

    @property
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._running

    def stop(self):
        """停止运行"""
        self._running = False
