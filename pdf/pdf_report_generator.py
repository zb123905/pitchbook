"""
PDF Report Generator for VC/PE Analysis System
Generates professional PDF reports with Chinese text support and embedded charts
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

# ReportLab imports
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

logger = logging.getLogger(__name__)

from pdf.font_manager import get_font_manager
from pdf.chart_generator import ChartGenerator
from report_generator import WeeklyReportGenerator
import config
from styling_utils import PDFStyler


class PDFReportGenerator(WeeklyReportGenerator):
    """
    Generate professional PDF reports for VC/PE analysis

    Features:
    - Chinese text support (automatic font registration)
    - Embedded charts and visualizations
    - Professional layout and styling
    - Table of contents
    - Executive summary
    - Detailed analysis sections
    - Appendix with data sources
    """

    def __init__(self, enable_charts: bool = True, use_llm: bool = False, use_template: bool = True):
        """
        Initialize PDF report generator

        Args:
            enable_charts: Whether to include visualization charts
            use_llm: Whether to use LLM for content generation
            use_template: Whether to use background template (default: True)
        """
        # Initialize parent class attributes
        self.enable_charts = enable_charts
        self.use_llm = use_llm
        self.use_template = use_template  # Allow background template control

        # Initialize LLM client if enabled
        if self.use_llm:
            try:
                from llm.deepseek_client import get_default_client
                self.llm_client = get_default_client()
                if self.llm_client and not self.llm_client.is_available():
                    self.llm_client = None
                    logger.warning("LLM client not available for PDF report")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM client for PDF: {e}")
                self.llm_client = None
        else:
            self.llm_client = None

        # Get font manager
        self.font_manager = get_font_manager()
        self.font_config = self.font_manager.get_font_config()

        # Get font manager
        self.font_manager = get_font_manager()
        self.font_config = self.font_manager.get_font_config()

        # Initialize chart generator if enabled
        if self.enable_charts:
            try:
                self.chart_generator = ChartGenerator(figure_size=(7, 4))
                logger.info("✓ PDF chart generator initialized")
            except Exception as e:
                logger.warning(f"Chart generator init failed: {e}")
                self.chart_generator = None
        else:
            self.chart_generator = None

        # Setup styles
        self.styles = self._setup_styles()

    def _setup_styles(self):
        """Setup paragraph styles for PDF using config constants"""
        styles = getSampleStyleSheet()

        # Get font config
        font_normal = self.font_config['default_font']
        font_bold = self.font_config['bold_font']
        font_title = self.font_config['title_font']

        # Get style config from config.py
        style_config = PDFStyler.create_style_dict()

        # Custom styles using config constants
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontName=font_title,
            fontSize=config.FONT_SIZE_MAIN_TITLE,
            textColor=PDFStyler.get_color(config.COLOR_ACCENT_BLUE),
            spaceAfter=30,
            alignment=TA_CENTER,
            leading=int(config.FONT_SIZE_MAIN_TITLE * 1.5)
        ))

        styles.add(ParagraphStyle(
            name='CustomHeading1',
            parent=styles['Heading1'],
            fontName=font_bold,
            fontSize=config.FONT_SIZE_HEADING1,
            textColor=PDFStyler.get_color(config.COLOR_ACCENT_BLUE),
            spaceAfter=12,
            spaceBefore=20
        ))

        styles.add(ParagraphStyle(
            name='CustomHeading2',
            parent=styles['Heading2'],
            fontName=font_bold,
            fontSize=config.FONT_SIZE_HEADING2,
            textColor=PDFStyler.get_color(config.COLOR_TEXT_DARK),
            spaceAfter=10,
            spaceBefore=15
        ))

        styles.add(ParagraphStyle(
            name='CustomBody',
            parent=styles['BodyText'],
            fontName=font_normal,
            fontSize=config.FONT_SIZE_BODY,
            textColor=PDFStyler.get_color(config.COLOR_TEXT_DARK),
            spaceAfter=8,
            leading=int(config.FONT_SIZE_BODY * config.LINE_SPACING)
        ))

        styles.add(ParagraphStyle(
            name='CustomCaption',
            parent=styles['BodyText'],
            fontName=font_normal,
            fontSize=config.FONT_SIZE_DATA,
            textColor=PDFStyler.get_color(config.COLOR_TEXT_DARK),
            alignment=TA_CENTER,
            spaceAfter=15
        ))

        return styles

    def generate_weekly_report(
        self,
        analyses: List[Dict],
        output_path: Optional[str] = None,
        market_overview: Optional[Dict] = None
    ) -> Optional[str]:
        """
        Generate PDF format weekly report

        Args:
            analyses: List of content analyses
            output_path: Output PDF file path
            market_overview: Market overview data

        Returns:
            str: Path to generated PDF file
        """
        logger.info("Starting PDF report generation")

        if not analyses:
            logger.warning("No analyses provided")
            return None

        # Generate output path if not provided
        if output_path is None:
            output_path = os.path.join(
                config.PDF_REPORT_DIR,
                f'VC_PE_Weekly_AI分析_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            )

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            # Create PDF document with config margins
            from reportlab.lib.units import cm
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=config.MARGIN_RIGHT_CM * cm,
                leftMargin=config.MARGIN_LEFT_CM * cm,
                topMargin=config.MARGIN_TOP_CM * cm,
                bottomMargin=config.MARGIN_BOTTOM_CM * cm
            )

            # Build document content
            story = []
            story.extend(self._create_cover_page(analyses, market_overview))
            story.append(PageBreak())

            story.extend(self._create_executive_summary(analyses, market_overview))
            story.append(PageBreak())

            story.extend(self._create_overview_section(analyses, market_overview))
            story.append(PageBreak())

            story.extend(self._create_charts_section(analyses))
            story.append(PageBreak())

            story.extend(self._create_detailed_analysis(analyses))
            story.append(PageBreak())

            story.extend(self._create_key_trends(analyses, market_overview))
            story.append(PageBreak())

            story.extend(self._create_recommendations(analyses))

            # Build PDF with background and footer on all pages
            doc.build(
                story,
                onFirstPage=self._add_all_pages_decorations,
                onLaterPages=self._add_all_pages_decorations
            )

            logger.info(f"✓ PDF report generated: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to generate PDF report: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _create_cover_page(self, analyses: List[Dict], market_overview: Optional[Dict]) -> List:
        """Create cover page"""
        story = []

        # Title
        title = Paragraph("VC/PE 行业每周市场观察报告", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.5*inch))

        # Subtitle
        subtitle = Paragraph(
            f"VC/PE Industry Weekly Market Observation Report",
            self.styles['CustomHeading2']
        )
        story.append(subtitle)
        story.append(Spacer(1, 1*inch))

        # Report info
        report_date = datetime.now().strftime('%Y年%m月%d日')
        version_text = 'v4.1 (PDF + Charts + NLP + 猫背景)' if self.use_template else 'v4.1 (PDF + Charts + NLP)'
        info_data = [
            ['报告日期 (Report Date)', report_date],
            ['分析项目数 (Items Analyzed)', str(len(analyses))],
            ['生成时间 (Generated)', datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
            ['报告版本 (Version)', version_text]
        ]

        # Add AI attribution if LLM is used
        if self.use_llm:
            info_data.append(['AI 分析 (AI Analysis)', 'DeepSeek AI'])

        info_table = Table(info_data, colWidths=[2.5*inch, 3*inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), PDFStyler.get_color(config.COLOR_HIGHLIGHT_BG)),
            ('TEXTCOLOR', (0, 0), (0, -1), PDFStyler.get_color(config.COLOR_TEXT_DARK)),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), self.font_config['default_font']),
            ('FONTSIZE', (0, 0), (-1, -1), config.FONT_SIZE_BODY),
            ('PAD', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 0.5, PDFStyler.get_color(config.COLOR_DIVIDER))
        ]))

        story.append(info_table)
        story.append(Spacer(1, 1*inch))

        # Disclaimer
        disclaimer = Paragraph(
            "<b>免责声明 (Disclaimer):</b> 本报告基于公开信息和PitchBook订阅邮件内容生成，"
            "仅供内部参考使用。本报告中的信息准确性经过最大努力验证，但不构成投资建议。",
            self.styles['CustomBody']
        )
        story.append(disclaimer)

        return story

    def _create_executive_summary(self, analyses: List[Dict], market_overview: Optional[Dict]) -> List:
        """Create executive summary section"""
        story = []

        # Heading
        heading = Paragraph("执行摘要 (Executive Summary)", self.styles['CustomHeading1'])
        story.append(heading)
        story.append(Spacer(1, 0.2*inch))

        # Generate summary text using parent method
        summary_text = self._generate_executive_summary(analyses, market_overview or {})

        # Convert to paragraphs
        for line in summary_text.split('\n'):
            if line.strip():
                p = Paragraph(line.strip(), self.styles['CustomBody'])
                story.append(p)

        return story

    def _create_overview_section(self, analyses: List[Dict], market_overview: Optional[Dict]) -> List:
        """Create market overview section"""
        story = []

        # Heading
        heading = Paragraph("市场概览 (Market Overview)", self.styles['CustomHeading1'])
        story.append(heading)
        story.append(Spacer(1, 0.2*inch))

        # Market sentiment
        if market_overview:
            sentiment = market_overview.get('market_sentiment', 'neutral')
            sentiment_text = {
                'positive': '积极 (Positive)',
                'negative': '消极 (Negative)',
                'neutral': '中性 (Neutral)'
            }.get(sentiment, sentiment)

            p = Paragraph(f"<b>市场情绪 (Market Sentiment):</b> {sentiment_text}", self.styles['CustomBody'])
            story.append(p)
            story.append(Spacer(1, 0.1*inch))

        # Content type distribution
        content_types = [a['content_type'] for a in analyses]
        from collections import Counter
        type_counts = Counter(content_types)

        if type_counts:
            p = Paragraph("<b>内容类型分布 (Content Type Distribution):</b>", self.styles['CustomBody'])
            story.append(p)

            # Create table
            type_data = [['类型 (Type)', '数量 (Count)', '占比 (Percentage)']]
            for content_type, count in type_counts.most_common():
                percentage = (count / len(analyses)) * 100
                type_data.append([content_type, str(count), f'{percentage:.1f}%'])

            type_table = Table(type_data, colWidths=[2.5*inch, 1*inch, 1.5*inch])
            type_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), PDFStyler.get_color(config.COLOR_ACCENT_BLUE)),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.white),  # White text on blue background
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), self.font_config['default_font']),
                ('FONTSIZE', (0, 0), (-1, -1), config.FONT_SIZE_DATA),
                ('PAD', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, PDFStyler.get_color(config.COLOR_DIVIDER))
            ]))

            story.append(type_table)

        return story

    def _create_charts_section(self, analyses: List[Dict]) -> List:
        """Create charts section"""
        story = []

        # Heading
        heading = Paragraph("数据可视化分析 (Data Visualization)", self.styles['CustomHeading1'])
        story.append(heading)
        story.append(Spacer(1, 0.2*inch))

        if not self.chart_generator:
            p = Paragraph("图表功能未启用 (Charts not enabled)", self.styles['CustomBody'])
            story.append(p)
            return story

        # Generate charts
        charts = self.chart_generator.create_all_charts(analyses)

        if not charts:
            p = Paragraph("暂无足够数据生成图表 (Insufficient data for charts)", self.styles['CustomBody'])
            story.append(p)
            return story

        # Add charts with captions
        chart_info = {
            'industry': ('行业分布 (Industry Distribution)', '行业板块分布饼图'),
            'stages': ('融资轮次分布 (Deal Stage Distribution)', '各融资轮次占比'),
            'investors': ('活跃投资机构 (Top Investors)', '交易数量排名'),
            'timeline': ('投资趋势 (Investment Trends)', '投资金额与交易数量时间线'),
            'network': ('投资关系网络 (Investment Network)', '投资机构与被投企业关系网络图')
        }

        for chart_key, chart_path in charts.items():
            if chart_path and os.path.exists(chart_path):
                # Chart title
                if chart_key in chart_info:
                    title, desc = chart_info[chart_key]
                    title_para = Paragraph(title, self.styles['CustomHeading2'])
                    story.append(title_para)

                # Add image
                img = Image(chart_path, width=6*inch, height=3.5*inch)
                img.hAlign = 'CENTER'
                story.append(img)
                story.append(Spacer(1, 0.1*inch))

                # Caption
                if chart_key in chart_info:
                    caption = Paragraph(f"图: {desc}", self.styles['CustomCaption'])
                    story.append(caption)

                story.append(Spacer(1, 0.3*inch))

        logger.info(f"Added {len(charts)} charts to PDF")
        return story

    def _create_detailed_analysis(self, analyses: List[Dict]) -> List:
        """Create detailed analysis section"""
        story = []

        # Heading
        heading = Paragraph("详细内容分析 (Detailed Analysis)", self.styles['CustomHeading1'])
        story.append(heading)
        story.append(Spacer(1, 0.2*inch))

        # Email analyses
        email_analyses = [a for a in analyses if a.get('email_index') or a.get('subject')]

        if email_analyses:
            email_heading = Paragraph("邮件内容分析 (Email Analysis)", self.styles['CustomHeading2'])
            story.append(email_heading)
            story.append(Spacer(1, 0.1*inch))

            for idx, analysis in enumerate(email_analyses[:5], 1):  # Limit to 5
                # Item heading
                item_title = analysis.get('subject', 'No Subject')[:80]
                item_heading = Paragraph(f"{idx}. {item_title}", self.styles['CustomHeading2'])
                story.append(item_heading)

                # Metadata
                metadata = [
                    ['发件人 (From)', analysis.get('from', 'N/A')],
                    ['日期 (Date)', analysis.get('date', 'N/A')],
                    ['内容类型 (Type)', analysis.get('content_type', 'N/A')]
                ]

                metadata_table = Table(metadata, colWidths=[1.5*inch, 4*inch])
                metadata_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), self.font_config['default_font']),
                    ('FONTSIZE', (0, 0), (-1, -1), config.FONT_SIZE_DATA),
                    ('PAD', (0, 0), (-1, -1), 3),
                    ('GRID', (0, 0), (-1, -1), 0.5, PDFStyler.get_color(config.COLOR_DIVIDER))
                ]))
                story.append(metadata_table)
                story.append(Spacer(1, 0.1*inch))

                # Topics
                if analysis.get('key_topics'):
                    topics_str = " | ".join(analysis['key_topics'])
                    p = Paragraph(f"<b>关键主题 (Key Topics):</b> {topics_str}", self.styles['CustomBody'])
                    story.append(p)

                story.append(Spacer(1, 0.2*inch))

        # NLP enhanced data
        if any('entities' in a for a in analyses):
            story.append(PageBreak())
            nlp_heading = Paragraph("智能分析结果 (Intelligent Analysis)", self.styles['CustomHeading2'])
            story.append(nlp_heading)

            # Show deals
            all_deals = []
            for analysis in analyses:
                if 'investment_deals' in analysis:
                    all_deals.extend(analysis['investment_deals'])

            if all_deals:
                for deal in all_deals[:5]:  # Show top 5
                    deal_text = f"<b>{deal.get('company', 'Unknown')}</b> - {deal.get('stage', 'Unknown Round')}"
                    p = Paragraph(deal_text, self.styles['CustomBody'])
                    story.append(p)

                    investors = deal.get('investors', [])
                    if investors:
                        inv_text = f"投资方 (Investors): {', '.join(investors[:3])}"
                        p = Paragraph(inv_text, self.styles['CustomBody'])
                        story.append(p)

                    amount = deal.get('amount', {})
                    if amount and amount.get('amount'):
                        amt_text = f"金额 (Amount): {amount.get('normalized', 'N/A')}"
                        p = Paragraph(amt_text, self.styles['CustomBody'])
                        story.append(p)

                    story.append(Spacer(1, 0.1*inch))

        return story

    def _create_key_trends(self, analyses: List[Dict], market_overview: Optional[Dict]) -> List:
        """Create key trends section"""
        story = []

        heading = Paragraph("关键趋势和观察 (Key Trends and Observations)", self.styles['CustomHeading1'])
        story.append(heading)
        story.append(Spacer(1, 0.2*inch))

        # Generate trends using parent method
        trends_text = self._generate_key_trends(analyses, market_overview or {})

        for line in trends_text.split('\n'):
            if line.strip():
                if line.strip().startswith('**') and line.strip().endswith('**'):
                    title_text = line.strip().replace('**', '')
                    p = Paragraph(title_text, self.styles['CustomHeading2'])
                else:
                    p = Paragraph(line.strip().lstrip(), self.styles['CustomBody'])
                story.append(p)

        return story

    def _create_recommendations(self, analyses: List[Dict]) -> List:
        """Create recommendations section"""
        story = []

        heading = Paragraph("市场观察和建议 (Market Observations and Recommendations)", self.styles['CustomHeading1'])
        story.append(heading)
        story.append(Spacer(1, 0.2*inch))

        # Generate recommendations using parent method
        rec_text = self._generate_recommendations(analyses)

        for line in rec_text.split('\n'):
            if line.strip():
                if line.strip().startswith(('1. ', '2. ', '3. ', '4. ')):
                    p = Paragraph(line.strip(), self.styles['CustomHeading2'])
                else:
                    p = Paragraph(line.strip().lstrip(), self.styles['CustomBody'])
                story.append(p)

        # Appendix
        story.append(PageBreak())
        appendix_heading = Paragraph("附录 (Appendix)", self.styles['CustomHeading1'])
        story.append(appendix_heading)
        story.append(Spacer(1, 0.2*inch))

        # Data sources
        p = Paragraph("<b>数据来源 (Data Sources):</b>", self.styles['CustomBody'])
        story.append(p)
        p = Paragraph("主要数据来源: PitchBook 订阅邮件", self.styles['CustomBody'])
        story.append(p)

        p = Paragraph(f"处理周期: {datetime.now().strftime('%Y-%m-%d')}", self.styles['CustomBody'])
        story.append(p)
        story.append(Spacer(1, 0.2*inch))

        # Generation info
        p = Paragraph("<b>报告生成信息 (Report Info):</b>", self.styles['CustomBody'])
        story.append(p)
        p = Paragraph(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.styles['CustomBody'])
        story.append(p)
        p = Paragraph("报告版本: v4.1 (专业格式 + 猫背景)", self.styles['CustomBody'])
        story.append(p)
        p = Paragraph("系统: VC/PE PitchBook 自动化分析系统", self.styles['CustomBody'])
        story.append(p)

        # Add DeepSeek attribution if LLM was used
        if self.use_llm:
            p = Paragraph("AI 分析: 本报告内容部分由 DeepSeek AI 生成", self.styles['CustomBody'])
            story.append(p)

        return story

    def _add_page_footer(self, canvas, doc):
        """Add page footer to each page"""
        from reportlab.lib.units import inch

        # Save state
        canvas.saveState()

        # Footer line using config divider color
        divider_color = PDFStyler.get_color(config.COLOR_DIVIDER)
        canvas.setStrokeColor(divider_color)
        canvas.line(config.MARGIN_LEFT_CM * inch/2.54, 0.5*inch,
                   (8.27 - config.MARGIN_RIGHT_CM) * inch, 0.5*inch)

        # Page number
        page_num = canvas.getPageNumber()
        footer_text = f"第 {page_num} 页 | VC/PE PitchBook 自动化分析系统"

        canvas.setFont(self.font_config['default_font'], config.FONT_SIZE_DATA)

        # Use config text dark color
        text_color = PDFStyler.get_color(config.COLOR_TEXT_DARK)
        canvas.setFillColor(text_color)
        canvas.drawString(config.MARGIN_LEFT_CM * inch/2.54, 0.35*inch, footer_text)

        # Restore state
        canvas.restoreState()

    def _add_page_background(self, canvas, doc):
        """
        Add cat background image with transparency to each page
        Only applies if self.use_template is True
        """
        # Skip if template is disabled
        if not self.use_template:
            return

        from reportlab.lib.units import inch

        try:
            # Load background image from template
            manager = BackgroundTemplateManager()
            image_data = manager._load_template()

            if image_data:
                # Save to temp file
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                    f.write(image_data)
                    temp_image_path = f.name

                canvas.saveState()

                # Set background transparency (50%-70%)
                canvas.setFillAlpha(config.BACKGROUND_TRANSPARENCY_PDF)

                # Get page dimensions
                page_width = canvas._pagesize[0]
                page_height = canvas._pagesize[1]

                # Draw background image
                canvas.drawImage(
                    temp_image_path,
                    0, 0,
                    width=page_width,
                    height=page_height,
                    preserveAspectRatio=True
                )

                canvas.restoreState()

                # Draw content white semi-transparent overlay (80%)
                if config.CONTENT_OVERLAY_ENABLED:
                    canvas.saveState()
                    canvas.setFillAlpha(config.CONTENT_OVERLAY_TRANSPARENCY)

                    # Calculate content area (within margins)
                    left = config.MARGIN_LEFT_CM * inch / 2.54
                    bottom = config.MARGIN_BOTTOM_CM * inch / 2.54
                    width = (8.27 - config.MARGIN_LEFT_CM - config.MARGIN_RIGHT_CM) * inch / 2.54
                    height = (11.69 - config.MARGIN_TOP_CM - config.MARGIN_BOTTOM_CM) * inch / 2.54

                    canvas.setFillColor(colors.white)
                    canvas.rect(left, bottom, width, height, fill=1, stroke=0)

                    canvas.restoreState()

        except Exception as e:
            logger.debug(f"Background not applied: {e}")

    def _add_all_pages_decorations(self, canvas, doc):
        """
        Apply all page decorations (background + footer) to each page
        """
        self._add_page_background(canvas, doc)
        self._add_page_footer(canvas, doc)


# Demo
if __name__ == "__main__":
    import config

    # Test data
    test_analyses = [
        {
            'subject': 'Test Email',
            'from': 'test@test.com',
            'date': '2024-03-17',
            'content_type': 'Deal Announcement',
            'key_topics': ['AI/Machine Learning', 'FinTech'],
            'categories': ['VC', 'AI/ML'],
            'relations': [],
            'investment_deals': []
        }
    ]

    # Generate PDF
    generator = PDFReportGenerator(enable_charts=False)  # Disable charts for quick test

    print("="*70)
    print("PDF Report Generator Test")
    print("="*70)

    output_path = os.path.join(
        config.PDF_REPORT_DIR,
        'test_report.pdf'
    )

    result = generator.generate_weekly_report(test_analyses, output_path)

    if result:
        print(f"\n✓ PDF report generated: {result}")
        print(f"  File size: {os.path.getsize(result):,} bytes")
    else:
        print("\n✗ Failed to generate PDF report")
