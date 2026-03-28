"""
LLM Utility Functions
Provides text analysis utilities for LLM content validation
"""
import re
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def count_chinese_words(text: str) -> int:
    """
    统计中文文本的字数（不包括标点符号和空格）

    Args:
        text: 待统计文本

    Returns:
        中文字数
    """
    # Match Chinese characters (Unicode range for CJK Unified Ideographs)
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)
    return len(chinese_chars)


def count_total_words(text: str) -> Dict[str, int]:
    """
    统计文本的字数信息

    Args:
        text: 待统计文本

    Returns:
        包含各种统计信息的字典:
        - chinese_chars: 中文字数
        - english_words: 英文单词数
        - numbers: 数字序列数
        - total_words: 总词数（中文+英文）
        - total_chars: 总字符数（包括标点和空格）
    """
    # Count Chinese characters
    chinese_chars = re.findall(r'[\u4e00-\u9fff]', text)

    # Count English words (sequences of letters)
    english_words = re.findall(r'[a-zA-Z]+', text)

    # Count numbers (sequences of digits)
    numbers = re.findall(r'\d+', text)

    return {
        'chinese_chars': len(chinese_chars),
        'english_words': len(english_words),
        'numbers': len(numbers),
        'total_words': len(chinese_chars) + len(english_words),
        'total_chars': len(text)
    }


def validate_word_count(text: str, target: int = 2000, tolerance: float = 0.1) -> Dict[str, any]:
    """
    验证文本字数是否达标

    Args:
        text: 待验证文本
        target: 目标字数（默认2000字）
        tolerance: 容差范围（默认10%）

    Returns:
        验证结果字典:
        - is_valid: 是否达标
        - word_count: 实际字数
        - target: 目标字数
        - difference: 与目标的差距
        - percentage: 达成百分比
    """
    word_count = count_chinese_words(text)
    min_words = int(target * (1 - tolerance))
    max_words = int(target * (1 + tolerance))

    is_valid = min_words <= word_count <= max_words
    difference = word_count - target
    percentage = (word_count / target * 100) if target > 0 else 0

    return {
        'is_valid': is_valid,
        'word_count': word_count,
        'target': target,
        'min_words': min_words,
        'max_words': max_words,
        'difference': difference,
        'percentage': percentage
    }


def truncate_to_word_count(text: str, max_words: int) -> str:
    """
    将文本截断到指定字数（保留完整段落）

    Args:
        text: 待截断文本
        max_words: 最大字数

    Returns:
        截断后的文本
    """
    paragraphs = text.split('\n\n')
    result = []
    current_count = 0

    for paragraph in paragraphs:
        para_word_count = count_chinese_words(paragraph)
        if current_count + para_word_count > max_words:
            # Try to find a good breaking point within the paragraph
            sentences = re.split(r'[。！？]', paragraph)
            for sentence in sentences:
                if not sentence.strip():
                    continue
                sentence_words = count_chinese_words(sentence)
                if current_count + sentence_words <= max_words:
                    result.append(sentence + '。')
                    current_count += sentence_words
                else:
                    break
            break
        else:
            result.append(paragraph)
            current_count += para_word_count

    return '\n\n'.join(result)


def estimate_reading_time(text: str, words_per_minute: int = 500) -> Dict[str, any]:
    """
    估算阅读时间

    Args:
        text: 待估算文本
        words_per_minute: 每分钟阅读字数（默认500字/分钟）

    Returns:
        阅读时间信息字典:
        - word_count: 字数
        - minutes: 分钟数
        - seconds: 秒数
        - formatted: 格式化时间字符串
    """
    word_count = count_chinese_words(text)
    total_seconds = int((word_count / words_per_minute) * 60)

    minutes = total_seconds // 60
    seconds = total_seconds % 60

    if minutes > 0:
        formatted = f"{minutes}分{seconds}秒"
    else:
        formatted = f"{seconds}秒"

    return {
        'word_count': word_count,
        'minutes': minutes,
        'seconds': seconds,
        'total_seconds': total_seconds,
        'formatted': formatted
    }


if __name__ == "__main__":
    # Test the utility functions
    test_text = """
    这是一个测试文本。用于验证中文字数统计功能是否正常工作。
    This is a test text with 123 numbers and English words.
    """

    print("=== 字数统计测试 ===")
    print(f"中文字数: {count_chinese_words(test_text)}")
    print(f"详细统计: {count_total_words(test_text)}")

    print("\n=== 字数验证测试 ===")
    long_text = "这是一个" * 1000 + "。"
    validation = validate_word_count(long_text, target=2000)
    print(f"验证结果: {validation}")

    print("\n=== 阅读时间估算测试 ===")
    reading_time = estimate_reading_time(long_text)
    print(f"阅读时间: {reading_time['formatted']}")
