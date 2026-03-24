"""
GUI 启动器

简化版的 GUI 启动入口
"""
import sys
import os

# 确保路径正确（使用 path_utils 支持打包环境）
from path_utils import get_app_dir
project_root = get_app_dir()
if project_root not in sys.path:
    sys.path.insert(0, project_root)


def launch_gui():
    """启动 GUI"""
    try:
        import customtkinter as ctk
        from gui.main_window import MainWindow

        app = MainWindow()
        app.run()

    except ImportError as e:
        print("错误: 缺少必要的依赖包")
        print(f"详情: {e}")
        print("\n请运行: pip install customtkinter>=5.2.0")
        input("\n按回车键退出...")
        sys.exit(1)
    except Exception as e:
        print(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
        sys.exit(1)


if __name__ == "__main__":
    launch_gui()
