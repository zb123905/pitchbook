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

        # ================= 步骤3.5：自动发现报告链接 =================
        discovered_links = []
        if self.config.download.auto_discover.enable:
            if self._check_stop():
                raise Exception("用户取消操作")

            self._update_progress(2, "running", "正在从 PitchBook 官网发现报告链接...")
            self._log("INFO", "🔍 启用自动发现报告链接功能")

            try:
                from services.pitchbook_discovery import PitchBookLinkDiscovery

                discovery = PitchBookLinkDiscovery()
                if discovery.is_available():
                    self._log("INFO", f"📡 正在搜索报告（最多 {self.config.download.auto_discover.max_links} 个，最近 {self.config.download.auto_discover.recent_days} 天）...")

                    discovered = discovery.discover_report_links(
                        max_links=self.config.download.auto_discover.max_links,
                        recent_days=self.config.download.auto_discover.recent_days
                    )

                    if discovered:
                        self._log("INFO", f"✅ 发现 {len(discovered)} 个报告链接")

                        # 转换为链接格式并添加到列表
                        for item in discovered:
                            discovered_links.append({
                                'url': item['url'],
                                'text': item['title'],
                                'source': 'auto_discovery'
                            })

                        # 显示前3个发现的链接
                        for i, link in enumerate(discovered[:3], 1):
                            title = link.get('title', 'N/A')[:50]
                            self._log("DEBUG", f"   [{i}] {title}")
                    else:
                        self._log("WARNING", "⚠️ 未发现任何报告链接")
                else:
                    self._log("WARNING", "⚠️ 链接发现服务不可用")
            except Exception as e:
                self._log("ERROR", f"❌ 自动发现失败: {e}")

            # 更新链接统计
            if discovered_links:
                pitchbook_links.extend(discovered_links)
                results['pitchbook_links_count'] = len(pitchbook_links)
                self._log("INFO", f"🔗 合并后总链接数: {len(pitchbook_links)}")
                self._update_stats(results)

        # ================= 步骤4：自动下载报告 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        self._update_progress(3, "running", "正在尝试下载报告...")

        downloaded_reports = []

        # 检查是否启用下载
        enable_download = self.config.download.enable_download

        if not pitchbook_links:
            self._update_progress(3, "skipped", "无 PitchBook 链接，跳过下载")
        elif not enable_download:
            self._update_progress(3, "skipped", "文件下载已禁用")
            self._log("INFO", "⏭️ 文件下载已禁用（可在配置中启用）")
        else:
            self._log("INFO", f"📥 开始下载 {len(pitchbook_links)} 个报告...")

            # 检查是否使用 Playwright (已移除，回退到标准下载)
            use_playwright = False  # Playwright 下载器已移除
            playwright_downloader = None
            if use_playwright:
                try:
                    from services.playwright_downloader import PlaywrightDownloader
                    playwright_downloader = PlaywrightDownloader()
                    if playwright_downloader.is_available():
                        self._log("INFO", "🎭 使用 Playwright 下载器（绕过 403 错误）")
                    else:
                        self._log("WARNING", "⚠️ Playwright 不可用，使用标准下载")
                except ImportError:
                    self._log("DEBUG", "Playwright 模块不可用，使用标准下载")

            for idx, link in enumerate(pitchbook_links, 1):
                if self._check_stop():
                    raise Exception("用户取消操作")

                url = link.get('url', '') or ''
                # 安全地获取链接文本
                link_text = link.get('text', '') or url[:50] if url else '无效链接'
                self._log("INFO", f"   [{idx}/{len(pitchbook_links)}] 📥 {link_text}")

                # 跳过无效URL
                if not url:
                    self._log("DEBUG", "   ⏭️ 跳过：空URL")
                    continue

                try:
                    result = {'success': False}

                    # Playwright 优先
                    if use_playwright and playwright_downloader and playwright_downloader.is_available():
                        self._log("DEBUG", "      🎭 尝试 Playwright 下载...")
                        playwright_result = playwright_downloader.download_single(url, retries=1)

                        if playwright_result.get('success'):
                            result = playwright_result
                            self._log("INFO", "      ✅ Playwright 下载成功！")
                        else:
                            error_msg = playwright_result.get('error', '未知')[:50] if playwright_result.get('error') else '未知错误'
                            self._log("DEBUG", f"      ⚠️ Playwright 失败，回退到标准下载: {error_msg}")

                    # 标准下载（Playwright 未启用、不可用或失败时）
                    if not result.get('success'):
                        result = processor.download_report_from_link(url)

                    if result.get('success'):
                        downloaded_reports.append(result)
                        filename = result.get('filename', '未知')
                        self._log("INFO", f"   ✅ {filename}")
                    else:
                        self._log("DEBUG", f"   ❌ 失败: {result.get('error', '未知错误')}")

                except Exception as e:
                    self._log("DEBUG", f"   ❌ 下载异常: {e}")

            results['downloaded_count'] = len(downloaded_reports)
            self._update_progress(3, "success", f"下载 {len(downloaded_reports)} 个报告")
            self._log("INFO", f"✅ 成功下载 {len(downloaded_reports)} 个报告")
            self._update_stats(results)

        # ================= 步骤5：Web爬取内容 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        # 步骤5已移除（原Web爬取功能）
        # 爬虫功能已被移除，直接跳过
        scraped_results = []
        results['scraped_count'] = 0
        self._update_progress(4, "skipped", "爬虫功能已移除")
        self._log("INFO", "⏭️ 爬虫功能已移除")

        # ================= 步骤4：提取报告内容 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        self._update_progress(4, "running", "正在提取报告内容...")

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
            self._update_progress(4, "success", f"提取 {extracted_count} 个报告内容")
            self._log("INFO", f"✅ 成功提取 {extracted_count}/{len(downloaded_reports)} 个报告内容")
        else:
            self._update_progress(4, "skipped", "无下载报告")

        # ================= 步骤5：综合分析 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        self._update_progress(5, "running", "正在进行综合分析...")

        analyzer = VCPEContentAnalyzer(use_llm=self.config.analysis.enable_llm)

        # Analyze emails using analyze_batch method
        email_count = len(processed_emails)
        self._log("INFO", f"🔍 开始分析 {email_count} 封邮件...")

        if self._check_stop():
            raise Exception("用户取消操作")

        self._update_progress(5, "running", f"正在分析 {email_count} 封邮件...")

        email_analyses = []
        try:
            email_analyses = analyzer.analyze_batch(processed_emails)
            self._log("INFO", f"✅ 邮件分析: {len(email_analyses)} 封")
        except Exception as e:
            self._log("ERROR", f"邮件批量分析失败: {e}")
            email_analyses = []

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
        self._update_progress(5, "success", f"分析 {len(all_analyses)} 个项目")
        self._update_stats(results)

        # Empty result warning mechanism
        if len(all_analyses) == 0:
            self._log("WARNING", "⚠️ 警告: 没有成功分析任何内容！")
            self._log("WARNING", "⚠️ 报告将不包含任何实际数据")

        # ================= 步骤6：生成报告 =================
        if self._check_stop():
            raise Exception("用户取消操作")

        report_format = self.config.analysis.report_format
        generate_both = report_format == "both"
        generate_pdf = self.config.analysis.generate_pdf or generate_both

        self._update_progress(5, "running", "正在生成报告...")

        try:
            output_files = []
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # 生成 Word 报告（如果需要）
            if report_format in ["word", "both"]:
                self._update_progress(5, "running", "正在生成 Word 报告...")
                word_generator = WeeklyReportGenerator()
                word_output = os.path.join(
                    config.SUMMARY_REPORT_DIR,
                    f'VC_PE_Weekly_AI分析_{timestamp}.docx'
                )
                word_generator.generate_weekly_report(all_analyses, word_output, market_overview)
                output_files.append(("Word", word_output))
                self._log("INFO", f"✅ Word 报告已生成: {word_output}")

            # 生成 PDF 报告（如果需要）
            if generate_pdf:
                self._update_progress(5, "running", "正在生成 PDF 报告...")
                try:
                    from pdf.pdf_report_generator import PDFReportGenerator
                    pdf_generator = PDFReportGenerator(
                        enable_charts=self.config.analysis.enable_charts,
                        use_llm=self.config.analysis.enable_llm,
                        use_template=False
                    )
                    pdf_output = os.path.join(
                        config.PDF_REPORT_DIR,
                        f'VC_PE_Weekly_AI分析_{timestamp}.pdf'
                    )
                    result = pdf_generator.generate_weekly_report(all_analyses, pdf_output, market_overview)
                    if result and os.path.exists(pdf_output):
                        output_files.append(("PDF", pdf_output))
                        self._log("INFO", f"✅ PDF 报告已生成: {pdf_output}")
                    else:
                        self._log("WARNING", "PDF 报告生成失败（分析结果为空或生成器返回None）")
                except ImportError as e:
                    self._log("WARNING", f"PDF 报告生成器不可用: {e}")

            # 更新结果
            results['output_files'] = output_files
            results['report_formats'] = [f[0] for f in output_files]

            if len(output_files) == 1:
                results['output_file'] = output_files[0][1]
                results['report_type'] = output_files[0][0]

            file_count = len(output_files)
            total_size = sum(os.path.getsize(f[1]) for f in output_files if os.path.exists(f[1])) / 1024

            self._update_progress(5, "success", f"已生成 {file_count} 个报告文件 ({total_size:.1f} KB)")
            self._update_stats(results)

        except Exception as e:
            self._update_progress(5, "error", f"报告生成失败: {e}")
            raise

        # ================= 直接下载功能已移除 =================
        # 直接下载功能已从主流程中移除
        # 请使用 PitchBook 下载面板进行独立下载
        direct_download_results = {
            'direct_downloaded_count': 0,
            'direct_download_errors': 0
        }

        # 合并结果
        results['direct_download'] = direct_download_results

        # 更新总下载统计
        total_downloads = results.get('downloaded_count', 0) + direct_download_results.get('direct_downloaded_count', 0)
        results['total_downloaded'] = total_downloads

        self._results = results
        return results

    @property
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._running

    def stop(self):
        """停止运行"""
        self._running = False

    def _run_direct_download(self) -> int:
        """运行直接下载脚本，返回成功下载数量"""
        import subprocess
        import os

        skill_dir = r"E:\pitch\skills\pitchbook-downloader\package"
        script_path = os.path.join(skill_dir, "scripts", "download_pitchbook_reports.mjs")

        if not os.path.exists(script_path):
            self._log("ERROR", f"❌ 直接下载脚本不存在: {script_path}")
            return 0

        max_count = self.config.download.auto_discover.max_links

        cmd = [
            "node",
            script_path,
            "--listing-url", "https://pitchbook.com/news/reports",
            "--max-from-listing", str(max_count),
            "--retries", "2"
        ]

        self._log("INFO", f"📁 输出目录: {config.FILE_DOWNLOAD_DIR}")
        self._log("INFO", f"📋 最大下载数量: {max_count}")

        result = subprocess.run(
            cmd,
            cwd=skill_dir,
            capture_output=True,
            text=True,
            encoding='utf-8',
            timeout=300
        )

        # 输出日志（限制输出行数）
        if result.stdout:
            lines = result.stdout.split('\n')[:10]
            for line in lines:
                if line.strip() and ('成功' in line or '完成' in line or '报告' in line or '[' in line):
                    self._log("DEBUG", f"  {line.strip()}")

        if result.stderr:
            self._log("DEBUG", f"脚本输出: {result.stderr[:200] if result.stderr else ''}")

        return self._count_recent_downloads()

    def _count_recent_downloads(self) -> int:
        """统计最近下载的文件数量"""
        from datetime import datetime, timedelta

        download_dir = config.FILE_DOWNLOAD_DIR
        if not os.path.exists(download_dir):
            return 0

        now = datetime.now()
        recent_threshold = now - timedelta(minutes=10)

        count = 0
        for filename in os.listdir(download_dir):
            filepath = os.path.join(download_dir, filename)
            if os.path.isfile(filepath):
                mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                if mtime > recent_threshold:
                    count += 1

        return count
