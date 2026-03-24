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

logger = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """DeepSeek API Configuration"""
    base_url: str = "https://openrouter.fans/v1"
    api_key: str = ""
    model: str = "deepseek-chat"
    timeout: int = 30
    max_retries: int = 3
    retry_delay_base: float = 2.0  # Base for exponential backoff
    temperature: float = 0.3
    max_tokens: int = 2000

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
            max_retries=int(os.getenv('DEEPSEEK_MAX_RETRIES', '3')),
            temperature=float(os.getenv('DEEPSEEK_TEMPERATURE', '0.3')),
            max_tokens=int(os.getenv('DEEPSEEK_MAX_TOKENS', '2000'))
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

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send chat completion request with retry logic

        Args:
            messages: Chat messages in OpenAI format
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: Response format (e.g., "json_object")

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
            'max_tokens': max_tokens
        }

        # Add response format if specified
        if response_format == 'json_object':
            request_params['response_format'] = {'type': 'json_object'}

        # Retry logic with exponential backoff
        last_error = None
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"API request (attempt {attempt + 1}/{self.config.max_retries})")

                response = self._client.chat.completions.create(**request_params)

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

            return {
                'success': True,
                'data': parsed_data,
                'usage': result.get('usage', {}),
                'raw_response': result['content']
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM JSON response: {e}")

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
