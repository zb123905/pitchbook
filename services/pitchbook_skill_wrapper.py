"""
PitchBook Skill 包装器

包装现有的 Node.js Playwright skill，提供 Python 接口
"""
import subprocess
import os
import json
import re
from pathlib import Path
from typing import Dict, Any, Callable, Optional, List
from datetime import datetime


class PitchBookSkillWrapper:
    """
    PitchBook Skill 包装器

    调用现有的 Node.js skill 进行报告下载
    """

    def __init__(self, skill_dir: str = None):
        """
        初始化包装器

        Args:
            skill_dir: Skill 目录路径
        """
        if skill_dir is None:
            skill_dir = r"E:\pitch\skills\pitchbook-downloader\package"

        self.skill_dir = Path(skill_dir)
        self.script_path = self.skill_dir / "scripts" / "download_pitchbook_reports.mjs"
        self.env_path = self.skill_dir / ".env"

        # 默认输出目录
        self.default_output_dir = Path(r"E:\pitch\数据储存\文件抓取")

    def is_available(self) -> bool:
        """
        检查 skill 是否可用

        Returns:
            True 如果 Node.js 和脚本都存在
        """
        if not self.script_path.exists():
            return False

        try:
            result = subprocess.run(
                ["node", "--version"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_credentials(self) -> Dict[str, str]:
        """
        从 .env 文件读取凭据

        Returns:
            凭据字典（键名不带 PB_ 前缀，与 PitchBookCredentials 匹配）
        """
        credentials = {
            'first_name': '',
            'last_name': '',
            'email': '',
            'company': '',
            'title': '',
            'phone': '',
            'country': ''
        }

        if not self.env_path.exists():
            return credentials

        # 环境变量键名映射
        env_mapping = {
            'PB_FIRST_NAME': 'first_name',
            'PB_LAST_NAME': 'last_name',
            'PB_EMAIL': 'email',
            'PB_COMPANY': 'company',
            'PB_TITLE': 'title',
            'PB_PHONE': 'phone',
            'PB_COUNTRY': 'country'
        }

        try:
            with open(self.env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        # 映射到不带前缀的键名
                        if key in env_mapping:
                            credentials[env_mapping[key]] = value
        except Exception as e:
            print(f"读取凭据文件失败: {e}")

        return credentials

    def save_credentials(self, credentials: Dict[str, str]) -> bool:
        """
        保存凭据到 .env 文件

        Args:
            credentials: 凭据字典（键名不带 PB_ 前缀）

        Returns:
            是否成功
        """
        # 环境变量键名映射
        env_mapping = {
            'first_name': 'PB_FIRST_NAME',
            'last_name': 'PB_LAST_NAME',
            'email': 'PB_EMAIL',
            'company': 'PB_COMPANY',
            'title': 'PB_TITLE',
            'phone': 'PB_PHONE',
            'country': 'PB_COUNTRY'
        }

        try:
            self.skill_dir.mkdir(parents=True, exist_ok=True)

            with open(self.env_path, 'w', encoding='utf-8') as f:
                for key, value in credentials.items():
                    if value and key in env_mapping:
                        f.write(f'{env_mapping[key]}="{value}"\n')
            return True
        except Exception as e:
            print(f"保存凭据失败: {e}")
            return False

    def validate_credentials(self) -> tuple[bool, str]:
        """
        验证凭据是否完整

        Returns:
            (是否有效, 错误消息)
        """
        creds = self.get_credentials()

        required_fields = ['first_name', 'last_name', 'email', 'company', 'title']
        missing = [field for field in required_fields if not creds.get(field)]

        if missing:
            return False, f"缺少必填字段: {', '.join(missing)}"

        if '@' not in creds['email']:
            return False, "邮箱格式不正确"

        return True, ""

    def download_from_listing(
        self,
        max_count: int = 10,
        retries: int = 2,
        listing_url: str = None,
        output_dir: str = None,
        progress_callback: Callable[[str], None] = None,
        log_callback: Callable[[str, str], None] = None
    ) -> Dict[str, Any]:
        """
        从列表页下载报告

        Args:
            max_count: 最大下载数量
            retries: 重试次数
            listing_url: 列表页 URL
            output_dir: 输出目录
            progress_callback: 进度回调 (message)
            log_callback: 日志回调 (level, message)

        Returns:
            下载结果字典
        """
        if log_callback:
            log_callback("INFO", "正在从 PitchBook 官网下载报告...")

        # 检查凭据
        valid, error = self.validate_credentials()
        if not valid:
            if log_callback:
                log_callback("ERROR", f"凭据验证失败: {error}")
            return {
                'success': False,
                'error': error,
                'downloaded': 0,
                'failed': 0
            }

        # 构建命令
        cmd = [
            "node",
            str(self.script_path),
            "--listing-url", listing_url or "https://pitchbook.com/news/reports",
            "--max-from-listing", str(max_count),
            "--retries", str(retries)
        ]

        if output_dir:
            cmd.extend(["--output-dir", output_dir])

        # 准备环境变量（需要添加 PB_ 前缀给 Node.js）
        env = os.environ.copy()
        credentials = self.get_credentials()
        env_mapping = {
            'first_name': 'PB_FIRST_NAME',
            'last_name': 'PB_LAST_NAME',
            'email': 'PB_EMAIL',
            'company': 'PB_COMPANY',
            'title': 'PB_TITLE',
            'phone': 'PB_PHONE',
            'country': 'PB_COUNTRY'
        }
        for key, value in credentials.items():
            if key in env_mapping:
                env[env_mapping[key]] = value

        # 执行命令
        try:
            if log_callback:
                log_callback("INFO", f"执行命令: {' '.join(cmd[:4])}...")

            process = subprocess.Popen(
                cmd,
                cwd=self.skill_dir,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                bufsize=1
            )

            # 实时读取输出
            downloaded_count = 0
            failed_count = 0
            current_url = None

            for line in process.stdout:
                line = line.strip()
                if not line:
                    continue

                if log_callback:
                    # 解析日志级别
                    if '[成功]' in line or '[success]' in line.lower():
                        log_callback("INFO", line)
                        downloaded_count += 1
                    elif '[失败]' in line or '[错误]' in line or '[error]' in line.lower():
                        log_callback("ERROR", line)
                        failed_count += 1
                    elif '[信息]' in line or '[info]' in line.lower():
                        log_callback("INFO", line)
                    elif '[重试]' in line or '[retry]' in line.lower():
                        log_callback("WARNING", line)
                    else:
                        log_callback("DEBUG", line)

                if progress_callback:
                    # 提取进度信息
                    if '第' in line and '次尝试' in line:
                        match = re.search(r'\[(.*?)\]', line)
                        if match:
                            current_url = match.group(1)
                            progress_callback(f"正在下载: {current_url}")

            # 等待进程结束
            return_code = process.wait()
            stderr_output = process.stderr.read()

            if stderr_output and log_callback:
                log_callback("ERROR", stderr_output)

            # 查找结果 JSON 文件
            result_json = self._find_latest_result_json(output_dir or self.default_output_dir)

            result = {
                'success': return_code in [0, 2],  # 2 表示部分成功
                'return_code': return_code,
                'downloaded': downloaded_count,
                'failed': failed_count,
                'stderr': stderr_output,
                'result_json': result_json
            }

            if result_json and log_callback:
                log_callback("INFO", f"结果日志: {result_json}")

            return result

        except FileNotFoundError:
            if log_callback:
                log_callback("ERROR", "Node.js 未安装或未找到")
            return {
                'success': False,
                'error': 'Node.js 未安装',
                'downloaded': 0,
                'failed': 0
            }
        except Exception as e:
            if log_callback:
                log_callback("ERROR", f"执行失败: {e}")
            return {
                'success': False,
                'error': str(e),
                'downloaded': 0,
                'failed': 0
            }

    def download_single(
        self,
        url: str,
        retries: int = 2,
        output_dir: str = None,
        log_callback: Callable[[str, str], None] = None
    ) -> Dict[str, Any]:
        """
        下载单个报告

        Args:
            url: 报告 URL
            retries: 重试次数
            output_dir: 输出目录
            log_callback: 日志回调

        Returns:
            下载结果字典
        """
        # 检查凭据
        valid, error = self.validate_credentials()
        if not valid:
            return {
                'success': False,
                'error': error
            }

        cmd = [
            "node",
            str(self.script_path),
            "--url", url,
            "--retries", str(retries)
        ]

        if output_dir:
            cmd.extend(["--output-dir", output_dir])

        # 准备环境变量（需要添加 PB_ 前缀给 Node.js）
        env = os.environ.copy()
        credentials = self.get_credentials()
        env_mapping = {
            'first_name': 'PB_FIRST_NAME',
            'last_name': 'PB_LAST_NAME',
            'email': 'PB_EMAIL',
            'company': 'PB_COMPANY',
            'title': 'PB_TITLE',
            'phone': 'PB_PHONE',
            'country': 'PB_COUNTRY'
        }
        for key, value in credentials.items():
            if key in env_mapping:
                env[env_mapping[key]] = value

        try:
            result = subprocess.run(
                cmd,
                cwd=self.skill_dir,
                env=env,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=300  # 5 分钟超时
            )

            success = result.returncode == 0

            return {
                'success': success,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode
            }

        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': '下载超时'
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def _find_latest_result_json(self, output_dir: str) -> Optional[str]:
        """
        查找最新的结果 JSON 文件

        Args:
            output_dir: 输出目录

        Returns:
            JSON 文件路径，如果未找到返回 None
        """
        output_path = Path(output_dir)
        if not output_path.exists():
            return None

        json_files = list(output_path.glob("run-*.json"))
        if not json_files:
            return None

        # 按修改时间排序，返回最新的
        json_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
        return str(json_files[0])

    def get_download_history(self, output_dir: str = None) -> List[Dict[str, Any]]:
        """
        获取下载历史记录

        Args:
            output_dir: 输出目录

        Returns:
            历史记录列表
        """
        output_path = Path(output_dir or self.default_output_dir)
        if not output_path.exists():
            return []

        json_files = list(output_path.glob("run-*.json"))
        json_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        history = []
        for json_file in json_files[:10]:  # 最多返回 10 条
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    data['_file'] = str(json_file)
                    data['_timestamp'] = datetime.fromtimestamp(json_file.stat().st_mtime)
                    history.append(data)
            except Exception:
                continue

        return history
