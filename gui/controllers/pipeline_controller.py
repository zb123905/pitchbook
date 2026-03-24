"""
流程控制器

管理后台工作线程的生命周期和通信
"""
import threading
import queue
from typing import Optional, Callable, Any, Dict

from ..models import PipelineConfig
from ..workers import PipelineWorker
from ..utils.thread_safe_notifier import ThreadSafeNotifier


class PipelineController:
    """
    流程控制器

    连接 GUI 和后台工作线程，提供线程安全的通信机制
    """

    def __init__(self, main_window):
        """
        初始化控制器

        Args:
            main_window: 主窗口引用，用于 after() 调用
        """
        self.main_window = main_window
        self.worker: Optional[PipelineWorker] = None
        self.worker_thread: Optional[threading.Thread] = None
        self.notifier = ThreadSafeNotifier(main_window)
        self._stop_requested = False
        self._current_config: Optional[PipelineConfig] = None

        # 注册回调
        self.notifier.register_callback('progress', self._on_progress)
        self.notifier.register_callback('log', self._on_log)
        self.notifier.register_callback('stats', self._on_stats)
        self.notifier.register_callback('complete', self._on_complete)

    def start_pipeline(self, config: PipelineConfig) -> bool:
        """
        启动流程

        Args:
            config: 流程配置

        Returns:
            是否成功启动
        """
        if self.is_running():
            return False

        self._stop_requested = False
        self._current_config = config

        # 创建工作线程
        self.worker = PipelineWorker(
            config_obj=config,
            progress_callback=self._on_progress_from_worker,
            log_callback=self._on_log_from_worker,
            stats_callback=self._on_stats_from_worker,
            stop_check=lambda: self._stop_requested
        )

        # 在后台线程运行
        self.worker_thread = threading.Thread(
            target=self._run_worker,
            daemon=True
        )
        self.worker_thread.start()

        return True

    def _run_worker(self):
        """工作线程入口"""
        try:
            results = self.worker.run()
            self.notifier.notify('complete', results)
        except Exception as e:
            self.notifier.notify('complete', {
                'success': False,
                'error': str(e),
                'results': {}
            })

    def stop_pipeline(self):
        """停止流程"""
        if self.is_running():
            self._stop_requested = True
            # 通知 GUI
            self.notifier.notify('log', ('INFO', '正在停止流程...'))

    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.worker is not None and self.worker.is_running

    def _on_progress_from_worker(self, step: int, status: str, message: str):
        """来自工作线程的进度更新"""
        self.notifier.notify('progress', (step, status, message))

    def _on_log_from_worker(self, level: str, message: str):
        """来自工作线程的日志"""
        self.notifier.notify('log', (level, message))

    def _on_stats_from_worker(self, stats: Dict):
        """来自工作线程的统计更新"""
        self.notifier.notify('stats', stats)

    def _on_progress(self, data: tuple):
        """处理进度事件（主线程）"""
        step, status, message = data
        if hasattr(self.main_window, 'update_progress'):
            self.main_window.update_progress(step, status, message)

    def _on_log(self, data: tuple):
        """处理日志事件（主线程）"""
        level, message = data
        if hasattr(self.main_window, 'add_log'):
            self.main_window.add_log(level, message)

    def _on_stats(self, data: Dict):
        """处理统计事件（主线程）"""
        if hasattr(self.main_window, 'update_stats'):
            self.main_window.update_stats(data)

    def _on_complete(self, data: Dict):
        """处理完成事件（主线程）"""
        if hasattr(self.main_window, 'on_pipeline_complete'):
            self.main_window.on_pipeline_complete(data)

    def process_queue(self):
        """处理通知队列（应在主循环中定期调用）"""
        self.notifier.process_queue()
