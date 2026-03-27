"""
Chinese text processing utilities
"""
import re
from typing import List, Tuple, Optional


def is_chinese_char(char: str) -> bool:
    """Check if a character is Chinese"""
    return '\u4e00' <= char <= '\u9fff'


def has_chinese(text: str) -> bool:
    """Check if text contains Chinese characters"""
    return any(is_chinese_char(c) for c in text)


def normalize_chinese_numbers(text: str) -> str:
    """
    Normalize Chinese numbers to Arabic numerals
    例如: 一百二十三 -> 123
    """
    chinese_num_map = {
        '零': '0', '一': '1', '二': '2', '三': '3', '四': '4',
        '五': '5', '六': '6', '七': '7', '八': '8', '九': '9',
        '十': '10'
    }

    result = text
    for cn, ar in chinese_num_map.items():
        result = result.replace(cn, ar)

    return result


def extract_chinese_amount(text: str) -> List[dict]:
    """
    Extract amounts in Chinese format
    例如: 1亿美元, 500万人民币, 2.5亿元
    """
    amount_pattern = r'(\d+(?:\.\d+)?)\s*(亿|万|千)?\s*(美元|人民币|元|港币|欧元|日元|GBP|EUR|USD|CNY|HKD|JPY)'

    amounts = []
    matches = re.finditer(amount_pattern, text)

    for match in matches:
        number = float(match.group(1))
        unit = match.group(2) or ''
        currency = match.group(3)

        # Convert to standard format
        if unit == '亿':
            number = number * 100000000
        elif unit == '万':
            number = number * 10000

        amounts.append({
            'amount': number,
            'currency': currency,
            'original_text': match.group(0),
            'position': match.span()
        })

    return amounts


def split_chinese_english(text: str) -> Tuple[str, str]:
    """Split text into Chinese and English parts"""
    chinese_chars = []
    english_chars = []

    for char in text:
        if is_chinese_char(char):
            chinese_chars.append(char)
        else:
            english_chars.append(char)

    return ''.join(chinese_chars), ''.join(english_chars)


def clean_chinese_punctuation(text: str) -> str:
    """Normalize Chinese punctuation"""
    punct_map = {
        '。': '.',
        '，': ',',
        '！': '!',
        '？': '?',
        '；': ';',
        '：': ':',
        '（': '(',
        '）': ')',
        '【': '[',
        '】': ']',
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
    }

    for cn, en in punct_map.items():
        text = text.replace(cn, en)

    return text
