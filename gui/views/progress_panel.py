"""
进度面板

显示 6 步流程的实时进度和状态
"""
import customtkinter as ctk
from typing import Optional

from ..utils.apple_theme import AppleTheme, get_color, get_font, get_spacing, get_corner_radius
from ..utils.fluent_theme import FluentTheme as Fluent, get_font as get_fluent_font, get_spacing as get_fluent_spacing, get_padding as get_fluent_padding

STEP_NAMES = [
    "连接MCP服务器",
    "读取PitchBook邮件",
    "提取邮件内容和链接",
    "自动下载报告",
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
        # 整体进度卡片 - 统一蓝色
        header_frame = ctk.CTkFrame(
            self,
            corner_radius=Fluent.get_corner_radius('medium'),  # 8px
            fg_color=Fluent.color('surface_primary'),
            border_width=Fluent.get_border_width('medium'),  # 2px
            border_color=Fluent.color('accent_primary')  # 统一蓝色
        )
        header_frame.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_padding('lg'), get_fluent_spacing('lg')))

        # 卡片头部
        header_top = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_top.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_padding('md'), get_fluent_spacing('md')))

        # 图标圆圈
        icon_circle = ctk.CTkFrame(
            header_top,
            width=32,
            height=32,
            corner_radius=Fluent.get_corner_radius('large'),  # 12px
            fg_color=Fluent.color('accent_primary')  # 统一蓝色
        )
        icon_circle.pack(side="left")
        icon_circle.pack_propagate(False)
        ctk.CTkLabel(
            icon_circle,
            text="📊",
            font=ctk.CTkFont(size=14)
        ).pack(expand=True)

        header_label = ctk.CTkLabel(
            header_top,
            text="运行监控",
            font=get_fluent_font('title', 'bold'),
            text_color=Fluent.color('text_primary')
        )
        header_label.pack(side="left", padx=get_fluent_spacing('md'))

        # 进度百分比装饰
        percent_badge = ctk.CTkFrame(
            header_top,
            corner_radius=Fluent.get_corner_radius('medium'),  # 8px (from 12px)
            fg_color=Fluent.color('bg_layer_1')
        )
        percent_badge.pack(side="right")
        self.progress_label = ctk.CTkLabel(
            percent_badge,
            text="0%",
            font=get_fluent_font('body', 'bold'),
            text_color=Fluent.color('accent_primary'),  # 统一蓝色
            padx=get_fluent_spacing('sm'),
            pady=4
        )
        self.progress_label.pack()

        # 总体进度条
        progress_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        progress_frame.pack(fill="x", padx=get_fluent_padding('lg'), pady=(0, get_fluent_padding('md')))

        self.overall_progress = ctk.CTkProgressBar(
            progress_frame,
            width=400,
            progress_color=Fluent.color('accent_primary'),  # 统一蓝色
            corner_radius=Fluent.get_corner_radius('small'),  # 4px
            height=8
        )
        self.overall_progress.pack(side="left", fill="x", expand=True)
        self.overall_progress.set(0)

        # 步骤列表容器 - 统一蓝色边框
        steps_container = ctk.CTkScrollableFrame(
            self,
            label_text="",
            corner_radius=Fluent.get_corner_radius('medium'),  # 8px
            fg_color=Fluent.color('surface_primary'),
            border_width=Fluent.get_border_width('medium'),  # 2px
            border_color=Fluent.color('accent_primary')  # 统一蓝色
        )
        steps_container.pack(fill="both", expand=True, padx=get_fluent_padding('lg'), pady=(0, get_fluent_padding('lg')))

        for idx, step_name in enumerate(STEP_NAMES):
            # 步骤卡片 - 统一蓝色
            border_color = Fluent.color('accent_primary')  # 统一蓝色

            step_frame = ctk.CTkFrame(
                steps_container,
                fg_color=Fluent.color('bg_layer_1'),
                corner_radius=Fluent.get_corner_radius('small'),  # 4px
                border_width=Fluent.get_border_width('thin'),  # 1px
                border_color=border_color
            )
            # 增加步骤间距：从 xs 增加到 md (12px)
            step_frame.pack(fill="x", pady=get_fluent_spacing('md'))

            # 序号徽章 - 蓝色
            num_badge = ctk.CTkLabel(
                step_frame,
                text=f"{idx + 1}",
                width=28,
                font=get_fluent_font('body', 'bold'),
                text_color=Fluent.color('surface_primary'),
                fg_color=border_color,
                corner_radius=Fluent.get_corner_radius('medium'),  # 8px (from 14px)
            )
            num_badge.pack(side="left", padx=(get_fluent_padding('sm'), get_fluent_spacing('xs')), pady=get_fluent_spacing('sm'))

            # 状态图标
            icon_label = ctk.CTkLabel(
                step_frame,
                text=STATUS_ICONS['pending'],
                width=30,
                font=ctk.CTkFont(size=14)
            )
            icon_label.pack(side="left", padx=(0, get_fluent_spacing('md')), pady=get_fluent_spacing('sm'))

            # 步骤名称
            name_label = ctk.CTkLabel(
                step_frame,
                text=step_name,
                font=get_fluent_font('body'),
                text_color=Fluent.color('text_primary')
            )
            name_label.pack(side="left", padx=(0, get_fluent_spacing('md')), pady=get_fluent_spacing('sm'))

            # 消息标签（右侧）
            msg_label = ctk.CTkLabel(
                step_frame,
                text="等待开始",
                text_color=Fluent.get_status_colors('pending'),
                font=get_fluent_font('caption')
            )
            msg_label.pack(side="right", padx=get_fluent_padding('sm'), pady=get_fluent_spacing('sm'))

            self.step_labels[idx] = {
                'icon': icon_label,
                'name': name_label,
                'message': msg_label
            }
            self.step_status[idx] = 'pending'

        # 统计信息区域卡片 - 统一蓝色
        stats_frame = ctk.CTkFrame(
            self,
            corner_radius=Fluent.get_corner_radius('medium'),  # 8px
            fg_color=Fluent.color('surface_primary'),
            border_width=Fluent.get_border_width('medium'),  # 2px
            border_color=Fluent.color('accent_primary')  # 统一蓝色
        )
        stats_frame.pack(fill="x", padx=get_fluent_padding('lg'), pady=(0, get_fluent_padding('lg')))

        # 卡片头部
        stats_header = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_header.pack(fill="x", padx=get_fluent_padding('lg'), pady=(get_fluent_padding('md'), get_fluent_spacing('md')))

        # 图标圆圈
        icon_circle2 = ctk.CTkFrame(
            stats_header,
            width=28,
            height=28,
            corner_radius=Fluent.get_corner_radius('large'),  # 12px
            fg_color=Fluent.color('accent_primary')  # 统一蓝色
        )
        icon_circle2.pack(side="left")
        icon_circle2.pack_propagate(False)
        ctk.CTkLabel(
            icon_circle2,
            text="📈",
            font=ctk.CTkFont(size=12)  # from 14px
        ).pack(expand=True)

        stats_label = ctk.CTkLabel(
            stats_header,
            text="实时统计",
            font=get_fluent_font('subtitle', 'bold'),  # 18px
            text_color=Fluent.color('text_primary')
        )
        stats_label.pack(side="left", padx=get_fluent_spacing('md'))

        # 统计网格
        grid_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        grid_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.stats_labels = {}
        stats_items = [
            ('emails', '处理邮件'),
            ('links', '提取链接'),
            ('pitchbook_links', 'PitchBook链接'),
            ('downloaded', '下载报告'),
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
                font=get_font('body'),
                text_color=AppleTheme.color('text_primary')
            )
            lbl.pack(anchor="w")

            self.stats_labels[key] = lbl

        # 时间信息
        time_frame = ctk.CTkFrame(stats_frame, fg_color="transparent")
        time_frame.pack(fill="x", padx=15, pady=(0, 10))

        self.elapsed_label = ctk.CTkLabel(
            time_frame,
            text="⏱️ 已用时间: 00:00",
            font=get_font('body'),
            text_color=AppleTheme.color('text_primary')
        )
        self.elapsed_label.pack(side="left", padx=(0, AppleTheme.get_spacing('xl')))

        self.estimated_label = ctk.CTkLabel(
            time_frame,
            text="⏳ 预计剩余: --",
            font=get_font('body'),
            text_color=AppleTheme.color('text_primary')
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
            text_color=AppleTheme.get_status_colors(status)
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
            if completed_steps > 0 and completed_steps < 7:
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
                'analyzed': '内容分析',
            }
            self.stats_labels[key].configure(text=f"{label_map[key]}: 0")

        self.elapsed_label.configure(text="⏱️ 已用时间: 00:00")
        self.estimated_label.configure(text="⏳ 预计剩余: --")
        self.overall_progress.set(0)
        self.progress_label.configure(text="0%")
