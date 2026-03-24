"""
Model Download Script for NLP Module
Downloads and sets up required spaCy models for Chinese and English text processing.
"""
import os
import sys
import logging
import subprocess

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_spacy_installed():
    """Check if spaCy is installed"""
    try:
        import spacy
        logger.info(f"✓ spaCy version: {spacy.__version__}")
        return True
    except ImportError:
        logger.error("✗ spaCy is not installed")
        logger.info("Run: pip install -r requirements/nlp.txt")
        return False


def download_chinese_model():
    """Download Chinese spaCy model"""
    logger.info("Downloading Chinese spaCy model (zh_core_web_sm)...")

    try:
        # Download and install Chinese model
        subprocess.run(
            [sys.executable, "-m", "spacy", "download", "zh_core_web_sm"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("✓ Chinese model installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"✗ Failed to download Chinese model: {e}")
        logger.info("Alternative: Manually run: python -m spacy download zh_core_web_sm")
        return False


def download_english_model():
    """Download English spaCy model"""
    logger.info("Downloading English spaCy model (en_core_web_sm)...")

    try:
        subprocess.run(
            [sys.executable, "-m", "spacy", "download", "en_core_web_sm"],
            check=True,
            capture_output=True,
            text=True
        )
        logger.info("✓ English model installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.warning(f"✗ Failed to download English model: {e}")
        logger.info("Alternative: Manually run: python -m spacy download en_core_web_sm")
        return False


def verify_models():
    """Verify that models can be loaded"""
    logger.info("\nVerifying model installation...")

    success = True

    # Test Chinese model
    try:
        import spacy
        nlp_zh = spacy.load("zh_core_web_sm")
        test_text = "这是一个测试。"
        doc = nlp_zh(test_text)
        logger.info(f"✓ Chinese model (zh_core_web_sm) - OK")
    except Exception as e:
        logger.warning(f"✗ Chinese model: {e}")
        success = False

    # Test English model
    try:
        import spacy
        nlp_en = spacy.load("en_core_web_sm")
        test_text = "This is a test."
        doc = nlp_en(test_text)
        logger.info(f"✓ English model (en_core_web_sm) - OK")
    except Exception as e:
        logger.warning(f"✗ English model: {e}")
        success = False

    return success


def main():
    """Main download function"""
    print("="*70)
    print("NLP Model Download Script")
    print("="*70)

    # Check spaCy installation
    if not check_spacy_installed():
        return False

    print("\n" + "="*70)
    print("Downloading Required Models")
    print("="*70)

    # Download models
    chinese_ok = download_chinese_model()
    english_ok = download_english_model()

    print("\n" + "="*70)
    print("Model Installation Summary")
    print("="*70)

    if chinese_ok:
        print("✓ Chinese model (zh_core_web_sm)")
    else:
        print("✗ Chinese model - Failed")

    if english_ok:
        print("✓ English model (en_core_web_sm)")
    else:
        print("✗ English model - Failed")

    # Verify
    if chinese_ok or english_ok:
        print("\nVerifying models...")
        verify_ok = verify_models()

        if verify_ok:
            print("\n✓ All models installed and verified successfully!")
            return True
        else:
            print("\n⚠ Some models failed verification")
            return False
    else:
        print("\n✗ No models were installed successfully")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
