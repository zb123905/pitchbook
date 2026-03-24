"""
线程安全通知工具

提供工作线程和主线程之间的安全通信机制
"""
import queue
import tkinter as tk
from typing import Callable, Any, Optional


class ThreadSafeNotifier:
    """线程安全通知器 - 使用队列 + after() 模式"""

    def __init__(self, main_window: Optional[tk.Tk] = None):
        """
        初始化通知器

        Args:
            main_window: Tk 主窗口实例，用于 after() 调用
        """
        self.queue = queue.Queue()
        self.main_window = main_window
        self._callbacks = {}

    def set_main_window(self, window: tk.Tk):
        """设置主窗口引用"""
        self.main_window = window

    def register_callback(self, event_type: str, callback: Callable):
        """
        注册事件回调

        Args:
            event_type: 事件类型 (如 'progress', 'log', 'complete')
            callback: 回调函数
        """
        self._callbacks[event_type] = callback

    def notify(self, event_type: str, data: Any = None):
        """
        从工作线程发送通知

        Args:
            event_type: 事件类型
            data: 事件数据
        """
        self.queue.put((event_type, data))

    def process_queue(self):
        """
        在主线程中处理队列（通过 after() 调用）

        应在主窗口初始化后定期调用
        """
        try:
            while True:
                event_type, data = self.queue.get_nowait()
                callback = self._callbacks.get(event_type)
                if callback:
                    # 使用 after 确保在主线程执行
                    if self.main_window:
                        self.main_window.after(0, lambda cb=callback, d=data: cb(d))
                    else:
                        callback(data)
                self.queue.task_done()
        except queue.Empty:
            pass

        # 继续调度
        if self.main_window:
            self.main_window.after(100, self.process_queue)


class ProgressEvent:
    """进度事件数据"""

    def __init__(self, step: int, total_steps: int, status: str, message: str):
        self.step = step
        self.total_steps = total_steps
        self.status = status  # 'pending', 'running', 'success', 'error', 'skipped'
        self.message = message


class LogEvent:
    """日志事件数据"""

    def __init__(self, level: str, message: str, timestamp: str = None):
        self.level = level  # 'DEBUG', 'INFO', 'WARNING', 'ERROR'
        self.message = message
        self.timestamp = timestamp or self._get_timestamp()

    @staticmethod
    def _get_timestamp() -> str:
        from datetime import datetime
        return datetime.now().strftime("%H:%M:%S")


class CompleteEvent:
    """完成事件数据"""

    def __init__(self, success: bool, results: dict = None, error: str = None):
        self.success = success
        self.results = results or {}
        self.error = error


class StatsEvent:
    """统计信息事件数据"""

    def __init__(self, stats: dict):
        self.stats = stats
        # 预期字段: emails_count, links_count, downloads_count,
        # scraped_count, analyzed_count, elapsed_time, estimated_time
