"""
GUI 入口点

启动图形化界面
"""
import sys
import os

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 检查依赖
try:
    import customtkinter as ctk
except ImportError:
    print("错误: 未安装 customtkinter")
    print("请运行: pip install customtkinter>=5.2.0")
    sys.exit(1)


def main():
    """启动 GUI"""
    from gui.main_window import MainWindow

    # 创建并运行主窗口
    app = MainWindow()
    app.run()


if __name__ == "__main__":
    main()
