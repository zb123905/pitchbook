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

# 导入 Web 爬虫模块
from pitchbook_scraper import PitchBookScraper
from markdown_converter import MarkdownConverter
from pdf_converter import PDFConverter

# 导入 PDF 报告生成器 (Phase 1) - Lazy import
PDF_AVAILABLE = True
# logger.info("✓ PDF报告生成器可用 (Phase 1)")  # Logger not defined yet

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

    pitchbook_links = [link for link in all_links if 'pitchbook.com' in link.get('url', '').lower()]

    print(f"🔗 提取链接总数: {len(all_links)}")
    print(f"🔗 PitchBook链接: {len(pitchbook_links)}")

    # ================= 步骤4：自动下载报告 =================
    print("\n" + "="*70)
    print("步骤4/7: 自动下载PitchBook报告")
    print("="*70)

    downloaded_reports = []

    if not pitchbook_links:
        print("⚠️ 未找到PitchBook链接，跳过下载")
    else:
        print(f"📥 开始下载 {len(pitchbook_links)} 个报告...")

        for idx, link in enumerate(pitchbook_links, 1):
            url = link['url']
            try:
                logger.info(f"[{idx}/{len(pitchbook_links)}] 下载: {url[:70]}...")
                result = processor.download_report_from_link(url)

                if result.get('success'):
                    downloaded_reports.append(result)
                    print(f"   ✅ {result['filename']}")
                else:
                    print(f"   ❌ 失败: {result.get('error', '未知错误')}")

            except Exception as e:
                logger.warning(f"下载失败: {e}")

        print(f"\n✅ 成功下载 {len(downloaded_reports)} 个报告")

    # ================= 步骤4.5：Web爬取PitchBook内容 =================
    print("\n" + "="*70)
    print("步骤4.5/7: Web爬取PitchBook网页内容")
    print("="*70)

    scraped_results = []

    # 检查是否启用爬虫
    enable_scraper = email_credentials.IMAP_CONFIG.get('enable_scraper', True)
    if not enable_scraper:
        print("⏭️ 爬虫功能已禁用，跳过网页爬取")
        print("💡 提示：如需启用爬虫，请将 email_credentials.py 中的 enable_scraper 设为 True")
    elif pitchbook_links:
        # 获取配置
        max_scrape = email_credentials.IMAP_CONFIG.get('max_scrape_links', 0)
        date_filter_days = email_credentials.IMAP_CONFIG.get('date_filter_days', 7)
        start_date, end_date = email_credentials.get_date_range(date_filter_days)

        print(f"📅 网页发布日期范围: {start_date} 至 {end_date}")
        print(f"📊 从邮件中提取: {len(pitchbook_links)} 个 PitchBook 链接")

        # 按日期过滤链接（从邮件的发送日期推断）
        links_to_scrape = []
        skipped_old = 0

        for link in pitchbook_links:
            # 使用链接所属邮件的日期
            email_date = link.get('email_date', '')
            if email_date and email_credentials.is_within_date_range(email_date, start_date, end_date):
                links_to_scrape.append(link)
            else:
                skipped_old += 1

        # 如果配置了数量限制，再应用数量限制
        if max_scrape > 0 and len(links_to_scrape) > max_scrape:
            links_to_scrape = links_to_scrape[:max_scrape]
            print(f"🕷️ 准备爬取 {len(links_to_scrape)} 个网页（日期过滤 + 配置限制）...")
        else:
            print(f"🕷️ 准备爬取全部 {len(links_to_scrape)} 个网页（最近 {date_filter_days} 天）...")

        print(f"📊 跳过 {skipped_old} 个过期链接")

        # 获取快速失败配置
        fast_fail = email_credentials.IMAP_CONFIG.get('fast_fail', True)
        if fast_fail:
            print(f"⚡ 快速失败模式已启用（反爬虫页面将跳过）")

        print(f"⚠️ 使用反爬虫技术，每个网页需要 {email_credentials.IMAP_CONFIG.get('scrape_delay_min', 2)}-{email_credentials.IMAP_CONFIG.get('scrape_delay_max', 5)} 秒")

        # 计算预计时间
        delay_min = email_credentials.IMAP_CONFIG.get('scrape_delay_min', 2)
        delay_max = email_credentials.IMAP_CONFIG.get('scrape_delay_max', 5)
        delay_avg = (delay_min + delay_max) / 2
        estimated_time = len(links_to_scrape) * delay_avg / 60
        print(f"⏱️ 预计需要 {estimated_time:.1f} 分钟")

        try:
            # 初始化爬虫（传入 fast_fail 参数）
            scraper = PitchBookScraper(headless=True, fast_fail=fast_fail)

            if not await scraper.initialize():
                print("❌ 爬虫初始化失败，跳过网页爬取")
            else:
                # 初始化转换器
                md_converter = MarkdownConverter()
                pdf_converter = PDFConverter()

                # 爬取每个链接
                for idx, link in enumerate(links_to_scrape, 1):
                    url = link['url']
                    print(f"\n[{idx}/{len(links_to_scrape)}] 爬取: {url[:70]}...")

                    try:
                        # 爬取网页（传入日期参数进行双重验证）
                        scraped_data = await scraper.scrape_url(
                            url,
                            start_date=start_date,
                            end_date=end_date
                        )

                        if scraped_data:
                            # 检查是否被跳过
                            if scraped_data.get('skip_reason'):
                                reason = scraped_data.get('skip_reason')
                                pub_date = scraped_data.get('pub_date', 'N/A')
                                print(f"   ⏭️ 跳过: {reason}")
                                if pub_date != 'N/A':
                                    print(f"   📅 发布日期: {pub_date}")
                                continue

                            # 转换为 Markdown
                            md_path = md_converter.convert(scraped_data)
                            # 转换为 PDF
                            pdf_path = pdf_converter.convert(scraped_data)

                            scraped_results.append({
                                'url': url,
                                'title': scraped_data.get('title', ''),
                                'markdown_path': md_path,
                                'pdf_path': pdf_path,
                                'word_count': scraped_data.get('word_count', 0),
                                'scraped_at': scraped_data.get('scraped_at', '')
                            })

                            print(f"   ✅ 成功: {scraped_data.get('title', 'N/A')[:50]}")
                            if md_path:
                                print(f"   📝 Markdown: {md_path}")
                            if pdf_path:
                                print(f"   📄 PDF: {pdf_path}")
                        else:
                            print(f"   ❌ 爬取失败")

                    except Exception as e:
                        logger.warning(f"爬取网页失败: {e}")
                        print(f"   ❌ 错误: {e}")
                        continue

                # 清理资源
                await scraper.close()

                print(f"\n✅ 成功爬取 {len(scraped_results)} 个页面")

        except Exception as e:
            logger.error(f"Web 爬取过程出错: {e}")
            print(f"❌ Web 爬取出错: {e}")
            print("💡 系统将继续处理其他内容")
    else:
        print("⏭️ 没有 PitchBook 链接，跳过网页爬取")

    # ================= 步骤5：提取报告内容 =================
    print("\n" + "="*70)
    print("步骤5/7: 提取报告内容")
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
    print("步骤6/7: 综合分析（邮件 + 报告）")
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
    print("步骤7/7: 生成报告")
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
