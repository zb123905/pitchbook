"""
PitchBook 下载面板

独立的 PitchBook 报告下载控制界面
"""
import customtkinter as ctk
import subprocess
import os
from pathlib import Path
from typing import Optional, Callable, List

from ..models.pitchbook_config import PitchBookDownloadConfig, PitchBookCredentials
from services.pitchbook_skill_wrapper import PitchBookSkillWrapper
from ..utils.fluent_theme import FluentTheme as Fluent, get_color as get_fluent_color, get_font as get_fluent_font, get_spacing as get_fluent_spacing, get_padding as get_fluent_padding
from ..components import AnimatedButton, AnimatedSwitch


class PitchBookPanel(ctk.CTkFrame):
    """PitchBook 下载面板"""

    def __init__(self, master, on_download_start: Optional[Callable] = None, **kwargs):
        """
        初始化下载面板

        Args:
            master: 父容器
            on_download_start: 下载开始回调 (config: PitchBookDownloadConfig)
        """
        super().__init__(master, **kwargs)

        self.on_download_start = on_download_start
        self.config = PitchBookDownloadConfig()
        self.worker = None
        self.skill_wrapper = PitchBookSkillWrapper()

        # 凭据
        self.credentials = PitchBookCredentials(**self.skill_wrapper.get_credentials())

        # 日志条目
        self.log_entries: List[str] = []

        self._create_widgets()
        self._load_credentials()

    def _create_widgets(self):
        """创建界面组件"""
        # 主容器
        container = ctk.CTkScrollableFrame(
            self,
            label_text="",
            fg_color="transparent"
        )
        container.pack(fill="both", expand=True, padx=get_fluent_padding('lg'), pady=get_fluent_padding('lg'))

        # 顶部装饰条
        header_bar = ctk.CTkFrame(
            container,
            height=3,
            corner_radius=Fluent.get_corner_radius('xsmall'),
            fg_color=Fluent.color('accent_primary')
        )
        header_bar.pack(fill="x", pady=(0, get_fluent_spacing('lg')))

        # 标题
        title_frame = ctk.CTkFrame(container, fg_color="transparent")
        title_frame.pack(fill="x", pady=(0, get_fluent_spacing('xl')))

        # 图标
        icon_frame = ctk.CTkFrame(
            title_frame,
            width=36,
            height=36,
            corner_radius=Fluent.get_corner_radius('large'),
            fg_color=Fluent.color('accent_primary')
        )
        icon_frame.pack(side="left")
        icon_frame.pack_propagate(False)
        ctk.CTkLabel(
            icon_frame,
            text="📥",
            font=ctk.CTkFont(size=16)
        ).pack(expand=True)

        # 标题文本
        title_text_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_text_frame.pack(side="left", padx=get_fluent_spacing('md'), expand=True, fill="x")

        ctk.CTkLabel(
            title_text_frame,
            text="PitchBook 报告下载器",
            font=get_fluent_font('title_large', 'bold'),
            text_color=Fluent.color('text_primary'),
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            title_text_frame,
            text="从 PitchBook 官网自动下载 PDF/Excel 报告",
            font=get_fluent_font('caption'),
            text_color=Fluent.color('text_tertiary'),
            anchor="w"
        ).pack(fill="x")

        # ================= 下载设置卡片 =================
        settings_card = self._create_fluent_card(container)
        settings_card.pack(fill="x", pady=(0, get_fluent_spacing('lg')))

        # 卡片头部
        settings_header = ctk.CTkFrame(settings_card, fg_color="transparent")
        settings_header.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_padding('md'), get_fluent_spacing('sm')))

        ctk.CTkLabel(
            settings_header,
            text="⚙️  下载设置",
            font=get_fluent_font('title', 'bold'),
            text_color=Fluent.color('text_primary'),
            anchor="w"
        ).pack(fill="x")

        # 最大下载数量
        max_count_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        max_count_frame.pack(fill="x", padx=get_fluent_padding('lg'), pady=get_fluent_spacing('sm'))

        ctk.CTkLabel(
            max_count_frame,
            text="最大下载数量",
            font=get_fluent_font('body'),
            text_color=Fluent.color('text_secondary'),
            width=100
        ).pack(side="left")

        self.max_count_label = ctk.CTkLabel(
            max_count_frame,
            text=f"{self.config.max_count}",
            font=get_fluent_font('body_large', 'bold'),
            text_color=Fluent.color('accent_primary'),
            width=40
        )
        self.max_count_label.pack(side="right", padx=get_fluent_spacing('sm'))

        self.max_count_slider = ctk.CTkSlider(
            max_count_frame,
            from_=1,
            to=50,
            number_of_steps=49,
            command=self._on_max_count_change
        )
        self.max_count_slider.set(self.config.max_count)
        self.max_count_slider.pack(side="left", fill="x", expand=True, padx=get_fluent_spacing('sm'))

        # 重试次数
        retries_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        retries_frame.pack(fill="x", padx=get_fluent_padding('lg'), pady=get_fluent_spacing('sm'))

        ctk.CTkLabel(
            retries_frame,
            text="重试次数",
            font=get_fluent_font('body'),
            text_color=Fluent.color('text_secondary'),
            width=100
        ).pack(side="left")

        self.retries_label = ctk.CTkLabel(
            retries_frame,
            text=f"{self.config.retries}",
            font=get_fluent_font('body_large', 'bold'),
            text_color=Fluent.color('accent_primary'),
            width=40
        )
        self.retries_label.pack(side="right", padx=get_fluent_spacing('sm'))

        self.retries_slider = ctk.CTkSlider(
            retries_frame,
            from_=1,
            to=5,
            number_of_steps=4,
            command=self._on_retries_change
        )
        self.retries_slider.set(self.config.retries)
        self.retries_slider.pack(side="left", fill="x", expand=True, padx=get_fluent_spacing('sm'))

        # 无头模式开关
        headless_frame = ctk.CTkFrame(settings_card, fg_color="transparent")
        headless_frame.pack(fill="x", padx=get_fluent_padding('lg'), pady=get_fluent_spacing('sm'))

        ctk.CTkLabel(
            headless_frame,
            text="无头模式",
            font=get_fluent_font('body'),
            text_color=Fluent.color('text_secondary'),
            width=100
        ).pack(side="left")

        self.headless_switch = AnimatedSwitch(
            headless_frame,
            text="",
            switch_width=40,
            progress_color=Fluent.color('accent_primary') if not self.config.headless else Fluent.color('text_disabled'),
            button_color=Fluent.color('surface_primary'),
            button_hover_color=Fluent.color('bg_layer_2'),
            command=self._on_headless_change
        )
        self.headless_switch.pack(side="right")

        # 使用 select 方法设置初始状态
        if self.config.headless:
            self.headless_switch.select()
        else:
            self.headless_switch.deselect()

        ctk.CTkLabel(
            headless_frame,
            text="后台运行，不显示浏览器窗口",
            font=get_fluent_font('caption'),
            text_color=Fluent.color('text_tertiary')
        ).pack(side="left", padx=get_fluent_spacing('sm'))

        # ================= 凭据状态卡片 =================
        creds_card = self._create_fluent_card(container)
        creds_card.pack(fill="x", pady=(0, get_fluent_spacing('lg')))

        creds_header = ctk.CTkFrame(creds_card, fg_color="transparent")
        creds_header.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_padding('md'), get_fluent_spacing('sm')))

        ctk.CTkLabel(
            creds_header,
            text="🔐  凭据状态",
            font=get_fluent_font('title', 'bold'),
            text_color=Fluent.color('text_primary'),
            anchor="w"
        ).pack(fill="x")

        # 凭据状态显示
        self.creds_status_frame = ctk.CTkFrame(creds_card, fg_color="transparent")
        self.creds_status_frame.pack(fill="x", padx=get_fluent_padding('lg'), pady=get_fluent_spacing('sm'))

        self._update_creds_status()

        # ================= 进度显示卡片 =================
        progress_card = self._create_fluent_card(container)
        progress_card.pack(fill="x", pady=(0, get_fluent_spacing('lg')))

        progress_header = ctk.CTkFrame(progress_card, fg_color="transparent")
        progress_header.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_padding('md'), get_fluent_spacing('sm')))

        ctk.CTkLabel(
            progress_header,
            text="📊  执行状态",
            font=get_fluent_font('title', 'bold'),
            text_color=Fluent.color('text_primary'),
            anchor="w"
        ).pack(fill="x")

        # 进度条
        self.progress_bar = ctk.CTkProgressBar(
            progress_card,
            height=20,
            corner_radius=Fluent.get_corner_radius('small')
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=get_fluent_padding('lg'), pady=(0, get_fluent_spacing('sm')))

        # 状态文本
        self.status_label = ctk.CTkLabel(
            progress_card,
            text="等待开始...",
            font=get_fluent_font('body'),
            text_color=Fluent.color('text_secondary'),
            anchor="w"
        )
        self.status_label.pack(fill="x", padx=get_fluent_padding('lg'), pady=(0, get_fluent_spacing('sm')))

        # 日志区域
        log_container = ctk.CTkFrame(progress_card, fg_color=Fluent.color('bg_layer_1'), corner_radius=Fluent.get_corner_radius('small'))
        log_container.pack(fill="both", expand=True, padx=get_fluent_padding('lg'), pady=get_fluent_spacing('sm'))

        self.log_text = ctk.CTkTextbox(
            log_container,
            height=150,
            font=ctk.CTkFont(size=11, family="Consolas"),
            text_color=Fluent.color('text_primary'),
            fg_color="transparent"
        )
        self.log_text.pack(fill="both", expand=True, padx=get_fluent_padding('xs'), pady=get_fluent_padding('xs'))

        # ================= 控制按钮 =================
        control_frame = ctk.CTkFrame(container, fg_color="transparent")
        control_frame.pack(fill="x", pady=(get_fluent_spacing('lg'), 0))

        # 开始按钮
        self.start_btn = AnimatedButton(
            control_frame,
            text="▶ 开始下载",
            command=self._on_start_click,
            font=get_fluent_font('body_large', 'bold'),
            height=Fluent.HEIGHT['button_large'],
            fg_color=Fluent.color('accent_primary'),
            hover_color=Fluent.color('accent_hover'),
            text_color=(Fluent.LIGHT['text_on_accent'], Fluent.DARK['text_on_accent']),
            corner_radius=Fluent.get_corner_radius('small')
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, get_fluent_spacing('xs')))

        # 停止按钮
        self.stop_btn = AnimatedButton(
            control_frame,
            text="⏹ 停止",
            command=self._on_stop_click,
            font=get_fluent_font('body', 'bold'),
            height=Fluent.HEIGHT['button'],
            fg_color='transparent',
            border_width=Fluent.get_border_width('medium'),
            border_color=Fluent.color('error'),
            text_color=Fluent.color('error'),
            corner_radius=Fluent.get_corner_radius('small'),
            state="disabled"
        )
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=get_fluent_spacing('xs'))

        # 打开目录按钮
        self.open_dir_btn = AnimatedButton(
            control_frame,
            text="📁 打开目录",
            command=self._on_open_dir_click,
            font=get_fluent_font('body', 'bold'),
            height=Fluent.HEIGHT['button'],
            fg_color='transparent',
            border_width=Fluent.get_border_width('medium'),
            border_color=Fluent.color('accent_primary'),
            text_color=Fluent.color('accent_primary'),
            corner_radius=Fluent.get_corner_radius('small')
        )
        self.open_dir_btn.pack(side="left", fill="x", expand=True, padx=(get_fluent_spacing('xs'), 0))

    def _create_fluent_card(self, parent):
        """创建 Fluent 风格卡片"""
        card = ctk.CTkFrame(
            parent,
            corner_radius=Fluent.get_corner_radius('medium'),
            fg_color=Fluent.color('surface_primary'),
            border_width=Fluent.get_border_width('medium'),
            border_color=Fluent.color('accent_primary')
        )
        return card

    def _load_credentials(self):
        """加载凭据状态"""
        creds = self.skill_wrapper.get_credentials()
        self.credentials = PitchBookCredentials(**creds)
        self._update_creds_status()

    def _update_creds_status(self):
        """更新凭据状态显示"""
        # 清空现有内容
        for widget in self.creds_status_frame.winfo_children():
            widget.destroy()

        valid, error = self.skill_wrapper.validate_credentials()

        if valid:
            # 显示已配置状态
            status_text = f"✅ 已配置: {self.credentials.email}"
            status_color = Fluent.color('success')

            # 显示部分信息
            detail_text = f"{self.credentials.first_name} {self.credentials.last_name} - {self.credentials.company}"
        else:
            # 显示未配置状态
            status_text = f"⚠️ 未配置凭据"
            status_color = Fluent.color('warning')

            detail_text = error if error else "请在 skill 目录配置 .env 文件"

        ctk.CTkLabel(
            self.creds_status_frame,
            text=status_text,
            font=get_fluent_font('body', 'bold'),
            text_color=status_color,
            anchor="w"
        ).pack(fill="x")

        ctk.CTkLabel(
            self.creds_status_frame,
            text=detail_text,
            font=get_fluent_font('caption'),
            text_color=Fluent.color('text_tertiary'),
            anchor="w"
        ).pack(fill="x")

    def _on_max_count_change(self, value):
        """最大数量滑块变化"""
        self.config.max_count = int(value)
        self.max_count_label.configure(text=f"{int(value)}")

    def _on_retries_change(self, value):
        """重试次数滑块变化"""
        self.config.retries = int(value)
        self.retries_label.configure(text=f"{int(value)}")

    def _on_headless_change(self, value):
        """无头模式开关变化"""
        self.config.headless = value

    def _on_start_click(self):
        """开始下载"""
        if not self.skill_wrapper.is_available():
            self.add_log("ERROR", "Node.js 不可用，请检查安装")
            return

        valid, error = self.skill_wrapper.validate_credentials()
        if not valid:
            self.add_log("ERROR", f"凭据验证失败: {error}")
            return

        # 更新状态
        self._set_running_state(True)
        self.progress_bar.set(0)
        self.status_label.configure(text="正在初始化...")
        self.log_text.delete("1.0", "end")

        self.add_log("INFO", f"开始下载，最大数量: {self.config.max_count}")

        # 触发下载
        if self.on_download_start:
            self.on_download_start(self.config)

    def _on_stop_click(self):
        """停止下载"""
        if self.worker:
            self.worker.stop()
        self._set_running_state(False)
        self.add_log("WARNING", "下载已停止")

    def _on_open_dir_click(self):
        """打开下载目录"""
        output_dir = Path(self.config.output_dir) if self.config.output_dir else Path.home() / "Downloads" / "pitchbook-reports"

        # 如果目录不存在，尝试创建
        if not output_dir.exists():
            try:
                output_dir.mkdir(parents=True, exist_ok=True)
            except Exception:
                output_dir = Path.home() / "Downloads"

        try:
            os.startfile(str(output_dir))
        except Exception as e:
            self.add_log("ERROR", f"无法打开目录: {e}")

    def _set_running_state(self, running: bool):
        """设置运行状态"""
        if running:
            self.start_btn.configure(state="disabled", text="下载中...")
            self.stop_btn.configure(state="normal")
            self.max_count_slider.configure(state="disabled")
            self.retries_slider.configure(state="disabled")
            self.headless_switch.configure(state="disabled")
        else:
            self.start_btn.configure(state="normal", text="▶ 开始下载")
            self.stop_btn.configure(state="disabled")
            self.max_count_slider.configure(state="normal")
            self.retries_slider.configure(state="normal")
            self.headless_switch.configure(state="normal")
            self.progress_bar.set(0)
            self.status_label.configure(text="等待开始...")

    def update_progress(self, message: str):
        """更新进度"""
        self.status_label.configure(text=message)
        self.add_log("DEBUG", message)

    def add_log(self, level: str, message: str):
        """添加日志"""
        # 格式化时间戳
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")

        # 颜色映射
        colors = {
            'INFO': Fluent.color('info'),
            'WARNING': Fluent.color('warning'),
            'ERROR': Fluent.color('error'),
            'DEBUG': Fluent.color('text_tertiary')
        }

        log_entry = f"[{timestamp}] [{level}] {message}\n"
        self.log_text.insert("end", log_entry)
        self.log_text.see("end")

        # 限制日志行数
        line_count = int(self.log_text.index("end-1c").split(".")[0])
        if line_count > 500:
            self.log_text.delete("1.0", "100.0")

    def set_worker(self, worker):
        """设置工作线程"""
        self.worker = worker

    def get_config(self) -> PitchBookDownloadConfig:
        """获取当前配置"""
        return self.config
