"""
日志面板

显示实时日志，支持过滤和导出
"""
import customtkinter as ctk
import os
from datetime import datetime
from typing import Optional


class LogPanel(ctk.CTkFrame):
    """日志面板 - 第四个标签页"""

    # 日志颜色映射
    LOG_COLORS = {
        'DEBUG': ('#999', '#666'),
        'INFO': ('#333', '#DDD'),
        'WARNING': ('#FF9800', '#FF9800'),
        'ERROR': ('#F44336', '#F44336'),
    }

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.log_filter = "ALL"
        self.max_lines = 1000

        self._create_widgets()
        self._load_existing_logs()

    def _create_widgets(self):
        """创建界面组件"""
        # 头部
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        header_label = ctk.CTkLabel(
            header_frame,
            text="📋 日志查看",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=(15, 10), padx=15, anchor="w")

        # 过滤器
        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="right", padx=15, pady=10)

        ctk.CTkLabel(filter_frame, text="过滤:").pack(side="left", padx=(0, 5))

        self.filter_segmented = ctk.CTkSegmentedButton(
            filter_frame,
            values=["全部", "INFO", "WARNING", "ERROR"],
            width=250,
            command=self._on_filter_change
        )
        self.filter_segmented.pack(side="left")
        self.filter_segmented.set("全部")

        # 清空和导出按钮
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=(0, 15), pady=10)

        self.export_button = ctk.CTkButton(
            btn_frame,
            text="📤 导出",
            command=self._export_logs,
            width=80
        )
        self.export_button.pack(side="left", padx=(0, 5))

        self.clear_button = ctk.CTkButton(
            btn_frame,
            text="🗑️ 清空",
            command=self._clear_logs,
            width=80,
            fg_color="transparent",
            border_width=1
        )
        self.clear_button.pack(side="left")

        # 日志文本框（使用 CTkTextbox，支持滚动）
        log_frame = ctk.CTkFrame(self)
        log_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.log_text = ctk.CTkTextbox(
            log_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word"
        )
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        # 配置标签
        self._configure_tags()

        # 自动滚动开关
        self.autoscroll_var = ctk.BooleanVar(value=True)

        autoscroll_frame = ctk.CTkFrame(self)
        autoscroll_frame.pack(fill="x", padx=10, pady=(0, 10))

        self.autoscroll_check = ctk.CTkCheckBox(
            autoscroll_frame,
            text="自动滚动到最新",
            variable=self.autoscroll_var,
            onvalue=True,
            offvalue=False
        )
        self.autoscroll_check.pack(side="left", padx=15, pady=5)

        # 状态
        self.status_label = ctk.CTkLabel(
            autoscroll_frame,
            text="",
            text_color=("#999", "#666")
        )
        self.status_label.pack(side="left", padx=15)

    def _configure_tags(self):
        """配置文本标签颜色"""
        self.log_text.tag_config("DEBUG", foreground="#999")
        self.log_text.tag_config("INFO", foreground="#333")
        self.log_text.tag_config("WARNING", foreground="#FF9800")
        self.log_text.tag_config("ERROR", foreground="#F44336")
        self.log_text.tag_config("TIMESTAMP", foreground="#666")
        self.log_text.tag_config("DIM", foreground="#AAA")

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

        # 格式化日志
        line = f"[{timestamp}] [{level}] {message}\n"

        # 插入文本
        self.log_text.configure(state="normal")
        self.log_text.insert("end", line, (level, "TIMESTAMP"))

        # 限制行数
        line_count = int(self.log_text.index("end-1c").split(".")[0])
        if line_count > self.max_lines:
            # 删除最早的行
            delete_count = line_count - self.max_lines
            self.log_text.delete(1.0, f"{delete_count}.0")

        self.log_text.configure(state="disabled")

        # 自动滚动
        if self.autoscroll_var.get():
            self.log_text.see("end")

        # 更新状态
        self.status_label.configure(text=f"最新: {level}")

    def _load_existing_logs(self):
        """加载现有的系统日志"""
        import config
        log_file = os.path.join(config.LOGS_DIR, 'system.log')

        if not os.path.exists(log_file):
            return

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

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
                            self.log_text.configure(state="normal")
                            display_line = f"[{timestamp}] [{level}] {message}\n"
                            self.log_text.insert("end", display_line, (level, "TIMESTAMP", "DIM"))
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
                text_color=("#4CAF50", "#4CAF50")
            )
        except Exception as e:
            self.status_label.configure(
                text=f"导出失败: {e}",
                text_color=("#F44336", "#F44336")
            )
