"""
配置数据模型

GUI 配置的数据类定义，包含验证和序列化功能
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any
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
class ScraperConfig:
    """爬虫配置"""
    enable_scraper: bool = True   # 是否启用爬虫
    fast_fail: bool = True        # 快速失败模式（403/400错误不重试）
    max_scrape_links: int = 3     # 默认限制3个链接（优化后）
    scrape_delay_min: int = 2     # 优化后默认值
    scrape_delay_max: int = 5     # 优化后默认值
    date_filter_days: int = 7

    def validate(self) -> tuple[bool, str]:
        """验证配置"""
        if self.max_scrape_links < 0:
            return False, "链接数量不能为负数"
        if self.scrape_delay_min < 1 or self.scrape_delay_min > 60:
            return False, "最小延迟应在 1-60 秒之间"
        if self.scrape_delay_max < self.scrape_delay_min:
            return False, "最大延迟应大于最小延迟"
        if self.date_filter_days < 1 or self.date_filter_days > 30:
            return False, "日期过滤范围应在 1-30 天之间"
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
class PipelineConfig:
    """完整流程配置"""
    email: EmailConfig = field(default_factory=EmailConfig)
    scraper: ScraperConfig = field(default_factory=ScraperConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)

    def validate_all(self) -> list[tuple[str, bool, str]]:
        """验证所有配置，返回 (section, is_valid, error_message) 列表"""
        results = []
        results.append(("邮箱", *self.email.validate()))
        results.append(("爬虫", *self.scraper.validate()))
        results.append(("分析", *self.analysis.validate()))
        return results

    def is_valid(self) -> bool:
        """检查所有配置是否有效"""
        return all(valid for _, valid, _ in self.validate_all())

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'email': asdict(self.email),
            'scraper': asdict(self.scraper),
            'analysis': asdict(self.analysis)
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PipelineConfig':
        """从字典创建配置"""
        return cls(
            email=EmailConfig(**data.get('email', {})),
            scraper=ScraperConfig(**data.get('scraper', {})),
            analysis=AnalysisConfig(**data.get('analysis', {}))
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
