"""
日志面板

显示实时日志，支持过滤和导出
"""
import customtkinter as ctk
import os
from datetime import datetime
from typing import Optional

from ..utils.apple_theme import AppleTheme, get_color, get_font, get_spacing, get_corner_radius
from ..components import AnimatedButton, AnimatedSegmentedButton


class LogPanel(ctk.CTkFrame):
    """日志面板 - 第四个标签页"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.log_filter = "ALL"
        self.max_lines = 1000
        self._current_line_count = 0  # 跟踪当前行数

        self._create_widgets()
        self._load_existing_logs()

    def _create_widgets(self):
        """创建界面组件"""
        # 头部卡片
        header_frame = ctk.CTkFrame(
            self,
            corner_radius=AppleTheme.get_corner_radius('medium'),
            fg_color=AppleTheme.color('bg_secondary'),
            border_width=AppleTheme.BORDER_WIDTH['thin'],
            border_color=AppleTheme.color('separator')
        )
        header_frame.pack(fill="x", padx=AppleTheme.get_padding('lg'), pady=(AppleTheme.get_padding('lg'), AppleTheme.get_spacing('lg')))

        header_label = ctk.CTkLabel(
            header_frame,
            text="📋 日志查看",
            font=get_font('title', 'bold'),
            text_color=AppleTheme.color('text_primary')
        )
        header_label.pack(pady=(AppleTheme.get_padding('md'), AppleTheme.get_spacing('md')), padx=AppleTheme.get_padding('lg'), anchor="w")

        # 过滤器和按钮容器
        control_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        control_frame.pack(side="right", padx=AppleTheme.get_padding('lg'), pady=AppleTheme.get_padding('md'))

        # 清空和导出按钮
        self.export_button = AnimatedButton(
            control_frame,
            text="📤 导出",
            command=self._export_logs,
            style='secondary',
            width=80
        )
        self.export_button.pack(side="left", padx=(0, AppleTheme.get_spacing('sm')))

        self.clear_button = AnimatedButton(
            control_frame,
            text="🗑️ 清空",
            command=self._clear_logs,
            style='ghost',
            width=80
        )
        self.clear_button.pack(side="left", padx=(0, AppleTheme.get_spacing('lg')))

        # 过滤器
        ctk.CTkLabel(
            control_frame,
            text="过滤:",
            font=get_font('body'),
            text_color=AppleTheme.color('text_secondary')
        ).pack(side="left", padx=(0, AppleTheme.get_spacing('sm')))

        self.filter_segmented = AnimatedSegmentedButton(
            control_frame,
            values=["全部", "INFO", "WARNING", "ERROR"],
            width=280,
            command=self._on_filter_change
        )
        self.filter_segmented.pack(side="left")
        self.filter_segmented.set("全部")

        # 日志文本框（使用 CTkTextbox，支持滚动）
        log_frame = ctk.CTkFrame(
            self,
            corner_radius=AppleTheme.get_corner_radius('medium'),
            fg_color=AppleTheme.color('bg_secondary'),
            border_width=AppleTheme.BORDER_WIDTH['thin'],
            border_color=AppleTheme.color('separator')
        )
        log_frame.pack(fill="both", expand=True, padx=AppleTheme.get_padding('lg'), pady=(0, AppleTheme.get_padding('lg')))

        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=AppleTheme.get_font_size('caption')),
            wrap="word",
            fg_color=AppleTheme.color('bg_primary'),
            border_width=0,
            corner_radius=AppleTheme.get_corner_radius('small')
        )
        self.log_text.pack(fill="both", expand=True, padx=AppleTheme.get_spacing('md'), pady=AppleTheme.get_spacing('md'))

        # 配置标签
        self._configure_tags()

        # 自动滚动开关
        self.autoscroll_var = ctk.BooleanVar(value=True)

        autoscroll_frame = ctk.CTkFrame(
            self,
            corner_radius=AppleTheme.get_corner_radius('medium'),
            fg_color=AppleTheme.color('bg_secondary'),
            border_width=AppleTheme.BORDER_WIDTH['thin'],
            border_color=AppleTheme.color('separator')
        )
        autoscroll_frame.pack(fill="x", padx=AppleTheme.get_padding('lg'), pady=(0, AppleTheme.get_padding('lg')))

        self.autoscroll_check = ctk.CTkCheckBox(
            autoscroll_frame,
            text="自动滚动到最新",
            variable=self.autoscroll_var,
            onvalue=True,
            offvalue=False,
            font=get_font('body'),
            text_color=AppleTheme.color('text_primary')
        )
        self.autoscroll_check.pack(side="left", padx=AppleTheme.get_padding('lg'), pady=AppleTheme.get_padding('sm'))

        # 状态
        self.status_label = ctk.CTkLabel(
            autoscroll_frame,
            text="",
            font=get_font('caption'),
            text_color=AppleTheme.color('text_tertiary')
        )
        self.status_label.pack(side="left", padx=AppleTheme.get_padding('lg'))

    def _configure_tags(self):
        """配置文本标签颜色"""
        colors = AppleTheme.get_colors()
        mode = ctk.get_appearance_mode()
        text_color = colors['text_primary'] if mode == 'Dark' else AppleTheme.LIGHT['text_primary']
        tertiary_color = colors['text_tertiary'] if mode == 'Dark' else AppleTheme.LIGHT['text_tertiary']

        self.log_text.tag_config("DEBUG", foreground=colors['text_tertiary'])
        self.log_text.tag_config("INFO", foreground=text_color)
        self.log_text.tag_config("WARNING", foreground=colors['accent_orange'])
        self.log_text.tag_config("ERROR", foreground=colors['accent_red'])
        self.log_text.tag_config("TIMESTAMP", foreground=tertiary_color)
        self.log_text.tag_config("DIM", foreground=colors['text_tertiary'])

    def _on_filter_change(self, value: str):
        """过滤变更"""
        filter_map = {
            "全部": "ALL",
            "INFO": "INFO",
            "WARNING": "WARNING",
            "ERROR": "ERROR"
        }
        self.log_filter = filter_map.get(value, "ALL")

    def add_log(self, level: str, message: str):
        """
        添加日志

        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
            message: 日志消息
        """
        # 检查过滤
        if self.log_filter != "ALL" and level != self.log_filter:
            return

        # 生成时间戳
        timestamp = datetime.now().strftime("%H:%M:%S")
        line = f"[{timestamp}] [{level}] {message}\n"

        # 插入文本
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line, (level, "TIMESTAMP"))

        # 使用跟踪的行数而不是每次计算
        self._current_line_count += 1
        if self._current_line_count > self.max_lines:
            # 计算需要删除的行数
            lines_to_delete = self._current_line_count - self.max_lines
            # 删除最早的行
            self.log_text.delete(1.0, f"{lines_to_delete}.0")
            self._current_line_count = self.max_lines

        self.log_text.configure(state="disabled")

        # 自动滚动
        if self.autoscroll_var.get():
            self.log_text.see("end")

        # 更新状态
        self.status_label.configure(text=f"最新: {level}")

    def _load_existing_logs(self):
        """异步加载现有的系统日志"""
        self.log_text.configure(state="normal")
        self.log_text.insert("end", "正在加载日志...\n", ("INFO", "TIMESTAMP"))
        self.log_text.configure(state="disabled")

        # 使用 after 延迟加载，避免阻塞 UI
        self.after(100, self._do_load_logs)

    def _do_load_logs(self):
        """实际执行日志加载"""
        import config
        log_file = os.path.join(config.LOGS_DIR, 'system.log')

        if not os.path.exists(log_file):
            self.log_text.configure(state="normal")
            self.log_text.delete(1.0, "end")
            self.log_text.insert("end", "无现有日志\n", ("INFO", "TIMESTAMP"))
            self.log_text.configure(state="disabled")
            return

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # 清空"正在加载"提示
            self.log_text.configure(state="normal")
            self.log_text.delete(1.0, "end")

            # 只显示最后 100 行
            for line in lines[-100:]:
                line = line.strip()
                if not line:
                    continue

                # 简单解析
                if "] [" in line:
                    parts = line.split("] [")
                    if len(parts) >= 3:
                        timestamp = parts[0].strip("[")
                        level = parts[1].split("]")[0]
                        message = "]".join(parts[1:]).split("]", 1)[-1]

                        if self.log_filter == "ALL" or level == self.log_filter:
                            display_line = f"[{timestamp}] [{level}] {message}\n"
                            self.log_text.insert("end", display_line, (level, "TIMESTAMP", "DIM"))
                            self._current_line_count += 1

            self.log_text.configure(state="disabled")

            if self.autoscroll_var.get():
                self.log_text.see("end")

        except Exception as e:
            self.add_log("WARNING", f"加载日志文件失败: {e}")

    def _clear_logs(self):
        """清空日志显示"""
        self.log_text.configure(state="normal")
        self.log_text.delete(1.0, "end")
        self.log_text.configure(state="disabled")
        self.status_label.configure(text="日志已清空")

    def _export_logs(self):
        """导出日志到文件"""
        from path_utils import get_user_data_path
        import config
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # 使用 get_user_data_path 确保导出到正确的用户数据目录
        logs_dir = get_user_data_path('data/logs')
        export_path = os.path.join(
            logs_dir,
            f"gui_log_export_{timestamp}.txt"
        )

        try:
            content = self.log_text.get(1.0, "end")
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(content)

            self.status_label.configure(
                text=f"日志已导出: {export_path}",
                text_color=AppleTheme.color('success')
            )
        except Exception as e:
            self.status_label.configure(
                text=f"导出失败: {e}",
                text_color=AppleTheme.color('error')
            )
