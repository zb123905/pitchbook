"""
配置面板

提供邮箱、爬虫、分析配置的界面
"""
import customtkinter as ctk
from typing import Optional, Callable

from ..models import PipelineConfig


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
        # 主容器 - 可滚动
        container = ctk.CTkScrollableFrame(self, label_text="系统配置")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # ================= 邮箱配置 =================
        email_frame = ctk.CTkFrame(container)
        email_frame.pack(fill="x", pady=(0, 15))

        email_label = ctk.CTkLabel(
            email_frame,
            text="📧 邮箱配置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        email_label.pack(pady=(15, 10), padx=15, anchor="w")

        # 邮箱地址
        addr_frame = ctk.CTkFrame(email_frame, fg_color="transparent")
        addr_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(addr_frame, text="邮箱地址:", width=80).pack(side="left", padx=(0, 10))
        self.email_entry = ctk.CTkEntry(addr_frame, placeholder_text="your-email@outlook.com")
        self.email_entry.pack(side="left", fill="x", expand=True)

        # 密码
        pwd_frame = ctk.CTkFrame(email_frame, fg_color="transparent")
        pwd_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(pwd_frame, text="密码/授权码:", width=80).pack(side="left", padx=(0, 10))
        self.password_entry = ctk.CTkEntry(pwd_frame, placeholder_text="邮箱密码或应用专用密码", show="•")
        self.password_entry.pack(side="left", fill="x", expand=True)

        # 日期范围和数量
        range_frame = ctk.CTkFrame(email_frame, fg_color="transparent")
        range_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(range_frame, text="日期范围:", width=80).pack(side="left", padx=(0, 10))
        self.days_entry = ctk.CTkEntry(range_frame, width=100)
        self.days_entry.pack(side="left", padx=(0, 15))
        ctk.CTkLabel(range_frame, text="天").pack(side="left")

        ctk.CTkLabel(range_frame, text="最多邮件:", width=80).pack(side="left", padx=(20, 10))
        self.max_emails_entry = ctk.CTkEntry(range_frame, width=100)
        self.max_emails_entry.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(range_frame, text="封").pack(side="left")

        # ================= 爬虫配置 =================
        scraper_frame = ctk.CTkFrame(container)
        scraper_frame.pack(fill="x", pady=(0, 15))

        scraper_label = ctk.CTkLabel(
            scraper_frame,
            text="🕷️ 爬虫配置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        scraper_label.pack(pady=(15, 10), padx=15, anchor="w")

        # 爬虫开关
        enable_frame = ctk.CTkFrame(scraper_frame, fg_color="transparent")
        enable_frame.pack(fill="x", padx=15, pady=5)

        self.enable_scraper_switch = ctk.CTkSwitch(
            enable_frame,
            text="启用网页爬取",
            width=200
        )
        self.enable_scraper_switch.pack(side="left", padx=(0, 20))

        self.fast_fail_switch = ctk.CTkSwitch(
            enable_frame,
            text="快速失败模式（跳过反爬虫页面）",
            width=250
        )
        self.fast_fail_switch.pack(side="left")

        # 最大链接数
        links_frame = ctk.CTkFrame(scraper_frame, fg_color="transparent")
        links_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(links_frame, text="爬取链接:", width=80).pack(side="left", padx=(0, 10))
        self.max_links_entry = ctk.CTkEntry(links_frame, width=100)
        self.max_links_entry.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(links_frame, text="个 (0=全部)").pack(side="left")

        # 延迟范围
        delay_frame = ctk.CTkFrame(scraper_frame, fg_color="transparent")
        delay_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(delay_frame, text="延迟范围:", width=80).pack(side="left", padx=(0, 10))
        self.delay_min_entry = ctk.CTkEntry(delay_frame, width=80)
        self.delay_min_entry.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(delay_frame, text="-").pack(side="left", padx=2)
        self.delay_max_entry = ctk.CTkEntry(delay_frame, width=80)
        self.delay_max_entry.pack(side="left", padx=(5, 5))
        ctk.CTkLabel(delay_frame, text="秒").pack(side="left")

        # 日期过滤
        filter_frame = ctk.CTkFrame(scraper_frame, fg_color="transparent")
        filter_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(filter_frame, text="内容日期:", width=80).pack(side="left", padx=(0, 10))
        self.date_filter_entry = ctk.CTkEntry(filter_frame, width=100)
        self.date_filter_entry.pack(side="left", padx=(0, 5))
        ctk.CTkLabel(filter_frame, text="天内").pack(side="left")

        # 爬虫说明
        scraper_tip = ctk.CTkLabel(
            scraper_frame,
            text="💡 提示：关闭爬虫可跳过网页爬取，仅分析邮件内容（速度更快）",
            text_color=("#4CAF50", "#4CAF50"),
            font=ctk.CTkFont(size=11)
        )
        scraper_tip.pack(pady=(10, 5), padx=15, anchor="w")

        scraper_tip2 = ctk.CTkLabel(
            scraper_frame,
            text="⚠️ 爬虫会使用真实浏览器，每个页面需要 2-5 秒延迟",
            text_color=("#999", "#666"),
            font=ctk.CTkFont(size=11)
        )
        scraper_tip2.pack(pady=(0, 15), padx=15, anchor="w")

        # ================= 分析配置 =================
        analysis_frame = ctk.CTkFrame(container)
        analysis_frame.pack(fill="x", pady=(0, 15))

        analysis_label = ctk.CTkLabel(
            analysis_frame,
            text="🔬 分析配置",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        analysis_label.pack(pady=(15, 10), padx=15, anchor="w")

        # 开关选项
        options_frame = ctk.CTkFrame(analysis_frame, fg_color="transparent")
        options_frame.pack(fill="x", padx=15, pady=5)

        self.nlp_switch = ctk.CTkSwitch(
            options_frame,
            text="启用 NLP 实体识别",
            width=200
        )
        self.nlp_switch.pack(side="left", padx=(0, 20))

        self.llm_switch = ctk.CTkSwitch(
            options_frame,
            text="启用 LLM 智能分析",
            width=200
        )
        self.llm_switch.pack(side="left", padx=(0, 20))

        self.charts_switch = ctk.CTkSwitch(
            options_frame,
            text="启用可视化图表",
            width=200
        )
        self.charts_switch.pack(side="left")

        # 报告格式
        format_frame = ctk.CTkFrame(analysis_frame, fg_color="transparent")
        format_frame.pack(fill="x", padx=15, pady=10)

        ctk.CTkLabel(format_frame, text="报告格式:", width=80).pack(side="left", padx=(0, 10))

        self.format_segmented = ctk.CTkSegmentedButton(
            format_frame,
            values=["Word", "PDF", "Both"],
            width=250
        )
        self.format_segmented.pack(side="left", padx=(0, 15))
        self.format_segmented.set("Word")

        # ================= 底部按钮 =================
        button_frame = ctk.CTkFrame(container)
        button_frame.pack(fill="x", pady=(10, 0))

        self.save_button = ctk.CTkButton(
            button_frame,
            text="💾 保存配置",
            command=self._on_save,
            width=120
        )
        self.save_button.pack(side="left", padx=15, pady=15)

        self.reset_button = ctk.CTkButton(
            button_frame,
            text="↺ 重置默认",
            command=self._on_reset,
            width=120,
            fg_color="transparent",
            border_width=1
        )
        self.reset_button.pack(side="left", padx=(0, 15), pady=15)

        self.status_label = ctk.CTkLabel(
            button_frame,
            text="",
            text_color=("#4CAF50", "#4CAF50")
        )
        self.status_label.pack(side="left", padx=15)

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

        # 爬虫开关
        self.enable_scraper_switch.select() if self.config.scraper.enable_scraper else self.enable_scraper_switch.deselect()
        self.fast_fail_switch.select() if self.config.scraper.fast_fail else self.fast_fail_switch.deselect()

        self.max_links_entry.delete(0, "end")
        self.max_links_entry.insert(0, str(self.config.scraper.max_scrape_links))

        self.delay_min_entry.delete(0, "end")
        self.delay_min_entry.insert(0, str(self.config.scraper.scrape_delay_min))

        self.delay_max_entry.delete(0, "end")
        self.delay_max_entry.insert(0, str(self.config.scraper.scrape_delay_max))

        self.date_filter_entry.delete(0, "end")
        self.date_filter_entry.insert(0, str(self.config.scraper.date_filter_days))

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

        try:
            config.scraper.enable_scraper = self.enable_scraper_switch.get() == 1
            config.scraper.fast_fail = self.fast_fail_switch.get() == 1
            config.scraper.max_scrape_links = int(self.max_links_entry.get() or "3")
            config.scraper.scrape_delay_min = int(self.delay_min_entry.get() or "2")
            config.scraper.scrape_delay_max = int(self.delay_max_entry.get() or "5")
            config.scraper.date_filter_days = int(self.date_filter_entry.get() or "7")
        except ValueError:
            config.scraper.enable_scraper = True
            config.scraper.fast_fail = True
            config.scraper.max_scrape_links = 3
            config.scraper.scrape_delay_min = 2
            config.scraper.scrape_delay_max = 5
            config.scraper.date_filter_days = 7

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

        return config

    def _on_save(self):
        """保存配置"""
        self.config = self._get_config_from_ui()

        validation_results = self.config.validate_all()
        errors = [(section, msg) for section, valid, msg in validation_results if not valid]

        if errors:
            error_text = "\n".join([f"• {section}: {msg}" for section, msg in errors])
            self.status_label.configure(text=f"❌ 配置错误:\n{error_text}", text_color=("#F44336", "#F44336"))
        else:
            if self.config.save(PipelineConfig.get_default_path()):
                self.status_label.configure(text="✅ 配置已保存", text_color=("#4CAF50", "#4CAF50"))
                if self.on_config_change:
                    self.on_config_change(self.config)
            else:
                self.status_label.configure(text="❌ 保存失败", text_color=("#F44336", "#F44336"))

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
        self.status_label.configure(text="↺ 已重置为默认配置（保留邮箱凭据）", text_color=("#FF9800", "#FF9800"))

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
