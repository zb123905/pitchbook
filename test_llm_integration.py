"""
LLM Integration Test Script
Tests DeepSeek API client initialization and connectivity
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("LLM Integration Diagnostic Test")
print("=" * 60)

# Step 1: Check environment variables
print("\n[1] Environment Variables Check:")
print("-" * 40)
print(f"  LLM_ENABLED:              {os.getenv('LLM_ENABLED', 'NOT SET')}")
print(f"  DEEPSEEK_API_KEY:         {'SET (len=' + str(len(os.getenv('DEEPSEEK_API_KEY', ''))) + ')' if os.getenv('DEEPSEEK_API_KEY') else 'NOT SET'}")
print(f"  DEEPSEEK_BASE_URL:        {os.getenv('DEEPSEEK_BASE_URL', 'NOT SET')}")
print(f"  DEEPSEEK_MODEL:           {os.getenv('DEEPSEEK_MODEL', 'NOT SET')}")
print(f"  DEEPSEEK_TIMEOUT:         {os.getenv('DEEPSEEK_TIMEOUT', 'NOT SET')}")
print(f"  DEEPSEEK_MAX_RETRIES:     {os.getenv('DEEPSEEK_MAX_RETRIES', 'NOT SET')}")

# Step 2: Check if openai package is installed
print("\n[2] Package Dependencies Check:")
print("-" * 40)
try:
    import openai
    print(f"  openai package:           ✓ Installed (v{openai.__version__})")
except ImportError:
    print(f"  openai package:           ✗ NOT INSTALLED")
    print(f"                            Run: pip install openai")
    sys.exit(1)

# Step 3: Test APIConfig
print("\n[3] APIConfig Initialization:")
print("-" * 40)
try:
    from llm.deepseek_client import APIConfig
    config = APIConfig.from_env()
    print(f"  APIConfig.from_env():     ✓ Success")
    print(f"  base_url:                 {config.base_url}")
    print(f"  model:                    {config.model}")
    print(f"  api_key length:           {len(config.api_key) if config.api_key else 0}")
    print(f"  validate():               {config.validate()}")

    if not config.validate():
        print(f"\n  ✗ ERROR: API key is empty or invalid!")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    sys.exit(1)

# Step 4: Test DeepSeekClient initialization
print("\n[4] DeepSeekClient Initialization:")
print("-" * 40)
try:
    from llm.deepseek_client import DeepSeekClient
    client = DeepSeekClient(config)
    print(f"  DeepSeekClient():         ✓ Success")
    print(f"  is_available():           {client.is_available()}")

    if not client.is_available():
        print(f"\n  ✗ ERROR: Client not available!")
        sys.exit(1)
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    sys.exit(1)

# Step 5: Test API connection
print("\n[5] API Connection Test:")
print("-" * 40)
try:
    result = client.test_connection()
    print(f"  test_connection():        {'✓ Success' if result['success'] else '✗ Failed'}")
    if result['success']:
        print(f"  Response:                 {result.get('response', 'N/A')}")
    else:
        print(f"  Error:                    {result.get('error', 'Unknown')}")
except Exception as e:
    print(f"  ✗ ERROR: {e}")
    sys.exit(1)

# Step 6: Test balance check
print("\n[6] API Balance Check:")
print("-" * 40)
try:
    balance = client.check_balance()
    print(f"  check_balance():           {'✓ Success' if balance['success'] else '✗ Failed'}")
    if balance['success']:
        print(f"  Message:                  {balance.get('message', 'N/A')}")
    else:
        print(f"  Error:                    {balance.get('error', 'Unknown')}")
except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Step 7: Test actual content analysis
print("\n[7] Content Analysis Test:")
print("-" * 40)
try:
    test_content = """
    PitchBook reported that AI startup Anthropic raised $2B in Series C funding
    led by Spark Capital and Altimeter Capital. The round values the company at $20B.
    This is one of the largest AI funding rounds in 2024.
    """

    result = client.analyze_content(
        content=test_content,
        analysis_type='email',
        metadata={'subject': 'Test: Anthropic Funding'}
    )

    print(f"  analyze_content():        {'✓ Success' if result['success'] else '✗ Failed'}")
    if result['success']:
        print(f"  Tokens used:              {result.get('usage', {}).get('total_tokens', 'N/A')}")
        print(f"  Data keys:               {list(result.get('data', {}).keys())}")
    else:
        print(f"  Error:                    {result.get('error', 'Unknown')}")
except Exception as e:
    print(f"  ✗ ERROR: {e}")

# Final summary
print("\n" + "=" * 60)
print("Diagnostic Complete")
print("=" * 60)
print("\nIf all tests passed, LLM integration is working correctly.")
print("If tests failed, check the error messages above.")
