"""
Chart Generator for PDF Reports
Creates matplotlib charts optimized for PDF embedding
"""
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
import io
import logging
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Configure matplotlib for PDF
matplotlib.rcParams['figure.dpi'] = 150
matplotlib.rcParams['savefig.dpi'] = 300
matplotlib.rcParams['figure.facecolor'] = 'white'

from pdf.font_manager import get_font_manager
from visualization.chart_config import setup_chinese_font, get_color_for_label

logger = logging.getLogger(__name__)


class ChartGenerator:
    """
    Generate charts optimized for PDF reports

    Creates charts with:
    - Proper sizing for PDF embedding
    - High resolution
    - Chinese font support
    - Clean, publication-ready styling
    """

    def __init__(self, figure_size: Tuple[float, float] = (8, 5)):
        """
        Initialize chart generator

        Args:
            figure_size: Default figure size in inches (width, height)
        """
        self.figure_size = figure_size
        self.font_manager = get_font_manager()
        setup_chinese_font()

    def create_industry_pie_chart(
        self,
        topic_data: Dict[str, int],
        title: str = "行业分布 (Industry Distribution)"
    ) -> str:
        """
        Create industry distribution pie chart for PDF

        Args:
            topic_data: Dictionary of {topic: count}
            title: Chart title

        Returns:
            str: Path to saved chart image
        """
        import tempfile
        import os

        fig, ax = plt.subplots(figsize=self.figure_size)

        # Prepare data
        labels = list(topic_data.keys())
        sizes = list(topic_data.values())
        colors = [get_color_for_label(label, 'industry') for label in labels]

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10}
        )

        # Styling
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Save to temp file
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        plt.tight_layout()
        plt.savefig(temp_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        logger.debug(f"Created industry pie chart: {temp_path}")
        return temp_path

    def create_stage_pie_chart(
        self,
        stage_data: List[Dict],
        title: str = "融资轮次分布 (Deal Stage Distribution)"
    ) -> str:
        """Create deal stage distribution pie chart"""
        import tempfile

        fig, ax = plt.subplots(figsize=self.figure_size)

        # Prepare data
        stages = [s['stage'] for s in stage_data]
        counts = [s['deal_count'] for s in stage_data]
        colors = [get_color_for_label(stage, 'deal_stage') for stage in stages]

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            counts,
            labels=stages,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85
        )

        # Styling
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)

        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Save
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        plt.tight_layout()
        plt.savefig(temp_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        logger.debug(f"Created stage pie chart: {temp_path}")
        return temp_path

    def create_investor_bar_chart(
        self,
        investors: List[Dict],
        top_n: int = 10,
        title: str = "活跃投资机构 (Top Investors)"
    ) -> str:
        """Create top investors horizontal bar chart"""
        import tempfile
        import numpy as np

        fig, ax = plt.subplots(figsize=(10, 6))

        # Prepare data
        top_investors = investors[:top_n]
        names = [inv['investor'] for inv in top_investors][::-1]
        counts = [inv['deal_count'] for inv in top_investors][::-1]

        # Create bar chart
        y_pos = np.arange(len(names))
        ax.barh(y_pos, counts, color='#FF6B6B', alpha=0.8, edgecolor='white', linewidth=1.5)

        ax.set_yticks(y_pos)
        ax.set_yticklabels(names, fontsize=10)
        ax.invert_yaxis()
        ax.set_xlabel('交易数量 (Deal Count)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Add value labels
        for i, v in enumerate(counts):
            ax.text(v + 0.1, i, str(v), va='center', fontsize=9)

        ax.grid(axis='x', alpha=0.3)
        ax.set_axisbelow(True)

        # Save
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        plt.tight_layout()
        plt.savefig(temp_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        logger.debug(f"Created investor bar chart: {temp_path}")
        return temp_path

    def create_timeline_chart(
        self,
        timeline_data: List[Dict],
        title: str = "投资趋势时间线 (Investment Timeline)"
    ) -> str:
        """Create investment timeline chart"""
        import tempfile
        import numpy as np

        fig, ax1 = plt.subplots(figsize=(12, 6))

        if not timeline_data:
            # Create empty chart
            ax1.text(0.5, 0.5, '暂无数据', ha='center', va='center', fontsize=14, color='gray')
            ax1.set_title(title, fontsize=14, fontweight='bold', pad=20)
        else:
            # Prepare data
            periods = [t['period'] for t in timeline_data]
            amounts = [t.get('total_amount', 0) / 1e6 for t in timeline_data]
            deal_counts = [t['deal_count'] for t in timeline_data]

            x = np.arange(len(periods))
            width = 0.35

            # Deal counts bar chart
            ax1.bar(x - width/2, deal_counts, width, label='交易数量', color='#4ECDC4', alpha=0.8)
            ax1.set_xlabel('时间周期 (Period)', fontsize=12)
            ax1.set_ylabel('交易数量 (Deal Count)', fontsize=12, color='#4ECDC4')
            ax1.tick_params(axis='y', labelcolor='#4ECDC4')
            ax1.set_xticks(x)
            ax1.set_xticklabels(periods, rotation=45, ha='right')

            # Amounts on second y-axis
            ax2 = ax1.twinx()
            ax2.bar(x + width/2, amounts, width, label='投资总额 ($M)', color='#FF6B6B', alpha=0.8)
            ax2.set_ylabel('投资总额 (百万美元)', fontsize=12, color='#FF6B6B')
            ax2.tick_params(axis='y', labelcolor='#FF6B6B')

            # Legend
            lines1, labels1 = ax1.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

            ax1.set_title(title, fontsize=14, fontweight='bold', pad=20)

        # Save
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        plt.tight_layout()
        plt.savefig(temp_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close(fig)

        logger.debug(f"Created timeline chart: {temp_path}")
        return temp_path

    def create_network_chart(
        self,
        relations: List[Dict],
        title: str = "投资关系网络 (Investment Network)"
    ) -> str:
        """Create investment network graph"""
        import tempfile

        # Use existing network generator
        from visualization.investment_network import InvestmentNetworkGenerator

        generator = InvestmentNetworkGenerator(figsize=(12, 8))
        fig = generator.generate_network_graph(relations)

        # Save
        temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
        temp_path = temp_file.name
        temp_file.close()

        fig.savefig(temp_path, dpi=300, bbox_inches='tight', facecolor='white')
        from matplotlib.pyplot import close
        close(fig)

        logger.debug(f"Created network chart: {temp_path}")
        return temp_path

    def create_all_charts(
        self,
        analyses: List[Dict],
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create all charts for PDF report

        Args:
            analyses: List of content analyses
            output_dir: Directory to save charts (optional)

        Returns:
            Dictionary with chart types as keys and file paths as values
        """
        logger.info(f"Creating all PDF charts from {len(analyses)} analyses")

        # Get trend analysis
        from visualization.trend_analyzer import MarketTrendAnalyzer
        trend_analyzer = MarketTrendAnalyzer()
        trends = trend_analyzer.analyze_investment_trends(analyses)

        charts = {}

        # Industry distribution
        topic_counter = {}
        for analysis in analyses:
            for topic in analysis.get('key_topics', []):
                topic_counter[topic] = topic_counter.get(topic, 0) + 1

        if topic_counter:
            charts['industry'] = self.create_industry_pie_chart(topic_counter)

        # Deal stages
        stage_data = trends.get('stage_distribution', [])
        if stage_data:
            charts['stages'] = self.create_stage_pie_chart(stage_data)

        # Top investors
        investors = trends.get('top_investors', [])
        if investors:
            charts['investors'] = self.create_investor_bar_chart(investors)

        # Timeline
        timeline_data = trends.get('timeline_trends', [])
        if timeline_data:
            charts['timeline'] = self.create_timeline_chart(timeline_data)

        # Network
        all_relations = []
        for analysis in analyses:
            all_relations.extend(analysis.get('relations', []))

        if all_relations:
            charts['network'] = self.create_network_chart(all_relations)

        logger.info(f"Created {len(charts)} charts for PDF")
        return charts


# Demo
if __name__ == "__main__":
    generator = ChartGenerator()

    # Test data
    test_topics = {'AI/Machine Learning': 15, 'FinTech': 12, 'Healthcare': 8}
    chart_path = generator.create_industry_pie_chart(test_topics)

    print(f"✓ Created test chart: {chart_path}")

    # Clean up
    import os
    try:
        os.unlink(chart_path)
        print("✓ Cleaned up test file")
    except:
        pass
