"""
主窗口

VC/PE PitchBook 系统的主 GUI 窗口
"""
import customtkinter as ctk
from typing import Optional
import threading
import time

from .models import PipelineConfig
from .controllers import PipelineController, PitchbookDownloadController
from .views import ConfigPanel, ProgressPanel, OutputPanel, LogPanel, ModernDashboardPanel, PitchBookPanel
from .utils.apple_theme import AppleTheme, get_color, get_font, get_spacing, get_corner_radius
from .utils.fluent_theme import FluentTheme as Fluent, get_color as get_fluent_color, get_font as get_fluent_font, get_spacing as get_fluent_spacing, get_padding as get_fluent_padding
from .components import AnimatedButton


class MainWindow(ctk.CTk):
    """主窗口类"""

    # 自适应轮询间隔（优化帧率和 CPU 占用）
    POLL_INTERVAL_ACTIVE = 33      # 活跃时 33ms (~30fps) - 更流畅的队列处理
    POLL_INTERVAL_IDLE = 500       # 空闲时 0.5秒（降低CPU占用）
    IDLE_THRESHOLD = 2000          # 约1分钟无活动后进入空闲模式 (33ms * 2000 = 66s)

    def __init__(self):
        super().__init__()

        # 窗口配置
        self.title("VC/PE PitchBook 自动化系统")
        self.geometry("900x700")
        self.minsize(800, 600)

        # 设置主题
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # 控制器和状态
        self.controller = PipelineController(self)
        self.pitchbook_controller = PitchbookDownloadController(self)
        self.current_config: Optional[PipelineConfig] = None

        # 自适应轮询变量
        self._poll_interval = self.POLL_INTERVAL_ACTIVE
        self._idle_counter = 0

        # 标签页动画状态
        self._tab_animation_running = False
        self._previous_tab = None

        # 创建界面
        self._create_widgets()

        # 加载配置
        self._load_config()

        # 启动队列处理
        self._process_queue()

    def _create_widgets(self):
        """创建界面组件"""
        # ========== Fluent Design 顶部栏 - 简洁风格 ==========
        # 高度从 64px 减少到 48px
        title_frame = ctk.CTkFrame(
            self,
            height=Fluent.HEIGHT['header'],  # 48px
            corner_radius=0,
            fg_color=Fluent.color('surface_primary'),
            border_width=Fluent.get_border_width('thin'),
            border_color=Fluent.color('separator')
        )
        title_frame.pack(fill="x", side="top")
        title_frame.pack_propagate(False)

        # 左侧 - 简洁图标 + 标题
        logo_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        logo_frame.pack(side="left", padx=get_fluent_padding('lg'), pady=get_fluent_padding('sm'))

        # 简化的图标圆圈 (36px -> 28px)
        logo_bg = ctk.CTkFrame(
            logo_frame,
            width=28,
            height=28,
            corner_radius=14,
            fg_color=Fluent.color('accent_primary')
        )
        logo_bg.pack(side="left")
        logo_bg.pack_propagate(False)
        ctk.CTkLabel(
            logo_bg,
            text="📊",
            font=ctk.CTkFont(size=14)
        ).pack(expand=True)

        title_label = ctk.CTkLabel(
            logo_frame,
            text="VC/PE PitchBook 自动化",
            font=get_fluent_font('subtitle', 'bold'),  # 18px
            text_color=Fluent.color('text_primary')
        )
        title_label.pack(side="left", padx=(Fluent.get_spacing('md'), 0))

        # 右侧状态区域 - 简化设计
        status_frame = ctk.CTkFrame(
            title_frame,
            corner_radius=Fluent.get_corner_radius('medium'),  # 8px (更小)
            fg_color=Fluent.color('bg_layer_1'),
        )
        status_frame.pack(side="right", padx=get_fluent_padding('lg'), pady=get_fluent_padding('sm'))

        self.status_indicator = ctk.CTkLabel(
            status_frame,
            text="●",
            font=ctk.CTkFont(size=10),
            text_color=Fluent.color('success')
        )
        self.status_indicator.pack(side="left", padx=(get_fluent_padding('sm'), Fluent.get_spacing('xs')), pady=get_fluent_padding('xsm'))

        self.status_text = ctk.CTkLabel(
            status_frame,
            text="就绪",
            font=get_fluent_font('body'),
            text_color=Fluent.color('text_secondary')
        )
        self.status_text.pack(side="left", padx=(0, get_fluent_padding('sm')), pady=get_fluent_padding('xsm'))

        # 主标签页
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=get_fluent_padding('lg'), pady=(0, get_fluent_padding('lg')))

        # 删除默认标签页并创建自定义标签页
        default_tabs = self.tab_view._tab_dict.copy()
        for tab_name in default_tabs:
            self.tab_view.delete(tab_name)

        # 创建六个标签页
        self.tab_view.add("控制台")
        self.tab_view.add("配置")
        self.tab_view.add("运行监控")
        self.tab_view.add("输出预览")
        self.tab_view.add("日志查看")
        self.tab_view.add("PitchBook下载")  # 新增

        # 创建控制台 - 现代化仪表盘 (连接回调)
        self.dashboard_panel = ModernDashboardPanel(
            self.tab_view.tab("控制台"),
            on_run=self._on_run,
            on_config=self._handle_dashboard_config,
            fg_color="transparent"
        )
        self.dashboard_panel.pack(fill="both", expand=True)

        # 创建配置面板
        self.config_panel = ConfigPanel(
            self.tab_view.tab("配置"),
            fg_color="transparent"
        )
        self.config_panel.pack(fill="both", expand=True)

        self.progress_panel = ProgressPanel(
            self.tab_view.tab("运行监控"),
            fg_color="transparent"
        )
        self.progress_panel.pack(fill="both", expand=True)

        self.output_panel = OutputPanel(
            self.tab_view.tab("输出预览"),
            fg_color="transparent"
        )
        self.output_panel.pack(fill="both", expand=True)

        self.log_panel = LogPanel(
            self.tab_view.tab("日志查看"),
            fg_color="transparent"
        )
        self.log_panel.pack(fill="both", expand=True)

        # 创建 PitchBook 下载面板 (新增)
        self.pitchbook_panel = PitchBookPanel(
            self.tab_view.tab("PitchBook下载"),
            on_download_start=self._on_pitchbook_download_start,
            fg_color="transparent"
        )
        self.pitchbook_panel.pack(fill="both", expand=True)

        # 绑定标签页切换事件
        self._bind_tab_switching()

        # ========== Fluent Design 底部控制栏 - 简洁风格 ==========
        control_frame = ctk.CTkFrame(
            self,
            height=Fluent.HEIGHT['header'],  # 48px (统一高度)
            corner_radius=0,
            fg_color=Fluent.color('surface_primary'),
            border_width=Fluent.get_border_width('thin'),
            border_color=Fluent.color('separator')
        )
        control_frame.pack(fill="x", side="bottom")
        control_frame.pack_propagate(False)

        # 左侧装饰条 - 使用统一蓝色
        decor_bar_bottom = ctk.CTkFrame(
            control_frame,
            width=Fluent.get_border_width('thick'),  # 3px (更细)
            corner_radius=Fluent.get_corner_radius('xsmall'),
            fg_color=Fluent.color('accent_primary')  # 统一蓝色
        )
        decor_bar_bottom.pack(side="left", padx=(get_fluent_padding('lg'), get_fluent_padding('md')), pady=get_fluent_padding('sm'))

        # 运行按钮
        run_btn_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        run_btn_frame.pack(side="left", padx=(0, Fluent.get_spacing('md')), pady=get_fluent_padding('sm'))

        self.run_button = AnimatedButton(
            run_btn_frame,
            text="▶ 开始运行",
            command=self._on_run,
            style='primary',
            width=140,
            font=get_fluent_font('body', 'bold'),  # 14px
            corner_radius=Fluent.get_corner_radius('small'),  # 4px
        )
        self.run_button.pack()

        # 停止按钮
        self.stop_button = AnimatedButton(
            control_frame,
            text="⏹ 停止",
            command=self._on_stop,
            style='danger',
            width=120,
            font=get_fluent_font('body', 'bold'),
            corner_radius=Fluent.get_corner_radius('small'),
        )
        self.stop_button.pack(side="left", padx=(0, get_fluent_padding('lg')), pady=get_fluent_padding('sm'))
        self.stop_button.configure(state="disabled")

        # 信息显示
        info_frame = ctk.CTkFrame(control_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=get_fluent_padding('lg'), pady=get_fluent_padding('sm'))

        self.info_icon = ctk.CTkLabel(
            info_frame,
            text="ℹ️",
            font=ctk.CTkFont(size=12)
        )
        self.info_icon.pack(side="left")

        self.info_label = ctk.CTkLabel(
            info_frame,
            text="配置并运行系统以生成报告",
            font=get_fluent_font('body'),
            text_color=Fluent.color('text_secondary'),
            anchor="w"
        )
        self.info_label.pack(side="left", padx=(Fluent.get_spacing('xs'), 0))

        # 主题切换 - 简化设计
        theme_frame = ctk.CTkFrame(
            control_frame,
            corner_radius=Fluent.get_corner_radius('medium'),  # 8px
            fg_color=Fluent.color('bg_layer_1'),
        )
        theme_frame.pack(side="right", padx=get_fluent_padding('lg'), pady=get_fluent_padding('sm'))

        ctk.CTkLabel(
            theme_frame,
            text="🎨",
            font=ctk.CTkFont(size=12)
        ).pack(side="left", padx=(get_fluent_padding('sm'), Fluent.get_spacing('xs')), pady=get_fluent_padding('xsm'))

        self.appearance_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["System", "Light", "Dark"],
            command=self._change_appearance,
            width=90,
            corner_radius=Fluent.get_corner_radius('small'),  # 4px
            font=get_fluent_font('body'),
        )
        self.appearance_menu.pack(side="left", padx=(0, get_fluent_padding('sm')), pady=get_fluent_padding('xsm'))
        self.appearance_menu.set("System")

    def _bind_tab_switching(self):
        """绑定标签页切换事件"""
        # 重写 tabview 的切换方法以添加动画
        original_set = self.tab_view.set

        def animated_set(tab_name: str):
            if self._tab_animation_running or tab_name == self._previous_tab:
                return original_set(tab_name)

            # 记录当前标签
            current_tab = self.tab_view.get()

            # 执行切换
            original_set(tab_name)

            # 记录新标签
            self._previous_tab = current_tab

        self.tab_view.set = animated_set

    def _load_config(self):
        """加载配置"""
        self.current_config = PipelineConfig.load(PipelineConfig.get_default_path())
        if self.current_config:
            self.config_panel.set_config(self.current_config)

    def _handle_dashboard_config(self):
        """处理控制台的配置按钮点击"""
        self.tab_view.set("配置")

    def _on_run(self):
        """开始运行"""
        # 获取配置
        config = self.config_panel.get_config()
        if not config:
            self.info_label.configure(
                text="⚠️ 配置无效，请检查后重试",
                text_color=AppleTheme.color('warning')
            )
            return

        self.current_config = config

        # 更新 UI 状态
        self.run_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_indicator.configure(
            text="●",
            text_color=AppleTheme.color('accent_blue')
        )
        self.status_text.configure(
            text="运行中",
            text_color=AppleTheme.color('accent_blue')
        )
        self.info_label.configure(
            text="正在运行流程...",
            text_color=AppleTheme.color('text_primary')
        )
        self.info_icon.configure(text="🔄")
        self.tab_view.set("运行监控")

        # 重置进度面板
        self.progress_panel.reset()

        # 启动流程
        if not self.controller.start_pipeline(config):
            self.info_label.configure(text="⚠️ 流程已在运行中")
            self._reset_ui_state()

    def _on_stop(self):
        """停止运行"""
        self.controller.stop_pipeline()
        self.info_label.configure(text="正在停止...")
        self.log_panel.add_log("INFO", "用户请求停止流程")

    def _on_pitchbook_download_start(self, config):
        """处理 PitchBook 下载开始"""
        self.pitchbook_controller.start_download(config)

    def _reset_ui_state(self):
        """重置 UI 状态"""
        self.run_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.dashboard_panel.set_direct_download_enabled(True)
        self.dashboard_panel.set_direct_download_running(False)

        self.status_indicator.configure(
            text="●",
            text_color=AppleTheme.color('success')
        )
        self.status_text.configure(
            text="就绪",
            text_color=AppleTheme.color('text_secondary')
        )
        self.info_icon.configure(text="ℹ️")

    def _change_appearance(self, choice: str):
        """更改主题"""
        ctk.set_appearance_mode(choice)

    # ================= 回调方法 =================

    def update_progress(self, step: int, status: str, message: str):
        """更新进度（来自控制器）"""
        self.progress_panel.update_step(step, status, message)

        # 切换到进度标签页
        if self.tab_view.get() != "运行监控":
            # 只在关键步骤切换
            if status in ['running', 'success', 'error']:
                pass  # 可以选择是否自动切换

    def add_log(self, level: str, message: str):
        """添加日志（来自控制器）"""
        self.log_panel.add_log(level, message)

    def update_stats(self, stats: dict):
        """更新统计（来自控制器）"""
        self.progress_panel.update_stats(stats)

    def on_pipeline_complete(self, result: dict):
        """流程完成（来自控制器）"""
        success = result.get('success', False)
        results = result.get('results', {})
        error = result.get('error')

        # 重置 UI 状态
        self._reset_ui_state()

        if success:
            # 检查直接下载结果
            direct_download = results.get('direct_download', {})
            direct_count = direct_download.get('direct_downloaded_count', 0)

            if direct_count > 0:
                self.add_log("INFO", f"🎉 直接下载完成: {direct_count} 个报告")

            # 处理多个输出文件（支持新的 output_files 格式）
            output_files = results.get('output_files', [])

            # 兼容旧格式（单个文件）
            if not output_files and results.get('output_file'):
                output_files = [
                    (results.get('report_type', '报告'), results.get('output_file'))
                ]

            # 计算总下载数
            total_downloads = results.get('total_downloaded', results.get('downloaded_count', 0))

            if output_files or total_downloads > 0:
                # 显示成功信息（多个文件）
                file_count = len(output_files)
                format_list = ", ".join([f[0] for f in output_files])

                # 格式化文件路径显示
                if file_count == 1:
                    file_info = output_files[0][1]
                else:
                    file_info = f"{file_count} 个文件 ({format_list})"

                self.status_indicator.configure(
                    text="●",
                    text_color=AppleTheme.color('success')
                )
                self.status_text.configure(
                    text="已完成",
                    text_color=AppleTheme.color('success')
                )
                self.info_label.configure(
                    text=f"✅ 完成！报告已生成: {file_info}",
                    text_color=AppleTheme.color('success')
                )
                self.info_icon.configure(text="✅")

                # 添加所有文件到输出面板
                for report_type, filepath in output_files:
                    self.log_panel.add_log("INFO", f"✅ {report_type} 报告: {filepath}")
                    self.output_panel.add_output_file(filepath, report_type)

                # 切换到输出标签页
                self.tab_view.set("输出预览")
            else:
                # 只有下载没有报告生成的情况
                total_downloads = results.get('total_downloaded', results.get('downloaded_count', 0))
                if total_downloads > 0:
                    self.status_indicator.configure(
                        text="●",
                        text_color=AppleTheme.color('success')
                    )
                    self.status_text.configure(
                        text="已完成",
                        text_color=AppleTheme.color('success')
                    )
                    self.info_label.configure(
                        text=f"✅ 完成！共下载 {total_downloads} 个报告",
                        text_color=AppleTheme.color('success')
                    )
                    self.info_icon.configure(text="✅")
                else:
                    self.status_indicator.configure(
                        text="●",
                        text_color=AppleTheme.color('success')
                    )
                    self.status_text.configure(
                        text="已完成",
                        text_color=AppleTheme.color('success')
                    )
                    self.info_label.configure(
                        text="✅ 流程完成",
                        text_color=AppleTheme.color('success')
                    )
                    self.info_icon.configure(text="✅")
        else:
            # 显示错误信息
            error_msg = error or "未知错误"
            self.status_indicator.configure(
                text="●",
                text_color=AppleTheme.color('error')
            )
            self.status_text.configure(
                text="失败",
                text_color=AppleTheme.color('error')
            )
            self.info_label.configure(
                text=f"❌ 失败: {error_msg}",
                text_color=AppleTheme.color('error')
            )
            self.info_icon.configure(text="❌")
            self.log_panel.add_log("ERROR", f"流程失败: {error_msg}")

            # 切换到日志标签页
            self.tab_view.set("日志查看")

    def _process_queue(self):
        """处理通知队列（自适应间隔）"""
        had_events = self.controller.process_queue()

        # 自适应间隔调整
        if had_events:
            self._idle_counter = 0
            self._poll_interval = self.POLL_INTERVAL_ACTIVE
        else:
            self._idle_counter += 1
            if self._idle_counter > self.IDLE_THRESHOLD:
                self._poll_interval = self.POLL_INTERVAL_IDLE

        self.after(self._poll_interval, self._process_queue)

    def run(self):
        """运行主窗口"""
        self.log_panel.add_log("INFO", "系统已启动")
        super().mainloop()
