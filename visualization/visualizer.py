"""
Report Visualizer
Creates all visualization charts for VC/PE reports
"""
# Use non-interactive backend to prevent GUI blocking
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from collections import Counter
import logging

from visualization.chart_config import (
    setup_chinese_font,
    save_chart,
    get_color_for_label,
    COLOR_SCHEMES,
    apply_chart_style
)
from visualization.investment_network import InvestmentNetworkGenerator
from visualization.trend_analyzer import MarketTrendAnalyzer

logger = logging.getLogger(__name__)


class ReportVisualizer:
    """
    Creates visualization charts for VC/PE analysis reports

    Generates:
    - Industry distribution pie charts
    - Investment timeline charts
    - Top investor rankings
    - Deal stage distribution
    - Investment network graphs
    - Market sentiment radar charts
    - Geographic distribution maps
    """

    def __init__(self):
        """Initialize visualizer"""
        setup_chinese_font()
        self.network_generator = InvestmentNetworkGenerator()
        self.trend_analyzer = MarketTrendAnalyzer()

    def create_dashboard(
        self,
        analyses: List[Dict],
        output_dir: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Create complete dashboard with all charts

        Args:
            analyses: List of content analyses
            output_dir: Directory to save charts (optional)

        Returns:
            Dictionary with chart types as keys and file paths as values
        """
        logger.info(f"Creating dashboard from {len(analyses)} analyses")

        charts = {}

        # Generate all chart types
        charts['industry_distribution'] = self._create_industry_pie_chart(
            analyses, output_dir
        )

        charts['investment_timeline'] = self._create_timeline_chart(
            analyses, output_dir
        )

        charts['top_investors'] = self._create_investor_ranking(
            analyses, output_dir
        )

        charts['deal_stage_pie'] = self._create_stage_pie_chart(
            analyses, output_dir
        )

        charts['investment_network'] = self._create_network_graph(
            analyses, output_dir
        )

        charts['stage_bar'] = self._create_stage_bar_chart(
            analyses, output_dir
        )

        # Trend analysis charts
        trends = self.trend_analyzer.analyze_investment_trends(analyses)
        if trends.get('hot_sectors'):
            charts['hot_sectors_bar'] = self._create_hot_sectors_chart(
                trends['hot_sectors'], output_dir
            )

        logger.info(f"Created {len(charts)} charts")
        return charts

    def _create_industry_pie_chart(
        self,
        analyses: List[Dict],
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """Create industry distribution pie chart"""
        logger.info("Creating industry distribution pie chart")

        # Extract industries from topics
        all_topics = []
        for analysis in analyses:
            topics = analysis.get('key_topics', [])
            all_topics.extend(topics)

        if not all_topics:
            logger.warning("No topics found for industry chart")
            return None

        # Count topics
        topic_counts = Counter(all_topics)
        top_topics = topic_counts.most_common(8)

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))

        # Prepare data
        labels = [topic[0] for topic in top_topics]
        sizes = [topic[1] for topic in top_topics]
        colors = [get_color_for_label(label, 'industry') for label in labels]

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            sizes,
            labels=None,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 10}
        )

        # Beautify
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')

        # Add legend
        ax.legend(
            wedges,
            labels,
            title="行业板块 (Sectors)",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=9
        )

        ax.set_title('行业分布 (Industry Distribution)', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        # Save
        if output_dir:
            filepath = f"{output_dir}/industry_distribution.png"
            save_chart(fig, filepath)
            return filepath

        return None

    def _create_timeline_chart(
        self,
        analyses: List[Dict],
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """Create investment timeline trend chart"""
        logger.info("Creating timeline chart")

        # Get trends
        trends = self.trend_analyzer.analyze_investment_trends(analyses)
        timeline_data = trends.get('timeline_trends', [])

        if not timeline_data:
            logger.warning("No timeline data available")
            return None

        # Create figure
        fig, ax1 = plt.subplots(figsize=(14, 7))

        # Prepare data
        periods = [t['period'] for t in timeline_data]
        amounts = [t['total_amount'] / 1e6 for t in timeline_data]  # Convert to millions
        deal_counts = [t['deal_count'] for t in timeline_data]

        # Create bar chart for deal counts
        x = np.arange(len(periods))
        width = 0.35

        bars1 = ax1.bar(
            x - width/2,
            deal_counts,
            width,
            label='交易数量 (Deal Count)',
            color='#4ECDC4',
            alpha=0.8
        )

        ax1.set_xlabel('时间周期 (Period)', fontsize=12)
        ax1.set_ylabel('交易数量 (Deal Count)', fontsize=12, color='#4ECDC4')
        ax1.tick_params(axis='y', labelcolor='#4ECDC4')
        ax1.set_xticks(x)
        ax1.set_xticklabels(periods, rotation=45, ha='right')

        # Create second y-axis for amounts
        ax2 = ax1.twinx()

        bars2 = ax2.bar(
            x + width/2,
            amounts,
            width,
            label='投资总额 (Total Amount $M)',
            color='#FF6B6B',
            alpha=0.8
        )

        ax2.set_ylabel('投资总额 (百万美元)', fontsize=12, color='#FF6B6B')
        ax2.tick_params(axis='y', labelcolor='#FF6B6B')

        # Add legends
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left')

        ax1.set_title('投资趋势时间线 (Investment Timeline)', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        # Save
        if output_dir:
            filepath = f"{output_dir}/investment_timeline.png"
            save_chart(fig, filepath)
            return filepath

        return None

    def _create_investor_ranking(
        self,
        analyses: List[Dict],
        output_dir: Optional[str] = None,
        top_n: int = 15
    ) -> Optional[str]:
        """Create top investors ranking chart"""
        logger.info("Creating investor ranking chart")

        # Get top investors from trend analysis
        trends = self.trend_analyzer.analyze_investment_trends(analyses)
        investors = trends.get('top_investors', [])[:top_n]

        if not investors:
            logger.warning("No investor data available")
            return None

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))

        # Prepare data (reverse order for horizontal chart)
        investor_names = [inv['investor'] for inv in investors][::-1]
        deal_counts = [inv['deal_count'] for inv in investors][::-1]

        # Create horizontal bar chart
        y_pos = np.arange(len(investor_names))

        ax.barh(
            y_pos,
            deal_counts,
            color='#FF6B6B',
            alpha=0.8,
            edgecolor='white',
            linewidth=1.5
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(investor_names, fontsize=10)
        ax.invert_yaxis()  # Labels read top-to-bottom
        ax.set_xlabel('交易数量 (Deal Count)', fontsize=12)
        ax.set_title(f'TOP {len(investors)} 投资机构 (Top Investors)', fontsize=14, fontweight='bold', pad=20)

        # Add value labels
        for i, v in enumerate(deal_counts):
            ax.text(v + 0.1, i, str(v), va='center', fontsize=9)

        ax.grid(axis='x', alpha=0.3)
        ax.set_axisbelow(True)

        plt.tight_layout()

        # Save
        if output_dir:
            filepath = f"{output_dir}/top_investors.png"
            save_chart(fig, filepath)
            return filepath

        return None

    def _create_stage_pie_chart(
        self,
        analyses: List[Dict],
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """Create deal stage distribution pie chart"""
        logger.info("Creating deal stage pie chart")

        # Get trends
        trends = self.trend_analyzer.analyze_investment_trends(analyses)
        stage_data = trends.get('stage_distribution', [])

        if not stage_data:
            logger.warning("No stage data available")
            return None

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))

        # Prepare data
        stages = [s['stage'] for s in stage_data]
        counts = [s['deal_count'] for s in stage_data]
        colors = [get_color_for_label(stage, 'deal_stage') for stage in stages]

        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            counts,
            labels=None,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.85
        )

        # Beautify percentage text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)

        # Add legend
        legend_labels = [f"{stage}: {count} ({s['percentage']:.1f}%)"
                        for stage, count, s in zip(stages, counts, stage_data)]

        ax.legend(
            wedges,
            legend_labels,
            title="融资轮次 (Deal Stage)",
            loc="center left",
            bbox_to_anchor=(1, 0, 0.5, 1),
            fontsize=9
        )

        ax.set_title('融资轮次分布 (Deal Stage Distribution)', fontsize=14, fontweight='bold', pad=20)

        plt.tight_layout()

        # Save
        if output_dir:
            filepath = f"{output_dir}/deal_stage_distribution.png"
            save_chart(fig, filepath)
            return filepath

        return None

    def _create_network_graph(
        self,
        analyses: List[Dict],
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """Create investment network graph"""
        logger.info("Creating investment network graph")

        # Extract all relations
        all_relations = []
        for analysis in analyses:
            relations = analysis.get('relations', [])
            all_relations.extend(relations)

        if not all_relations:
            logger.warning("No relations for network graph")
            return None

        # Generate network
        if output_dir:
            filepath = f"{output_dir}/investment_network.png"
            fig = self.network_generator.generate_network_graph(
                all_relations,
                output_path=filepath
            )
            plt.close(fig)
            return filepath

        return None

    def _create_stage_bar_chart(
        self,
        analyses: List[Dict],
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """Create deal stage bar chart with amounts"""
        logger.info("Creating deal stage bar chart")

        # Get trends
        trends = self.trend_analyzer.analyze_investment_trends(analyses)
        stage_data = trends.get('stage_distribution', [])

        if not stage_data:
            return None

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 6))

        # Prepare data
        stages = [s['stage'] for s in stage_data]
        amounts = [s.get('total_amount', 0) / 1e6 for s in stage_data]  # Convert to millions

        # Create bar chart
        bars = ax.bar(
            stages,
            amounts,
            color=[get_color_for_label(stage, 'deal_stage') for stage in stages],
            alpha=0.8,
            edgecolor='white',
            linewidth=1.5
        )

        ax.set_xlabel('融资轮次 (Deal Stage)', fontsize=12)
        ax.set_ylabel('投资总额 (百万美元)', fontsize=12)
        ax.set_title('各轮次投资总额 (Total Investment by Stage)', fontsize=14, fontweight='bold', pad=20)

        # Rotate x labels
        plt.xticks(rotation=45, ha='right')

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(
                    bar.get_x() + bar.get_width()/2.,
                    height,
                    f'{height:.1f}M',
                    ha='center',
                    va='bottom',
                    fontsize=9
                )

        ax.grid(axis='y', alpha=0.3)
        ax.set_axisbelow(True)

        plt.tight_layout()

        # Save
        if output_dir:
            filepath = f"{output_dir}/stage_amounts.png"
            save_chart(fig, filepath)
            return filepath

        return None

    def _create_hot_sectors_chart(
        self,
        hot_sectors: List[Dict],
        output_dir: Optional[str] = None
    ) -> Optional[str]:
        """Create hot sectors ranking chart"""
        logger.info("Creating hot sectors chart")

        if not hot_sectors:
            return None

        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))

        # Prepare data
        sectors = [s['sector'] for s in hot_sectors][::-1]
        amounts = [s.get('total_amount', 0) / 1e6 for s in hot_sectors][::-1]

        # Create horizontal bar chart
        y_pos = np.arange(len(sectors))

        bars = ax.barh(
            y_pos,
            amounts,
            color=[get_color_for_label(sector, 'industry') for sector in sectors],
            alpha=0.8,
            edgecolor='white',
            linewidth=1.5
        )

        ax.set_yticks(y_pos)
        ax.set_yticklabels(sectors, fontsize=10)
        ax.invert_yaxis()
        ax.set_xlabel('投资总额 (百万美元)', fontsize=12)
        ax.set_title('热门投资领域 (Hot Investment Sectors)', fontsize=14, fontweight='bold', pad=20)

        # Add value labels
        for i, (bar, amount) in enumerate(zip(bars, amounts)):
            if amount > 0:
                ax.text(
                    amount + max(amounts) * 0.01,
                    i,
                    f'{amount:.1f}M',
                    va='center',
                    fontsize=9
                )

        ax.grid(axis='x', alpha=0.3)
        ax.set_axisbelow(True)

        plt.tight_layout()

        # Save
        if output_dir:
            filepath = f"{output_dir}/hot_sectors.png"
            save_chart(fig, filepath)
            return filepath

        return None


# Demo
if __name__ == "__main__":
    # Test data
    test_analyses = [
        {
            'key_topics': ['AI/Machine Learning', 'FinTech'],
            'relations': [],
            'investment_deals': []
        }
    ]

    visualizer = ReportVisualizer()

    print("="*70)
    print("Report Visualizer Test")
    print("="*70)

    charts = visualizer.create_dashboard(
        test_analyses,
        output_dir='E:/pitch/数据储存/temp_charts'
    )

    print(f"\n✓ Created {len(charts)} charts")
    for chart_type, path in charts.items():
        if path:
            print(f"  {chart_type}: {path}")
