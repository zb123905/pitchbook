"""
配置数据模型

GUI 配置的数据类定义，包含验证和序列化功能
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any, List
import json
import os


@dataclass
class EmailConfig:
    """邮箱配置"""
    email_address: str = ""
    password: str = ""
    fetch_days: int = 7
    max_emails: int = 50

    def validate(self) -> tuple[bool, str]:
        """验证配置"""
        if not self.email_address or "@" not in self.email_address:
            return False, "邮箱地址格式不正确"
        if not self.password:
            return False, "请输入邮箱密码或授权码"
        if self.fetch_days < 1 or self.fetch_days > 30:
            return False, "日期范围应在 1-30 天之间"
        if self.max_emails < 1 or self.max_emails > 500:
            return False, "邮件数量应在 1-500 之间"
        return True, ""



@dataclass
class AnalysisConfig:
    """分析配置"""
    enable_nlp: bool = True
    enable_llm: bool = False
    enable_charts: bool = True
    generate_pdf: bool = False
    report_format: str = "word"  # word, pdf, both

    def validate(self) -> tuple[bool, str]:
        """验证配置"""
        if self.report_format not in ["word", "pdf", "both"]:
            return False, "报告格式只能是 word、pdf 或 both"
        if self.enable_llm and not self.enable_nlp:
            return False, "启用 LLM 需要同时启用 NLP"
        return True, ""


@dataclass
class DatabaseConfig:
    """数据库配置"""
    enabled: bool = False
    host: str = ""
    port: int = 5432
    database: str = "vcpe_pitchbook"
    user: str = "postgres"
    password: str = ""
    pool_size: int = 5
    keep_json_backup: bool = True

    def validate(self) -> tuple[bool, str]:
        """验证配置"""
        if self.enabled:
            if not self.host:
                return False, "数据库主机地址不能为空"
            if not self.database:
                return False, "数据库名称不能为空"
            if not self.user:
                return False, "数据库用户名不能为空"
            if self.port < 1 or self.port > 65535:
                return False, "端口范围应在 1-65535 之间"
        return True, ""


@dataclass
class AutoDiscoverConfig:
    """自动发现配置"""
    enable: bool = False                  # 启用自动发现
    max_links: int = 10                    # 最大发现数量
    recent_days: int = 30                  # 只下载最近N天
    source_url: str = "https://pitchbook.com/news/reports"  # 列表页URL

    def validate(self) -> tuple[bool, str]:
        """验证配置"""
        if self.max_links < 1 or self.max_links > 100:
            return False, "最大发现数量应在 1-100 之间"
        if self.recent_days < 1 or self.recent_days > 365:
            return False, "日期范围应在 1-365 天之间"
        return True, ""


@dataclass
class DownloadConfig:
    """下载配置"""
    enable_download: bool = True           # 启用自动下载
    enable_dedup: bool = True             # 启用去重
    use_playwright: bool = True           # 使用 Playwright 下载器（推荐，绕过 403 错误）
    retry_count: int = 3                  # 重试次数 (1-10)
    timeout: int = 30                     # 超时秒数 (10-120)
    file_types: list = field(default_factory=lambda: ["pdf", "excel"])  # 文件类型

    # 自动发现配置
    auto_discover: AutoDiscoverConfig = field(default_factory=AutoDiscoverConfig)

    def validate(self) -> tuple[bool, str]:
        """验证配置"""
        if self.retry_count < 1 or self.retry_count > 10:
            return False, "重试次数应在 1-10 之间"
        if self.timeout < 10 or self.timeout > 120:
            return False, "超时时间应在 10-120 秒之间"
        valid_types = {"pdf", "excel", "word", "all"}
        if not set(self.file_types).issubset(valid_types):
            return False, f"文件类型只能是: {', '.join(valid_types)}"
        return True, ""


@dataclass
class PipelineConfig:
    """完整流程配置"""
    email: EmailConfig = field(default_factory=EmailConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    download: DownloadConfig = field(default_factory=DownloadConfig)

    def validate_all(self) -> list[tuple[str, bool, str]]:
        """验证所有配置，返回 (section, is_valid, error_message) 列表"""
        results = []
        results.append(("邮箱", *self.email.validate()))
        results.append(("分析", *self.analysis.validate()))
        results.append(("数据库", *self.database.validate()))
        results.append(("下载", *self.download.validate()))
        results.append(("自动发现", *self.download.auto_discover.validate()))
        return results

    def is_valid(self) -> bool:
        """检查所有配置是否有效"""
        return all(valid for _, valid, _ in self.validate_all())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'email': asdict(self.email),
            'analysis': asdict(self.analysis),
            'database': asdict(self.database),
            'download': {
                **asdict(self.download),
                'auto_discover': asdict(self.download.auto_discover)
            }
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineConfig':
        """从字典创建配置"""
        # 处理 download 配置（包含 auto_discover）
        download_data = data.get('download', {})
        auto_discover_data = download_data.pop('auto_discover', {})

        download_config = DownloadConfig(**download_data)
        download_config.auto_discover = AutoDiscoverConfig(**auto_discover_data)

        return cls(
            email=EmailConfig(**data.get('email', {})),
            analysis=AnalysisConfig(**data.get('analysis', {})),
            database=DatabaseConfig(**data.get('database', {})),
            download=download_config
        )

    def save(self, filepath: str) -> bool:
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存配置失败: {e}")
            return False

    @classmethod
    def load(cls, filepath: str) -> 'PipelineConfig':
        """从文件加载配置"""
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return cls.from_dict(data)
            except Exception as e:
                print(f"加载配置失败: {e}")
        return cls()

    @classmethod
    def get_default_path(cls) -> str:
        """获取默认配置文件路径"""
        return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'gui_config.json')
