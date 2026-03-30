"""
DeepSeek API Client for VC/PE Content Analysis
Provides LLM-powered content analysis with retry logic and fallback support
"""
import os
import time
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

# Import config for token limits
try:
    import config
    MAX_TOKENS_DEFAULT = getattr(config, 'LLM_MAX_TOKENS', 3000)
    MAX_TOKENS_LONG = getattr(config, 'LLM_MAX_TOKENS_LONG', 6000)
    MAX_TOKENS_EXECUTIVE = getattr(config, 'LLM_MAX_TOKENS_EXECUTIVE', 4000)  # For 2000 word executive summary
    MAX_TOKENS_ARTICLE = getattr(config, 'LLM_MAX_TOKENS_ARTICLE', 8000)  # For full 3000+ word articles
except ImportError:
    MAX_TOKENS_DEFAULT = 3000
    MAX_TOKENS_LONG = 6000
    MAX_TOKENS_EXECUTIVE = 4000

logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """DeepSeek API Configuration"""
    base_url: str = "https://openrouter.fans/v1"
    api_key: str = ""
    model: str = "deepseek-chat"
    timeout: int = 30
    timeout_long: int = 180  # Longer timeout for article generation (3 minutes)
    max_retries: int = 3
    retry_delay_base: float = 2.0  # Base for exponential backoff
    temperature: float = 0.2  # Lower temperature for more focused output
    max_tokens: int = MAX_TOKENS_DEFAULT  # Default token limit
    max_tokens_long: int = MAX_TOKENS_LONG  # For long reports
    max_tokens_article: int = MAX_TOKENS_ARTICLE  # For full articles
    top_p: float = 0.9  # Nucleus sampling parameter
    frequency_penalty: float = 0.1  # Reduce repetition
    presence_penalty: float = 0.0  # Encourage new topics

    @classmethod
    def from_env(cls) -> 'APIConfig':
        """Load configuration from environment variables"""
        # Ensure environment variables are loaded from .env file
        from dotenv import load_dotenv
        load_dotenv()

        return cls(
            base_url=os.getenv('DEEPSEEK_BASE_URL', 'https://openrouter.fans/v1'),
            api_key=os.getenv('DEEPSEEK_API_KEY', ''),
            model=os.getenv('DEEPSEEK_MODEL', 'deepseek-chat'),
            timeout=int(os.getenv('DEEPSEEK_TIMEOUT', '30')),
            timeout_long=int(os.getenv('DEEPSEEK_TIMEOUT_LONG', '180')),
            max_retries=int(os.getenv('DEEPSEEK_MAX_RETRIES', '3')),
            temperature=float(os.getenv('DEEPSEEK_TEMPERATURE', '0.2')),
            max_tokens=int(os.getenv('DEEPSEEK_MAX_TOKENS', '3000')),
            top_p=float(os.getenv('DEEPSEEK_TOP_P', '0.9')),
            frequency_penalty=float(os.getenv('DEEPSEEK_FREQUENCY_PENALTY', '0.1')),
            presence_penalty=float(os.getenv('DEEPSEEK_PRESENCE_PENALTY', '0.0'))
        )

    def validate(self) -> bool:
        """Validate configuration"""
        return bool(self.api_key)


class DeepSeekClient:
    """
    DeepSeek API Client for VC/PE content analysis
    Compatible with OpenAI API format
    """

    def __init__(self, config: Optional[APIConfig] = None):
        """
        Initialize DeepSeek client

        Args:
            config: API configuration, defaults to env-based config
        """
        self.config = config or APIConfig.from_env()
        self._client = None
        self._init_client()

    def _init_client(self):
        """Initialize OpenAI-compatible client"""
        if not self.config.validate():
            logger.warning("DeepSeek API key not configured, LLM features disabled")
            return

        try:
            from openai import OpenAI
            self._client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout
            )
            logger.info(f"✓ DeepSeek client initialized (model: {self.config.model})")
        except ImportError:
            logger.error("openai package not installed. Run: pip install openai>=1.0.0")
            self._client = None
        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek client: {e}")
            self._client = None

    def is_available(self) -> bool:
        """Check if client is available"""
        return self._client is not None and self.config.validate()

    def _get_long_timeout_client(self):
        """
        Get or create a client with longer timeout for large requests

        Returns:
            OpenAI client with 180 second timeout
        """
        if not hasattr(self, '_long_timeout_client'):
            from openai import OpenAI
            self._long_timeout_client = OpenAI(
                api_key=self.config.api_key,
                base_url=self.config.base_url,
                timeout=self.config.timeout_long  # 180 seconds
            )
            logger.debug(f"Created long timeout client (timeout={self.config.timeout_long}s)")
        return self._long_timeout_client

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None,
        use_long_timeout: bool = False
    ) -> Dict[str, Any]:
        """
        Send chat completion request with retry logic

        Args:
            messages: Chat messages in OpenAI format
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: Response format (e.g., "json_object")
            use_long_timeout: Whether to use longer timeout (180s) for large requests

        Returns:
            Response dict with content and metadata
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Client not available',
                'content': None
            }

        temperature = temperature or self.config.temperature
        max_tokens = max_tokens or self.config.max_tokens

        # Prepare request parameters
        request_params = {
            'model': self.config.model,
            'messages': messages,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'top_p': self.config.top_p,
            'frequency_penalty': self.config.frequency_penalty,
            'presence_penalty': self.config.presence_penalty
        }

        # Add response format if specified
        if response_format == 'json_object':
            request_params['response_format'] = {'type': 'json_object'}

        # Choose client based on timeout requirement
        client = self._get_long_timeout_client() if use_long_timeout else self._client

        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                timeout_desc = "long timeout" if use_long_timeout else "standard timeout"
                logger.debug(f"API request ({timeout_desc}, attempt {attempt + 1}/{self.config.max_retries})")

                response = client.chat.completions.create(**request_params)

                content = response.choices[0].message.content

                # Parse usage info
                usage = {
                    'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                    'completion_tokens': response.usage.completion_tokens if response.usage else 0,
                    'total_tokens': response.usage.total_tokens if response.usage else 0,
                }

                logger.debug(f"API success: {usage['total_tokens']} tokens")

                return {
                    'success': True,
                    'content': content,
                    'usage': usage,
                    'model': response.model,
                    'finish_reason': response.choices[0].finish_reason
                }

            except Exception as e:
                last_error = e
                error_type = type(e).__name__

                # Don't retry on certain errors
                if error_type in ['AuthenticationError', 'PermissionError']:
                    logger.error(f"API authentication error: {e}")
                    return {
                        'success': False,
                        'error': str(e),
                        'error_type': error_type,
                        'content': None
                    }

                # Calculate backoff delay
                delay = self.config.retry_delay_base * (2 ** attempt)

                if attempt < self.config.max_retries - 1:
                    logger.warning(f"API request failed (attempt {attempt + 1}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"API request failed after {self.config.max_retries} attempts: {e}")

        # All retries exhausted
        return {
            'success': False,
            'error': str(last_error),
            'error_type': type(last_error).__name__,
            'content': None
        }

    def check_balance(self) -> Dict[str, Any]:
        """
        Check API account balance

        Returns:
            Balance info dict
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Client not available'
            }

        try:
            # For OpenRouter-compatible APIs, check balance via headers
            response = self._client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "ping"}],
                max_tokens=1
            )

            # Extract balance info from response headers if available
            headers = getattr(response, '_response', {}).headers if hasattr(response, '_response') else {}

            return {
                'success': True,
                'message': 'API connection successful',
                'model': self.config.model
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def analyze_content(
        self,
        content: str,
        analysis_type: str = 'email',
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Analyze VC/PE content using LLM

        Args:
            content: Text content to analyze
            analysis_type: Type of content ('email', 'report', 'scraped')
            metadata: Additional context (subject, url, etc.)

        Returns:
            Structured analysis results
        """
        from .prompts import VCPEPromptTemplates

        # Generate prompt
        prompt_templates = VCPEPromptTemplates()
        messages = prompt_templates.get_analysis_prompt(content, analysis_type, metadata)

        # Debug logging
        logger.info(f"[LLM] Analyzing content (type={analysis_type}, length={len(content)})")
        logger.debug(f"[LLM] Input preview: {content[:200]}...")
        logger.debug(f"[LLM] API params: temp={self.config.temperature}, max_tokens={self.config.max_tokens}, top_p={self.config.top_p}")

        # Request JSON response
        result = self.chat_completion(
            messages=messages,
            response_format='json_object'
        )

        if not result['success']:
            return {
                'success': False,
                'error': result.get('error'),
                'raw_response': None
            }

        # Parse JSON response
        try:
            parsed_data = json.loads(result['content'])

            # Debug logging for successful analysis
            logger.info(f"[LLM] Analysis completed (tokens={result.get('usage', {}).get('total_tokens', 'N/A')})")
            logger.debug(f"[LLM] Output preview: {str(parsed_data)[:300]}...")

            return {
                'success': True,
                'data': parsed_data,
                'usage': result.get('usage', {}),
                'raw_response': result['content']
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")
            logger.debug(f"[LLM] Raw response that failed to parse: {result['content'][:200]}...")

            return {
                'success': False,
                'error': f'JSON parse error: {e}',
                'raw_response': result['content']
            }

    def test_connection(self) -> Dict[str, Any]:
        """
        Test API connection with simple request

        Returns:
            Test result dict
        """
        if not self.is_available():
            return {
                'success': False,
                'error': 'Client not initialized or API key missing'
            }

        result = self.chat_completion(
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Reply with 'OK' if you receive this."}
            ],
            max_tokens=10
        )

        return {
            'success': result['success'],
            'response': result.get('content'),
            'error': result.get('error')
        }


    def generate_executive_summary(
        self,
        analyses: List[Dict],
        time_range: str = "本周"
    ) -> Dict[str, Any]:
        """
        Generate executive summary using LLM (1500-2000 words)

        Args:
            analyses: List of analysis results
            time_range: Time period description

        Returns:
            Dict with success status and content
        """
        from .prompts import VCPEPromptTemplates

        prompt_templates = VCPEPromptTemplates()
        messages = prompt_templates.get_executive_summary_prompt(analyses, time_range)

        logger.info(f"[LLM] Generating executive summary for {len(analyses)} analyses")

        # Increase max_tokens to ensure 1500-2000 word output (Chinese ~1.5 tokens/word)
        # Use long timeout for large request (processing multiple email analyses)
        result = self.chat_completion(
            messages=messages,
            max_tokens=MAX_TOKENS_EXECUTIVE,  # Use config value (default: 4000)
            use_long_timeout=True  # Use 180s timeout for large requests
        )

        if result['success']:
            content = result['content']

            # Import word count utility
            try:
                from .utils import count_chinese_words, count_total_words
                word_count = count_chinese_words(content)
                total_stats = count_total_words(content)
                logger.info(f"[LLM] Executive summary generated: {word_count} Chinese words, {total_stats['total_chars']} chars")
            except ImportError:
                # Fallback to simple character count if utils not available
                word_count = len(content)
                logger.info(f"[LLM] Executive summary generated: {word_count} chars (utils not available)")

            logger.info(f"[LLM] Executive summary generated ({result.get('usage', {}).get('total_tokens', 'N/A')} tokens)")

            # Validate word count meets target (1500-2000 words)
            if word_count < 1400:
                logger.warning(f"[LLM] Executive summary is shorter than target: {word_count} words (target: 1500-2000)")
            elif word_count >= 1500 and word_count <= 2000:
                logger.info(f"[LLM] Executive summary meets 1500-2000 word requirement: {word_count} words")
            elif word_count > 2000:
                logger.info(f"[LLM] Executive summary exceeds 2000 words: {word_count} words")

            return {
                'success': True,
                'content': content,
                'word_count': word_count,
                'usage': result.get('usage', {})
            }
        else:
            logger.error(f"[LLM] Failed to generate executive summary: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error'),
                'content': None
            }

    def generate_key_trends(
        self,
        analyses: List[Dict],
        time_range: str = "本周"
    ) -> Dict[str, Any]:
        """
        Generate key trends analysis using LLM

        Args:
            analyses: List of analysis results
            time_range: Time period description

        Returns:
            Dict with success status and content
        """
        from .prompts import VCPEPromptTemplates

        prompt_templates = VCPEPromptTemplates()
        messages = prompt_templates.get_key_trends_prompt(analyses, time_range)

        logger.info(f"[LLM] Generating key trends for {len(analyses)} analyses")

        result = self.chat_completion(
            messages=messages,
            max_tokens=self.config.max_tokens_long,
            use_long_timeout=True  # Use 180s timeout for large requests
        )

        if result['success']:
            logger.info(f"[LLM] Key trends generated ({result.get('usage', {}).get('total_tokens', 'N/A')} tokens)")
            return {
                'success': True,
                'content': result['content'],
                'usage': result.get('usage', {})
            }
        else:
            logger.error(f"[LLM] Failed to generate key trends: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error'),
                'content': None
            }

    def generate_recommendations(
        self,
        analyses: List[Dict],
        time_range: str = "本周"
    ) -> Dict[str, Any]:
        """
        Generate investment recommendations using LLM

        Args:
            analyses: List of analysis results
            time_range: Time period description

        Returns:
            Dict with success status and content
        """
        from .prompts import VCPEPromptTemplates

        prompt_templates = VCPEPromptTemplates()
        messages = prompt_templates.get_recommendations_prompt(analyses, time_range)

        logger.info(f"[LLM] Generating recommendations for {len(analyses)} analyses")

        result = self.chat_completion(
            messages=messages,
            max_tokens=self.config.max_tokens_long,
            use_long_timeout=True  # Use 180s timeout for large requests
        )

        if result['success']:
            logger.info(f"[LLM] Recommendations generated ({result.get('usage', {}).get('total_tokens', 'N/A')} tokens)")
            return {
                'success': True,
                'content': result['content'],
                'usage': result.get('usage', {})
            }
        else:
            logger.error(f"[LLM] Failed to generate recommendations: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error'),
                'content': None
            }

    def generate_email_analysis(
        self,
        analysis: Dict,
        email_index: int
    ) -> Dict[str, Any]:
        """
        Generate deep email analysis using LLM

        Args:
            analysis: Single analysis result
            email_index: Email index number

        Returns:
            Dict with success status and content
        """
        from .prompts import VCPEPromptTemplates

        prompt_templates = VCPEPromptTemplates()
        messages = prompt_templates.get_email_analysis_prompt(analysis, email_index)

        logger.info(f"[LLM] Generating deep analysis for email {email_index}")

        result = self.chat_completion(
            messages=messages,
            max_tokens=self.config.max_tokens_long
        )

        if result['success']:
            logger.info(f"[LLM] Email analysis generated ({result.get('usage', {}).get('total_tokens', 'N/A')} tokens)")
            return {
                'success': True,
                'content': result['content'],
                'usage': result.get('usage', {})
            }
        else:
            logger.error(f"[LLM] Failed to generate email analysis: {result.get('error')}")
            return {
                'success': False,
                'error': result.get('error'),
                'content': None
            }

    def generate_full_article(
        self,
        weekly_data: Dict,
        all_analyses: List[Dict]
    ) -> Dict:
        """
        生成完整的2000字周报文章

        Args:
            weekly_data: 本周汇总数据
            all_analyses: 所有邮件分析结果

        Returns:
            包含成功状态、文章内容和使用量的字典
        """
        from .prompts import VCPEPromptTemplates
        from openai import OpenAI

        prompt_templates = VCPEPromptTemplates()
        messages = prompt_templates.get_full_article_prompt(weekly_data, all_analyses)

        logger.info(f"[LLM] Generating full article ({len(all_analyses)} emails, 2000+ words)")

        # Create a temporary client with longer timeout for article generation
        long_timeout_client = OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            timeout=self.config.timeout_long  # Use longer timeout (180 seconds)
        )

        # Prepare request parameters
        request_params = {
            'model': self.config.model,
            'messages': messages,
            'temperature': self.config.temperature,
            'max_tokens': self.config.max_tokens_long + 2000,
            'top_p': self.config.top_p,
            'frequency_penalty': self.config.frequency_penalty,
            'presence_penalty': self.config.presence_penalty
        }

        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"API request for full article (attempt {attempt + 1}/{self.config.max_retries})")

                response = long_timeout_client.chat.completions.create(**request_params)
                content = response.choices[0].message.content

                # Parse usage info
                usage = {
                    'prompt_tokens': response.usage.prompt_tokens if response.usage else 0,
                    'completion_tokens': response.usage.completion_tokens if response.usage else 0,
                    'total_tokens': response.usage.total_tokens if response.usage else 0,
                }

                logger.info(f"[LLM] Full article API success: {usage['total_tokens']} tokens")

                word_count = len(content)

                # 验证字数是否达标
                if word_count < 1500:
                    logger.warning(f"[LLM] Article may be too short: {word_count} chars (target: 2000+)")
                elif word_count >= 2000:
                    logger.info(f"[LLM] Article meets 2000+ word requirement: {word_count} chars")

                return {
                    'success': True,
                    'content': content,
                    'word_count': word_count,
                    'usage': usage
                }

            except Exception as e:
                last_error = e
                error_type = type(e).__name__

                # Don't retry on certain errors
                if error_type in ['AuthenticationError', 'PermissionError']:
                    logger.error(f"API authentication error: {e}")
                    return {
                        'success': False,
                        'error': str(e),
                        'error_type': error_type,
                        'content': None
                    }

                # Calculate backoff delay
                delay = self.config.retry_delay_base * (2 ** attempt)

                if attempt < self.config.max_retries - 1:
                    logger.warning(f"API request for full article failed (attempt {attempt + 1}): {e}. Retrying in {delay}s...")
                    time.sleep(delay)
                else:
                    logger.error(f"API request for full article failed after {self.config.max_retries} attempts: {e}")

        # All retries exhausted
        return {
            'success': False,
            'error': str(last_error),
            'error_type': type(last_error).__name__,
            'content': None
        }


def get_default_client() -> Optional[DeepSeekClient]:
    """
    Get default LLM client from environment configuration

    Returns:
        DeepSeekClient instance or None if not configured
    """
    config = APIConfig.from_env()

    if not config.validate():
        return None

    return DeepSeekClient(config)
