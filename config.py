"""
配置文件
"""
import os
from path_utils import get_app_dir, get_user_data_path, ensure_directory

# 项目根目录
PROJECT_ROOT = get_app_dir()

# 数据存储路径（使用用户数据目录，跨机器兼容）
DATA_DIR = get_user_data_path('data')
EMAILS_DIR = os.path.join(DATA_DIR, 'emails')      # 存储原始邮件文件
REPORTS_DIR = os.path.join(DATA_DIR, 'reports')     # 存储分析报告
DOWNLOADS_DIR = os.path.join(DATA_DIR, 'downloads') # 存储下载的报告文件
LOGS_DIR = os.path.join(DATA_DIR, 'logs')        # 存储日志文件

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

# Web 爬虫存储路径
SCRAPER_MARKDOWN_DIR = AI_ANALYSIS_DIR  # Markdown 输出（用于AI分析）
SCRAPER_PDF_DIR = HUMAN_READABLE_PDF_DIR  # PDF 输出（供人工阅读）
SCRAPER_CACHE_DIR = os.path.join(DATA_DIR, 'scraper_cache')  # 爬虫缓存
SCRAPER_LOGS_DIR = os.path.join(LOGS_DIR, 'scraper')   # 爬虫日志

# 创建必要的目录
def setup_directories():
    directories = [
        DATA_DIR, EMAILS_DIR, REPORTS_DIR, DOWNLOADS_DIR, LOGS_DIR,
        HUMAN_READABLE_DIR, HUMAN_READABLE_PDF_DIR,
        HUMAN_READABLE_SUMMARY_DIR, HUMAN_READABLE_EMAIL_DIR,
        AI_ANALYSIS_DIR, SCRAPER_CACHE_DIR, SCRAPER_LOGS_DIR,
        MODEL_CACHE_DIR, NLP_MODELS_DIR, CHART_TEMP_DIR
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
