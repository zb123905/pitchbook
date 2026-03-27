"""
Content Analysis Module
For analyzing content extracted from emails and downloaded reports

Enhanced with NLP entity recognition and relationship extraction (Phase 2)
"""
import os
import logging
import re
from datetime import datetime
from collections import Counter
from typing import Dict, List, Optional, Any
import json
import config
from report_content_extractor import ReportContentExtractor

# LLM imports (DeepSeek API integration)
try:
    from llm.deepseek_client import DeepSeekClient, APIConfig
    from llm.response_parser import LLMResponseParser
    from llm.quality_validator import LLMQualityValidator
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# NLP imports (Phase 2)
try:
    from nlp.entity_extractor import FinancialEntityExtractor
    from nlp.relation_extractor import InvestmentRelationExtractor
    NLP_AVAILABLE = True
    logger.info("NLP modules loaded successfully")
except ImportError as e:
    NLP_AVAILABLE = False
    logger.warning(f"NLP modules not available: {e}. Using keyword-based analysis only.")


class VCPEContentAnalyzer:
    """VC/PE Content Analyzer (Enhanced with NLP)"""

    def __init__(self, use_nlp: bool = True, use_llm: bool = None):
        """
        Initialize analyzer

        Args:
            use_nlp: Whether to use NLP for entity/relation extraction (Phase 2 feature)
            use_llm: Whether to use LLM API for enhanced analysis (None=use config setting)
        """
        self.analyses = []
        self.use_nlp = use_nlp and NLP_AVAILABLE

        # LLM configuration
        self.use_llm = use_llm if use_llm is not None else config.ENABLE_LLM_ANALYSIS
        self.llm_client = None
        self.llm_parser = LLMResponseParser() if LLM_AVAILABLE else None
        self.quality_validator = LLMQualityValidator() if LLM_AVAILABLE else None

        # Initialize LLM client if enabled
        if self.use_llm and LLM_AVAILABLE:
            try:
                # Debug logging before APIConfig initialization
                logger.info(f"[DEBUG] LLM Initialization Check:")
                logger.info(f"[DEBUG]   LLM_ENABLED from env: {os.getenv('LLM_ENABLED')}")
                logger.info(f"[DEBUG]   DEEPSEEK_API_KEY present: {bool(os.getenv('DEEPSEEK_API_KEY'))}")
                logger.info(f"[DEBUG]   DEEPSEEK_BASE_URL: {os.getenv('DEEPSEEK_BASE_URL')}")
                logger.info(f"[DEBUG]   use_llm parameter: {use_llm}")
                logger.info(f"[DEBUG]   config.ENABLE_LLM_ANALYSIS: {config.ENABLE_LLM_ANALYSIS}")
                logger.info(f"[DEBUG]   LLM_AVAILABLE: {LLM_AVAILABLE}")

                api_config = APIConfig.from_env()

                # Debug logging after APIConfig initialization
                logger.info(f"[DEBUG] APIConfig State:")
                logger.info(f"[DEBUG]   api_key length: {len(api_config.api_key) if api_config.api_key else 0}")
                logger.info(f"[DEBUG]   base_url: {api_config.base_url}")
                logger.info(f"[DEBUG]   model: {api_config.model}")
                logger.info(f"[DEBUG]   validate(): {api_config.validate()}")

                if api_config.validate():
                    self.llm_client = DeepSeekClient(api_config)
                    if self.llm_client.is_available():
                        logger.info("✓ LLM analysis enabled (DeepSeek API)")
                    else:
                        logger.warning("LLM client initialization failed, falling back to NLP/keyword analysis")
                        self.llm_client = None
                        self.use_llm = False
                else:
                    logger.warning("DEEPSEEK_API_KEY not configured, LLM features disabled")
                    self.use_llm = False
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {e}, falling back to NLP/keyword analysis")
                self.llm_client = None
                self.use_llm = False

        # Initialize NLP components if available
        if self.use_nlp:
            try:
                self.entity_extractor = FinancialEntityExtractor(use_spacy=False)
                self.relation_extractor = InvestmentRelationExtractor(self.entity_extractor)
                logger.info("✓ NLP entity extraction enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize NLP: {e}, falling back to keyword analysis")
                self.use_nlp = False
                self.entity_extractor = None
                self.relation_extractor = None
        else:
            self.entity_extractor = None
            self.relation_extractor = None

    def analyze_batch(self, emails):
        """Analyze emails in batch (enhanced with NLP)"""
        logger.info(f"Starting analysis of {len(emails)} emails")

        analyses = []

        for idx, email_data in enumerate(emails, 1):
            try:
                logger.info(f"Analyzing email {idx}/{len(emails)}: {email_data.get('subject', 'No subject')}")

                # Prepare text content for NLP
                email_text = self._get_email_text(email_data)

                # Base analysis
                analysis = {
                    'email_index': idx,
                    'subject': email_data.get('subject', ''),
                    'from': email_data.get('from', ''),
                    'date': email_data.get('date', ''),
                    'content_type': self._classify_content_type(email_data),
                    'categories': self._categorize_email(email_data),
                    'key_topics': self._extract_key_topics(email_data),
                    'metrics': self._extract_metrics(email_data),
                    'links': email_data.get('links', []),
                    'source_file': email_data.get('source_file', '')
                }

                # NLP enhancement (Phase 2)
                if self.use_nlp and email_text:
                    # Extract entities
                    entities = self.entity_extractor.extract_entities(email_text)
                    analysis['entities'] = entities

                    # Extract relations and deals
                    relations = self.relation_extractor.extract_relations(email_text, entities)
                    analysis['relations'] = relations

                    # Extract structured deals
                    deals = self.relation_extractor.extract_deals(email_text)
                    analysis['investment_deals'] = deals

                    # Enhanced metrics with NLP
                    analysis['nlp_metrics'] = {
                        'entity_count': sum(len(v) if isinstance(v, list) else 0 for v in entities.values()),
                        'relation_count': len(relations),
                        'deal_count': len(deals),
                        'company_count': len(entities.get('companies', [])),
                        'amount_count': len(entities.get('amounts', []))
                    }

                # LLM enhancement (DeepSeek API)
                if self.use_llm and self.llm_client and email_text:
                    try:
                        llm_result = self.llm_client.analyze_content(
                            content=email_text,
                            analysis_type='email',
                            metadata={
                                'subject': email_data.get('subject', ''),
                                'from': email_data.get('from', ''),
                                'date': email_data.get('date', '')
                            }
                        )

                        if llm_result['success']:
                            # Quality validation
                            if self.quality_validator:
                                is_valid, issues = self.quality_validator.validate_analysis_quality(llm_result['data'])

                                if not is_valid:
                                    logger.warning(f"[LLM Quality] Issues detected for email {idx}: {issues}")

                                # Log quality metrics
                                self.quality_validator.log_quality_metrics(llm_result['data'], f"email_{idx}")

                                # Calculate and log quality score
                                quality_score = self.quality_validator.get_quality_score(llm_result['data'])
                                logger.info(f"[LLM Quality] Score for email {idx}: {quality_score:.2f}/1.0")

                            # Merge LLM results with base analysis
                            analysis = self.llm_parser.merge_with_base_analysis(llm_result, analysis)
                            logger.debug(f"✓ LLM analysis complete for email {idx}")
                        else:
                            logger.warning(f"LLM analysis failed for email {idx}: {llm_result.get('error')}")
                            if config.LLM_FALLBACK_TO_NLP:
                                logger.debug("Falling back to NLP/keyword analysis")

                    except Exception as e:
                        logger.warning(f"LLM analysis error for email {idx}: {e}")
                        if config.LLM_FALLBACK_TO_NLP:
                            logger.debug("Falling back to NLP/keyword analysis")
                    # Extract entities
                    entities = self.entity_extractor.extract_entities(email_text)
                    analysis['entities'] = entities

                    # Extract relations and deals
                    relations = self.relation_extractor.extract_relations(email_text, entities)
                    analysis['relations'] = relations

                    # Extract structured deals
                    deals = self.relation_extractor.extract_deals(email_text)
                    analysis['investment_deals'] = deals

                    # Enhanced metrics with NLP
                    analysis['nlp_metrics'] = {
                        'entity_count': sum(len(v) if isinstance(v, list) else 0 for v in entities.values()),
                        'relation_count': len(relations),
                        'deal_count': len(deals),
                        'company_count': len(entities.get('companies', [])),
                        'amount_count': len(entities.get('amounts', []))
                    }

                analyses.append(analysis)

            except Exception as e:
                logger.warning(f"Error analyzing email {idx}: {str(e)}")

        logger.info(f"Successfully analyzed {len(analyses)} emails")
        return analyses

    def _get_email_text(self, email_data):
        """Extract full text content from email for NLP processing"""
        text_parts = []

        # Add subject
        if email_data.get('subject'):
            text_parts.append(email_data['subject'])

        # Add body
        if email_data.get('body'):
            text_parts.append(email_data['body'])

        # Add HTML body (stripped)
        if email_data.get('html_body'):
            from bs4 import BeautifulSoup
            try:
                soup = BeautifulSoup(email_data['html_body'], 'lxml')
                text_parts.append(soup.get_text(separator=' ', strip=True))
            except:
                pass

        return ' '.join(text_parts)

    def analyze_downloaded_reports(self, report_files):
        """Analyze downloaded report files - enhanced with NLP"""
        logger.info(f"Starting analysis of {len(report_files)} report files")

        extractor = ReportContentExtractor()
        report_analyses = []

        for report_file in report_files:
            try:
                filepath = report_file.get('filepath', '')
                filename = report_file.get('filename', 'unknown')

                logger.info(f"Analyzing report file: {filename}")

                # Extract content from file
                content = extractor.extract_content(filepath)

                if not content:
                    logger.warning(f"No content extracted from {filename}, skipping...")
                    continue

                logger.info(f"✓ Extracted {len(content)} characters from {filename}")

                # Analyze the extracted content
                analysis = {
                    'filename': filename,
                    'filepath': filepath,
                    'file_type': 'Downloaded Report',
                    'full_text': content,  # Complete extracted text
                    'content_type': self._classify_report_content(content),
                    'categories': self._categorize_report(content),
                    'key_topics': self._extract_topics_from_text(content),
                    'metrics': self._extract_metrics_from_text(content, report_file),
                    'analysis_date': datetime.now().isoformat()
                }

                # NLP enhancement (Phase 2)
                if self.use_nlp:
                    # Extract entities
                    entities = self.entity_extractor.extract_entities(content)
                    analysis['entities'] = entities

                    # Extract relations and deals
                    relations = self.relation_extractor.extract_relations(content, entities)
                    analysis['relations'] = relations

                    # Extract structured deals
                    deals = self.relation_extractor.extract_deals(content)
                    analysis['investment_deals'] = deals

                    # Enhanced metrics
                    analysis['nlp_metrics'] = {
                        'entity_count': sum(len(v) if isinstance(v, list) else 0 for v in entities.values()),
                        'relation_count': len(relations),
                        'deal_count': len(deals),
                        'company_count': len(entities.get('companies', [])),
                        'amount_count': len(entities.get('amounts', []))
                    }

                report_analyses.append(analysis)

            except Exception as e:
                logger.warning(f"Error analyzing report file {report_file.get('filename', 'unknown')}: {str(e)}")

        logger.info(f"Successfully analyzed {len(report_analyses)} report files")
        return report_analyses

    def _classify_content_type(self, email_data):
        """Classify email content type"""
        subject = email_data.get('subject', '').lower()
        body = email_data.get('body', '').lower()

        if 'newsletter' in subject or 'weekly' in subject:
            return 'Weekly Newsletter'
        elif 'report' in subject or 'analysis' in subject:
            return 'Market Report'
        elif 'deal' in subject or 'acquisition' in subject or 'funding' in subject:
            return 'Deal Announcement'
        elif 'trend' in subject or 'outlook' in subject:
            return 'Market Trends'
        else:
            return 'General News'

    def _categorize_email(self, email_data):
        """Categorize email"""
        content = (email_data.get('subject', '') + ' ' + email_data.get('body', '')).lower()

        categories = []

        if any(term in content for term in ['venture capital', 'vc', 'startup', 'funding', 'series a', 'seed']):
            categories.append('VC')
        if any(term in content for term in ['private equity', 'pe', 'buyout', 'acquisition', 'm&a']):
            categories.append('PE')
        if any(term in content for term in ['ai', 'artificial intelligence', 'machine learning', 'ml']):
            categories.append('AI/ML')
        if any(term in content for term in ['fintech', 'financial technology', 'digital payment', 'blockchain']):
            categories.append('FinTech')
        if any(term in content for term in ['healthcare', 'biotech', 'medical', 'digital health']):
            categories.append('Healthcare')
        if any(term in content for term in ['cleantech', 'clean energy', 'renewable', 'sustainability']):
            categories.append('CleanTech')

        return categories if categories else ['General']

    def _extract_key_topics(self, email_data):
        """Extract key topics"""
        content = (email_data.get('subject', '') + ' ' + email_data.get('body', '')).lower()

        topics = []

        if any(term in content for term in ['ai', 'artificial intelligence', 'machine learning', 'ml']):
            topics.append('AI/Machine Learning')
        if any(term in content for term in ['fintech', 'financial technology', 'digital payment', 'blockchain', 'crypto']):
            topics.append('FinTech')
        if any(term in content for term in ['healthcare', 'biotech', 'medical', 'pharmaceutical', 'digital health']):
            topics.append('Healthcare')
        if any(term in content for term in ['cleantech', 'clean energy', 'renewable', 'sustainability']):
            topics.append('CleanTech')

        return topics if topics else ['Market Overview']

    def _extract_metrics(self, email_data):
        """Extract key metrics"""
        content = email_data.get('body', '')

        metrics = {
            'mentioned_companies': self._extract_companies(content),
            'deal_count': self._count_deals(content),
            'investment_found': self._has_investment(content)
        }

        return metrics

    def _extract_companies(self, content):
        """Extract company names"""
        company_pattern = r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\s+(?:Inc|Corp|Ltd|LLP|Group)\b'
        companies = re.findall(company_pattern, content)
        return list(set(companies))[:8]

    def _count_deals(self, content):
        """Count deal quantities"""
        deal_keywords = ['acquisition', 'funding', 'investment', 'buyout', 'merger']
        count = sum(1 for word in deal_keywords if word in content.lower())
        return count

    def _has_investment(self, content):
        """Check if content contains investment information"""
        investment_keywords = ['$', 'million', 'billion', 'funding', 'investment']
        return any(keyword in content.lower() for keyword in investment_keywords)

    def generate_market_overview(self, analyses):
        """Generate market overview"""
        if not analyses:
            return None

        total_emails = len(analyses)
        content_types = [a['content_type'] for a in analyses]
        type_counts = Counter(content_types)

        all_topics = []
        for analysis in analyses:
            all_topics.extend(analysis['key_topics'])
        topic_counts = Counter(all_topics)

        # Simple sentiment analysis
        positive_words = ['growth', 'increase', 'rise', 'positive', 'strong', 'record']
        negative_words = ['decline', 'decrease', 'fall', 'negative', 'weak', 'loss']

        sentiment_score = 0
        for analysis in analyses:
            content = (analysis['subject'] + ' ' + str(analysis.get('metrics', {}))).lower()
            sentiment_score += sum(1 for word in positive_words if word in content)
            sentiment_score -= sum(1 for word in negative_words if word in content)

        market_sentiment = 'positive' if sentiment_score > 0 else 'negative' if sentiment_score < 0 else 'neutral'

        overview = {
            'total_emails': total_emails,
            'content_type_distribution': dict(type_counts),
            'top_topics': topic_counts.most_common(5),
            'market_sentiment': market_sentiment
        }

        return overview

    def _sentiment_english(self, sentiment):
        """Convert market sentiment to English"""
        sentiment_map = {
            'positive': 'positive',
            'negative': 'negative',
            'neutral': 'neutral'
        }
        return sentiment_map.get(sentiment, 'neutral')

    def save_analysis_results(self, analyses):
        """Save analysis results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # 将分析结果保存到 ai分析使用 目录
        filepath = os.path.join(config.AI_ANALYSIS_DIR, f'content_analysis_AI分析_{timestamp}.json')

        # 自定义 JSON 编码器处理 datetime 对象
        class DateTimeEncoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, datetime):
                    return obj.isoformat()
                return super().default(obj)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(analyses, f, ensure_ascii=False, indent=2, cls=DateTimeEncoder)
            logger.info(f"Analysis results saved to: {filepath}")
            return filepath

        except Exception as e:
            logger.error(f"Failed to save analysis results: {str(e)}")
            return None

    # ========== New methods for downloaded report analysis ==========

    def _classify_report_content(self, content):
        """Classify report type based on full text content"""
        content_lower = content.lower()

        # Check for quarterly reports
        if 'quarterly' in content_lower and 'market report' in content_lower:
            return 'Quarterly Market Report'
        elif 'quarterly' in content_lower:
            return 'Quarterly Report'

        # Check for trend/outlook reports
        if 'trend' in content_lower and ('outlook' in content_lower or 'forecast' in content_lower):
            return 'Market Trend & Outlook'
        elif 'trend' in content_lower:
            return 'Market Trend Analysis'
        elif 'outlook' in content_lower or 'forecast' in content_lower:
            return 'Market Outlook'

        # Check for VC/PE industry reports
        if 'venture capital' in content_lower and 'private equity' in content_lower:
            return 'VC/PE Industry Report'
        elif 'venture capital' in content_lower or 'vc ' in content_lower:
            return 'Venture Capital Report'
        elif 'private equity' in content_lower or 'pe ' in content_lower:
            return 'Private Equity Report'

        # Check for deal-related reports
        if 'deal' in content_lower and ('flow' in content_lower or 'activity' in content_lower):
            return 'Deal Flow Report'
        elif 'exit' in content_lower and ('report' in content_lower or 'analysis' in content_lower):
            return 'Exit Analysis Report'

        # Default
        return 'General Market Report'

    def _categorize_report(self, content):
        """Categorize report content"""
        categories = []
        content_lower = content.lower()

        # VC/PE categories
        if 'venture capital' in content_lower or ' vc ' in content_lower:
            categories.append('VC')
        if 'private equity' in content_lower or ' pe ' in content_lower:
            categories.append('PE')

        # Industry sectors
        if 'fintech' in content_lower or 'financial technology' in content_lower:
            categories.append('FinTech')
        if 'healthcare' in content_lower or 'medical' in content_lower or 'biotech' in content_lower:
            categories.append('Healthcare')
        if 'saas' in content_lower or 'software as a service' in content_lower:
            categories.append('SaaS')
        if 'cleantech' in content_lower or 'clean energy' in content_lower:
            categories.append('CleanTech')

        # Report type categories
        if 'market' in content_lower:
            categories.append('Market Analysis')
        if 'deal' in content_lower:
            categories.append('Deal Analysis')

        return categories if categories else ['General']

    def _extract_topics_from_text(self, text):
        """Extract key topics from full text"""
        topics = []
        text_lower = text.lower()

        # Define topic keywords
        topic_keywords = {
            'AI/Machine Learning': ['ai', 'artificial intelligence', 'machine learning', 'ml', 'deep learning', 'neural network'],
            'FinTech': ['fintech', 'financial technology', 'payments', 'digital banking', 'blockchain', 'cryptocurrency'],
            'Healthcare': ['healthcare', 'medical', 'biotech', 'pharmaceutical', 'digital health', 'telemedicine'],
            'CleanTech': ['clean tech', 'clean energy', 'renewable', 'climate', 'sustainability', 'esg'],
            'SaaS': ['saas', 'software as a service', 'cloud software', 'subscription software'],
            'E-commerce': ['e-commerce', 'ecommerce', 'online marketplace', 'digital commerce'],
            'Cybersecurity': ['cybersecurity', 'information security', 'data security', 'network security'],
            'EdTech': ['edtech', 'education technology', 'online learning', 'ed-tech'],
            'Real Estate': ['real estate', 'proptech', 'property technology'],
            'Mobility': ['mobility', 'automotive', 'electric vehicle', 'ev', 'autonomous vehicle']
        }

        # Match topics
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                topics.append(topic)

        return topics if topics else ['General Market']

    def _extract_metrics_from_text(self, text, report_file=None):
        """Extract numerical metrics from text"""
        # Extract monetary amounts
        amounts = re.findall(r'[\$€£][\d.,]+(?:\s?(?:million|billion|trillion))?', text)
        percentages = re.findall(r'\d+\.?\d*%', text)

        # Extract years (for reports spanning multiple years)
        years = re.findall(r'\b(20\d{2})\b', text)

        # Extract deal/funding counts
        deal_mentions = len(re.findall(r'\bdeal\b', text.lower()))
        funding_mentions = len(re.findall(r'\bfunding\b', text.lower()))

        metrics = {
            'text_length': len(text),
            'amounts_found': len(amounts),
            'percentages_found': len(percentages),
            'years_found': list(set(years))[:10],
            'deal_mentions': deal_mentions,
            'funding_mentions': funding_mentions,
            'sample_amounts': amounts[:10],
            'sample_percentages': percentages[:10]
        }

        # Add file metadata if available
        if report_file:
            metrics['file_size_bytes'] = report_file.get('file_size_bytes', 0)
            metrics['source_url'] = report_file.get('source_url', '')

        return metrics

    def analyze_scraped_content(self, scraped_files):
        """Analyze scraped web content - enhanced with NLP"""
        logger.info(f"Starting analysis of {len(scraped_files)} scraped web pages")

        analyses = []

        for idx, scraped in enumerate(scraped_files, 1):
            try:
                markdown_path = scraped.get('markdown_path', '')
                url = scraped.get('url', '')
                title = scraped.get('title', 'Unknown')

                logger.info(f"Analyzing scraped content {idx}/{len(scraped_files)}: {title[:50]}...")

                # Read Markdown content
                try:
                    with open(markdown_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    logger.info(f"✓ Read {len(content)} characters from {markdown_path}")

                except Exception as e:
                    logger.warning(f"Failed to read Markdown file: {e}")
                    continue

                # Analyze the scraped content
                analysis = {
                    'url': url,
                    'title': title,
                    'source': 'web_scraped',
                    'file_type': 'Scraped Web Content',
                    'full_text': content,
                    'content_type': self._classify_report_content(content),
                    'categories': self._categorize_report(content),
                    'key_topics': self._extract_topics_from_text(content),
                    'metrics': self._extract_metrics_from_text(content, scraped),
                    'markdown_path': markdown_path,
                    'pdf_path': scraped.get('pdf_path', ''),
                    'scraped_at': scraped.get('scraped_at', ''),
                    'word_count': scraped.get('word_count', 0),
                    'analysis_date': datetime.now().isoformat()
                }

                # NLP enhancement (Phase 2) - crucial for scraped content
                if self.use_nlp:
                    # Extract entities
                    entities = self.entity_extractor.extract_entities(content)
                    analysis['entities'] = entities

                    # Extract relations and deals
                    relations = self.relation_extractor.extract_relations(content, entities)
                    analysis['relations'] = relations

                    # Extract structured deals
                    deals = self.relation_extractor.extract_deals(content)
                    analysis['investment_deals'] = deals

                    # Enhanced metrics for scraped content
                    analysis['nlp_metrics'] = {
                        'entity_count': sum(len(v) if isinstance(v, list) else 0 for v in entities.values()),
                        'relation_count': len(relations),
                        'deal_count': len(deals),
                        'company_count': len(entities.get('companies', [])),
                        'amount_count': len(entities.get('amounts', [])),
                        'reading_time_minutes': len(content) // 500  # Approximate reading time
                    }

                analyses.append(analysis)

            except Exception as e:
                logger.warning(f"Error analyzing scraped content {idx}: {str(e)}")

        logger.info(f"Successfully analyzed {len(analyses)} scraped web pages")
        return analyses

    # ========== LLM-Enhanced Analysis Methods ==========

    def analyze_with_llm(
        self,
        content: str,
        content_type: str = 'email',
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze content using LLM (DeepSeek API)

        Args:
            content: Text content to analyze
            content_type: Type of content ('email', 'report', 'scraped')
            metadata: Additional context

        Returns:
            LLM analysis results
        """
        if not self.use_llm or not self.llm_client:
            logger.warning("LLM not available for analysis")
            return {'success': False, 'error': 'LLM not configured'}

        result = self.llm_client.analyze_content(content, content_type, metadata)

        if result['success']:
            parsed = self.llm_parser.parse_analysis_response(result['raw_response'])
            return parsed
        else:
            return result

    def generate_llm_summary(self, analyses: List[Dict]) -> Optional[Dict]:
        """
        Generate market summary using LLM

        Args:
            analyses: List of individual analyses

        Returns:
            LLM-generated summary
        """
        if not self.use_llm or not self.llm_client:
            return None

        if not analyses:
            return None

        try:
            from llm.prompts import VCPEPromptTemplates

            prompts = VCPEPromptTemplates()
            messages = prompts.get_summary_prompt(analyses)

            result = self.llm_client.chat_completion(
                messages=messages,
                response_format='json_object'
            )

            if result['success']:
                import json
                summary_data = json.loads(result['content'])
                return {
                    'success': True,
                    'data': summary_data,
                    'usage': result.get('usage', {})
                }
            else:
                logger.warning(f"LLM summary generation failed: {result.get('error')}")
                return None

        except Exception as e:
            logger.warning(f"LLM summary error: {e}")
            return None

    def test_llm_connection(self) -> Dict[str, Any]:
        """
        Test LLM API connection

        Returns:
            Connection test result
        """
        if not self.use_llm or not self.llm_client:
            return {
                'success': False,
                'error': 'LLM not enabled or client not initialized',
                'configured': bool(self.llm_client)
            }

        return self.llm_client.test_connection()
