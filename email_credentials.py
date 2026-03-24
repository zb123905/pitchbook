"""
Email credentials configuration
For IMAP email fetching
"""
from datetime import datetime, timedelta

# IMAP Email Configuration (QQ邮箱)
IMAP_CONFIG = {
    'email_address': '3185709067@qq.com',  # Your QQ email
    'password': 'glhziqkekwmpdfdc',  # Your QQ mail authorization code (16 chars)

    # 邮件日期范围配置
    'fetch_days': 7,          # 只读取最近 7 天的邮件（默认一周）
    'max_emails': 50,         # 最多读取 50 封邮件（增加数量以确保覆盖一周）

    # 爬虫配置
    'max_scrape_links': 0,    # 0 表示爬取所有符合条件的链接，>0 表示限制数量
    'scrape_delay_min': 5,    # 每个请求的最小延迟（秒）
    'scrape_delay_max': 12,   # 每个请求的最大延迟（秒）

    # 日期过滤
    'date_filter_days': 7,    # 只爬取最近 7 天发布的内容

    # 报告格式配置 (Phase 1)
    'generate_pdf': False,     # 是否生成PDF报告（包含图表）
                               # False = 生成Word报告
}

# Use IMAP mode? Set to True to use IMAP, False to use local files
USE_IMAP_MODE = False


def get_date_range(days=7):
    """
    获取日期范围（从今天往前推 N 天）

    Args:
        days: 往前推的天数

    Returns:
        tuple: (start_date, end_date) 日期对象
    """
    today = datetime.now().date()
    start_date = today - timedelta(days=days)
    return start_date, today


def is_within_date_range(date_str, start_date, end_date):
    """
    检查日期字符串是否在指定范围内

    Args:
        date_str: 日期字符串
        start_date: 开始日期对象
        end_date: 结束日期对象

    Returns:
        bool: 是否在范围内
    """
    try:
        # 尝试多种日期格式（包括中文格式的斜杠）
        date_formats = [
            '%Y-%m-%d',
            '%Y-%m-%d %H:%M:%S',
            '%Y/%m/%d %H:%M:%S',  # 中文格式：2026/3/16 19:21:34
            '%Y/%m/%d',
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
        ]
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str.strip(), fmt).date()
                return start_date <= date_obj <= end_date
            except ValueError:
                continue
        return False
    except Exception:
        return False
