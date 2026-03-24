"""
路径工具模块 - PyInstaller 打包路径管理

处理开发和打包环境下的路径问题：
- 开发环境：使用项目根目录
- 打包后：资源使用 sys._MEIPASS，数据使用 exe 所在目录或用户文档目录
"""
import sys
import os


def get_resource_path(relative_path: str = '') -> str:
    """
    获取只读资源文件路径（打包后使用 sys._MEIPASS）

    用于访问打包的资源文件，如：
    - MCP 服务器脚本
    - Node.js 运行时
    - 其他只读数据文件

    Args:
        relative_path: 相对路径

    Returns:
        资源文件的绝对路径
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 打包后的临时解压目录
        base_path = sys._MEIPASS
    else:
        # 开发环境：使用当前文件所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))

    if relative_path:
        return os.path.join(base_path, relative_path)
    return base_path


def get_app_dir() -> str:
    """
    获取应用程序根目录

    - 开发环境：项目根目录
    - 打包后：exe 所在目录

    Returns:
        应用程序根目录的绝对路径
    """
    if getattr(sys, 'frozen', False):
        # 打包后：使用 exe 所在目录
        return os.path.dirname(sys.executable)
    else:
        # 开发环境：使用项目根目录
        return os.path.dirname(os.path.abspath(__file__))


def get_user_data_path(relative_path: str = '') -> str:
    """
    获取用户数据路径（可写目录）

    用于存储运行时生成的数据文件，如：
    - 日志文件
    - 分析报告
    - 下载的文件
    - 用户配置

    Args:
        relative_path: 相对路径

    Returns:
        用户数据目录的绝对路径
    """
    if getattr(sys, 'frozen', False):
        # 打包后：使用 exe 所在目录（数据储存在程序旁边）
        app_dir = os.path.dirname(sys.executable)
    else:
        # 开发环境：使用项目根目录
        app_dir = os.path.dirname(os.path.abspath(__file__))

    if relative_path:
        return os.path.join(app_dir, relative_path)
    return app_dir


def ensure_directory(path: str) -> str:
    """
    确保目录存在，不存在则创建

    Args:
        path: 目录路径

    Returns:
        目录路径（确保存在）
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as e:
            # 如果创建失败，尝试使用临时目录
            import tempfile
            temp_dir = os.path.join(tempfile.gettempdir(), 'VC_PE_PitchBook')
            if not os.path.exists(temp_dir):
                os.makedirs(temp_dir, exist_ok=True)
            return temp_dir
    return path


def get_node_executable() -> str:
    """
    获取 Node.js 可执行文件路径

    - 打包后：使用打包的 node.exe（从 resources/node/）
    - 开发环境：使用系统的 node 命令

    Returns:
        Node.js 可执行文件的路径或命令
    """
    if getattr(sys, 'frozen', False):
        # 打包后：使用打包的 node.exe
        node_exe = get_resource_path('node.exe')
        if os.path.exists(node_exe):
            return node_exe
        else:
            # 回退到系统 node
            return 'node'
    else:
        # 开发环境：使用系统 node
        return 'node'


def is_frozen() -> bool:
    """
    检查是否为打包后的环境

    Returns:
        True 如果是打包后的环境
    """
    return getattr(sys, 'frozen', False)


def get_project_root() -> str:
    """
    获取项目根目录（兼容旧代码）

    Returns:
        项目根目录路径
    """
    return get_app_dir()


# 导出
__all__ = [
    'get_resource_path',
    'get_app_dir',
    'get_user_data_path',
    'ensure_directory',
    'get_node_executable',
    'is_frozen',
    'get_project_root',
]
