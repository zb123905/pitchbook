"""
配置文件
"""
import os
from path_utils import get_app_dir, get_user_data_path, ensure_directory

# 项目根目录
PROJECT_ROOT = get_app_dir()

# 数据存储路径（使用用户数据目录，跨机器兼容）
DATA_DIR = get_user_data_path('data')
EMAILS_DIR = get_user_data_path('数据储存/原始邮件')      # 存储原始邮件文件
REPORTS_DIR = get_user_data_path('数据储存/JSON报告')     # 存储分析报告
DOWNLOADS_DIR = os.path.join(DATA_DIR, 'downloads') # 存储下载的报告文件
LOGS_DIR = get_user_data_path('数据储存/logs')        # 存储日志文件

# 用户指定输出路径 - 统一到两个主目录
# 供人阅读使用的文件（使用用户文档目录，跨机器兼容）
HUMAN_READABLE_DIR = get_user_data_path('数据储存/供人阅读使用')
HUMAN_READABLE_PDF_DIR = os.path.join(HUMAN_READABLE_DIR, 'PDF报告')
HUMAN_READABLE_SUMMARY_DIR = os.path.join(HUMAN_READABLE_DIR, '汇总总结')
HUMAN_READABLE_EMAIL_DIR = os.path.join(HUMAN_READABLE_DIR, '提取邮件')

# AI 分析使用的文件
AI_ANALYSIS_DIR = get_user_data_path('数据储存/ai分析使用')

# 兼容旧路径（保持向后兼容）
EMAIL_EXTRACTION_DIR = HUMAN_READABLE_EMAIL_DIR
SUMMARY_REPORT_DIR = HUMAN_READABLE_SUMMARY_DIR
PDF_REPORT_DIR = HUMAN_READABLE_PDF_DIR
USER_WORD_REPORT_DIR = HUMAN_READABLE_SUMMARY_DIR

# NLP模型缓存目录 (Phase 2 - Entity Recognition)
MODEL_CACHE_DIR = get_user_data_path('models')
NLP_MODELS_DIR = get_user_data_path('nlp/models')

# 图表临时目录 (Phase 3 - Visualization)
CHART_TEMP_DIR = os.path.join(DATA_DIR, 'temp_charts')

# 创建必要的目录
def setup_directories():
    directories = [
        DATA_DIR, EMAILS_DIR, REPORTS_DIR, DOWNLOADS_DIR, LOGS_DIR,
        HUMAN_READABLE_DIR, HUMAN_READABLE_PDF_DIR,
        HUMAN_READABLE_SUMMARY_DIR, HUMAN_READABLE_EMAIL_DIR,
        AI_ANALYSIS_DIR, MODEL_CACHE_DIR, NLP_MODELS_DIR, CHART_TEMP_DIR
    ]
    for directory in directories:
        ensure_directory(directory)

setup_directories()

# ================= Phase 2: NLP Configuration =================
# NLP功能开关
ENABLE_NLP_ENTITY_EXTRACTION = True  # 启用实体识别
ENABLE_NLP_RELATION_EXTRACTION = True  # 启用关系抽取

# NLP处理配置
MAX_CONTENT_LENGTH = 100000  # 最大内容长度（字符）
BATCH_SIZE = 10  # 批处理大小
NLP_USE_SPACY = True  # 使用spaCy（如果可用）

# ================= LLM Configuration =================
# DeepSeek API配置 - 增强内容分析能力
ENABLE_LLM_ANALYSIS = os.getenv('LLM_ENABLED', 'false').lower() == 'true'  # 默认关闭
LLM_API_BASE_URL = os.getenv('DEEPSEEK_BASE_URL', 'https://openrouter.fans/v1')
LLM_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')  # 从环境变量读取
LLM_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek-chat')
LLM_FALLBACK_TO_NLP = True  # API失败时降级到本地NLP
LLM_MAX_RETRIES = int(os.getenv('DEEPSEEK_MAX_RETRIES', '3'))  # 最大重试次数
LLM_TIMEOUT = int(os.getenv('DEEPSEEK_TIMEOUT', '30'))  # 超时时间（秒）
LLM_TEMPERATURE = float(os.getenv('DEEPSEEK_TEMPERATURE', '0.3'))  # 采样温度
LLM_MAX_TOKENS = int(os.getenv('DEEPSEEK_MAX_TOKENS', '3000'))  # 默认token限制
LLM_MAX_TOKENS_LONG = int(os.getenv('DEEPSEEK_MAX_TOKENS_LONG', '6000'))  # 长报告token限制
LLM_MAX_TOKENS_EXECUTIVE = int(os.getenv('DEEPSEEK_MAX_TOKENS_EXECUTIVE', '4000'))  # 执行摘要token限制 (目标1500-2000字中文)

# ================= Professional Formatting Configuration =================

# Page Settings (in centimeters)
MARGIN_TOP_CM = 2.5
MARGIN_BOTTOM_CM = 2.5
MARGIN_LEFT_CM = 2.0
MARGIN_RIGHT_CM = 2.0

# Template Path
CAT_BACKGROUND_TEMPLATE = r'D:\模拟c盘\猫通用背景板.docx'

# Typography - 标题使用黑体，正文使用宋体
FONT_MAIN_TITLE = '黑体'      # 标题使用黑体
FONT_HEADING1 = '黑体'        # 一级标题使用黑体
FONT_HEADING2 = '黑体'        # 二级标题使用黑体
FONT_BODY = '宋体'            # 正文使用宋体
FONT_DATA = '等线'

# Font Sizes (points)
FONT_SIZE_MAIN_TITLE = 22  # pt (二号)
FONT_SIZE_HEADING1 = 15    # pt (小三)
FONT_SIZE_HEADING2 = 14    # pt (四号)
FONT_SIZE_BODY = 12        # pt (小四)
FONT_SIZE_DATA = 10.5      # pt (五号)

# Color Scheme
COLOR_TEXT_DARK = '#333333'      # Dark gray for body text
COLOR_TEXT_LIGHT = '#666666'     # Light gray for secondary text
COLOR_ACCENT_BLUE = '#0066CC'    # Deep blue for titles/keywords
COLOR_DIVIDER = '#EEEEEE'        # Light gray for dividers
COLOR_HIGHLIGHT_BG = '#E6F3FF'   # Light blue background
COLOR_BORDER_LIGHT = '#DDDDDD'   # Light border color

# Spacing
LINE_SPACING = 1.0               # 1.0x line spacing (compact to reduce whitespace)
SPACING_BEFORE_PARA = 0.5        # lines
SPACING_AFTER_PARA = 0.5         # lines
FIRST_LINE_INDENT_CHARS = 2      # 2 characters

# Heading Spacing (points) - Compact spacing to reduce whitespace
HEADING1_BEFORE_PT = 4           # Reduced from 6pt
HEADING1_AFTER_PT = 2            # Reduced from 3pt
HEADING2_BEFORE_PT = 3           # Reduced from 4pt
HEADING2_AFTER_PT = 2            # Reduced from 2pt
BODY_BEFORE_PT = 0               # No space before body paragraphs
BODY_AFTER_PT = 0                # No space after body paragraphs

# Background Settings
BACKGROUND_TRANSPARENCY = 0.6    # 50-70%
CONTENT_OVERLAY_TRANSPARENCY = 0.8  # 80%

# Content Overlay Settings
CONTENT_OVERLAY_COLOR = 'FFFFFF'  # White overlay color (hex)
CONTENT_OVERLAY_ENABLED = True    # Enable white semi-transparent overlay on content

# Background Transparency Range (for different output formats)
BACKGROUND_TRANSPARENCY_MIN = 0.5  # 50% minimum
BACKGROUND_TRANSPARENCY_MAX = 0.7  # 70% maximum
BACKGROUND_TRANSPARENCY_DEFAULT = 0.6  # 60% default
BACKGROUND_TRANSPARENCY_WORD = 0.6  # Word document (60%)
BACKGROUND_TRANSPARENCY_PDF = 0.6  # PDF document (60%)

# ================= Database Configuration =================
# PostgreSQL database configuration
DB_ENABLED = os.getenv('DB_ENABLED', 'false').lower() == 'true'
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', '5432'))
DB_NAME = os.getenv('DB_NAME', 'vcpe_pitchbook')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', '')
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '5'))
DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '10'))

# Database connection URL
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Backup configuration
KEEP_JSON_BACKUP = os.getenv('KEEP_JSON_BACKUP', 'true').lower() == 'true'
JSON_BACKUP_DIR = get_user_data_path('数据储存/json_backup')

# ================= File Download Configuration =================
# Download directory for PDF/Excel reports
FILE_DOWNLOAD_DIR = get_user_data_path('数据储存/文件抓取')
ensure_directory(FILE_DOWNLOAD_DIR)

# Download service configuration
DOWNLOAD_RETRY_COUNT = int(os.getenv('DOWNLOAD_RETRY_COUNT', '5'))  # Increased from 3 to 5 for better success rate
DOWNLOAD_TIMEOUT = int(os.getenv('DOWNLOAD_TIMEOUT', '30'))
DOWNLOAD_USER_AGENT = os.getenv('DOWNLOAD_USER_AGENT', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# Complete browser headers to bypass 403 errors
DOWNLOAD_HEADERS = {
    'User-Agent': DOWNLOAD_USER_AGENT,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Referer': 'https://pitchbook.com/',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'same-origin',
    'Sec-Fetch-User': '?1',
}

# ================= CloudScraper Configuration =================
# CloudScraper settings for bypassing 403 Forbidden errors
# Note: CloudScraper functionality has been removed from the system
