"""
进度面板

显示 7 步流程的实时进度和状态
"""
import customtkinter as ctk
from typing import Optional

STEP_NAMES = [
    "连接MCP服务器",
    "读取PitchBook邮件",
    "提取邮件内容和链接",
    "自动下载报告",
    "Web爬取内容",
    "提取报告内容",
    "综合分析",
    "生成报告"
]

STATUS_ICONS = {
    'pending': '⏳',
    'running': '🔄',
    'success': '✅',
    'error': '❌',
    'skipped': '⏭️'
}

STATUS_COLORS = {
    'pending': ('#999', '#666'),
    'running': ('#2196F3', '#2196F3'),
    'success': ('#4CAF50', '#4CAF50'),
    'error': ('#F44336', '#F44336'),
    'skipped': ('#FF9800', '#FF9800')
}


class ProgressPanel(ctk.CTkFrame):
    """进度面板 - 第二个标签页"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.step_labels = {}
        self.step_status = {}
        self.current_stats = {}

        self._create_widgets()

    def _create_widgets(self):
        """创建界面组件"""
        # 整体进度
        header_frame = ctk.CTkFrame(self)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))

        header_label = ctk.CTkLabel(
            header_frame,
            text="📊 运行监控",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header_label.pack(pady=(15, 10), padx=15, anchor="w")

        # 总体进度条
        progress_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.overall_progress = ctk.CTkProgressBar(progress_frame, width=400)
        self.overall_progress.pack(side="left", fill="x", expand=True)
        self.overall_progress.set(0)

        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="0%",
            width=50
        )
        self.progress_label.pack(side="right", padx=(10, 0))

        # 步骤列表
        steps_container = ctk.CTkScrollableFrame(self, label_text="执行步骤")
        steps_container.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        for idx, step_name in enumerate(STEP_NAMES):
            step_frame = ctk.CTkFrame(steps_container)
            step_frame.pack(fill="x", pady=5)

            # 序号
            num_label = ctk.CTkLabel(
                step_frame,
                text=f"{idx + 1}",
                width=30,
                font=ctk.CTkFont(weight="bold")
            )
            num_label.pack(side="left", padx=(10, 5), pady=8)

            # 状态图标
            icon_label = ctk.CTkLabel(
                step_frame,
                text=STATUS_ICONS['pending'],
                width=30,
                font=ctk.CTkFont(size=14)
            )
            icon_label.pack(side="left", padx=(0, 10), pady=8)

            # 步骤名称
            name_label = ctk.CTkLabel(
                step_frame,
                text=step_name,
                font=ctk.CTkFont(size=13)
            )
            name_label.pack(side="left", padx=(0, 10), pady=8)

            # 消息标签（右侧）
            msg_label = ctk.CTkLabel(
                step_frame,
                text="等待开始",
                text_color=STATUS_COLORS['pending'],
                font=ctk.CTkFont(size=11)
            )
            msg_label.pack(side="right", padx=10, pady=8)

            self.step_labels[idx] = {
                'icon': icon_label,
                'name': name_label,
                'message': msg_label
            }
            self.step_status[idx] = 'pending'

        # 统计信息区域
        stats_frame = ctk.CTkFrame(self)
        stats_frame.pack(fill="x", padx=10, pady=(0, 10))

        stats_label = ctk.CTkLabel(
            stats_frame,
            text="📈 实时统计",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        stats_label.pack(pady=(10, 5), padx=15, anchor="w")

        # 统计网格
        grid_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.stats_labels = {}
        stats_items = [
            ('emails', '处理邮件'),
            ('links', '提取链接'),
            ('pitchbook_links', 'PitchBook链接'),
            ('downloaded', '下载报告'),
            ('scraped', '网页爬取'),
            ('analyzed', '内容分析'),
        ]

        for idx, (key, label) in enumerate(stats_items):
            row = idx // 3
            col = idx % 3

            if row == 0:
                row_frame = ctk.CTkFrame(grid_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)

            item_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            item_frame.pack(side="left", expand=True, fill="x")

            lbl = ctk.CTkLabel(
                item_frame,
                text=f"{label}: 0",
                font=ctk.CTkFont(size=12)
            )
            lbl.pack(anchor="w")

            self.stats_labels[key] = lbl

        # 时间信息
        time_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        time_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.elapsed_label = ctk.CTkLabel(
            time_frame,
            text="⏱️ 已用时间: 00:00",
            font=ctk.CTkFont(size=12)
        )
        self.elapsed_label.pack(side="left", padx=(0, 20))

        self.estimated_label = ctk.CTkLabel(
            time_frame,
            text="⏳ 预计剩余: --",
            font=ctk.CTkFont(size=12)
        )
        self.estimated_label.pack(side="left")

    def update_step(self, step: int, status: str, message: str):
        """
        更新步骤状态

        Args:
            step: 步骤索引 (0-7)
            status: 状态 ('pending', 'running', 'success', 'error', 'skipped')
            message: 状态消息
        """
        if step not in self.step_labels:
            return

        self.step_status[step] = status

        labels = self.step_labels[step]
        labels['icon'].configure(text=STATUS_ICONS.get(status, '⏳'))
        labels['message'].configure(
            text=message,
            text_color=STATUS_COLORS.get(status, STATUS_COLORS['pending'])
        )

        # 更新整体进度
        self._update_overall_progress()

    def _update_overall_progress(self):
        """更新整体进度条"""
        total = len(self.step_status)
        if total == 0:
            return

        # 计算进度权重
        progress = 0
        for step, status in self.step_status.items():
            if status == 'success':
                progress += 1
            elif status == 'running':
                progress += 0.5
            elif status == 'skipped':
                progress += 1

        ratio = progress / total
        self.overall_progress.set(ratio)
        self.progress_label.configure(text=f"{int(ratio * 100)}%")

    def update_stats(self, stats: dict):
        """
        更新统计信息

        Args:
            stats: 统计数据字典
        """
        stat_mapping = {
            'emails_count': 'emails',
            'links_count': 'links',
            'pitchbook_links_count': 'pitchbook_links',
            'downloaded_count': 'downloaded',
            'scraped_count': 'scraped',
            'analyzed_count': 'analyzed',
        }

        for key, label_key in stat_mapping.items():
            value = stats.get(key, 0)
            if label_key in self.stats_labels:
                label_map = {
                    'emails': '处理邮件',
                    'links': '提取链接',
                    'pitchbook_links': 'PitchBook链接',
                    'downloaded': '下载报告',
                    'scraped': '网页爬取',
                    'analyzed': '内容分析',
                }
                self.stats_labels[label_key].configure(
                    text=f"{label_map[label_key]}: {value}"
                )

        # 更新时间
        if 'elapsed_time' in stats:
            elapsed = int(stats['elapsed_time'])
            minutes = elapsed // 60
            seconds = elapsed % 60
            self.elapsed_label.configure(text=f"⏱️ 已用时间: {minutes:02d}:{seconds:02d}")

        # 更新预计剩余时间（简化估算）
        if 'elapsed_time' in stats:
            completed_steps = sum(1 for s in self.step_status.values() if s == 'success')
            if completed_steps > 0 and completed_steps < 8:
                avg_time = stats['elapsed_time'] / completed_steps
                remaining = (8 - completed_steps) * avg_time
                minutes = int(remaining // 60)
                seconds = int(remaining % 60)
                self.estimated_label.configure(text=f"⏳ 预计剩余: {minutes:02d}:{seconds:02d}")

    def reset(self):
        """重置所有状态"""
        for step in self.step_labels:
            self.update_step(step, 'pending', '等待开始')

        for key in self.stats_labels:
            label_map = {
                'emails': '处理邮件',
                'links': '提取链接',
                'pitchbook_links': 'PitchBook链接',
                'downloaded': '下载报告',
                'scraped': '网页爬取',
                'analyzed': '内容分析',
            }
            self.stats_labels[key].configure(text=f"{label_map[key]}: 0")

        self.elapsed_label.configure(text="⏱️ 已用时间: 00:00")
        self.estimated_label.configure(text="⏳ 预计剩余: --")
        self.overall_progress.set(0)
        self.progress_label.configure(text="0%")
