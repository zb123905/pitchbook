"""
LLM Response Parser for VC/PE Analysis
Parses and validates structured LLM responses
"""
import json
import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class LLMResponseParser:
    """
    Parser for LLM responses in VC/PE analysis context
    """

    # Expected fields in analysis response
    ANALYSIS_FIELDS = [
        'content_type',
        'industries',
        'key_topics',
        'mentioned_companies',
        'investment_deals',
        'market_sentiment',
        'key_insights',
        'summary_chinese'
    ]

    # Content type options
    CONTENT_TYPES = [
        'weekly_newsletter',
        'market_report',
        'deal_announcement',
        'trend_analysis',
        'general_news'
    ]

    # Sentiment options
    SENTIMENTS = ['positive', 'neutral', 'negative']

    @staticmethod
    def parse_analysis_response(response_content: str) -> Dict[str, Any]:
        """
        Parse LLM analysis response

        Args:
            response_content: Raw JSON string from LLM

        Returns:
            Parsed and validated analysis dict
        """
        try:
            data = json.loads(response_content)

            # Validate and normalize
            parsed = {
                'content_type': LLMResponseParser._normalize_content_type(
                    data.get('content_type', 'general_news')
                ),
                'industries': LLMResponseParser._ensure_list(
                    data.get('industries', [])
                ),
                'key_topics': LLMResponseParser._ensure_list(
                    data.get('key_topics', [])
                ),
                'mentioned_companies': LLMResponseParser._normalize_companies(
                    data.get('mentioned_companies', [])
                ),
                'investment_deals': LLMResponseParser._normalize_deals(
                    data.get('investment_deals', [])
                ),
                'market_sentiment': LLMResponseParser._normalize_sentiment(
                    data.get('market_sentiment', 'neutral')
                ),
                'key_insights': LLMResponseParser._ensure_list(
                    data.get('key_insights', [])
                ),
                'summary_chinese': data.get('summary_chinese', ''),
                'raw_response': response_content
            }

            return {
                'success': True,
                'data': parsed
            }

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            return {
                'success': False,
                'error': f'Invalid JSON: {e}',
                'raw_response': response_content
            }

        except Exception as e:
            logger.error(f"Response parsing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'raw_response': response_content
            }

    @staticmethod
    def _normalize_content_type(content_type: str) -> str:
        """Normalize content type to known values"""
        content_type = content_type.lower().replace('-', '_').replace(' ', '_')

        for valid_type in LLMResponseParser.CONTENT_TYPES:
            if valid_type in content_type or content_type in valid_type:
                return valid_type

        return 'general_news'

    @staticmethod
    def _normalize_sentiment(sentiment: str) -> str:
        """Normalize sentiment to known values"""
        sentiment = sentiment.lower()

        for valid_sentiment in LLMResponseParser.SENTIMENTS:
            if valid_sentiment in sentiment:
                return valid_sentiment

        return 'neutral'

    @staticmethod
    def _ensure_list(value: Any) -> List[str]:
        """Ensure value is a list of strings"""
        if isinstance(value, list):
            return [str(item) for item in value if item]
        elif isinstance(value, str):
            return [value]
        return []

    @staticmethod
    def _normalize_companies(companies: Any) -> List[Dict[str, str]]:
        """Normalize company data to standard format"""
        normalized = []

        if not isinstance(companies, list):
            return normalized

        for company in companies:
            if isinstance(company, dict):
                normalized.append({
                    'name': str(company.get('name', 'Unknown')),
                    'role': str(company.get('role', 'unknown'))
                })
            elif isinstance(company, str):
                normalized.append({
                    'name': company,
                    'role': 'unknown'
                })

        return normalized

    @staticmethod
    def _normalize_deals(deals: Any) -> List[Dict[str, Any]]:
        """Normalize deal data to standard format"""
        normalized = []

        if not isinstance(deals, list):
            return normalized

        for deal in deals:
            if isinstance(deal, dict):
                normalized.append({
                    'company': str(deal.get('company', '')),
                    'amount': str(deal.get('amount', '')),
                    'round': str(deal.get('round', '')),
                    'investors': LLMResponseParser._ensure_list(deal.get('investors', [])),
                    'valuation': str(deal.get('valuation', ''))
                })

        return normalized

    @staticmethod
    def merge_with_base_analysis(
        llm_result: Dict[str, Any],
        base_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Merge LLM analysis results with base keyword/NLP analysis

        Args:
            llm_result: Result from LLM analysis
            base_analysis: Original keyword/NLP analysis

        Returns:
            Merged analysis dict
        """
        if not llm_result.get('success'):
            return base_analysis

        llm_data = llm_result['data']

        # Start with base analysis
        merged = base_analysis.copy()

        # Add LLM-specific fields
        merged['llm_enhanced'] = True
        merged['llm_content_type'] = llm_data.get('content_type')
        merged['llm_industries'] = llm_data.get('industries', [])
        merged['llm_key_insights'] = llm_data.get('key_insights', [])
        merged['llm_summary_chinese'] = llm_data.get('summary_chinese', '')

        # Merge companies (LLM + base)
        base_companies = merged.get('mentioned_companies', [])
        llm_companies = llm_data.get('mentioned_companies', [])

        # Deduplicate companies by name
        company_names = {c['name'] for c in base_companies}
        for company in llm_companies:
            if company['name'] not in company_names:
                base_companies.append(company)

        # Merge deals
        llm_deals = llm_data.get('investment_deals', [])
        if llm_deals:
            merged['llm_investment_deals'] = llm_deals
            merged['investment_deal_count'] = len(llm_deals)

        # Merge topics
        base_topics = merged.get('key_topics', [])
        llm_topics = llm_data.get('key_topics', [])
        merged['llm_topics'] = llm_topics

        # Combine topics without duplicates
        all_topics = list(set(base_topics + llm_topics))
        merged['all_topics'] = all_topics

        # Override sentiment with LLM's (more accurate)
        merged['llm_sentiment'] = llm_data.get('market_sentiment')

        return merged

    @staticmethod
    def extract_error_message(error_response: Dict) -> str:
        """
        Extract human-readable error message from API response

        Args:
            error_response: Error response dict

        Returns:
            Readable error message
        """
        if isinstance(error_response, str):
            return error_response

        error_type = error_response.get('error_type', 'Unknown')
        error_msg = error_response.get('error', 'No details')

        return f"{error_type}: {error_msg}"
