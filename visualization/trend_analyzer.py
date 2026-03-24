"""
Market Trend Analyzer
Analyzes investment trends and identifies emerging opportunities
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from collections import Counter
import logging

logger = logging.getLogger(__name__)


class MarketTrendAnalyzer:
    """
    Analyze market trends from VC/PE investment data

    Provides:
    - Monthly/quarterly investment trends
    - Hot sector identification
    - Deal stage distribution
    - Geographic distribution
    - Investor activity rankings
    - Emerging trend predictions
    """

    def __init__(self):
        """Initialize trend analyzer"""
        pass

    def analyze_investment_trends(
        self,
        analyses: List[Dict],
        time_period: str = 'monthly'
    ) -> Dict:
        """
        Analyze overall investment trends

        Args:
            analyses: List of content analyses with NLP data
            time_period: 'monthly' or 'quarterly'

        Returns:
            Dictionary with trend analysis results
        """
        logger.info(f"Analyzing investment trends ({time_period}) from {len(analyses)} analyses")

        # Extract all deals from analyses
        all_deals = self._extract_all_deals(analyses)

        if not all_deals:
            logger.warning("No deals found for trend analysis")
            return self._empty_trend_result()

        # Time-based trends
        timeline_trends = self._calculate_timeline_trends(all_deals, time_period)

        # Hot sectors
        hot_sectors = self._identify_hot_sectors(all_deals)

        # Stage distribution
        stage_distribution = self._analyze_stage_distribution(all_deals)

        # Geographic distribution
        geo_distribution = self._analyze_geo_distribution(analyses)

        # Top investors
        top_investors = self._rank_investors(all_deals)

        # Average deal sizes
        avg_deal_sizes = self._calculate_avg_deal_sizes(all_deals)

        # Predict emerging sectors
        emerging_sectors = self._predict_emerging_sectors(all_deals, hot_sectors)

        return {
            'timeline_trends': timeline_trends,
            'hot_sectors': hot_sectors,
            'stage_distribution': stage_distribution,
            'geo_distribution': geo_distribution,
            'top_investors': top_investors,
            'avg_deal_sizes': avg_deal_sizes,
            'emerging_sectors': emerging_sectors,
            'total_deals_analyzed': len(all_deals),
            'analysis_date': datetime.now().isoformat()
        }

    def _extract_all_deals(self, analyses: List[Dict]) -> List[Dict]:
        """Extract all investment deals from analyses"""
        all_deals = []

        for analysis in analyses:
            # Get investment_deals if available
            if 'investment_deals' in analysis:
                deals = analysis['investment_deals']
                if isinstance(deals, list):
                    all_deals.extend(deals)

            # Also extract from relations if needed
            if 'relations' in analysis:
                for rel in analysis['relations']:
                    if rel.get('type') == 'investment':
                        # Convert relation to deal format
                        deal = {
                            'company': rel.get('target', ''),
                            'investors': [rel.get('investor', '')],
                            'lead_investor': rel.get('investor', ''),
                            'stage': rel.get('stage', ''),
                            'amount': rel.get('amount'),
                            'date': rel.get('date', ''),
                            'description': rel.get('text', ''),
                            'confidence': rel.get('confidence', 0.5)
                        }
                        all_deals.append(deal)

        logger.info(f"Extracted {len(all_deals)} deals from analyses")
        return all_deals

    def _calculate_timeline_trends(
        self,
        deals: List[Dict],
        time_period: str
    ) -> List[Dict]:
        """Calculate investment amount trends over time"""
        # Parse dates and amounts
        timeline_data = []

        for deal in deals:
            date_str = deal.get('date', '')
            amount = deal.get('amount', {})

            if isinstance(amount, dict):
                amount_value = amount.get('amount', 0)
            else:
                amount_value = 0

            # Parse date
            try:
                if date_str:
                    date = self._parse_date(date_str)
                    if date:
                        timeline_data.append({
                            'date': date,
                            'amount': amount_value,
                            'deal_count': 1
                        })
            except:
                continue

        if not timeline_data:
            return []

        # Create DataFrame
        df = pd.DataFrame(timeline_data)

        # Group by time period
        if time_period == 'monthly':
            df['period'] = df['date'].dt.to_period('M')
        else:  # quarterly
            df['period'] = df['date'].dt.to_period('Q')

        # Aggregate
        grouped = df.groupby('period').agg({
            'amount': 'sum',
            'deal_count': 'sum'
        }).reset_index()

        # Convert to list of dicts
        trends = []
        for _, row in grouped.iterrows():
            trends.append({
                'period': str(row['period']),
                'total_amount': row['amount'],
                'deal_count': int(row['deal_count']),
                'avg_deal_size': row['amount'] / row['deal_count'] if row['deal_count'] > 0 else 0
            })

        logger.info(f"Calculated {len(trends)} {time_period} trends")
        return trends

    def _identify_hot_sectors(self, deals: List[Dict], top_n: int = 10) -> List[Dict]:
        """Identify most active investment sectors"""
        # Count deals by sector (using deal descriptions and company context)
        sector_keywords = {
            'AI/Machine Learning': ['AI', 'artificial intelligence', 'machine learning', 'ML', '深度学习', '人工智能'],
            'FinTech': ['fintech', 'financial technology', 'payments', '区块链', 'blockchain', '支付'],
            'Healthcare': ['healthcare', 'medical', 'biotech', '医疗', '健康', '生物医药'],
            'CleanTech': ['clean', 'renewable', 'solar', 'climate', '清洁', '新能源', '环保'],
            'SaaS': ['SaaS', 'software as a service', 'cloud software'],
            'E-commerce': ['e-commerce', 'ecommerce', 'marketplace', '电商'],
            'EdTech': ['edtech', 'education', '在线教育'],
            'Mobility': ['mobility', 'automotive', 'EV', '汽车', '出行'],
        }

        sector_counts = Counter()
        sector_amounts = {}

        for deal in deals:
            description = deal.get('description', '').lower()
            company = deal.get('company', '').lower()
            combined_text = f"{description} {company}"

            amount = deal.get('amount', {})
            if isinstance(amount, dict):
                amount_value = amount.get('amount', 0)
            else:
                amount_value = 0

            # Match sector keywords
            for sector, keywords in sector_keywords.items():
                if any(keyword.lower() in combined_text for keyword in keywords):
                    sector_counts[sector] += 1
                    if sector not in sector_amounts:
                        sector_amounts[sector] = 0
                    sector_amounts[sector] += amount_value

        # Create results
        hot_sectors = []
        for sector, count in sector_counts.most_common(top_n):
            hot_sectors.append({
                'sector': sector,
                'deal_count': count,
                'total_amount': sector_amounts.get(sector, 0),
                'avg_amount': sector_amounts.get(sector, 0) / count if count > 0 else 0
            })

        logger.info(f"Identified {len(hot_sectors)} hot sectors")
        return hot_sectors

    def _analyze_stage_distribution(self, deals: List[Dict]) -> List[Dict]:
        """Analyze distribution of deal stages"""
        stage_counts = Counter()
        stage_amounts = {}

        for deal in deals:
            stage = deal.get('stage', 'Unknown')
            if not stage:
                stage = 'Unknown'

            stage_counts[stage] += 1

            amount = deal.get('amount', {})
            if isinstance(amount, dict):
                amount_value = amount.get('amount', 0)
            else:
                amount_value = 0

            if stage not in stage_amounts:
                stage_amounts[stage] = 0
            stage_amounts[stage] += amount_value

        # Create results
        distribution = []
        for stage, count in stage_counts.most_common():
            distribution.append({
                'stage': stage,
                'deal_count': count,
                'percentage': (count / len(deals)) * 100 if len(deals) > 0 else 0,
                'total_amount': stage_amounts.get(stage, 0)
            })

        logger.info(f"Analyzed stage distribution: {len(distribution)} stages")
        return distribution

    def _analyze_geo_distribution(self, analyses: List[Dict]) -> List[Dict]:
        """Analyze geographic distribution of deals"""
        # This is a simplified version - in production, you'd use more sophisticated geolocation
        geo_keywords = {
            'China': ['中国', 'Beijing', 'Shanghai', 'Shenzhen', 'Hangzhou', '北京', '上海', '深圳', '杭州'],
            'US': ['USA', 'United States', 'San Francisco', 'New York', 'Silicon Valley'],
            'Singapore': ['Singapore', '新加坡'],
            'Europe': ['London', 'Berlin', 'Paris', '欧洲'],
            'India': ['India', 'Bangalore', 'Mumbai', '印度'],
        }

        geo_counts = Counter()

        for analysis in analyses:
            # Extract text content
            text = ' '.join([
                analysis.get('subject', ''),
                analysis.get('full_text', ''),
                str(analysis.get('description', ''))
            ]).lower()

            # Match geographic keywords
            for geo, keywords in geo_keywords.items():
                if any(keyword.lower() in text for keyword in keywords):
                    geo_counts[geo] += 1

        # Create results
        distribution = []
        for geo, count in geo_counts.most_common():
            distribution.append({
                'region': geo,
                'mention_count': count,
                'percentage': (count / sum(geo_counts.values())) * 100 if geo_counts else 0
            })

        logger.info(f"Analyzed geographic distribution: {len(distribution)} regions")
        return distribution

    def _rank_investors(self, deals: List[Dict], top_n: int = 15) -> List[Dict]:
        """Rank investors by activity"""
        investor_stats = {}

        for deal in deals:
            investors = deal.get('investors', [])
            if not isinstance(investors, list):
                investors = [investors] if investors else []

            amount = deal.get('amount', {})
            if isinstance(amount, dict):
                amount_value = amount.get('amount', 0)
            else:
                amount_value = 0

            for investor in investors:
                if investor not in investor_stats:
                    investor_stats[investor] = {
                        'deal_count': 0,
                        'total_amount': 0,
                        'companies': set()
                    }

                investor_stats[investor]['deal_count'] += 1
                investor_stats[investor]['total_amount'] += amount_value
                investor_stats[investor]['companies'].add(deal.get('company', ''))

        # Convert to list and sort
        ranked_investors = []
        for investor, stats in investor_stats.items():
            ranked_investors.append({
                'investor': investor,
                'deal_count': stats['deal_count'],
                'total_amount': stats['total_amount'],
                'company_count': len(stats['companies']),
                'avg_deal_size': stats['total_amount'] / stats['deal_count'] if stats['deal_count'] > 0 else 0
            })

        # Sort by deal count
        ranked_investors.sort(key=lambda x: x['deal_count'], reverse=True)

        logger.info(f"Ranked {len(ranked_investors)} investors")
        return ranked_investors[:top_n]

    def _calculate_avg_deal_sizes(self, deals: List[Dict]) -> Dict:
        """Calculate average deal sizes by stage and sector"""
        # By stage
        stage_amounts = {}
        stage_counts = Counter()

        # By overall
        all_amounts = []

        for deal in deals:
            stage = deal.get('stage', 'Unknown')
            amount = deal.get('amount', {})

            if isinstance(amount, dict):
                amount_value = amount.get('amount', 0)
            else:
                amount_value = 0

            if amount_value > 0:
                all_amounts.append(amount_value)

                if stage not in stage_amounts:
                    stage_amounts[stage] = []

                stage_amounts[stage].append(amount_value)
                stage_counts[stage] += 1

        # Calculate averages
        avg_by_stage = {}
        for stage, amounts in stage_amounts.items():
            avg_by_stage[stage] = {
                'avg_amount': np.mean(amounts),
                'median_amount': np.median(amounts),
                'min_amount': np.min(amounts),
                'max_amount': np.max(amounts),
                'deal_count': stage_counts[stage]
            }

        overall_avg = np.mean(all_amounts) if all_amounts else 0

        return {
            'overall_average': overall_avg,
            'by_stage': avg_by_stage
        }

    def _predict_emerging_sectors(
        self,
        deals: List[Dict],
        current_hot_sectors: List[Dict],
        threshold: float = 0.5
    ) -> List[Dict]:
        """
        Predict emerging/up-and-coming sectors

        Looks for sectors with:
        - Increasing deal counts
        - New investor activity
        - Rising average deal sizes
        """
        # This is a simplified prediction
        # In production, you'd use historical time series data

        # Sectors not in top 5 but showing activity
        emerging = []
        top_sectors = set([s['sector'] for s in current_hot_sectors[:5]])

        for sector in current_hot_sectors:
            if sector['sector'] not in top_sectors and sector['deal_count'] >= 2:
                # Has some activity but not yet top
                emerging.append({
                    'sector': sector['sector'],
                    'deal_count': sector['deal_count'],
                    'trend_indicator': 'rising',
                    'confidence': min(0.9, sector['deal_count'] * 0.1)
                })

        return emerging

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """Parse date string with multiple format support"""
        if not date_str:
            return None

        date_formats = [
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%Y年%m月%d日',
            '%B %d, %Y',
            '%b %d, %Y',
            '%Y-%m-%dT%H:%M:%S',
        ]

        for fmt in date_formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except:
                continue

        return None

    def _empty_trend_result(self) -> Dict:
        """Return empty trend result structure"""
        return {
            'timeline_trends': [],
            'hot_sectors': [],
            'stage_distribution': [],
            'geo_distribution': [],
            'top_investors': [],
            'avg_deal_sizes': {'overall_average': 0, 'by_stage': {}},
            'emerging_sectors': [],
            'total_deals_analyzed': 0,
            'analysis_date': datetime.now().isoformat()
        }


# Demo
if __name__ == "__main__":
    # Test data
    test_analyses = [
        {
            'investment_deals': [
                {
                    'company': '字节跳动',
                    'investors': ['红杉资本', '高瓴资本'],
                    'stage': 'C轮',
                    'amount': {'amount': 200000000, 'currency': 'USD'},
                    'date': '2024-03-15',
                    'description': 'AI content platform'
                }
            ]
        }
    ]

    analyzer = MarketTrendAnalyzer()
    trends = analyzer.analyze_investment_trends(test_analyses)

    print("="*70)
    print("Market Trend Analyzer Test")
    print("="*70)
    print(f"\nAnalyzed {trends['total_deals_analyzed']} deals")
    print(f"Hot sectors: {len(trends['hot_sectors'])}")
    print(f"Top investors: {len(trends['top_investors'])}")
