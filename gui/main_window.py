"""
主窗口

VC/PE PitchBook 系统的主 GUI 窗口
"""
import customtkinter as ctk
import tkinter as tk
from typing import Optional
import threading
import time

from .models import PipelineConfig
from .controllers import PipelineController
from .views import ConfigPanel, ProgressPanel, OutputPanel, LogPanel


class MainWindow(ctk.CTk):
    """主窗口类"""

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
        self.current_config: Optional[PipelineConfig] = None

        # 创建界面
        self._create_widgets()

        # 加载配置
        self._load_config()

        # 启动队列处理
        self._process_queue()

    def _create_widgets(self):
        """创建界面组件"""
        # 顶部标题栏
        title_frame = ctk.CTkFrame(self, height=60)
        title_frame.pack(fill="x", side="top")
        title_frame.pack_propagate(False)

        title_label = ctk.CTkLabel(
            title_frame,
            text="VC/PE PitchBook 报告自动化系统",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(side="left", padx=20, pady=15)

        self.status_indicator = ctk.CTkLabel(
            title_frame,
            text="● 就绪",
            font=ctk.CTkFont(size=12),
            text_color=("#4CAF50", "#4CAF50")
        )
        self.status_indicator.pack(side="right", padx=20, pady=15)

        # 主标签页
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # 删除默认标签页并创建自定义标签页
        default_tabs = self.tab_view._tab_dict.copy()
        for tab_name in default_tabs:
            self.tab_view.delete(tab_name)

        # 创建四个标签页
        self.tab_view.add("配置")
        self.tab_view.add("运行监控")
        self.tab_view.add("输出预览")
        self.tab_view.add("日志查看")

        # 创建四个标签页内容
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

        # 底部控制栏
        control_frame = ctk.CTkFrame(self, height=60)
        control_frame.pack(fill="x", side="bottom")
        control_frame.pack_propagate(False)

        # 运行按钮
        self.run_button = ctk.CTkButton(
            control_frame,
            text="▶ 开始运行",
            command=self._on_run,
            width=120,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.run_button.pack(side="left", padx=20, pady=10)

        # 停止按钮
        self.stop_button = ctk.CTkButton(
            control_frame,
            text="⏹ 停止",
            command=self._on_stop,
            width=100,
            height=40,
            fg_color=("#F44336", "#F44336"),
            hover_color=("#D32F2F", "#D32F2F"),
            state="disabled"
        )
        self.stop_button.pack(side="left", padx=(0, 20), pady=10)

        # 信息显示
        self.info_label = ctk.CTkLabel(
            control_frame,
            text="配置并运行系统以生成报告",
            font=ctk.CTkFont(size=12),
            anchor="w"
        )
        self.info_label.pack(side="left", fill="x", expand=True, padx=20)

        # 主题切换
        self.appearance_menu = ctk.CTkOptionMenu(
            control_frame,
            values=["System", "Light", "Dark"],
            command=self._change_appearance,
            width=100
        )
        self.appearance_menu.pack(side="right", padx=20, pady=10)
        self.appearance_menu.set("System")

    def _load_config(self):
        """加载配置"""
        self.current_config = PipelineConfig.load(PipelineConfig.get_default_path())
        if self.current_config:
            self.config_panel.set_config(self.current_config)

    def _on_run(self):
        """开始运行"""
        # 获取配置
        config = self.config_panel.get_config()
        if not config:
            self.info_label.configure(
                text="⚠️ 配置无效，请检查后重试",
                text_color=("#FF9800", "#FF9800")
            )
            return

        self.current_config = config

        # 更新 UI 状态
        self.run_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_indicator.configure(text="● 运行中", text_color=("#2196F3", "#2196F3"))
        self.info_label.configure(text="正在运行流程...")
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

    def _reset_ui_state(self):
        """重置 UI 状态"""
        self.run_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_indicator.configure(text="● 就绪", text_color=("#4CAF50", "#4CAF50"))

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
            # 显示成功信息
            output_file = results.get('output_file')
            if output_file:
                self.info_label.configure(
                    text=f"✅ 完成！报告已生成: {output_file}",
                    text_color=("#4CAF50", "#4CAF50")
                )
                self.log_panel.add_log("INFO", f"✅ 流程完成，报告: {output_file}")

                # 添加到输出面板
                report_type = results.get('report_type', '报告')
                self.output_panel.add_output_file(output_file, report_type)

                # 切换到输出标签页
                self.tab_view.set("输出预览")
            else:
                self.info_label.configure(
                    text="✅ 流程完成",
                    text_color=("#4CAF50", "#4CAF50")
                )
        else:
            # 显示错误信息
            error_msg = error or "未知错误"
            self.info_label.configure(
                text=f"❌ 失败: {error_msg}",
                text_color=("#F44336", "#F44336")
            )
            self.log_panel.add_log("ERROR", f"流程失败: {error_msg}")

            # 切换到日志标签页
            self.tab_view.set("日志查看")

    def _process_queue(self):
        """处理通知队列"""
        self.controller.process_queue()
        self.after(100, self._process_queue)

    def run(self):
        """运行主窗口"""
        self.log_panel.add_log("INFO", "系统已启动")
        super().mainloop()
