"""
输出面板

显示最新生成的文件列表，提供打开和预览功能
"""
import sys
import customtkinter as ctk
import os
import subprocess
from datetime import datetime
from typing import Optional

from ..utils.apple_theme import AppleTheme, get_color, get_font, get_spacing, get_corner_radius
from ..components import AnimatedButton


class OutputPanel(ctk.CTkFrame):
    """输出面板 - 第三个标签页"""

    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.output_files = []
        self._create_widgets()
        self._scan_output_dirs()

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
            text="📁 输出文件",
            font=get_font('title', 'bold'),
            text_color=AppleTheme.color('text_primary')
        )
        header_label.pack(pady=(AppleTheme.get_padding('md'), AppleTheme.get_spacing('md')), padx=AppleTheme.get_padding('lg'), anchor="w")

        # 刷新按钮
        self.refresh_button = AnimatedButton(
            header_frame,
            text="🔄 刷新",
            command=self._scan_output_dirs,
            style='secondary',
            width=100
        )
        self.refresh_button.pack(side="right", padx=AppleTheme.get_padding('lg'), pady=AppleTheme.get_padding('md'))

        # 文件列表（可滚动）
        list_frame = ctk.CTkScrollableFrame(
            self,
            label_text="最近生成的文件",
            corner_radius=AppleTheme.get_corner_radius('medium'),
            fg_color=AppleTheme.color('bg_secondary'),
            border_width=AppleTheme.BORDER_WIDTH['thin'],
            border_color=AppleTheme.color('separator')
        )
        list_frame.pack(fill="both", expand=True, padx=AppleTheme.get_padding('lg'), pady=(0, AppleTheme.get_padding('lg')))

        self.file_container = list_frame

        # 目录快捷访问卡片
        dirs_frame = ctk.CTkFrame(
            self,
            corner_radius=AppleTheme.get_corner_radius('medium'),
            fg_color=AppleTheme.color('bg_secondary'),
            border_width=AppleTheme.BORDER_WIDTH['thin'],
            border_color=AppleTheme.color('separator')
        )
        dirs_frame.pack(fill="x", padx=AppleTheme.get_padding('lg'), pady=(0, AppleTheme.get_padding('lg')))

        dirs_label = ctk.CTkLabel(
            dirs_frame,
            text="📂 快捷访问",
            font=get_font('headline', 'bold'),
            text_color=AppleTheme.color('text_primary')
        )
        dirs_label.pack(pady=(AppleTheme.get_padding('md'), AppleTheme.get_spacing('md')), padx=AppleTheme.get_padding('lg'), anchor="w")

        # 目录按钮
        dir_buttons_frame = ctk.CTkFrame(dirs_frame, fg_color="transparent")
        dir_buttons_frame.pack(fill="x", padx=15, pady=(0, 10))

        # 获取输出目录
        import config
        dirs = [
            ("Word报告", config.SUMMARY_REPORT_DIR),
            ("PDF报告", config.PDF_REPORT_DIR),
            ("提取邮件", config.EMAIL_EXTRACTION_DIR),
        ]

        for idx, (name, path) in enumerate(dirs):
            if idx % 2 == 0:
                row_frame = ctk.CTkFrame(dir_buttons_frame, fg_color="transparent")
                row_frame.pack(fill="x", pady=2)

            btn = AnimatedButton(
                row_frame,
                text=f"📂 {name}",
                command=lambda p=path: self._open_directory(p),
                style='secondary',
                width=200,
                height=36
            )
            btn.pack(side="left", padx=(0, AppleTheme.get_spacing('md')), pady=AppleTheme.get_spacing('xs'))

        # 状态栏
        self.status_label = ctk.CTkLabel(
            dirs_frame,
            text="",
            font=get_font('caption'),
            text_color=AppleTheme.color('text_tertiary')
        )
        self.status_label.pack(padx=AppleTheme.get_padding('lg'), pady=(0, AppleTheme.get_padding('md')))

    def _scan_output_dirs(self):
        """扫描输出目录"""
        # 清空现有列表
        for widget in self.file_container.winfo_children():
            widget.destroy()

        self.output_files = []

        # 扫描目录
        import config
        scan_dirs = [
            (config.PDF_REPORT_DIR, "PDF报告", ".pdf"),
            (config.SUMMARY_REPORT_DIR, "Word报告", ".docx"),
        ]

        for dir_path, category, ext in scan_dirs:
            if not os.path.exists(dir_path):
                continue

            try:
                files = []
                for f in os.listdir(dir_path):
                    if f.lower().endswith(ext):
                        full_path = os.path.join(dir_path, f)
                        stat = os.stat(full_path)
                        files.append({
                            'path': full_path,
                            'name': f,
                            'size': stat.st_size,
                            'mtime': stat.st_mtime,
                            'category': category
                        })

                self.output_files.extend(files)

            except Exception as e:
                print(f"扫描目录失败 {dir_path}: {e}")

        # 按修改时间排序
        self.output_files.sort(key=lambda x: x['mtime'], reverse=True)

        # 显示前 50 个文件
        for file_info in self.output_files[:50]:
            self._add_file_item(file_info)

        self.status_label.configure(text=f"共 {len(self.output_files)} 个文件")

    def _add_file_item(self, file_info: dict):
        """添加文件项到列表"""
        item_frame = ctk.CTkFrame(
            self.file_container,
            fg_color=AppleTheme.color('bg_primary'),
            corner_radius=AppleTheme.get_corner_radius('small')
        )
        item_frame.pack(fill="x", pady=AppleTheme.get_spacing('xs'))

        # 类型图标
        category_icons = {
            'PDF报告': '📄',
            'Word报告': '📝',
            'Markdown': '📃'
        }
        icon_label = ctk.CTkLabel(
            item_frame,
            text=category_icons.get(file_info['category'], '📄'),
            width=30,
            font=ctk.CTkFont(size=14)
        )
        icon_label.pack(side="left", padx=(AppleTheme.get_spacing('md'), AppleTheme.get_spacing('xs')), pady=AppleTheme.get_spacing('sm'))

        # 文件信息
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=AppleTheme.get_spacing('xs'))

        name_label = ctk.CTkLabel(
            info_frame,
            text=file_info['name'],
            font=get_font('body'),
            text_color=AppleTheme.color('text_primary'),
            anchor="w"
        )
        name_label.pack(fill="x")

        # 文件大小和日期
        size_kb = file_info['size'] / 1024
        mtime = datetime.fromtimestamp(file_info['mtime']).strftime("%Y-%m-%d %H:%M")
        meta_label = ctk.CTkLabel(
            info_frame,
            text=f"{file_info['category']} • {size_kb:.1f} KB • {mtime}",
            font=get_font('caption'),
            text_color=AppleTheme.color('text_tertiary'),
            anchor="w"
        )
        meta_label.pack(fill="x")

        # 打开按钮
        open_btn = AnimatedButton(
            item_frame,
            text="打开",
            command=lambda p=file_info['path']: self._open_file(p),
            style='primary',
            width=70,
            height=32
        )
        open_btn.pack(side="right", padx=(AppleTheme.get_spacing('xs'), AppleTheme.get_spacing('md')), pady=AppleTheme.get_spacing('xs'))

    def _open_file(self, filepath: str):
        """打开文件"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(filepath)
            elif os.name == 'posix':
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', filepath])
                else:  # Linux
                    subprocess.run(['xdg-open', filepath])
            self.status_label.configure(
                text=f"已打开: {os.path.basename(filepath)}",
                text_color=AppleTheme.color('text_tertiary')
            )
        except Exception as e:
            self.status_label.configure(
                text=f"打开失败: {e}",
                text_color=AppleTheme.color('error')
            )

    def _open_directory(self, dirpath: str):
        """打开目录"""
        try:
            if not os.path.exists(dirpath):
                os.makedirs(dirpath, exist_ok=True)

            if os.name == 'nt':  # Windows
                os.startfile(dirpath)
            elif os.name == 'posix':
                if sys.platform == 'darwin':  # macOS
                    subprocess.run(['open', dirpath])
                else:  # Linux
                    subprocess.run(['xdg-open', dirpath])
            self.status_label.configure(
                text=f"已打开目录: {dirpath}",
                text_color=AppleTheme.color('text_tertiary')
            )
        except Exception as e:
            self.status_label.configure(
                text=f"打开失败: {e}",
                text_color=AppleTheme.color('error')
            )

    def add_output_file(self, filepath: str, category: str = "其他"):
        """添加新输出的文件"""
        if not os.path.exists(filepath):
            return

        stat = os.stat(filepath)
        file_info = {
            'path': filepath,
            'name': os.path.basename(filepath),
            'size': stat.st_size,
            'mtime': stat.st_mtime,
            'category': category
        }

        self.output_files.insert(0, file_info)
        self._add_file_item(file_info)

        # 更新状态
        self.status_label.configure(text=f"新增: {file_info['name']}")
