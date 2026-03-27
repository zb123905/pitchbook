"""
LLM Output Quality Validator
Validates the quality of LLM-generated analysis results
"""
import logging
from typing import Dict, List, Tuple, Any

logger = logging.getLogger(__name__)


class LLMQualityValidator:
    """Validate LLM output quality for VC/PE analysis"""

    # Generic/template phrases that indicate low-quality output
    GENERIC_PHRASES = [
        "这是一封邮件",
        "需要更多信息",
        "无法确定",
        "请提供更多",
        "内容不足",
        "无法分析",
        "暂无数据"
    ]

    # Minimum quality thresholds
    MIN_SUMMARY_LENGTH = 20
    MIN_TOPICS_COUNT = 2
    MIN_INSIGHTS_COUNT = 1

    @staticmethod
    def _get_field(analysis: Dict, primary_field: str, fallback_field: str = None) -> Any:
        """Get field value, checking both primary and llm_ prefixed names"""
        # Try exact match first
        if primary_field in analysis and analysis[primary_field]:
            return analysis[primary_field]

        # Build list of possible field names to check
        possible_names = []
        if fallback_field:
            possible_names.append(f"llm_{fallback_field}")
        possible_names.append(f"llm_{primary_field}")

        # Also check alternative names for specific fields
        field_mappings = {
            'key_topics': ['llm_topics', 'topics'],
            'market_sentiment': ['llm_sentiment', 'sentiment'],
            'summary_chinese': ['llm_summary_chinese'],
        }
        if primary_field in field_mappings:
            possible_names.extend(field_mappings[primary_field])

        # Check each possible name
        for name in possible_names:
            if name in analysis and analysis[name]:
                value = analysis[name]
                # Ensure non-empty for lists
                if isinstance(value, list) and len(value) == 0:
                    continue
                if isinstance(value, str) and not value.strip():
                    continue
                return value

        return None

    @staticmethod
    def validate_analysis_quality(analysis: Dict) -> Tuple[bool, List[str]]:
        """
        Validate analysis output quality

        Args:
            analysis: Parsed LLM analysis response

        Returns:
            (is_valid, issues_list)
        """
        issues = []

        # Check required fields (supports both plain and llm_ prefixed names)
        required_fields = ['content_type', 'industries', 'key_topics', 'market_sentiment', 'summary_chinese']
        for field in required_fields:
            value = LLMQualityValidator._get_field(analysis, field, field)
            if value is None:
                issues.append(f"Missing required field: {field}")
            elif isinstance(value, list) and len(value) == 0:
                issues.append(f"Empty required field: {field}")
            elif isinstance(value, str) and not value.strip():
                issues.append(f"Empty required field: {field}")

        # Check summary quality
        summary = LLMQualityValidator._get_field(analysis, 'summary_chinese', 'summary_chinese')
        if summary:
            if len(summary) < LLMQualityValidator.MIN_SUMMARY_LENGTH:
                issues.append(f"Summary too short ({len(summary)} < {LLMQualityValidator.MIN_SUMMARY_LENGTH} chars)")

            # Check for generic/template content
            for phrase in LLMQualityValidator.GENERIC_PHRASES:
                if phrase in summary:
                    issues.append(f"Generic phrase detected in summary: '{phrase}'")
                    break

        # Check topics count
        topics = LLMQualityValidator._get_field(analysis, 'key_topics', 'topics')
        if topics is not None:
            if isinstance(topics, list) and len(topics) < LLMQualityValidator.MIN_TOPICS_COUNT:
                issues.append(f"Too few topics extracted ({len(topics)} < {LLMQualityValidator.MIN_TOPICS_COUNT})")

        # Check insights quality
        insights = LLMQualityValidator._get_field(analysis, 'key_insights', 'key_insights')
        if insights is not None:
            if isinstance(insights, list) and len(insights) < LLMQualityValidator.MIN_INSIGHTS_COUNT:
                issues.append(f"Too few insights ({len(insights)} < {LLMQualityValidator.MIN_INSIGHTS_COUNT})")

            # Check for generic insights
            if isinstance(insights, list):
                for insight in insights:
                    if any(phrase in insight for phrase in LLMQualityValidator.GENERIC_PHRASES):
                        issues.append(f"Generic phrase in insights: '{insight[:50]}...'")
                        break

        # Check market sentiment validity
        sentiment = LLMQualityValidator._get_field(analysis, 'market_sentiment', 'sentiment')
        if sentiment:
            valid_sentiments = ['积极', '中性', '消极', 'positive', 'neutral', 'negative']
            if sentiment not in valid_sentiments:
                issues.append(f"Invalid market sentiment: '{sentiment}'")

        # Check investment deals quality
        if 'investment_deals' in analysis:
            deals = analysis['investment_deals']
            if isinstance(deals, list):
                for deal in deals:
                    if 'amount' in deal and not deal['amount']:
                        issues.append("Empty amount in investment deal")
                    if 'company' in deal and not deal['company']:
                        issues.append("Empty company name in investment deal")

        is_valid = len(issues) == 0

        if not is_valid:
            logger.warning(f"[Quality Validator] Analysis quality issues: {issues}")

        return (is_valid, issues)

    @staticmethod
    def get_quality_score(analysis: Dict) -> float:
        """
        Calculate a quality score for the analysis (0.0 to 1.0)

        Args:
            analysis: Parsed LLM analysis response

        Returns:
            Quality score between 0.0 and 1.0
        """
        score = 0.0
        max_score = 10.0

        # Has all required fields (2 points)
        required_fields = ['content_type', 'industries', 'key_topics', 'market_sentiment', 'summary_chinese']
        if all(LLMQualityValidator._get_field(analysis, f, f) is not None for f in required_fields):
            score += 2.0

        # Summary quality (2 points)
        summary = LLMQualityValidator._get_field(analysis, 'summary_chinese', 'summary_chinese')
        if summary:
            if len(summary) >= 50:
                score += 1.0
            if len(summary) >= 100:
                score += 1.0

        # Topics diversity (1 point)
        topics = LLMQualityValidator._get_field(analysis, 'key_topics', 'topics')
        if topics and len(topics) >= 3:
            score += 1.0

        # Insights quality (2 points)
        insights = LLMQualityValidator._get_field(analysis, 'key_insights', 'key_insights')
        if insights:
            if len(insights) >= 3:
                score += 1.0
            # Check if insights have substance (not generic)
            generic_count = sum(1 for i in insights if any(p in i for p in LLMQualityValidator.GENERIC_PHRASES))
            if generic_count == 0:
                score += 1.0

        # Investment deals (1 point)
        deals = analysis.get('investment_deals', [])
        if deals and len(deals) > 0:
            score += 1.0

        # Companies mentioned (1 point)
        companies = analysis.get('mentioned_companies', [])
        if companies and len(companies) > 0:
            score += 1.0

        # Full analysis present (1 point)
        full_analysis = analysis.get('analysis_full')
        if full_analysis and len(full_analysis) > 50:
            score += 1.0

        return min(score / max_score, 1.0)

    @staticmethod
    def log_quality_metrics(analysis: Dict, analysis_id: str = "unknown"):
        """
        Log quality metrics for analysis

        Args:
            analysis: Parsed LLM analysis response
            analysis_id: Identifier for the analysis (e.g., email index)
        """
        summary = LLMQualityValidator._get_field(analysis, 'summary_chinese', 'summary_chinese') or ''
        topics = LLMQualityValidator._get_field(analysis, 'key_topics', 'topics') or []
        insights = LLMQualityValidator._get_field(analysis, 'key_insights', 'key_insights') or []
        sentiment = LLMQualityValidator._get_field(analysis, 'market_sentiment', 'sentiment') or 'N/A'
        content_type = LLMQualityValidator._get_field(analysis, 'content_type', 'content_type') or 'N/A'

        metrics = {
            'id': analysis_id,
            'summary_length': len(summary),
            'topics_count': len(topics) if isinstance(topics, list) else 0,
            'insights_count': len(insights) if isinstance(insights, list) else 0,
            'deals_count': len(analysis.get('investment_deals', [])),
            'companies_count': len(analysis.get('mentioned_companies', [])),
            'has_full_analysis': bool(analysis.get('analysis_full')),
            'sentiment': sentiment,
            'content_type': content_type
        }

        logger.info(f"[Quality Metrics] Analysis {analysis_id}: {metrics}")

        return metrics
