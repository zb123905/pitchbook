"""
Date parsing and processing utilities
"""
from datetime import datetime, timedelta
from typing import Optional, List
import re
from dateutil import parser as date_parser


def parse_flexible_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string with multiple format support
    Handles Chinese and English date formats
    """
    if not date_str:
        return None

    date_formats = [
        # Chinese formats
        '%Y年%m月%d日',
        '%Y-%m-%d',
        '%Y/%m/%d',
        # English formats
        '%B %d, %Y',
        '%b %d, %Y',
        '%d %B %Y',
        '%d %b %Y',
        '%Y-%m-%d',
        '%Y/%m/%d',
        # ISO formats
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ',
        # RFC formats
        '%a, %d %b %Y %H:%M:%S %z',
    ]

    # Try each format
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue

    # Try dateutil parser as fallback
    try:
        return date_parser.parse(date_str)
    except:
        return None


def extract_dates_from_text(text: str) -> List[dict]:
    """
    Extract all dates from text
    Returns list of {'date': datetime, 'text': str, 'position': tuple}
    """
    dates = []

    # Date patterns
    patterns = [
        # Chinese: 2024年3月15日, 2024-03-15
        r'\d{4}[-年]\d{1,2}[-月]\d{1,2}[日]?',

        # English: March 15, 2024
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|December)[a-z]*\s+\d{1,2},?\s+\d{4}',

        # ISO: 2024-03-15
        r'\d{4}-\d{2}-\d{2}',
    ]

    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE)
        for match in matches:
            date_text = match.group(0)
            date_obj = parse_flexible_date(date_text)

            if date_obj:
                dates.append({
                    'date': date_obj,
                    'text': date_text,
                    'position': match.span()
                })

    # Sort by position
    dates.sort(key=lambda x: x['position'][0])

    return dates


def get_date_range_days(start_date: datetime, end_date: datetime) -> int:
    """Get number of days between two dates"""
    return (end_date - start_date).days


def is_date_in_range(date: datetime, start: datetime, end: datetime) -> bool:
    """Check if date is within range (inclusive)"""
    return start <= date <= end


def format_date_chinese(date: datetime) -> str:
    """Format date in Chinese format"""
    return date.strftime('%Y年%m月%d日')


def format_date_english(date: datetime) -> str:
    """Format date in English format"""
    return date.strftime('%B %d, %Y')
