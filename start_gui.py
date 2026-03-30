"""
VC/PE PitchBook 系统 - GUI 启动入口
提供图形界面进行配置和运行
"""
import sys
import os

# 确保项目根目录在路径中
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def check_dependencies():
    """检查GUI依赖"""
    missing = []

    try:
        import customtkinter
    except ImportError:
        missing.append("customtkinter")

    if missing:
        print("❌ 缺少GUI依赖包，请运行:")
        print(f"   pip install {' '.join(missing)}")
        return False

    return True

def main():
    """启动GUI"""
    print("=" * 60)
    print("VC/PE PitchBook 自动化系统 - GUI模式")
    print("=" * 60)

    if not check_dependencies():
        return

    try:
        from gui.main_window import MainWindow

        print("✓ GUI 启动中...")
        print()

        app = MainWindow()
        app.run()

    except KeyboardInterrupt:
        print("\n👋 用户取消，程序退出")
    except Exception as e:
        print(f"\n❌ GUI启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
