"""
Report Generation Module
Generate VC/PE industry weekly market observation reports based on analysis results

Enhanced with visualization charts (Phase 3)
"""
import os
import logging
from datetime import datetime
from collections import Counter
from docx import Document
from docx.shared import Pt, RGBColor, Inches, Mm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement
import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Phase 3 and Phase 1 availability flags (modules will be imported lazily)
VISUALIZATION_AVAILABLE = True
PDF_AVAILABLE = True


class WeeklyReportGenerator:
    """Weekly Market Observation Report Generator (Enhanced with Charts)"""

    def __init__(self, enable_charts: bool = True):
        """
        Initialize report generator

        Args:
            enable_charts: Whether to include visualization charts (Phase 3 feature)
        """
        self.enable_charts = enable_charts and VISUALIZATION_AVAILABLE
        self.visualizer = None  # Will be loaded lazily
        self.trend_analyzer = None  # Will be loaded lazily
        logger.info(f"WeeklyReportGenerator initialized (charts: {self.enable_charts})")

    def generate_weekly_report(self, analyses, output_path=None, market_overview=None):
        """Generate weekly report (enhanced version)"""
        logger.info("Starting weekly report generation")

        # 添加空列表检查
        if not analyses:
            logger.warning("No analyses data provided, creating minimal report")
            analyses = []

        try:
            # 创建Word文档
            doc = Document()

            # Set default font
            doc.styles['Normal'].font.name = 'Arial'

            # Add title
            title = doc.add_heading('VC/PE 行业每周市场观察报告', level=0)
            title.alignment = WD_ALIGN_PARAGRAPH.CENTER

            # Add report overview
            doc.add_heading('📊 报告概览', level=1)

            report_date = datetime.now().strftime('%Y年%m月%d日')
            total_items = len(analyses)
            email_analyses = [a for a in analyses if a.get('email_index') or a.get('subject')]
            report_analyses = [a for a in analyses if a.get('file_type') == 'Downloaded Report']

            # Add overview information
            overview = doc.add_paragraph()
            overview.add_run('报告日期: ').bold = True
            overview.add_run(f'{report_date}\n')
            overview.add_run('分析项目总数: ').bold = True
            overview.add_run(f'{total_items}\n')
            overview.add_run('邮件分析: ').bold = True
            overview.add_run(f'{len(email_analyses)} 封\n')
            overview.add_run('报告分析: ').bold = True
            overview.add_run(f'{len(report_analyses)} 份\n')

            if market_overview:
                market_sentiment = market_overview.get('market_sentiment', 'neutral')
                overview.add_run('市场情绪: ').bold = True
                overview.add_run(f'{market_sentiment}\n')

            # Add executive summary
            doc.add_heading('📝 执行摘要', level=1)

            executive_summary = self._generate_executive_summary(analyses, market_overview or {})
            for line in executive_summary.split('\n'):
                if line.strip():
                    doc.add_paragraph(line.strip())

            # Add market overview
            doc.add_heading('🌐 市场概览', level=1)

            content_types = [a['content_type'] for a in analyses]
            type_counts = Counter(content_types)

            doc.add_paragraph('内容类型分布:')
            for content_type, count in type_counts.most_common():
                percentage = (count / len(analyses)) * 100
                p = doc.add_paragraph()
                p.add_run(f'{content_type}: ').bold = True
                p.add_run(f'{count} ({percentage:.1f}%)')

            # Add industry sector analysis
            doc.add_heading('🏭 行业板块分析', level=1)

            all_topics = []
            for analysis in analyses:
                all_topics.extend(analysis['key_topics'])

            if all_topics:
                topic_counts = Counter(all_topics)

                doc.add_paragraph('热门行业板块:')
                for topic, count in topic_counts.most_common():
                    percentage = (count / len(analyses)) * 100
                    p = doc.add_paragraph()
                    p.add_run(f'{topic}: ').bold = True
                    p.add_run(f'{count} 次提及 ({percentage:.1f}%)')

            # Add email analysis section
            if email_analyses:
                self._add_email_analysis_section(doc, email_analyses)

            # Add report analysis section (NEW!)
            if report_analyses:
                self._add_report_analysis_section(doc, report_analyses)

            # Add key trends
            doc.add_heading('📈 关键趋势和观察', level=1)

            key_trends = self._generate_key_trends(analyses, market_overview or {})
            for line in key_trends.split('\n'):
                if line.strip():
                    if line.strip().startswith('**') and line.strip().endswith('**'):
                        title_text = line.strip().replace('**', '')
                        doc.add_heading(title_text, level=3)
                    else:
                        doc.add_paragraph(line.strip().lstrip())

            # Add market recommendations
            doc.add_heading('💡 市场观察和建议', level=1)

            recommendations = self._generate_recommendations(analyses)
            for line in recommendations.split('\n'):
                if line.strip():
                    if line.strip().startswith(('1. ', '2. ', '3. ', '4. ')):
                        doc.add_heading(line.strip(), level=3)
                    else:
                        doc.add_paragraph(line.strip().lstrip())

            # Add appendix
            doc.add_heading('📎 附录', level=1)

            # Add charts section (Phase 3: Visualization)
            if self.enable_charts:
                charts_section = self._add_charts_section(doc, analyses, market_overview)

            doc.add_paragraph('数据来源:')
            doc.add_paragraph('主要数据来源: PitchBook 订阅邮件')
            doc.add_paragraph(f'处理周期: {datetime.now().strftime("%Y-%m-%d")}')

            doc.add_paragraph('报告生成信息:')
            doc.add_paragraph(f'生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
            doc.add_paragraph('报告版本: v3.0 (Pure MCP)')

            # 保存文档
            if output_path is None:
                output_path = os.path.join(
                    config.SUMMARY_REPORT_DIR,
                    f'VC_PE_Weekly_AI分析_{datetime.now().strftime("%Y%m%d_%H%M%S")}.docx'
                )

            doc.save(output_path)
            logger.info(f"Weekly report saved to: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate weekly report: {str(e)}")
            return None

    def generate_word_report(self, analyses, market_overview):
        """Generate Word format report (legacy method for compatibility)"""
        return self.generate_weekly_report(analyses, None, market_overview)

    def _generate_executive_summary(self, analyses, market_overview):
        """Generate executive summary"""
        summary_lines = []

        total_emails = len(analyses)
        market_sentiment = market_overview.get('market_sentiment', 'neutral')
        sentiment_text = self._sentiment_chinese(market_sentiment)

        summary_lines.append(f"This week analyzed {total_emails} PitchBook industry emails, overall market sentiment is {market_sentiment}.")

        # Count top topics
        all_topics = []
        for analysis in analyses:
            all_topics.extend(analysis['key_topics'])

        if all_topics:
            topic_counts = Counter(all_topics)
            if topic_counts:  # 添加检查
                top_topics = topic_counts.most_common(3)
                topic_text = "、".join([topic[0] for topic in top_topics])
                summary_lines.append(f"Market hot topics include: {topic_text}.")

        summary_lines.append("Main content reflects current market focus and investment directions.")

        return "\n\n".join(summary_lines)

    def _generate_key_trends(self, analyses, market_overview):
        """Generate key trends content"""
        content_lines = []

        trends_count = 0

        # Trend 1: Market sentiment
        market_sentiment = market_overview.get('market_sentiment', 'neutral')
        if market_sentiment != 'neutral':
            sentiment_text = self._sentiment_chinese(market_sentiment)
            trends_count += 1
            content_lines.append(f"**{trends_count}. Market sentiment is {market_sentiment}**")
            content_lines.append(f"   Overall market sentiment this week is {market_sentiment}, investor confidence is {'improving' if market_sentiment == 'positive' else 'cautious' if market_sentiment == 'negative' else 'stable'}.")

        # Trend 2: Hot topics
        all_topics = []
        for analysis in analyses:
            all_topics.extend(analysis['key_topics'])

        if all_topics:
            topic_counts = Counter(all_topics)
            if topic_counts:  # 添加检查
                top_topic = topic_counts.most_common(1)[0][0]
                trends_count += 1
                content_lines.append(f"\n**{trends_count}. {top_topic} sector remains active**")
                content_lines.append(f"   {top_topic} is the most watched topic this week, related news and deal activities are frequent.")

        # Trend 3: Content characteristics
        content_types = [a['content_type'] for a in analyses]
        if content_types:  # 添加检查
            dominant_type = Counter(content_types).most_common(1)[0][0]
            trends_count += 1
            content_lines.append(f"\n**{trends_count}. {dominant_type} becomes main news type**")
            content_lines.append("   " + dominant_type + " dominates this week, reflecting key market focus areas.")

        # Trend 4: Deal activities
        deal_count = sum(1 for a in analyses if 'Deal' in a['content_type'])
        if deal_count > 0:
            trends_count += 1
            content_lines.append(f"\n**{trends_count}. Deal activities {'active' if deal_count >= 2 else 'stable'}**")
            content_lines.append(f"   This week has {deal_count} deal-related news, market deal activity is {'active' if deal_count >= 2 else 'relatively stable'}.")

        return "\n".join(content_lines)

    def _generate_recommendations(self, analyses):
        """Generate market recommendations content"""
        content_lines = []

        content_lines.append("Based on this week's market analysis, the following observations and recommendations are provided:")

        # Recommendation 1: Focus on hot sectors
        all_topics = []
        for analysis in analyses:
            all_topics.extend(analysis['key_topics'])

        if all_topics:
            topic_counts = Counter(all_topics)
            if topic_counts:  # 添加检查
                top_topics = [topic[0] for topic in topic_counts.most_common(2)]
                content_lines.append(f"\n1. **Key Focus Sectors**")
                for topic in top_topics:
                    content_lines.append(f"   - Continuously monitor developments in {topic}")

        # Recommendation 2: Market strategy
        deal_count = sum(1 for a in analyses if 'Deal' in a['content_type'])
        content_lines.append(f"\n2. **Market Strategy Recommendations**")
        if deal_count >= 2:
            content_lines.append("   - Market deal activity is active, consider increasing investment activities")
            content_lines.append("   - Focus on quality targets, seize investment opportunities")
        else:
            content_lines.append("   - Market is relatively stable, suggest prudent investment strategy")
            content_lines.append("   - Focus on targets with good fundamentals")

        # Recommendation 3: Risk warning
        content_lines.append(f"\n3. **Risk Warning**")
        content_lines.append("   - Pay attention to market volatility risks, implement proper risk control")
        content_lines.append("   - Monitor policy changes impact on relevant industries")
        content_lines.append("   - Suggest diversified investment to reduce concentration risk")

        # Recommendation 4: Continuous monitoring
        content_lines.append(f"\n4. **Continuous Monitoring**")
        content_lines.append("   - Establish continuous market monitoring mechanism")
        content_lines.append("   - Regularly track dynamics of industry leading companies")
        content_lines.append("   - Focus on development of emerging technologies and business models")

        return "\n".join(content_lines)

    def _sentiment_chinese(self, sentiment):
        """Convert market sentiment to Chinese (kept for compatibility)"""
        sentiment_map = {
            'positive': 'positive',
            'negative': 'negative',
            'neutral': 'neutral'
        }
        return sentiment_map.get(sentiment, 'neutral')

    def _add_email_analysis_section(self, doc, email_analyses):
        """Add email analysis section"""
        doc.add_page_break()
        doc.add_heading('📧 邮件内容分析', level=1)

        for idx, analysis in enumerate(email_analyses[:5], 1):  # Limit to 5 emails
            doc.add_heading(f"{idx}. {analysis.get('subject', 'No Subject')[:80]}", level=2)

            # Email metadata
            p = doc.add_paragraph()
            p.add_run('发件人: ').bold = True
            p.add_run(f"{analysis.get('from', 'N/A')}\n")
            p.add_run('日期: ').bold = True
            p.add_run(f"{analysis.get('date', 'N/A')}\n")
            p.add_run('内容类型: ').bold = True
            p.add_run(f"{analysis.get('content_type', 'N/A')}")

            # Categories
            if analysis.get('categories'):
                categories_str = " | ".join(analysis['categories'])
                doc.add_paragraph(f"🏷️ 分类: {categories_str}")

            # Key topics
            if analysis.get('key_topics'):
                topics_str = " | ".join(analysis['key_topics'])
                doc.add_paragraph(f"🔑 关键主题: {topics_str}")

    def _add_report_analysis_section(self, doc, report_analyses):
        """Add report content analysis section (NEW!)"""
        doc.add_page_break()
        doc.add_heading('📊 报告内容深度分析', level=1)

        doc.add_paragraph(f"本节对下载的 {len(report_analyses)} 份报告进行深度内容分析")

        for idx, analysis in enumerate(report_analyses, 1):
            doc.add_heading(f"{idx}. {analysis.get('filename', 'Unknown')}", level=2)

            # Content type
            p = doc.add_paragraph()
            p.add_run('📌 内容类型: ').bold = True
            p.add_run(f"{analysis.get('content_type', 'N/A')}")

            # Categories
            if analysis.get('categories'):
                categories_str = " | ".join(analysis['categories'])
                doc.add_paragraph(f"🏷️ 分类: {categories_str}")

            # Key topics
            if analysis.get('key_topics'):
                topics_str = " | ".join(analysis['key_topics'])
                doc.add_paragraph(f"🔑 关键主题: {topics_str}")

            # Content summary (first 800 characters)
            if 'full_text' in analysis and analysis['full_text']:
                summary = analysis['full_text'][:800]
                if len(analysis['full_text']) > 800:
                    summary += "..."

                doc.add_paragraph()
                doc.add_paragraph().add_run('📝 内容摘要:').bold = True
                doc.add_paragraph(summary)

            # Metrics data
            if analysis.get('metrics'):
                metrics = analysis['metrics']
                doc.add_paragraph()
                doc.add_paragraph().add_run('📈 统计指标:').bold = True
                doc.add_paragraph(f"  • 文本长度: {metrics.get('text_length', 0):,} 字符")
                doc.add_paragraph(f"  • 发现金额: {metrics.get('amounts_found', 0)} 处")
                doc.add_paragraph(f"  • 发现百分比: {metrics.get('percentages_found', 0)} 处")

                # Show sample amounts if available
                if metrics.get('sample_amounts'):
                    doc.add_paragraph(f"  • 金额示例: {', '.join(metrics['sample_amounts'][:5])}")

                # Show sample percentages if available
                if metrics.get('sample_percentages'):
                    doc.add_paragraph(f"  • 百分比示例: {', '.join(metrics['sample_percentages'][:5])}")

    def _add_charts_section(self, doc, analyses, market_overview):
        """
        Add visualization charts section to report (Phase 3 feature)

        Generates and embeds charts:
        - Industry distribution pie chart
        - Investment timeline
        - Top investors ranking
        - Deal stage distribution
        - Hot sectors bar chart
        """
        # Lazy import visualization modules to avoid circular dependency
        try:
            from visualization.visualizer import ReportVisualizer
            from visualization.trend_analyzer import MarketTrendAnalyzer
        except ImportError as e:
            logger.warning(f"Cannot import visualization modules: {e}")
            doc.add_paragraph('⚠️ 可视化模块不可用 (Visualization modules not available)')
            return None

        try:
            doc.add_page_break()
            doc.add_heading('📊 数据可视化分析 (Data Visualization)', level=1)

            doc.add_paragraph(
                '本节包含基于分析数据生成的可视化图表，'
                '提供投资趋势、行业分布、投资机构活跃度等关键指标的直观展示。'
            )

            # Generate all charts
            output_dir = config.CHART_TEMP_DIR
            os.makedirs(output_dir, exist_ok=True)

            # Create visualizer
            visualizer = ReportVisualizer()
            charts = visualizer.create_dashboard(analyses, output_dir)

            if not charts:
                doc.add_paragraph('暂无足够数据生成图表。')
                return None

            # Add charts to document
            chart_count = 0

            # Industry Distribution
            if charts.get('industry_distribution'):
                doc.add_heading('行业分布 (Industry Distribution)', level=2)
                self._add_chart_to_doc(doc, charts['industry_distribution'], '行业板块分布饼图')
                chart_count += 1

            # Deal Stages
            if charts.get('deal_stage_pie'):
                doc.add_heading('融资轮次分布 (Deal Stage Distribution)', level=2)
                self._add_chart_to_doc(doc, charts['deal_stage_pie'], '各融资轮次占比')
                chart_count += 1

            # Top Investors
            if charts.get('top_investors'):
                doc.add_heading('活跃投资机构 (Top Investors)', level=2)
                self._add_chart_to_doc(doc, charts['top_investors'], '交易数量排名')
                chart_count += 1

            # Investment Timeline
            if charts.get('investment_timeline'):
                doc.add_heading('投资趋势 (Investment Trends)', level=2)
                self._add_chart_to_doc(doc, charts['investment_timeline'], '投资金额与交易数量时间线')
                chart_count += 1

            # Stage Amounts
            if charts.get('stage_bar'):
                doc.add_heading('各轮次投资额 (Investment by Stage)', level=2)
                self._add_chart_to_doc(doc, charts['stage_bar'], '各轮次投资总额对比')
                chart_count += 1

            # Hot Sectors
            if charts.get('hot_sectors_bar'):
                doc.add_heading('热门投资领域 (Hot Investment Sectors)', level=2)
                self._add_chart_to_doc(doc, charts['hot_sectors_bar'], '热门领域投资金额排名')
                chart_count += 1

            # Investment Network
            if charts.get('investment_network'):
                doc.add_heading('投资关系网络 (Investment Network)', level=2)
                self._add_chart_to_doc(doc, charts['investment_network'], '投资机构与被投企业关系网络图')
                chart_count += 1

            logger.info(f"Added {chart_count} charts to report")
            return chart_count

        except Exception as e:
            logger.error(f"Failed to add charts section: {e}")
            doc.add_paragraph(f'图表生成失败: {str(e)}')
            return None

    def _add_chart_to_doc(self, doc, image_path, caption=None):
        """
        Add chart image to Word document

        Args:
            doc: Document object
            image_path: Path to chart image file
            caption: Optional caption text
        """
        if not os.path.exists(image_path):
            logger.warning(f"Chart image not found: {image_path}")
            return

        try:
            # Add image with appropriate size
            doc.add_picture(image_path, width=Inches(6.0))

            # Add caption if provided
            if caption:
                last_paragraph = doc.paragraphs[-1]
                last_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                run = p.add_run(f'图: {caption}')
                run.font.size = Pt(9)
                run.font.color.rgb = RGBColor(128, 128, 128)

        except Exception as e:
            logger.error(f"Failed to add chart to document: {e}")
