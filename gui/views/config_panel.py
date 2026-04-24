"""
配置面板

提供邮箱、爬虫、分析配置的界面
"""
import customtkinter as ctk
from typing import Optional, Callable

from ..models import PipelineConfig
from ..utils.apple_theme import AppleTheme, get_color, get_font, get_spacing, get_corner_radius
from ..utils.fluent_theme import FluentTheme as Fluent, get_color as get_fluent_color, get_font as get_fluent_font, get_spacing as get_fluent_spacing, get_padding as get_fluent_padding
from ..components import AnimatedButton, AnimatedSegmentedButton, AnimatedSwitch


class ConfigPanel(ctk.CTkFrame):
    """配置面板 - 第一个标签页"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.config: Optional[PipelineConfig] = None
        self.on_config_change: Optional[Callable] = None

        self._create_widgets()
        self._load_saved_config()

    def _create_widgets(self):
        """创建界面组件"""
        # 主容器 - 可滚动，使用 Fluent Design
        container = ctk.CTkScrollableFrame(
            self,
            label_text="",
            fg_color="transparent"
        )
        container.pack(fill="both", expand=True, padx=get_fluent_padding('lg'), pady=get_fluent_padding('lg'))

        # 顶部装饰条 - 统一蓝色
        header_bar = ctk.CTkFrame(
            container,
            height=3,  # 从 4px 减少到 3px
            corner_radius=Fluent.get_corner_radius('xsmall'),  # 2px
            fg_color=Fluent.color('accent_primary')  # 统一蓝色
        )
        header_bar.pack(fill="x", pady=(0, get_fluent_spacing('lg')))

        # 标题 - 简化 Fluent 风格
        title_frame = ctk.CTkFrame(container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, get_fluent_spacing('xl')))  # 24px

        # 左侧标题 - 移除多色装饰点，只保留简洁标题
        title_left = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_left.pack(side="left")

        # 简化装饰 - 只用一个蓝色点
        dot = ctk.CTkLabel(
            title_left,
            text="●",
            font=ctk.CTkFont(size=8),
            text_color=Fluent.color('accent_primary')  # 统一蓝色
        )
        dot.pack(side="left", padx=(0, 6))

        title_label = ctk.CTkLabel(
            title_left,
            text="系统配置",
            font=get_fluent_font('title_large', 'bold'),  # 24px
            text_color=Fluent.color('text_primary')
        )
        title_label.pack(side="left")

        # 右侧统计装饰 - 简化
        stats_decor = ctk.CTkFrame(
            title_frame,
            corner_radius=Fluent.get_corner_radius('medium'),  # 8px
            fg_color=Fluent.color('bg_layer_1'),
        )
        stats_decor.pack(side="right")
        ctk.CTkLabel(
            stats_decor,
            text="⚙️",
            font=ctk.CTkFont(size=12),
            text_color=Fluent.color('accent_primary')  # 统一蓝色
        ).pack(side="left", padx=(get_fluent_padding('sm'), 4), pady=4)
        ctk.CTkLabel(
            stats_decor,
            text="6 个模块",
            font=get_fluent_font('body'),
            text_color=Fluent.color('text_secondary')
        ).pack(side="left", padx=(0, get_fluent_padding('sm')), pady=4)

        # ================= 邮箱配置卡片 - 统一蓝色边框 =================
        email_frame = self._create_fluent_card(container)
        email_frame.pack(fill="x", pady=(0, get_fluent_spacing('lg')))  # 16px (from 12px)

        # 卡片头部
        email_header = ctk.CTkFrame(email_frame, fg_color="transparent")
        email_header.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_padding('md'), get_fluent_spacing('md')))

        # 图标和标题
        icon_frame = ctk.CTkFrame(
            email_header,
            width=36,
            height=36,
            corner_radius=Fluent.get_corner_radius('large'),  # 12px (from 20px)
            fg_color=Fluent.color('accent_primary')  # 统一蓝色
        )
        icon_frame.pack(side="left")
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(
            icon_frame,
            text="📧",
            font=ctk.CTkFont(size=16)  # from 18px
        ).pack(expand=True)

        title_frame_inner = ctk.CTkFrame(email_header, fg_color="transparent")
        title_frame_inner.pack(side="left", padx=get_fluent_spacing('md'), expand=True, fill="x")
        ctk.CTkLabel(
            title_frame_inner,
            text="邮箱配置",
            font=get_fluent_font('title', 'bold'),  # 20px
            text_color=Fluent.color('text_primary'),
            anchor="w"
        ).pack(fill="x")
        ctk.CTkLabel(
            title_frame_inner,
            text="配置 Outlook 邮箱连接",
            font=get_fluent_font('caption'),
            text_color=Fluent.color('text_tertiary'),
            anchor="w"
        ).pack(fill="x")

        # 邮箱地址
        addr_frame = ctk.CTkFrame(email_frame, fg_color="transparent")
        addr_frame.pack(fill="x", padx=AppleTheme.get_padding('lg'), pady=AppleTheme.get_spacing('sm'))

        ctk.CTkLabel(
            addr_frame,
            text="邮箱地址",
            font=get_font('subheadline', 'bold'),
            text_color=AppleTheme.color('text_secondary'),
            width=80
        ).pack(side="left", padx=(0, AppleTheme.get_spacing('md')))
        self.email_entry = self._create_entry(addr_frame, "your-email@outlook.com")
        self.email_entry.pack(side="left", fill="x", expand=True)

        # 密码
        pwd_frame = ctk.CTkFrame(email_frame, fg_color="transparent")
        pwd_frame.pack(fill="x", padx=AppleTheme.get_padding('lg'), pady=AppleTheme.get_spacing('sm'))

        ctk.CTkLabel(
            pwd_frame,
            text="密码/授权码",
            font=get_font('subheadline', 'bold'),
            text_color=AppleTheme.color('text_secondary'),
            width=80
        ).pack(side="left", padx=(0, AppleTheme.get_spacing('md')))
        self.password_entry = self._create_entry(pwd_frame, "邮箱密码或应用专用密码", show="•")
        self.password_entry.pack(side="left", fill="x", expand=True)

        # 日期范围和数量 - 两列布局
        range_container = ctk.CTkFrame(email_frame, fg_color="transparent")
        range_container.pack(fill="x", padx=AppleTheme.get_padding('lg'), pady=AppleTheme.get_spacing('sm'))

        # 第一列
        col1 = ctk.CTkFrame(range_container, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            col1,
            text="日期范围",
            font=get_font('subheadline', 'bold'),
            text_color=AppleTheme.color('text_secondary')
        ).pack(anchor="w")
        row1 = ctk.CTkFrame(col1, fg_color="transparent")
        row1.pack(fill="x", pady=(AppleTheme.get_spacing('xs'), 0))
        self.days_entry = self._create_entry(row1, width=80)
        self.days_entry.pack(side="left")
        ctk.CTkLabel(
            row1,
            text=" 天",
            font=get_font('body'),
            text_color=AppleTheme.color('text_tertiary')
        ).pack(side="left", padx=AppleTheme.get_spacing('xs'))

        # 第二列
        col2 = ctk.CTkFrame(range_container, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=(AppleTheme.get_spacing('xl'), 0))
        ctk.CTkLabel(
            col2,
            text="最多邮件",
            font=get_font('subheadline', 'bold'),
            text_color=AppleTheme.color('text_secondary')
        ).pack(anchor="w")
        row2 = ctk.CTkFrame(col2, fg_color="transparent")
        row2.pack(fill="x", pady=(AppleTheme.get_spacing('xs'), 0))
        self.max_emails_entry = self._create_entry(row2, width=80)
        self.max_emails_entry.pack(side="left")
        ctk.CTkLabel(
            row2,
            text=" 封",
            font=get_font('body'),
            text_color=AppleTheme.color('text_tertiary')
        ).pack(side="left", padx=AppleTheme.get_spacing('xs'))

        # ================= 分析配置卡片 - 统一蓝色边框 =================
        analysis_frame = self._create_fluent_card(container)
        analysis_frame.pack(fill="x", pady=(0, get_fluent_spacing('lg')))  # 16px

        # 卡片头部
        analysis_header = ctk.CTkFrame(analysis_frame, fg_color="transparent")
        analysis_header.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_padding('md'), get_fluent_spacing('md')))

        # 图标和标题 - 使用统一蓝色
        icon_frame3 = ctk.CTkFrame(
            analysis_header,
            width=36,
            height=36,
            corner_radius=Fluent.get_corner_radius('large'),
            fg_color=Fluent.color('accent_primary')  # 统一蓝色 (from purple)
        )
        icon_frame3.pack(side="left")
        icon_frame3.pack_propagate(False)
        ctk.CTkLabel(
            icon_frame3,
            text="🔬",
            font=ctk.CTkFont(size=16)
        ).pack(expand=True)

        title_frame3 = ctk.CTkFrame(analysis_header, fg_color="transparent")
        title_frame3.pack(side="left", padx=get_fluent_spacing('md'), expand=True, fill="x")
        ctk.CTkLabel(
            title_frame3,
            text="智能分析",
            font=get_fluent_font('title', 'bold'),
            text_color=Fluent.color('text_primary'),
            anchor="w"
        ).pack(fill="x")
        ctk.CTkLabel(
            title_frame3,
            text="NLP 实体识别 + LLM 内容生成",
            font=get_fluent_font('caption'),
            text_color=Fluent.color('text_tertiary'),
            anchor="w"
        ).pack(fill="x")

        # 开关选项
        options_frame = ctk.CTkFrame(analysis_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=AppleTheme.get_padding('lg'), pady=AppleTheme.get_spacing('sm'))

        self.nlp_switch = AnimatedSwitch(
            options_frame,
            text="启用 NLP 实体识别"
        )
        self.nlp_switch.pack(side="left", padx=(0, AppleTheme.get_spacing('lg')))

        self.llm_switch = AnimatedSwitch(
            options_frame,
            text="启用 LLM 智能分析"
        )
        self.llm_switch.pack(side="left", padx=(0, AppleTheme.get_spacing('lg')))

        self.charts_switch = AnimatedSwitch(
            options_frame,
            text="启用可视化图表"
        )
        self.charts_switch.pack(side="left")

        # 报告格式
        format_frame = ctk.CTkFrame(analysis_frame, fg_color="transparent")
        format_frame.pack(fill="x", padx=AppleTheme.get_padding('lg'), pady=(AppleTheme.get_spacing('md'), AppleTheme.get_padding('md')))

        ctk.CTkLabel(
            format_frame,
            text="报告格式",
            font=get_font('subheadline', 'bold'),
            text_color=AppleTheme.color('text_secondary'),
            width=80
        ).pack(side="left", padx=(0, AppleTheme.get_spacing('md')))

        self.format_segmented = AnimatedSegmentedButton(
            format_frame,
            values=["Word", "PDF", "Both"],
            width=280
        )
        self.format_segmented.pack(side="left")

        # ================= 数据库配置卡片 - 统一蓝色边框 =================
        database_frame = self._create_fluent_card(container)
        database_frame.pack(fill="x", pady=(0, get_fluent_spacing('lg')))  # 16px

        # 卡片头部
        database_header = ctk.CTkFrame(database_frame, fg_color="transparent")
        database_header.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_padding('md'), get_fluent_spacing('md')))

        # 图标和标题 - 使用统一蓝色
        icon_frame_db = ctk.CTkFrame(
            database_header,
            width=36,
            height=36,
            corner_radius=Fluent.get_corner_radius('large'),
            fg_color=Fluent.color('accent_primary')  # 统一蓝色
        )
        icon_frame_db.pack(side="left")
        icon_frame_db.pack_propagate(False)
        ctk.CTkLabel(
            icon_frame_db,
            text="🗄️",
            font=ctk.CTkFont(size=16)
        ).pack(expand=True)

        title_frame_db = ctk.CTkFrame(database_header, fg_color="transparent")
        title_frame_db.pack(side="left", padx=get_fluent_spacing('md'), expand=True, fill="x")
        ctk.CTkLabel(
            title_frame_db,
            text="数据库存储",
            font=get_fluent_font('title', 'bold'),
            text_color=Fluent.color('text_primary'),
            anchor="w"
        ).pack(fill="x")
        ctk.CTkLabel(
            title_frame_db,
            text="PostgreSQL 持久化存储（可选）",
            font=get_fluent_font('caption'),
            text_color=Fluent.color('text_tertiary'),
            anchor="w"
        ).pack(fill="x")

        # 数据库开关
        db_enable_frame = ctk.CTkFrame(database_frame, fg_color="transparent")
        db_enable_frame.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_spacing('sm'), get_fluent_spacing('sm')))

        self.db_enabled_switch = AnimatedSwitch(
            db_enable_frame,
            text="启用 PostgreSQL 数据库"
        )
        self.db_enabled_switch.pack(side="left", padx=(0, get_fluent_spacing('xl')))

        self.db_json_backup_switch = AnimatedSwitch(
            db_enable_frame,
            text="保留 JSON 备份"
        )
        self.db_json_backup_switch.pack(side="left")

        # 数据库连接参数
        # 主机和端口
        host_port_container = ctk.CTkFrame(database_frame, fg_color="transparent")
        host_port_container.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_spacing('xs'), get_fluent_spacing('sm')))

        col1 = ctk.CTkFrame(host_port_container, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            col1,
            text="主机地址",
            font=get_fluent_font('subheadline', 'bold'),
            text_color=Fluent.color('text_secondary')
        ).pack(anchor="w")
        self.db_host_entry = self._create_entry(col1)
        self.db_host_entry.pack(fill="x", pady=(get_fluent_spacing('xs'), 0))

        col2 = ctk.CTkFrame(host_port_container, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=(get_fluent_spacing('xl'), 0))
        ctk.CTkLabel(
            col2,
            text="端口",
            font=get_fluent_font('subheadline', 'bold'),
            text_color=Fluent.color('text_secondary')
        ).pack(anchor="w")
        self.db_port_entry = self._create_entry(col2, width=80)
        self.db_port_entry.pack(anchor="w", pady=(get_fluent_spacing('xs'), 0))

        # 数据库名和用户名
        db_user_container = ctk.CTkFrame(database_frame, fg_color="transparent")
        db_user_container.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_spacing('xs'), get_fluent_spacing('sm')))

        col1 = ctk.CTkFrame(db_user_container, fg_color="transparent")
        col1.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(
            col1,
            text="数据库名",
            font=get_fluent_font('subheadline', 'bold'),
            text_color=Fluent.color('text_secondary')
        ).pack(anchor="w")
        self.db_name_entry = self._create_entry(col1)
        self.db_name_entry.pack(fill="x", pady=(get_fluent_spacing('xs'), 0))

        col2 = ctk.CTkFrame(db_user_container, fg_color="transparent")
        col2.pack(side="left", fill="x", expand=True, padx=(get_fluent_spacing('xl'), 0))
        ctk.CTkLabel(
            col2,
            text="用户名",
            font=get_fluent_font('subheadline', 'bold'),
            text_color=Fluent.color('text_secondary')
        ).pack(anchor="w")
        self.db_user_entry = self._create_entry(col2)
        self.db_user_entry.pack(fill="x", pady=(get_fluent_spacing('xs'), 0))

        # 密码
        pwd_frame = ctk.CTkFrame(database_frame, fg_color="transparent")
        pwd_frame.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_spacing('xs'), get_fluent_padding('md')))

        ctk.CTkLabel(
            pwd_frame,
            text="密码",
            font=get_fluent_font('subheadline', 'bold'),
            text_color=Fluent.color('text_secondary'),
            width=80
        ).pack(side="left", padx=(0, get_fluent_spacing('md')))
        self.db_password_entry = self._create_entry(pwd_frame, show="•")
        self.db_password_entry.pack(side="left", fill="x", expand=True)

        # ================= 下载配置卡片 - 统一蓝色边框 =================
        download_frame = self._create_fluent_card(container)
        download_frame.pack(fill="x", pady=(0, get_fluent_spacing('lg')))  # 16px

        # 卡片头部
        download_header = ctk.CTkFrame(download_frame, fg_color="transparent")
        download_header.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_padding('md'), get_fluent_spacing('md')))

        # 图标和标题
        icon_frame_dl = ctk.CTkFrame(
            download_header,
            width=36,
            height=36,
            corner_radius=Fluent.get_corner_radius('large'),
            fg_color=Fluent.color('accent_primary')
        )
        icon_frame_dl.pack(side="left")
        icon_frame_dl.pack_propagate(False)
        ctk.CTkLabel(
            icon_frame_dl,
            text="📥",
            font=ctk.CTkFont(size=16)
        ).pack(expand=True)

        title_dl_frame = ctk.CTkFrame(download_header, fg_color="transparent")
        title_dl_frame.pack(side="left", padx=get_fluent_spacing('md'), expand=True, fill="x")
        ctk.CTkLabel(
            title_dl_frame,
            text="下载配置",
            font=get_fluent_font('title', 'bold'),
            text_color=Fluent.color('text_primary'),
            anchor="w"
        ).pack(fill="x")
        ctk.CTkLabel(
            title_dl_frame,
            text="自动下载 PDF/Excel 报告文件",
            font=get_fluent_font('caption'),
            text_color=Fluent.color('text_tertiary'),
            anchor="w"
        ).pack(fill="x")

        # 开关选项行1
        options_dl_row1 = ctk.CTkFrame(download_frame, fg_color="transparent")
        options_dl_row1.pack(fill="x", padx=get_fluent_padding('lg'), pady=get_fluent_spacing('sm'))

        self.enable_download_switch = AnimatedSwitch(
            options_dl_row1,
            text="启用自动下载"
        )
        self.enable_download_switch.pack(side="left", padx=(0, get_fluent_spacing('lg')))

        self.enable_dedup_switch = AnimatedSwitch(
            options_dl_row1,
            text="启用下载去重"
        )
        self.enable_dedup_switch.pack(side="left")

        # 开关选项行2 - Playwright
        options_dl_row2 = ctk.CTkFrame(download_frame, fg_color="transparent")
        options_dl_row2.pack(fill="x", padx=get_fluent_padding('lg'), pady=get_fluent_spacing('sm'))

        self.use_playwright_switch = AnimatedSwitch(
            options_dl_row2,
            text="使用 Playwright 下载器（推荐，绕过 403 错误）"
        )
        self.use_playwright_switch.pack(side="left")

        # Playwright 状态提示
        playwright_tip = ctk.CTkFrame(
            download_frame,
            corner_radius=Fluent.get_corner_radius('small'),
            fg_color=Fluent.color('bg_layer_1'),
        )
        playwright_tip.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_spacing('xs'), get_fluent_spacing('sm')))

        tip_label = ctk.CTkLabel(
            playwright_tip,
            text="💡 Playwright 使用真实浏览器自动化，可绕过 Cloudflare 保护，成功率约 80-90%",
            font=get_fluent_font('caption'),
            text_color=Fluent.color('text_secondary'),
            anchor="w"
        )
        tip_label.pack(side="left", padx=get_fluent_spacing('sm'), pady=get_fluent_spacing('xs'))

        # 文件类型选择
        filetype_frame = ctk.CTkFrame(download_frame, fg_color="transparent")
        filetype_frame.pack(fill="x", padx=get_fluent_padding('lg'), pady=get_fluent_spacing('sm'))

        ctk.CTkLabel(
            filetype_frame,
            text="文件类型",
            font=get_font('subheadline', 'bold'),
            text_color=AppleTheme.color('text_secondary'),
            width=80
        ).pack(side="left", padx=(0, get_fluent_spacing('md')))

        self.filetype_segmented = AnimatedSegmentedButton(
            filetype_frame,
            values=["PDF", "Excel", "全部"],
            width=280
        )
        self.filetype_segmented.pack(side="left")

        # 参数设置行
        params_dl_grid = ctk.CTkFrame(download_frame, fg_color="transparent")
        params_dl_grid.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_spacing('md'), get_fluent_padding('md')))

        # 重试次数
        retry_dl_frame = ctk.CTkFrame(params_dl_grid, fg_color="transparent")
        retry_dl_frame.pack(fill="x", pady=(0, get_fluent_spacing('sm')))
        ctk.CTkLabel(
            retry_dl_frame,
            text="重试次数",
            font=get_font('subheadline', 'bold'),
            text_color=AppleTheme.color('text_secondary'),
            width=80
        ).pack(side="left", padx=(0, get_fluent_spacing('md')))
        self.retry_entry = self._create_entry(retry_dl_frame, width=80)
        self.retry_entry.pack(side="left")
        ctk.CTkLabel(
            retry_dl_frame,
            text=" 次 (1-10)",
            font=get_font('body'),
            text_color=AppleTheme.color('text_tertiary')
        ).pack(side="left", padx=get_fluent_spacing('xs'))

        # 超时时间
        timeout_dl_frame = ctk.CTkFrame(params_dl_grid, fg_color="transparent")
        timeout_dl_frame.pack(fill="x")
        ctk.CTkLabel(
            timeout_dl_frame,
            text="超时时间",
            font=get_font('subheadline', 'bold'),
            text_color=AppleTheme.color('text_secondary'),
            width=80
        ).pack(side="left", padx=(0, get_fluent_spacing('md')))
        self.timeout_entry = self._create_entry(timeout_dl_frame, width=80)
        self.timeout_entry.pack(side="left")
        ctk.CTkLabel(
            timeout_dl_frame,
            text=" 秒 (10-120)",
            font=get_font('body'),
            text_color=AppleTheme.color('text_tertiary')
        ).pack(side="left", padx=get_fluent_spacing('xs'))

        # ================= 自动发现配置 =================
        auto_discover_section = ctk.CTkFrame(download_frame, fg_color="transparent")
        auto_discover_section.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_spacing('lg'), 0))

        # 标题行
        auto_discover_header = ctk.CTkFrame(auto_discover_section, fg_color="transparent")
        auto_discover_header.pack(fill="x", pady=(0, get_fluent_spacing('sm')))

        ctk.CTkLabel(
            auto_discover_header,
            text="🔍 自动发现报告链接",
            font=get_font('subheadline', 'bold'),
            text_color=Fluent.color('text_primary')
        ).pack(side="left")

        # 启用开关
        self.auto_discover_enable_switch = AnimatedSwitch(
            auto_discover_header,
            text="启用"
        )
        self.auto_discover_enable_switch.pack(side="right")

        # 配置选项行
        auto_discover_options = ctk.CTkFrame(auto_discover_section, fg_color="transparent")
        auto_discover_options.pack(fill="x", padx=get_fluent_padding('lg'), pady=get_fluent_spacing('sm'))

        # 最大数量
        max_links_frame = ctk.CTkFrame(auto_discover_options, fg_color="transparent")
        max_links_frame.pack(side="left", padx=(0, get_fluent_spacing('lg')))

        ctk.CTkLabel(
            max_links_frame,
            text="最大数量",
            font=get_fluent_font('body'),
            text_color=Fluent.color('text_secondary')
        ).pack(side="left")

        self.auto_discover_max_entry = self._create_entry(max_links_frame, width=60)
        self.auto_discover_max_entry.pack(side="left", padx=get_fluent_spacing('xs'))

        ctk.CTkLabel(
            max_links_frame,
            text="个 (1-100)",
            font=get_fluent_font('caption'),
            text_color=Fluent.color('text_tertiary')
        ).pack(side="left")

        # 最近天数
        recent_days_frame = ctk.CTkFrame(auto_discover_options, fg_color="transparent")
        recent_days_frame.pack(side="left")

        ctk.CTkLabel(
            recent_days_frame,
            text="最近",
            font=get_fluent_font('body'),
            text_color=Fluent.color('text_secondary')
        ).pack(side="left")

        self.auto_discover_days_entry = self._create_entry(recent_days_frame, width=60)
        self.auto_discover_days_entry.pack(side="left", padx=get_fluent_spacing('xs'))

        ctk.CTkLabel(
            recent_days_frame,
            text="天",
            font=get_fluent_font('caption'),
            text_color=Fluent.color('text_tertiary')
        ).pack(side="left")

        # 说明提示
        auto_discover_tip = ctk.CTkFrame(
            auto_discover_section,
            corner_radius=Fluent.get_corner_radius('small'),
            fg_color=Fluent.color('bg_layer_1'),
        )
        auto_discover_tip.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_spacing('xs'), get_fluent_spacing('sm')))

        ctk.CTkLabel(
            auto_discover_tip,
            text="💡 自动从 PitchBook 官网发现报告链接，成功率约 80-90%",
            font=get_fluent_font('caption'),
            text_color=Fluent.color('text_secondary'),
            anchor="w"
        ).pack(side="left", padx=get_fluent_spacing('sm'), pady=get_fluent_spacing('xs'))

        # ================= 底部按钮 =================
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(fill="x", pady=(get_fluent_spacing('xl'), 0))

        self.save_button = AnimatedButton(
            button_frame,
            text="💾 保存配置",
            command=self._on_save,
            style='primary',
            width=140,
            corner_radius=Fluent.get_corner_radius('small'),  # 4px
            font=get_fluent_font('body', 'bold')
        )
        self.save_button.pack(side="left", padx=(0, get_fluent_spacing('md')), pady=get_fluent_padding('md'))

        self.reset_button = AnimatedButton(
            button_frame,
            text="↺ 重置默认",
            command=self._on_reset,
            style='ghost',
            width=140,
            corner_radius=Fluent.get_corner_radius('small'),
            font=get_fluent_font('body', 'bold')
        )
        self.reset_button.pack(side="left", pady=get_fluent_padding('md'))

        self.status_label = ctk.CTkLabel(
            button_frame,
            text="",
            font=get_fluent_font('body'),
            text_color=Fluent.color('text_tertiary')
        )
        self.status_label.pack(side="left", padx=get_fluent_spacing('lg'))

    def _create_fluent_card(self, parent):
        """创建 Fluent 风格卡片 - 统一蓝色边框"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=Fluent.get_corner_radius('medium'),  # 8px (from 10px)
            fg_color=Fluent.color('surface_primary'),
            border_width=Fluent.get_border_width('medium'),  # 2px
            border_color=Fluent.color('accent_primary'),  # 统一蓝色
        )
        return card

    def _create_card(self, parent):
        """创建苹果风格卡片"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=AppleTheme.get_corner_radius('medium'),
            fg_color=AppleTheme.color('bg_secondary'),
            border_width=AppleTheme.BORDER_WIDTH['thin'],
            border_color=AppleTheme.color('separator')
        )
        return card

    def _create_entry(self, parent, placeholder_text="", width=None, show=None):
        """创建 Fluent 风格输入框"""
        kwargs = {
            'placeholder_text': placeholder_text,
            'placeholder_text_color': Fluent.color('text_tertiary'),
            'corner_radius': Fluent.get_corner_radius('small'),  # 4px
            'border_width': Fluent.get_border_width('thin'),
            'border_color': Fluent.color('border_default'),
            'height': Fluent.HEIGHT['input'],  # 36px (from 40px)
            'font': get_fluent_font('body'),
            'text_color': Fluent.color('text_primary'),
            'fg_color': Fluent.color('surface_primary'),
        }
        if width is not None:
            kwargs['width'] = width
        if show is not None:
            kwargs['show'] = show
        entry = ctk.CTkEntry(parent, **kwargs)
        return entry

    def _load_saved_config(self):
        """加载已保存的配置"""
        self.config = PipelineConfig.load(PipelineConfig.get_default_path())
        self._apply_config_to_ui()

    def _apply_config_to_ui(self):
        """将配置应用到 UI"""
        if not self.config:
            return

        self.email_entry.delete(0, "end")
        self.email_entry.insert(0, self.config.email.email_address)

        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, self.config.email.password)

        self.days_entry.delete(0, "end")
        self.days_entry.insert(0, str(self.config.email.fetch_days))

        self.max_emails_entry.delete(0, "end")
        self.max_emails_entry.insert(0, str(self.config.email.max_emails))

        self.nlp_switch.select() if self.config.analysis.enable_nlp else self.nlp_switch.deselect()
        self.llm_switch.select() if self.config.analysis.enable_llm else self.llm_switch.deselect()
        self.charts_switch.select() if self.config.analysis.enable_charts else self.charts_switch.deselect()

        # Handle report format: word, pdf, both
        format_val = self.config.analysis.report_format
        if format_val == "pdf":
            report_format = "PDF"
        elif format_val == "both":
            report_format = "Both"
        else:
            report_format = "Word"
        self.format_segmented.set(report_format)

        # Database configuration
        self.db_enabled_switch.select() if self.config.database.enabled else self.db_enabled_switch.deselect()
        self.db_json_backup_switch.select() if self.config.database.keep_json_backup else self.db_json_backup_switch.deselect()

        self.db_host_entry.delete(0, "end")
        self.db_host_entry.insert(0, self.config.database.host)

        self.db_port_entry.delete(0, "end")
        self.db_port_entry.insert(0, str(self.config.database.port))

        self.db_name_entry.delete(0, "end")
        self.db_name_entry.insert(0, self.config.database.database)

        self.db_user_entry.delete(0, "end")
        self.db_user_entry.insert(0, self.config.database.user)

        self.db_password_entry.delete(0, "end")
        self.db_password_entry.insert(0, self.config.database.password)

        # Download configuration
        self.enable_download_switch.select() if self.config.download.enable_download else self.enable_download_switch.deselect()
        self.enable_dedup_switch.select() if self.config.download.enable_dedup else self.enable_dedup_switch.deselect()
        self.use_playwright_switch.select() if self.config.download.use_playwright else self.use_playwright_switch.deselect()

        # Auto discover configuration
        self.auto_discover_enable_switch.select() if self.config.download.auto_discover.enable else self.auto_discover_enable_switch.deselect()
        self.auto_discover_max_entry.delete(0, "end")
        self.auto_discover_max_entry.insert(0, str(self.config.download.auto_discover.max_links))
        self.auto_discover_days_entry.delete(0, "end")
        self.auto_discover_days_entry.insert(0, str(self.config.download.auto_discover.recent_days))

        self.retry_entry.delete(0, "end")
        self.retry_entry.insert(0, str(self.config.download.retry_count))

        self.timeout_entry.delete(0, "end")
        self.timeout_entry.insert(0, str(self.config.download.timeout))

        # File type selection
        file_types = self.config.download.file_types
        if "excel" in file_types and "pdf" in file_types:
            filetype_val = "全部"
        elif "excel" in file_types:
            filetype_val = "Excel"
        else:
            filetype_val = "PDF"
        self.filetype_segmented.set(filetype_val)

    def _get_config_from_ui(self) -> PipelineConfig:
        """从 UI 获取配置"""
        config = PipelineConfig()

        config.email.email_address = self.email_entry.get()
        config.email.password = self.password_entry.get()
        try:
            config.email.fetch_days = int(self.days_entry.get() or "7")
            config.email.max_emails = int(self.max_emails_entry.get() or "50")
        except ValueError:
            config.email.fetch_days = 7
            config.email.max_emails = 50

        config.analysis.enable_nlp = self.nlp_switch.get() == 1
        config.analysis.enable_llm = self.llm_switch.get() == 1
        config.analysis.enable_charts = self.charts_switch.get() == 1

        # Handle report format selection
        selected_format = self.format_segmented.get()
        if selected_format == "PDF":
            config.analysis.generate_pdf = True
            config.analysis.report_format = "pdf"
        elif selected_format == "Both":
            config.analysis.generate_pdf = True
            config.analysis.report_format = "both"
        else:  # Word
            config.analysis.generate_pdf = False
            config.analysis.report_format = "word"

        # Database configuration
        config.database.enabled = self.db_enabled_switch.get() == 1
        config.database.keep_json_backup = self.db_json_backup_switch.get() == 1
        config.database.host = self.db_host_entry.get()
        try:
            config.database.port = int(self.db_port_entry.get() or "5432")
        except ValueError:
            config.database.port = 5432
        config.database.database = self.db_name_entry.get()
        config.database.user = self.db_user_entry.get()
        config.database.password = self.db_password_entry.get()

        # Download configuration
        try:
            config.download.enable_download = self.enable_download_switch.get() == 1
            config.download.enable_dedup = self.enable_dedup_switch.get() == 1
            config.download.use_playwright = self.use_playwright_switch.get() == 1
            config.download.retry_count = int(self.retry_entry.get() or "3")
            config.download.timeout = int(self.timeout_entry.get() or "30")

            # File type mapping
            filetype_val = self.filetype_segmented.get()
            if filetype_val == "全部":
                config.download.file_types = ["pdf", "excel"]
            elif filetype_val == "Excel":
                config.download.file_types = ["excel"]
            else:
                config.download.file_types = ["pdf"]

            # Auto discover configuration
            config.download.auto_discover.enable = self.auto_discover_enable_switch.get() == 1
            config.download.auto_discover.max_links = int(self.auto_discover_max_entry.get() or "10")
            config.download.auto_discover.recent_days = int(self.auto_discover_days_entry.get() or "30")
        except ValueError:
            config.download.enable_download = True
            config.download.enable_dedup = True
            config.download.retry_count = 3
            config.download.timeout = 30
            config.download.file_types = ["pdf", "excel"]
            config.download.auto_discover.enable = False
            config.download.auto_discover.max_links = 10
            config.download.auto_discover.recent_days = 30

        return config

    def _on_save(self):
        """保存配置"""
        self.config = self._get_config_from_ui()

        validation_results = self.config.validate_all()
        errors = [(section, msg) for section, valid, msg in validation_results if not valid]

        if errors:
            error_text = "\n".join([f"• {section}: {msg}" for section, msg in errors])
            self.status_label.configure(
                text=f"❌ 配置错误:\n{error_text}",
                text_color=AppleTheme.color('error')
            )
        else:
            if self.config.save(PipelineConfig.get_default_path()):
                self.status_label.configure(
                    text="✅ 配置已保存",
                    text_color=AppleTheme.color('success')
                )
                if self.on_config_change:
                    self.on_config_change(self.config)
            else:
                self.status_label.configure(
                    text="❌ 保存失败",
                    text_color=AppleTheme.color('error')
                )

    def _on_reset(self):
        """重置为默认配置（保留邮箱凭据）"""
        # 保存当前邮箱凭据
        current_email = self.email_entry.get()
        current_password = self.password_entry.get()

        # 创建新配置并应用
        self.config = PipelineConfig()

        # 恢复邮箱凭据
        if current_email:
            self.config.email.email_address = current_email
        if current_password:
            self.config.email.password = current_password

        self._apply_config_to_ui()
        self.status_label.configure(
            text="↺ 已重置为默认配置（保留邮箱凭据）",
            text_color=AppleTheme.color('warning')
        )

    def get_config(self) -> Optional[PipelineConfig]:
        """获取当前配置"""
        self.config = self._get_config_from_ui()
        validation_results = self.config.validate_all()
        if all(valid for _, valid, _ in validation_results):
            return self.config
        return None

    def set_config(self, config: PipelineConfig):
        """设置配置"""
        self.config = config
        self._apply_config_to_ui()
