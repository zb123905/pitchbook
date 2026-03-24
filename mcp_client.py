"""
MCP 客户端 - 连接到 Node.js MCP 服务器
使用 subprocess 和 stdio 与 MCP 服务器通信
"""
import json
import os
import sys
import subprocess
import signal
import threading
import queue
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

from path_utils import get_resource_path, get_node_executable, get_app_dir

logger = logging.getLogger(__name__)


def _ensure_mcp_server_files(target_dir: str) -> bool:
    """
    确保 MCP 服务器文件在目标目录中存在（用于打包环境）

    从 _MEIPASS 复制必要的文件到可写的 exe 目录

    注意：此函数当前未使用，因为改为直接从 _MEIPASS 运行
    """
    return True  # 不再需要此函数


def _ensure_mcp_env_config(server_dir: str) -> bool:
    """
    确保 MCP 服务器的 .env 配置文件存在

    从 email_credentials.py 读取配置并创建 .env 文件

    Args:
        server_dir: MCP 服务器目录

    Returns:
        是否成功创建或已存在
    """
    env_file = os.path.join(server_dir, '.env')

    # 如果 .env 已存在，直接返回
    if os.path.exists(env_file):
        return True

    try:
        # 从 email_credentials.py 读取配置
        import email_credentials
        config = email_credentials.IMAP_CONFIG

        email = config.get('email_address', '')
        password = config.get('password', '')

        if not email or not password:
            logger.warning("邮箱配置不完整，无法创建 MCP .env 文件")
            return False

        # 创建 .env 文件内容
        # QQ邮箱 IMAP 和 SMTP 配置
        env_content = f"""# MCP 邮件服务器配置
# 自动生成于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

# IMAP 配置（接收邮件）
IMAP_HOST=imap.qq.com
IMAP_PORT=993
IMAP_SECURE=true
IMAP_USER={email}
IMAP_PASS={password}

# SMTP 配置（发送邮件）
SMTP_HOST=smtp.qq.com
SMTP_PORT=587
SMTP_SECURE=true
SMTP_USER={email}
SMTP_PASS={password}

# 可选：默认发件人信息
DEFAULT_FROM_NAME=VC_PE_PitchBook
DEFAULT_FROM_EMAIL={email}
"""

        # 写入 .env 文件
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)

        logger.info(f"MCP .env 配置文件已创建: {env_file}")
        return True

    except Exception as e:
        logger.error(f"创建 MCP .env 文件失败: {e}")
        return False


class MCPClient:
    """MCP 客户端，与 Node.js MCP 服务器通信"""

    def __init__(self, server_dir: str = None):
        """
        初始化 MCP 客户端

        Args:
            server_dir: MCP 服务器目录路径，默认为 mcp-mail-master
        """
        if server_dir is None:
            # 在打包环境下，使用 _MEIPASS（node_modules 所在位置）
            # 在开发环境下，使用项目目录
            from path_utils import is_frozen
            if is_frozen():
                # 打包后：从 _MEIPASS 运行（runtime hook 已恢复 package.json）
                server_dir = get_resource_path('mcp-mail-master')
            else:
                # 开发环境：使用项目目录
                server_dir = get_resource_path('mcp-mail-master')

        self.server_dir = server_dir
        self.server_script = os.path.join(server_dir, 'dist', 'index.js')
        self.bridge_script = os.path.join(server_dir, 'bridging_mail_mcp.py')

        # 获取 Node.js 可执行文件路径（支持打包环境）
        self.node_exe = get_node_executable()

        self.process: Optional[subprocess.Popen] = None
        self.message_queue: queue.Queue = queue.Queue()
        self.request_id = 0
        self.is_connected = False

        # 检查服务器文件是否存在
        if not os.path.exists(self.server_script):
            logger.error(f"MCP 服务器脚本不存在: {self.server_script}")
            raise FileNotFoundError(f"MCP 服务器脚本不存在: {self.server_script}")

        if not os.path.exists(self.bridge_script):
            logger.warning(f"桥接脚本不存在: {self.bridge_script}")

    def connect(self) -> bool:
        """连接到 MCP 服务器"""
        try:
            logger.info("正在启动 MCP 服务器...")

            # 确保 .env 配置文件存在
            if not _ensure_mcp_env_config(self.server_dir):
                logger.error("MCP .env 配置文件创建失败")
                return False

            # 设置环境变量
            env = os.environ.copy()

            # 启动 Node.js MCP 服务器（使用打包的或系统的 node.exe）
            self.process = subprocess.Popen(
                [self.node_exe, self.server_script],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                encoding='utf-8',
                errors='ignore',
                bufsize=0,
                cwd=self.server_dir
            )

            # 启动读取线程（stdout 和 stderr）
            self._start_reader_thread()

            # 等待服务器启动
            import time
            time.sleep(2)

            # 检查进程状态
            if self.process.poll() is not None:
                # 读取 stderr 获取错误信息
                stderr_output = []
                if self.process.stderr:
                    try:
                        stderr_output = self.process.stderr.readlines()
                    except:
                        pass
                stderr_text = ''.join(stderr_output) if stderr_output else "未知错误"
                logger.error(f"MCP 服务器启动失败: {stderr_text}")
                return False

            self.is_connected = True
            logger.info("MCP 服务器连接成功")
            return True

        except Exception as e:
            logger.error(f"连接 MCP 服务器失败: {str(e)}")
            return False

    def _start_reader_thread(self):
        """启动读取线程（同时读取 stdout 和 stderr）"""
        def stdout_reader():
            while True:
                try:
                    line = self.process.stdout.readline()
                    if not line:
                        break
                    self.message_queue.put(line.strip())
                except Exception as e:
                    logger.error(f"读取服务器输出失败: {str(e)}")
                    break

        def stderr_reader():
            """读取 stderr 并记录到日志"""
            while True:
                try:
                    line = self.process.stderr.readline()
                    if not line:
                        break
                    line = line.strip()
                    if line:  # 只记录非空行
                        logger.warning(f"MCP 服务器: {line}")
                except Exception as e:
                    break

        self.reader_thread = threading.Thread(target=stdout_reader, daemon=True)
        self.reader_thread.start()

        self.stderr_thread = threading.Thread(target=stderr_reader, daemon=True)
        self.stderr_thread.start()

    def _send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        发送 JSON-RPC 请求

        Args:
            method: MCP 工具名称
            params: 工具参数

        Returns:
            响应结果
        """
        if not self.is_connected:
            return {"success": False, "error": "未连接到 MCP 服务器"}

        self.request_id += 1

        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "tools/call",
            "params": {
                "name": method,
                "arguments": params or {}
            }
        }

        try:
            # 发送请求
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()

            # 等待响应
            import time
            timeout = 30  # 30 秒超时
            start_time = time.time()

            while time.time() - start_time < timeout:
                try:
                    response_line = self.message_queue.get(timeout=1)
                    if not response_line:
                        continue

                    response = json.loads(response_line)

                    # 检查是否是我们的响应
                    if response.get("id") == self.request_id:
                        if "error" in response:
                            return {"success": False, "error": response["error"]}
                        return {"success": True, "data": response.get("result", {})}

                except queue.Empty:
                    continue
                except json.JSONDecodeError:
                    continue

            return {"success": False, "error": "请求超时"}

        except Exception as e:
            logger.error(f"发送请求失败: {str(e)}")
            return {"success": False, "error": str(e)}

    def search_emails(self, query: str = "PitchBook", limit: int = 20) -> List[Dict[str, Any]]:
        """
        搜索邮件（使用listEmails工具，然后在Python中筛选）

        Args:
            query: 搜索关键词
            limit: 最大结果数

        Returns:
            邮件列表（包含完整内容和链接）
        """
        try:
            # 先列出邮件
            result = self._send_request("listEmails", {
                "folder": "INBOX",
                "limit": limit * 2  # 获取更多邮件以便筛选
            })

            if not result.get("success"):
                logger.error(f"列出邮件失败: {result.get('error')}")
                return []

            # 解析响应
            data = result.get("data", {})
            content = data.get("content", [])
            if not content:
                return []

            # MCP 服务器返回的是文本内容，需要解析
            text_content = content[0].get("text", "")

            # 解析邮件列表格式
            emails = self._parse_email_text(text_content, query, limit)

            # 获取每封邮件的详细信息（包括正文和链接）
            detailed_emails = []
            for email in emails:
                uid = email.get('id')
                if uid:
                    try:
                        # 首先获取前 2000 字符，检查内容总长度
                        detail_result = self._send_request("getEmailDetail", {
                            "uid": int(uid),
                            "folder": "INBOX",
                            "contentRange": {
                                "start": 0,
                                "end": 2000
                            }
                        })

                        if detail_result.get("success"):
                            detail_data = detail_result.get("data", {})
                            detail_content = detail_data.get("content", [])
                            if detail_content:
                                detail_text = detail_content[0].get("text", "")

                                # 检查是否需要获取更多内容
                                # 查找内容总长度标记，例如 "内容 (1-2000/136167字符)"
                                import re
                                total_length = None
                                length_match = re.search(r'内容.*?/\s*(\d+)字符', detail_text)
                                if length_match:
                                    total_length = int(length_match.group(1))

                                # 如果内容超过 2000 字符，分批获取
                                if total_length and total_length > 2000:
                                    logger.info(f"邮件 {uid} 内容较长 ({total_length} 字符)，分批获取...")
                                    full_detail_text = detail_text
                                    offset = 2000
                                    while offset < total_length:
                                        chunk_result = self._send_request("getEmailDetail", {
                                            "uid": int(uid),
                                            "folder": "INBOX",
                                            "contentRange": {
                                                "start": offset,
                                                "end": min(offset + 2000, total_length)
                                            }
                                        })
                                        if chunk_result.get("success"):
                                            chunk_data = chunk_result.get("data", {})
                                            chunk_content = chunk_data.get("content", [])
                                            if chunk_content:
                                                chunk_text = chunk_content[0].get("text", "")
                                                # 移除重复的头部信息
                                                content_start = chunk_text.find("📄 内容")
                                                if content_start != -1:
                                                    # 找到实际内容开始的位置（跳过标题行）
                                                    lines = chunk_text.split('\n')
                                                    for i, line in enumerate(lines):
                                                        if line.strip() and not line.startswith('📄') and not line.startswith('主题:') and not line.startswith('发件人:'):
                                                            full_detail_text += '\n' + '\n'.join(lines[i:])
                                                            break
                                                else:
                                                    full_detail_text += '\n' + chunk_text
                                        offset += 2000
                                    detail_text = full_detail_text

                                # 解析详细信息并合并
                                detailed_email = self._parse_email_detail_text(detail_text, email)
                                if detailed_email:
                                    detailed_emails.append(detailed_email)
                                else:
                                    # 如果解析失败，使用原始邮件信息
                                    detailed_emails.append(email)
                        else:
                            # 获取详情失败，使用原始邮件信息
                            detailed_emails.append(email)
                    except Exception as e:
                        logger.warning(f"获取邮件 {uid} 详情失败: {e}")
                        detailed_emails.append(email)

            logger.info(f"找到 {len(detailed_emails)} 封包含'{query}'的邮件")
            return detailed_emails

        except Exception as e:
            logger.error(f"搜索邮件出错: {str(e)}")
            return []

    def _parse_email_text(self, text: str, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        解析 MCP 服务器返回的邮件文本

        Args:
            text: MCP 服务器返回的文本
            query: 搜索关键词
            limit: 最大结果数

        Returns:
            邮件列表
        """
        emails = []

        try:
            # 尝试解析 JSON 格式
            if text.strip().startswith('['):
                email_list = json.loads(text)
                for email_data in email_list:
                    if len(emails) >= limit:
                        break

                    subject = email_data.get('subject', '').lower()
                    from_addr = email_data.get('from', '').lower()

                    if self._match_email(subject, from_addr, query):
                        emails.append({
                            'id': email_data.get('uid', ''),
                            'subject': email_data.get('subject', ''),
                            'from': email_data.get('from', ''),
                            'date': email_data.get('date', ''),
                            'body': '',
                            'html_body': '',
                            'links': [],
                            'attachments': [],
                            'source_file': f"MCP_{email_data.get('uid', '')}"
                        })

                return emails

        except json.JSONDecodeError:
            pass

        # 解析中文文本格式（MCP 服务器实际返回的格式）
        # 格式示例：
        # 7. [已读]  来自: dui wai <dwjmdx001@outlook.com>
        #    主题: 转发: Fw:Public PE returns bounce back
        #    时间: 2026/3/16 19:21:34
        #    UID: 7

        import re
        lines = text.split('\n')
        current_email = {}

        for line in lines:
            line = line.strip()

            # 检测邮件条目开始（数字编号，如 "7. [已读]  来自:"）
            if re.match(r'^\d+\.\s*\[?\w+\]?\s*来自:', line):
                # 保存之前的邮件
                if current_email and self._match_email(
                    current_email.get('subject', ''),
                    current_email.get('from', ''),
                    query
                ):
                    emails.append(current_email)
                    if len(emails) >= limit:
                        break
                current_email = {}
                # 解析 "来自:" 字段
                if '来自:' in line:
                    from_part = line.split('来自:', 1)[1].strip()
                    current_email['from'] = from_part
                continue

            if not line:
                # 邮件条目结束
                if current_email and self._match_email(
                    current_email.get('subject', ''),
                    current_email.get('from', ''),
                    query
                ):
                    emails.append(current_email)
                    if len(emails) >= limit:
                        break
                current_email = {}
                continue

            # 解析邮件字段（支持中文和英文格式）
            if '主题:' in line:
                current_email['subject'] = line.split('主题:', 1)[1].strip()
            elif 'Subject:' in line:
                current_email['subject'] = line.split('Subject:', 1)[1].strip()
            elif '时间:' in line:
                current_email['date'] = line.split('时间:', 1)[1].strip()
            elif 'Date:' in line:
                current_email['date'] = line.split('Date:', 1)[1].strip()
            elif 'UID:' in line:
                current_email['id'] = line.split('UID:', 1)[1].strip()

        # 检查最后一个邮件
        if current_email and self._match_email(
            current_email.get('subject', ''),
            current_email.get('from', ''),
            query
        ):
            emails.append(current_email)

        # 添加缺失的字段
        for email in emails:
            if 'body' not in email:
                email['body'] = ''
            if 'html_body' not in email:
                email['html_body'] = ''
            if 'links' not in email:
                email['links'] = []
            if 'attachments' not in email:
                email['attachments'] = []
            if 'source_file' not in email:
                email['source_file'] = f"MCP_{email.get('id', '')}"

        return emails

    def _match_email(self, subject: str, from_addr: str, query: str) -> bool:
        """
        判断邮件是否匹配搜索条件

        匹配规则：
        1. 主题或发件人包含查询关键词
        2. 包含 VC/PE 相关关键词（PE、VC、PitchBook、Private Equity等）
        3. 发件人是特定邮箱（如outlook.com，可能包含转发邮件）

        Args:
            subject: 邮件主题（小写）
            from_addr: 发件人（小写）
            query: 查询关键词

        Returns:
            是否匹配
        """
        query_lower = query.lower()

        # 规则1: 直接匹配查询关键词
        if query_lower in subject or query_lower in from_addr:
            return True

        # 规则2: VC/PE 相关关键词
        vc_keywords = [
            'pitchbook', 'private equity', 'venture capital',
            'pe ', ' vc', 'pe/', 'vc/',
            'fund', 'investment', 'deals', 'startup',
            '私募', '股权', '投资', '基金'
        ]

        for keyword in vc_keywords:
            if keyword in subject:
                return True

        # 规则3: 特定发件人域名（可能包含转发邮件）
        professional_domains = [
            'outlook.com', 'pitchbook.com',
            'gmail.com', '163.com', 'qq.com'
        ]

        # 如果发件人是专业邮箱，且主题包含相关内容
        for domain in professional_domains:
            if domain in from_addr:
                # 检查主题是否看起来像专业内容
                if any(char in subject for char in ['fw:', 're:', '转发']):
                    return True

        return False

    def _parse_email_detail_text(self, text: str, base_email: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        解析邮件详情文本（从getEmailDetail返回）

        Args:
            text: MCP服务器返回的邮件详情文本
            base_email: 基础邮件信息（从列表获取）

        Returns:
            包含完整信息的邮件字典
        """
        import re
        from bs4 import BeautifulSoup

        try:
            # 创建邮件对象，基于基础信息
            email = base_email.copy()

            # 找到内容开始位置
            content_start = text.find('📄 内容')
            if content_start == -1:
                content_start = text.find('内容:')

            if content_start != -1:
                # 跳过 "📄 内容 (1-2000/136167字符):" 这一行
                # 找到下一个换行符后的内容
                content_start = text.find('\n', content_start)
                if content_start != -1:
                    # 跳过空行
                    while content_start < len(text) and text[content_start] in '\n\r':
                        content_start += 1

                    # 内容从 content_start 开始到文件结束
                    email_body = text[content_start:]

                    # 移除可能的尾部提示
                    end_marker = email_body.find('\n\n[...]')
                    if end_marker != -1:
                        email_body = email_body[:end_marker]

                    # 尝试检测是否是HTML内容
                    if '<' in email_body and '>' in email_body and '</' in email_body:
                        email['html_body'] = email_body
                        email['body'] = BeautifulSoup(email_body, 'html.parser').get_text(separator='\n')
                    else:
                        email['body'] = email_body
                        email['html_body'] = ''

                    # 提取链接
                    email['links'] = self._extract_links_from_content(email['html_body'] or email['body'])
                else:
                    email['body'] = ''
                    email['html_body'] = ''
                    email['links'] = []
            else:
                email['body'] = ''
                email['html_body'] = ''
                email['links'] = []

            # 添加缺失的字段
            if 'attachments' not in email:
                email['attachments'] = []
            if 'source_file' not in email:
                email['source_file'] = f"MCP_{email.get('id', '')}"

            return email

        except Exception as e:
            logger.error(f"解析邮件详情失败: {e}")
            return None

    def _extract_links_from_content(self, content: str) -> List[Dict[str, str]]:
        """
        从内容中提取链接

        Args:
            content: 邮件内容（HTML或纯文本）

        Returns:
            链接列表
        """
        import re
        from bs4 import BeautifulSoup

        links = []

        if not content:
            return links

        try:
            # 如果是HTML内容
            if '<' in content and '>' in content:
                try:
                    soup = BeautifulSoup(content, 'html.parser')
                    for a_tag in soup.find_all('a', href=True):
                        href = a_tag['href'].strip()
                        link_text = a_tag.get_text(strip=True) or '无链接文本'

                        # 只保存有效的链接
                        if href and not href.startswith('#') and not href.startswith('mailto:'):
                            href = self._clean_link(href)
                            if href:
                                links.append({
                                    'url': href,
                                    'text': link_text[:100]
                                })
                except Exception as e:
                    logger.warning(f"解析HTML链接失败: {e}")

            # 提取纯文本URL
            url_pattern = r'https?://[^\s<>"{}|\\^`\[\]\{\}\(\)\$\s]+'
            text_links = re.findall(url_pattern, content)

            for url in text_links:
                url = self._clean_link(url)
                if url and not any(link['url'] == url for link in links):
                    links.append({
                        'url': url,
                        'text': '直接链接'
                    })

        except Exception as e:
            logger.warning(f"提取链接失败: {e}")

        return links

    def _clean_link(self, url: str) -> Optional[str]:
        """
        清理和验证链接

        Args:
            url: 原始URL

        Returns:
            清理后的URL或None
        """
        import re

        if not url:
            return None

        # 移除尾部标点
        url = url.rstrip('.,;:!?)\'"`')

        # 保留有效字符
        url = re.sub(r'[^\w\-._~:/?#\[\]@!$&\'()*+,;=%]', '', url)

        # 确保以http开头
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url

        return url if url.startswith('http://') or url.startswith('https://') else None

    def list_emails(self, folder: str = "INBOX", limit: int = 20) -> List[Dict[str, Any]]:
        """
        列出邮件

        Args:
            folder: 文件夹名称
            limit: 最大结果数

        Returns:
            邮件列表
        """
        try:
            result = self._send_request("listEmails", {
                "folder": folder,
                "limit": limit
            })

            if not result.get("success"):
                logger.error(f"列出邮件失败: {result.get('error')}")
                return []

            # 解析响应
            data = result.get("data", {})
            content = data.get("content", [])

            return self._parse_email_list(content)

        except Exception as e:
            logger.error(f"列出邮件出错: {str(e)}")
            return []

    def get_email_detail(self, uid: str, folder: str = "INBOX") -> Optional[Dict[str, Any]]:
        """
        获取邮件详情

        Args:
            uid: 邮件 UID
            folder: 文件夹名称

        Returns:
            邮件详情
        """
        try:
            result = self._send_request("getEmailDetail", {
                "uid": uid,
                "folder": folder
            })

            if not result.get("success"):
                logger.error(f"获取邮件详情失败: {result.get('error')}")
                return None

            # 解析响应
            data = result.get("data", {})
            content = data.get("content", [])

            return self._parse_email_detail(content)

        except Exception as e:
            logger.error(f"获取邮件详情出错: {str(e)}")
            return None

    def _parse_email_list(self, content: List[Dict]) -> List[Dict[str, Any]]:
        """解析邮件列表响应"""
        emails = []

        if not content or not isinstance(content, list):
            return emails

        text = content[0].get("text", "")

        # 这里需要根据实际的 MCP 服务器响应格式来解析
        # 暂时返回空列表

        return emails

    def _parse_email_detail(self, content: List[Dict]) -> Optional[Dict[str, Any]]:
        """解析邮件详情响应"""
        if not content or not isinstance(content, list):
            return None

        text = content[0].get("text", "")

        # 这里需要根据实际的 MCP 服务器响应格式来解析
        # 暂时返回 None

        return None

    def disconnect(self):
        """断开连接"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass

            self.process = None
            self.is_connected = False
            logger.info("MCP 服务器已断开")

    def __enter__(self):
        """上下文管理器入口"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()


# 导出
__all__ = ['MCPClient']
