"""
VC/PE PitchBook 报告自动化系统（纯MCP方案）
完整流程：MCP读取邮件 → 提取链接 → 爬取网页 → 自动下载报告 → 提取内容 → 综合分析 → 生成报告
"""
import os
import sys
import logging
import asyncio
from datetime import datetime, timedelta

# 加载环境变量 (必须在其他导入之前)
from dotenv import load_dotenv
load_dotenv()

# 导入项目模块
import config
import email_credentials
from mcp_client import MCPClient
from email_processor import EmailProcessor
from report_content_extractor import ReportContentExtractor
from content_analyzer import VCPEContentAnalyzer
from report_generator import WeeklyReportGenerator

# 导入 GUI 配置模型
from gui.models.config_model import PipelineConfig

# 导入 PDF 报告生成器 (Phase 1) - Lazy import
PDF_AVAILABLE = True

# ================= 日志配置 =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(config.LOGS_DIR, 'system.log'), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================= 配置参数 =================
EMAIL_ADDRESS = email_credentials.IMAP_CONFIG.get('email_address', '')
EMAIL_PASSWORD = email_credentials.IMAP_CONFIG.get('password', '')


async def main():
    """纯MCP方案主流程（支持async）"""
    logger.info("=== VC/PE PitchBook 报告自动化系统（纯MCP方案） ===")

    print("""
╔══════════════════════════════════════════════════════════════╗
║         VC/PE PitchBook 报告自动化系统                       ║
║         Pure MCP Solution                                     ║
╚══════════════════════════════════════════════════════════════╝
    """)

    # 加载 GUI 配置（如果存在）
    gui_config_path = PipelineConfig.get_default_path()
    gui_config = None
    if os.path.exists(gui_config_path):
        gui_config = PipelineConfig.load(gui_config_path)
        logger.info(f"已加载 GUI 配置: {gui_config_path}")
    else:
        logger.info("未找到 GUI 配置文件，使用 email_credentials.py 配置")

    # ================= 步骤1：连接MCP服务器 =================
    print("\n" + "="*70)
    print("步骤1/7: 连接MCP服务器")
    print("="*70)

    if not EMAIL_PASSWORD:
        logger.error("未配置邮箱密码，请在 email_credentials.py 中设置")
        print("❌ 错误：未配置邮箱密码")
        print("💡 请在 email_credentials.py 中设置 IMAP_CONFIG['password']")
        return

    print(f"📧 使用邮箱: {EMAIL_ADDRESS}")

    mcp_client = MCPClient()
    if not mcp_client.connect():
        logger.error("MCP连接失败")
        print("❌ MCP连接失败，请检查：")
        print("   1. 邮箱地址和密码是否正确")
        print("   2. MCP服务器是否正在运行（cd mcp-mail-master && npm start）")
        return

    print("✅ MCP服务器连接成功")

    # ================= 步骤2：读取PitchBook邮件 =================
    print("\n" + "="*70)
    print("步骤2/7: 读取Outlook中的PitchBook邮件")
    print("="*70)

    fetch_days = email_credentials.IMAP_CONFIG.get('fetch_days', 7)
    max_emails = email_credentials.IMAP_CONFIG.get('max_emails', 50)

    # 获取日期范围
    start_date, end_date = email_credentials.get_date_range(fetch_days)

    print(f"📅 邮件日期范围: {start_date} 至 {end_date}")
    print(f"🔍 搜索参数：最近 {fetch_days} 天，最多 {max_emails} 封邮件")

    emails = mcp_client.search_emails(query="PitchBook", limit=max_emails)
    mcp_client.disconnect()

    if not emails:
        print("❌ 未找到PitchBook邮件")
        print("💡 请确保：")
        print("   1. Outlook中有PitchBook发送的邮件")
        print("   2. 或者有其他人转发的PitchBook邮件")
        return

    # 按日期过滤邮件
    filtered_emails = []
    for email in emails:
        email_date = email.get('date', '')
        if email_date and email_credentials.is_within_date_range(email_date, start_date, end_date):
            filtered_emails.append(email)

    print(f"✅ 找到 {len(emails)} 封邮件，符合日期范围: {len(filtered_emails)} 封")

    # 使用过滤后的邮件列表
    emails = filtered_emails

    # ================= 步骤3：提取邮件内容和链接 =================
    print("\n" + "="*70)
    print("步骤3/7: 提取邮件内容和链接")
    print("="*70)

    processor = EmailProcessor()
    processed_emails = []

    for idx, email in enumerate(emails, 1):
        try:
            # MCP 客户端已经返回格式化的邮件字典，只需确保所有必需字段存在
            email.setdefault('links', [])
            email.setdefault('attachments', [])
            email.setdefault('body', '')
            email.setdefault('html_body', '')
            email.setdefault('source_file', email.get('source_file', f"MCP_{email.get('id', '')}"))
            processed_emails.append(email)
            logger.info(f"[{idx}/{len(emails)}] 处理邮件: {email.get('subject', 'No subject')[:50]}")
        except Exception as e:
            logger.warning(f"处理邮件 {idx} 失败: {e}")

    print(f"✅ 成功处理 {len(processed_emails)} 封邮件")

    # 保存处理后的邮件
    saved_emails_path = processor.save_processed_emails(processed_emails)
    if saved_emails_path:
        print(f"💾 邮件数据已保存: {saved_emails_path}")

    # 统计链接
    all_links = []
    for email in processed_emails:
        # 将邮件日期附加到每个链接上
        email_date = email.get('date', '')
        for link in email.get('links', []):
            link_with_date = link.copy()
            link_with_date['email_date'] = email_date
            all_links.append(link_with_date)

    # 使用链接分类器筛选文件链接
    classifier = LinkClassifier()
    file_links = [link for link in all_links if classifier.is_direct_file_link(link.get('url', ''))]
    pitchbook_links = [link for link in all_links if 'pitchbook.com' in link.get('url', '').lower()]

    print(f"🔗 提取链接总数: {len(all_links)}")
    print(f"🔗 PDF/Excel文件链接: {len(file_links)}")
    print(f"🔗 PitchBook链接: {len(pitchbook_links)}")

    # ================= 步骤4：自动下载PDF/Excel报告 =================
    print("\n" + "="*70)
    print("步骤4/7: 自动下载PDF/Excel报告")
    print("="*70)

    downloaded_reports = []

    # 检查是否启用下载
    enable_download = email_credentials.IMAP_CONFIG.get('enable_download', False)

    if not file_links:
        print("⏭️ 未找到PDF/Excel文件链接，跳过下载")
    elif not enable_download:
        print("⏭️ 文件下载已禁用（无账号场景建议保持禁用）")
        print("💡 提示：如需启用，请将 email_credentials.py 中的 enable_download 设为 True")
        print("   注意：没有 PitchBook 账号时，下载会因 403 Forbidden 而失败")
    else:
        print(f"📥 开始下载 {len(file_links)} 个文件...")

        # 初始化下载服务
        download_service = EnhancedDownloadService()

        # 如果启用数据库，获取已下载列表用于去重
        downloaded_urls = set()
        db_enabled = getattr(config, 'DB_ENABLED', False)
        if db_enabled:
            try:
                from database.base import get_db_session
                from database.repositories import DownloadedReportRepository
                with get_db_session() as session:
                    repo = DownloadedReportRepository(session)
                    downloaded_urls = repo.get_all_downloaded_urls(limit=1000)
                    logger.info(f"已加载 {len(downloaded_urls)} 个历史下载记录")
            except Exception as e:
                logger.warning(f"加载历史下载记录失败: {e}")

        # 下载文件
        for idx, link in enumerate(file_links, 1):
            url = link.get('url', '')
            file_type = classifier.get_file_type(url)

            # 检查去重
            if url in downloaded_urls:
                link_text = link.get('text', url)[:50]
                print(f"   [{idx}/{len(file_links)}] ⏭️ 已下载: [{file_type.upper()}] {link_text}")
                continue

            link_text = link.get('text', url)[:50]
            print(f"   [{idx}/{len(file_links)}] 📥 [{file_type.upper()}] {link_text}")

            try:
                logger.info(f"下载文件: {url[:70]}...")

                # 检查是否使用 Playwright（GUI 配置优先）
                use_playwright = False
                if gui_config and gui_config.download.use_playwright:
                    use_playwright = True
                    logger.info("使用 Playwright 下载器（GUI 配置）")

                # 如果 Playwright 启用且可用，优先使用
                playwright_success = False
                if use_playwright:
                    try:
                        from services.playwright_downloader import PlaywrightDownloader
                        playwright_downloader = PlaywrightDownloader()
                        if playwright_downloader.is_available():
                            print(f"      🎭 使用 Playwright 下载...")
                            playwright_result = playwright_downloader.download_single(url, retries=1)

                            if playwright_result.get('success'):
                                print(f"      ✅ Playwright 下载成功!")
                                downloaded_urls.add(url)
                                playwright_success = True

                                # 解析输出获取文件名
                                output = playwright_result.get('output', '')
                                # 添加到下载报告（简化处理）
                                downloaded_reports.append({
                                    'success': True,
                                    'filename': 'playwright_download',
                                    'filepath': 'N/A',
                                    'file_size_bytes': 0,
                                    'source': 'playwright'
                                })
                            else:
                                print(f"      ❌ Playwright 失败: {playwright_result.get('error', '未知错误')[:50]}...")
                                print(f"      🔄 回退到标准下载...")
                        else:
                            print(f"      ⚠️ Playwright 不可用，使用标准下载...")
                    except ImportError:
                        print(f"      ⚠️ Playwright 模块不可用，使用标准下载...")

                # 标准下载（Playwright 未启用、不可用或失败时）
                if not playwright_success:
                    result = download_service.download_report(url)

                    if result.get('success'):
                        downloaded_reports.append(result)
                        downloaded_urls.add(url)
                        print(f"      ✅ {result['filename']} ({result['file_size_bytes']} bytes)")

                        # 保存到数据库
                        if db_enabled:
                            try:
                                from database.base import get_db_session
                                from database.repositories import DownloadedReportRepository
                                with get_db_session() as session:
                                    repo = DownloadedReportRepository(session)
                                    repo.create({
                                        'url': url,
                                        'filename': result['filename'],
                                        'filepath': result['filepath'],
                                        'file_size_bytes': result['file_size_bytes'],
                                        'content_type': result['content_type'],
                                        'download_status': 'success',
                                        'download_started_at': result.get('download_started_at'),
                                        'download_completed_at': result.get('download_completed_at')
                                    })
                            except Exception as e:
                                logger.warning(f"保存下载记录到数据库失败: {e}")
                    else:
                        # 标准下载也失败了
                        error = result.get('error', '未知错误')
                        print(f"      ❌ 下载失败: {error[:50]}...")

            except Exception as e:
                logger.warning(f"下载失败: {e}")
                print(f"      ❌ 异常: {e}")

        download_service.close()

        success_count = len([r for r in downloaded_reports if r.get('success')])
        print(f"\n✅ 成功下载 {success_count}/{len(file_links)} 个文件")

    # ================= 步骤5：提取报告内容 =================
    print("\n" + "="*70)
    print("步骤5/8: 提取报告内容")
    print("="*70)

    if downloaded_reports:
        extractor = ReportContentExtractor()

        for report in downloaded_reports:
            try:
                content = extractor.extract_content(report['filepath'])
                report['extracted_content'] = content
                logger.info(f"✓ 提取 {report['filename']}: {len(content)} 字符")
            except Exception as e:
                logger.warning(f"提取内容失败 {report.get('filename')}: {e}")
                report['extracted_content'] = ""

        extracted_count = sum(1 for r in downloaded_reports if r.get('extracted_content'))
        print(f"✅ 成功提取 {extracted_count}/{len(downloaded_reports)} 个报告内容")
    else:
        print("⏭️ 无下载报告，跳过内容提取")

    # ================= 步骤6：综合分析 =================
    print("\n" + "="*70)
    print("步骤6/8: 综合分析（邮件 + 报告）")
    print("="*70)

    analyzer = VCPEContentAnalyzer(use_llm=True)

    # 分析邮件
    logger.info("分析邮件内容...")
    email_analyses = analyzer.analyze_batch(processed_emails)
    print(f"✅ 邮件分析: {len(email_analyses)} 封")

    # 分析下载的报告
    report_analyses = []
    if downloaded_reports:
        logger.info("分析报告内容...")
        report_analyses = analyzer.analyze_downloaded_reports(downloaded_reports)
        print(f"✅ 报告分析: {len(report_analyses)} 份")

    # 分析爬取的网页内容
    scraped_analyses = []
    if scraped_results:
        logger.info("分析爬取的网页内容...")
        scraped_analyses = analyzer.analyze_scraped_content(scraped_results)
        print(f"✅ 网页内容分析: {len(scraped_analyses)} 篇")

    # 合并所有分析结果
    all_analyses = email_analyses + report_analyses + scraped_analyses

    # 生成市场概览
    market_overview = analyzer.generate_market_overview(all_analyses) or {}  # 确保 None 变为 {}
    if market_overview:
        print(f"📊 市场情绪: {market_overview.get('market_sentiment', 'N/A')}")
        print(f"📊 主要主题: {', '.join([t[0] for t in market_overview.get('top_topics', [])[:3]])}")

    # 保存分析结果
    analysis_save_path = analyzer.save_analysis_results(all_analyses)
    if analysis_save_path:
        print(f"💾 分析结果已保存: {analysis_save_path}")

    # ================= 步骤7：生成报告 =================
    print("\n" + "="*70)
    print("步骤7/8: 生成报告")
    print("="*70)

    # 选择报告格式
    generate_pdf = PDF_AVAILABLE and email_credentials.IMAP_CONFIG.get('generate_pdf', False)

    if generate_pdf:
        print("📄 生成PDF报告（包含图表和NLP分析）")
    else:
        print("📝 生成Word报告（传统格式）")

    # 生成报告
    if generate_pdf:
        # Lazy import PDF generator to avoid circular dependencies
        try:
            from pdf.pdf_report_generator import PDFReportGenerator
            generator = PDFReportGenerator(
                enable_charts=True,
                use_llm=True,  # Enable LLM for PDF content generation
                use_template=False
            )
            output_dir = config.PDF_REPORT_DIR
            file_ext = 'pdf'
            report_type = "PDF"
        except ImportError as e:
            logger.error(f"无法导入PDF生成器: {e}")
            print("❌ PDF报告生成器不可用，回退到Word报告")
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

    try:
        generator.generate_weekly_report(all_analyses, output_path, market_overview)
        print(f"✅ {report_type}报告已生成: {output_path}")

        # 显示文件大小
        file_size = os.path.getsize(output_path)
        size_kb = file_size / 1024
        print(f"   文件大小: {size_kb:.1f} KB")
    except Exception as e:
        logger.error(f"生成{report_type}报告失败: {e}")
        print(f"❌ {report_type}报告生成失败: {e}")
        return

    # ================= 最终总结 =================
    print("\n" + "="*70)
    print("📋 运行总结")
    print("="*70)
    print(f"处理邮件数:     {len(processed_emails)}")
    print(f"提取链接数:     {len(all_links)}")
    print(f"PitchBook链接:  {len(pitchbook_links)}")
    print(f"下载报告数:     {len(downloaded_reports)}")
    print(f"网页爬取数:     {len(scraped_results)}")
    print(f"内容提取数:     {sum(1 for r in downloaded_reports if r.get('extracted_content'))}")
    print(f"邮件分析数:     {len(email_analyses)}")
    print(f"报告分析数:     {len(report_analyses)}")
    print(f"网页内容分析数: {len(scraped_analyses)}")
    print(f"市场情绪:       {market_overview.get('market_sentiment', 'N/A') if market_overview else 'N/A'}")
    print(f"\n📄 {report_type}报告:")
    print(f"   {output_path}")
    print(f"\n📂 数据存储:")
    print(f"   邮件: {config.EMAIL_EXTRACTION_DIR}")
    print(f"   Word报告: {config.SUMMARY_REPORT_DIR}")
    print(f"   PDF报告: {config.PDF_REPORT_DIR}")
    print(f"   Markdown: {config.SCRAPER_MARKDOWN_DIR}")
    print(f"   供人阅读PDF: {config.SCRAPER_PDF_DIR}")
    print(f"   日志: {os.path.join(config.LOGS_DIR, 'system.log')}")

    # 显示NLP和可视化状态
    print(f"\n🤖 系统特性:")
    print(f"   NLP实体识别: {'✓ 启用' if any('entities' in a for a in all_analyses) else '✗ 未启用'}")
    print(f"   关系抽取: {'✓ 启用' if any('relations' in a for a in all_analyses) else '✗ 未启用'}")
    print(f"   可视化图表: {'✓ 启用' if generate_pdf else '✗ 未启用'}")
    print("="*70)

    logger.info("=== 系统执行完成 ===")


# ================= 程序入口 =================
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️ 操作被用户中断")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ 系统发生严重错误：{str(e)}")
        logger.error(f"系统严重错误：{str(e)}", exc_info=True)
        print("\n💡 提示：请查看日志文件获取详细错误信息")
        sys.exit(1)
