"""
现代化仪表盘面板

统一的蓝色系设计 + 简洁布局
"""
import customtkinter as ctk
from typing import Optional

from ..utils.apple_theme import AppleTheme, get_font, get_spacing, get_corner_radius
from ..utils.fluent_theme import FluentTheme as Fluent, get_font as get_fluent_font, get_spacing as get_fluent_spacing, get_padding as get_fluent_padding
from ..components import AnimatedButton


class ModernDashboardPanel(ctk.CTkFrame):
    """现代化仪表盘面板 - 统一蓝色系"""

    def __init__(self, master, on_run=None, on_stop=None, on_config=None, **kwargs):
        super().__init__(master, **kwargs)

        self.on_run = on_run
        self.on_stop = on_stop
        self.on_config = on_config

        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件 - 简洁网格布局"""

        # 主容器 - 浅灰背景
        main_container = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=AppleTheme.color('bg_primary'),
        )
        main_container.pack(fill="both", expand=True)

        # 顶部标题栏
        header_bar = ctk.CTkFrame(
            main_container,
            height=80,
            corner_radius=0,
            fg_color=AppleTheme.color('bg_secondary'),
        )
        header_bar.pack(fill="x")
        header_bar.pack_propagate(False)

        # 标题
        title_label = ctk.CTkLabel(
            header_bar,
            text="控制中心",
            font=ctk.CTkFont(size=32, weight="bold"),
            text_color=AppleTheme.color('text_primary')
        )
        title_label.pack(side="left", padx=24, pady=20)

        # 状态指示器
        self.status_frame = ctk.CTkFrame(
            header_bar,
            corner_radius=20,
            fg_color=AppleTheme.color('bg_primary'),
        )
        self.status_frame.pack(side="right", padx=24, pady=20)

        self.status_dot = ctk.CTkLabel(
            self.status_frame,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=AppleTheme.color('success')
        )
        self.status_dot.pack(side="left", padx=(12, 6), pady=8)

        self.status_label_text = ctk.CTkLabel(
            self.status_frame,
            text="系统就绪",
            font=get_font('body'),
            text_color=AppleTheme.color('text_secondary')
        )
        self.status_label_text.pack(side="left", padx=(0, 12), pady=8)

        # 主内容区 - 2x2 网格
        # 增加网格间距：从 24px 增加到 32px
        grid_container = ctk.CTkFrame(main_container, fg_color="transparent")
        grid_container.pack(fill="both", expand=True, padx=get_fluent_padding('xl'), pady=get_fluent_padding('xxl'))  # 32px

        # ========== 左上：快速操作 (大卡片) ==========
        action_card = self._create_card(
            grid_container,
            title="快速操作",
            icon="⚡",
            rowspan=2
        )
        # 增加卡片间距：从 6px 增加到 12px
        action_card.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=get_fluent_spacing('md'), pady=get_fluent_spacing('md'))

        # ========== 右上：运行状态 ==========
        run_card = self._create_card(
            grid_container,
            title="运行状态",
            icon="📊"
        )
        run_card.grid(row=0, column=1, sticky="nsew", padx=get_fluent_spacing('md'), pady=get_fluent_spacing('md'))

        # ========== 右中：系统信息 ==========
        info_card = self._create_card(
            grid_container,
            title="系统信息",
            icon="ℹ️"
        )
        info_card.grid(row=1, column=1, sticky="nsew", padx=get_fluent_spacing('md'), pady=get_fluent_spacing('md'))

        # 配置网格权重
        grid_container.grid_columnconfigure(0, weight=2)
        grid_container.grid_columnconfigure(1, weight=1)
        grid_container.grid_rowconfigure(0, weight=1)
        grid_container.grid_rowconfigure(1, weight=1)

        # 保存引用以便外部更新
        self.run_status_content = run_card.content
        self.info_content = info_card.content
        self._add_action_buttons(action_card.content)
        self._add_run_status(run_card.content)
        self._add_system_info(info_card.content)

    def _create_card(self, parent, title: str, icon: str, rowspan: int = 1):
        """创建 Fluent 风格卡片"""

        # 卡片外框 - 使用 Fluent 圆角 (12px from 16px)
        card_outer = ctk.CTkFrame(
            parent,
            corner_radius=Fluent.get_corner_radius('large'),  # 12px
            fg_color=Fluent.color('surface_primary'),
            border_width=Fluent.get_border_width('medium'),  # 2px
            border_color=Fluent.color('accent_primary'),  # 统一蓝色
        )

        # 卡片内容
        card_outer.content = ctk.CTkFrame(
            card_outer,
            corner_radius=Fluent.get_corner_radius('large'),  # 12px (from 14px)
            fg_color=Fluent.color('surface_primary'),
        )
        card_outer.content.pack(fill="both", expand=True, padx=2, pady=2)

        # 卡片头部
        header = ctk.CTkFrame(card_outer.content, fg_color="transparent")
        header.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_padding('lg'), get_fluent_spacing('md')))

        # 图标圆圈 - 使用 Fluent 圆角 (12px from 18px)
        icon_badge = ctk.CTkFrame(
            header,
            width=32,
            height=32,
            corner_radius=Fluent.get_corner_radius('large'),  # 12px
            fg_color=Fluent.color('accent_primary'),  # 统一蓝色
        )
        icon_badge.pack(side="left")
        icon_badge.pack_propagate(False)
        ctk.CTkLabel(
            icon_badge,
            text=icon,
            font=ctk.CTkFont(size=14)  # from 16px
        ).pack(expand=True)

        # 标题
        ctk.CTkLabel(
            header,
            text=title,
            font=get_fluent_font('title', 'bold'),  # 20px, weight="bold"
            text_color=Fluent.color('text_primary'),
        ).pack(side="left", padx=get_fluent_spacing('md'))  # 12px (from 10px)

        return card_outer

    def _add_action_buttons(self, parent):
        """添加操作按钮"""

        # 主按钮 - 使用 Fluent 样式
        self.main_run_btn = AnimatedButton(
            parent,
            text="▶ 开始运行",
            command=self._handle_run,
            font=get_fluent_font('body_large', 'bold'),  # 16px
            height=Fluent.HEIGHT['button_large'],  # 44px (from 52px)
            fg_color=Fluent.color('accent_primary'),
            hover_color=Fluent.color('accent_hover'),
            text_color='#FFFFFF',
            corner_radius=Fluent.get_corner_radius('medium'),  # 8px (from 12px)
        )
        self.main_run_btn.pack(fill="x", pady=(0, get_fluent_spacing('sm')))

        # 次要按钮行
        btn_row = ctk.CTkFrame(parent, fg_color="transparent")
        btn_row.pack(fill="x")

        AnimatedButton(
            btn_row,
            text="⚙️ 配置",
            command=self._handle_config,
            font=get_fluent_font('body', 'bold'),  # 14px (from 13px)
            height=Fluent.HEIGHT['button'],  # 36px (from 44px)
            fg_color='transparent',
            border_width=Fluent.get_border_width('medium'),  # 2px
            border_color=Fluent.color('accent_primary'),
            text_color=Fluent.color('accent_primary'),
            hover_color=Fluent.color('bg_layer_2'),
            corner_radius=Fluent.get_corner_radius('small'),  # 4px (from 10px)
        ).pack(side="left", fill="x", expand=True, padx=(0, get_fluent_spacing('xs')))

        AnimatedButton(
            btn_row,
            text="📊 监控",
            command=self._handle_monitor,
            font=get_fluent_font('body', 'bold'),
            height=Fluent.HEIGHT['button'],
            fg_color='transparent',
            border_width=Fluent.get_border_width('medium'),
            border_color=Fluent.color('accent_primary'),
            text_color=Fluent.color('accent_primary'),
            hover_color=Fluent.color('bg_layer_2'),
            corner_radius=Fluent.get_corner_radius('small'),
        ).pack(side="left", fill="x", expand=True, padx=(get_fluent_spacing('xs'), 0))

    def _add_run_status(self, parent):
        """添加运行状态"""

        # 状态圆圈
        self.run_status_circle = ctk.CTkLabel(
            parent,
            text="●",
            font=ctk.CTkFont(size=40),
            text_color=AppleTheme.color('text_tertiary'),
        )
        self.run_status_circle.pack(pady=(20, 10))

        self.run_status_text = ctk.CTkLabel(
            parent,
            text="等待启动",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=AppleTheme.color('text_primary'),
        )
        self.run_status_text.pack()

        self.run_status_desc = ctk.CTkLabel(
            parent,
            text="点击开始运行启动流程",
            font=ctk.CTkFont(size=11),
            text_color=AppleTheme.color('text_tertiary'),
        )
        self.run_status_desc.pack()

    def _add_system_info(self, parent):
        """添加系统信息"""

        info_items = [
            ("版本", "v2.0.1"),
            ("模式", "自动化"),
            ("状态", "就绪"),
        ]

        for label, value in info_items:
            item = ctk.CTkFrame(parent, fg_color="transparent")
            item.pack(fill="x", pady=8)

            ctk.CTkLabel(
                item,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=AppleTheme.color('text_tertiary'),
            ).pack(side="left")

            ctk.CTkLabel(
                item,
                text=value,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=AppleTheme.color('text_primary'),
            ).pack(side="right")

    def _handle_run(self):
        """处理运行按钮点击"""
        if self.on_run:
            self.on_run()

    def _handle_config(self):
        """处理配置按钮点击"""
        if self.on_config:
            self.on_config()

    def _handle_monitor(self):
        """处理监控按钮点击"""
        # 切换到运行监控标签页
        try:
            # 获取主窗口的tabview
            main_window = self.winfo_toplevel()
            if hasattr(main_window, 'tab_view'):
                main_window.tab_view.set("运行监控")
        except:
            pass

    def update_status(self, status: str, message: str = ""):
        """更新状态显示"""
        status_colors = {
            'ready': AppleTheme.color('text_tertiary'),
            'running': AppleTheme.color('accent_blue'),
            'success': AppleTheme.color('success'),
            'error': AppleTheme.color('error'),
        }

        color = status_colors.get(status, AppleTheme.color('text_tertiary'))

        self.run_status_circle.configure(text_color=color)
        self.run_status_text.configure(
            text=message if message else {"ready": "等待启动", "running": "运行中", "success": "完成", "error": "失败"}.get(status, "等待启动")
        )

        # 更新顶部状态
        top_status_colors = {
            'ready': AppleTheme.color('success'),
            'running': AppleTheme.color('accent_blue'),
            'success': AppleTheme.color('success'),
            'error': AppleTheme.color('error'),
        }
        self.status_dot.configure(text_color=top_status_colors.get(status, AppleTheme.color('success')))
        self.status_label_text.configure(
            text={"ready": "系统就绪", "running": "运行中", "success": "已完成", "error": "运行失败"}.get(status, "系统就绪")
        )
