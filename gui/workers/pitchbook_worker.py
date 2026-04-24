"""
PitchBook 下载工作线程

在后台线程中执行下载任务，通过回调与 GUI 通信
"""
import threading
import logging
from typing import Callable, Dict, Any, Optional
from pathlib import Path

from services.pitchbook_skill_wrapper import PitchBookSkillWrapper
from gui.models.pitchbook_config import PitchBookDownloadConfig


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PitchbookDownloadWorker:
    """
    PitchBook 下载工作线程

    在后台线程中执行下载任务，通过回调与 GUI 通信
    """

    def __init__(
        self,
        progress_callback: Callable[[str], None],
        log_callback: Callable[[str, str], None],
        complete_callback: Callable[[Dict], None]
    ):
        """
        初始化工作线程

        Args:
            progress_callback: 进度回调 (message)
            log_callback: 日志回调 (level, message)
            complete_callback: 完成回调 (result_dict)
        """
        self.progress_callback = progress_callback
        self.log_callback = log_callback
        self.complete_callback = complete_callback

        self._running = False
        self._stop_requested = False
        self._thread: Optional[threading.Thread] = None

        # 包装器实例
        self._wrapper: Optional[PitchBookSkillWrapper] = None

    def start(self, config: PitchBookDownloadConfig):
        """
        启动下载任务

        Args:
            config: 下载配置（包含输出目录）
        """
        if self._running:
            return

        self._running = True
        self._stop_requested = False

        # 创建包装器
        self._wrapper = PitchBookSkillWrapper()

        # 检查是否可用
        if not self._wrapper.is_available():
            self.log_callback("ERROR", "PitchBook Skill 不可用，请检查 Node.js 是否安装")
            self.complete_callback({
                'success': False,
                'error': 'Skill 不可用'
            })
            self._running = False
            return

        # 验证凭据
        valid, error = self._wrapper.validate_credentials()
        if not valid:
            self.log_callback("ERROR", f"凭据验证失败: {error}")
            self.complete_callback({
                'success': False,
                'error': error
            })
            self._running = False
            return

        # 在新线程中运行
        self._thread = threading.Thread(
            target=self._run_task,
            args=(config,),
            daemon=True
        )
        self._thread.start()

    def _run_task(self, config: PitchBookDownloadConfig):
        """
        运行下载任务

        Args:
            config: 下载配置
        """
        try:
            # 确定输出目录（使用配置中的目录）
            output_dir = config.output_dir or str(Path.home() / "Downloads" / "pitchbook-reports")

            # 确保输出目录存在
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            self.log_callback("INFO", f"输出目录: {output_dir}")

            # 执行下载
            if config.is_single_mode():
                # 单个报告下载
                result = self._wrapper.download_single(
                    url=config.single_url,
                    retries=config.retries,
                    output_dir=output_dir,
                    log_callback=self.log_callback
                )

                # 添加下载统计
                result['total'] = 1
                result['downloaded'] = 1 if result['success'] else 0
                result['failed'] = 0 if result['success'] else 1

            else:
                # 列表页批量下载
                result = self._wrapper.download_from_listing(
                    max_count=config.max_count,
                    retries=config.retries,
                    listing_url=config.listing_url,
                    output_dir=output_dir,
                    progress_callback=self.progress_callback,
                    log_callback=self.log_callback
                )

                # 添加总数
                result['total'] = config.max_count

            # 检查是否被停止
            if self._stop_requested:
                result['stopped'] = True
                self.log_callback("WARNING", "下载已被用户停止")

            # 完成回调
            self.complete_callback(result)

        except Exception as e:
            logger.error(f"下载任务异常: {e}")
            self.log_callback("ERROR", f"下载失败: {e}")
            self.complete_callback({
                'success': False,
                'error': str(e),
                'total': config.max_count if config else 0,
                'downloaded': 0,
                'failed': 0
            })

        finally:
            self._running = False

    def stop(self):
        """停止下载"""
        if not self._running:
            return

        self._stop_requested = True
        self.log_callback("WARNING", "正在停止下载...")

        # 注意：subprocess 进程会在超时后自动结束
        # 这里只是设置标志，让任务知道应该停止

    @property
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self._running

    @property
    def is_stop_requested(self) -> bool:
        """检查是否请求停止"""
        return self._stop_requested
