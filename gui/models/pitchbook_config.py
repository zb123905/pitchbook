"""
PitchBook 下载配置数据模型

GUI 配置的数据类定义
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional


@dataclass
class PitchBookDownloadConfig:
    """PitchBook 下载配置"""

    # 下载设置
    max_count: int = 10                    # 最大下载数量 (1-50)
    retries: int = 2                       # 重试次数 (1-5)
    headless: bool = False                 # 无头模式

    # 来源设置
    listing_url: str = "https://pitchbook.com/news/reports"  # 列表页 URL
    single_url: str = ""                   # 单个报告 URL（如果设置，则只下载这一个）

    # 输出设置
    output_dir: str = r"E:\pitch\数据储存\文件抓取"  # 输出目录

    # 凭据显示（不存储实际凭据，只显示状态）
    credentials_configured: bool = False   # 凭据是否已配置

    def validate(self) -> tuple[bool, str]:
        """
        验证配置

        Returns:
            (是否有效, 错误消息)
        """
        if self.max_count < 1 or self.max_count > 50:
            return False, "最大下载数量应在 1-50 之间"

        if self.retries < 1 or self.retries > 5:
            return False, "重试次数应在 1-5 之间"

        if self.listing_url and not self.listing_url.startswith("http"):
            return False, "列表页 URL 格式不正确"

        if self.single_url and not self.single_url.startswith("http"):
            return False, "报告 URL 格式不正确"

        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PitchBookDownloadConfig':
        """从字典创建配置"""
        return cls(
            max_count=data.get('max_count', 10),
            retries=data.get('retries', 2),
            headless=data.get('headless', False),
            listing_url=data.get('listing_url', 'https://pitchbook.com/news/reports'),
            single_url=data.get('single_url', ''),
            output_dir=data.get('output_dir', ''),
            credentials_configured=data.get('credentials_configured', False)
        )

    def get_source_url(self) -> str:
        """获取实际使用的来源 URL"""
        return self.single_url if self.single_url else self.listing_url

    def is_single_mode(self) -> bool:
        """是否为单个报告下载模式"""
        return bool(self.single_url)


@dataclass
class PitchBookCredentials:
    """PitchBook 凭据配置"""

    first_name: str = ""
    last_name: str = ""
    email: str = ""
    company: str = ""
    title: str = ""
    phone: str = ""
    country: str = ""

    def is_complete(self) -> bool:
        """检查必填字段是否完整"""
        return all([
            self.first_name,
            self.last_name,
            self.email,
            self.company,
            self.title
        ])

    def validate(self) -> tuple[bool, str]:
        """验证凭据"""
        if not self.first_name:
            return False, "请输入名"
        if not self.last_name:
            return False, "请输入姓"
        if not self.email or '@' not in self.email:
            return False, "请输入有效的邮箱地址"
        if not self.company:
            return False, "请输入公司名称"
        if not self.title:
            return False, "请输入职位"
        return True, ""

    def to_env_dict(self) -> Dict[str, str]:
        """转换为环境变量字典"""
        return {
            'PB_FIRST_NAME': self.first_name,
            'PB_LAST_NAME': self.last_name,
            'PB_EMAIL': self.email,
            'PB_COMPANY': self.company,
            'PB_TITLE': self.title,
            'PB_PHONE': self.phone,
            'PB_COUNTRY': self.country
        }

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PitchBookCredentials':
        """从字典创建凭据"""
        return cls(
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data.get('email', ''),
            company=data.get('company', ''),
            title=data.get('title', ''),
            phone=data.get('phone', ''),
            country=data.get('country', '')
        )
