"""
PitchBook 下载控制器

管理 PitchBook 下载工作线程的生命周期和通信
"""
import threading
from typing import Optional, Callable, Dict, Any

from ..models.pitchbook_config import PitchBookDownloadConfig
from ..workers.pitchbook_worker import PitchbookDownloadWorker
from services.pitchbook_skill_wrapper import PitchBookSkillWrapper


class PitchbookDownloadController:
    """
    PitchBook 下载控制器

    连接 GUI 和 PitchBook 下载工作线程
    """

    def __init__(self, main_window):
        """
        初始化控制器

        Args:
            main_window: 主窗口引用，用于 after() 调用
        """
        self.main_window = main_window
        self.worker: Optional[PitchbookDownloadWorker] = None
        self.skill_wrapper = PitchBookSkillWrapper()
        self._current_config: Optional[PitchBookDownloadConfig] = None

    def start_download(self, config: PitchBookDownloadConfig) -> bool:
        """
        启动下载

        Args:
            config: 下载配置

        Returns:
            是否成功启动
        """
        if self.is_running():
            return False

        self._current_config = config

        # 创建工作线程
        self.worker = PitchbookDownloadWorker(
            progress_callback=self._on_progress,
            log_callback=self._on_log,
            complete_callback=self._on_complete
        )

        # 设置 worker 到面板
        if hasattr(self.main_window, 'pitchbook_panel'):
            self.main_window.pitchbook_panel.set_worker(self.worker)

        # 启动任务（config 中已包含输出目录）
        self.worker.start(config)

        return True

    def stop_download(self):
        """停止下载"""
        if self.worker:
            self.worker.stop()

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.worker is not None and self.worker.is_running

    def _on_progress(self, message: str):
        """处理进度更新（从工作线程）"""
        # 线程安全地更新 GUI
        self.main_window.after(0, lambda: self._update_progress(message))

    def _on_log(self, level: str, message: str):
        """处理日志（从工作线程）"""
        self.main_window.after(0, lambda: self._update_log(level, message))

    def _on_complete(self, result: dict):
        """处理完成（从工作线程）"""
        self.main_window.after(0, lambda: self._update_complete(result))

    def _update_progress(self, message: str):
        """更新进度 GUI"""
        if hasattr(self.main_window, 'pitchbook_panel'):
            self.main_window.pitchbook_panel.update_progress(message)

    def _update_log(self, level: str, message: str):
        """更新日志 GUI"""
        if hasattr(self.main_window, 'pitchbook_panel'):
            self.main_window.pitchbook_panel.add_log(level, message)

    def _update_complete(self, result: dict):
        """更新完成状态 GUI"""
        if hasattr(self.main_window, 'pitchbook_panel'):
            panel = self.main_window.pitchbook_panel
            panel._set_running_state(False)

            # 显示结果
            if result.get('success'):
                downloaded = result.get('downloaded', 0)
                failed = result.get('failed', 0)
                panel.add_log("INFO", f"✅ 下载完成: {downloaded} 个成功, {failed} 个失败")

                if downloaded > 0:
                    panel.progress_bar.set(1.0)
                    panel.status_label.configure(
                        text=f"✅ 完成！下载了 {downloaded} 个报告",
                        text_color=Fluent.color('success')
                    )
                else:
                    panel.status_label.configure(
                        text="⚠️ 完成，但未下载任何报告",
                        text_color=Fluent.color('warning')
                    )
            else:
                error = result.get('error', '未知错误')
                panel.add_log("ERROR", f"❌ 下载失败: {error}")
                panel.status_label.configure(
                    text=f"❌ 失败: {error}",
                    text_color=Fluent.color('error')
                )


# 导入 Fluent 主题（用于颜色）
from ..utils.fluent_theme import FluentTheme as Fluent
