"""
诊断脚本 - 检查打包后的文件结构
运行打包后的 exe 并列出临时目录中的文件
"""
import sys
import os

print("=== 环境信息 ===")
print(f"Python: {sys.version}")
print(f"Frozen: {getattr(sys, 'frozen', False)}")
print(f"Executable: {sys.executable}")

if hasattr(sys, '_MEIPASS'):
    print(f"_MEIPASS: {sys._MEIPASS}")
    meipass = sys._MEIPASS

    print("\n=== _MEIPASS 目录结构 ===")
    for root, dirs, files in os.walk(meipass):
        level = root.replace(meipass, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files[:10]:  # 只显示前10个文件
            print(f'{subindent}{file}')
        if len(files) > 10:
            print(f'{subindent}... and {len(files) - 10} more files')

    print("\n=== 检查关键文件 ===")
    checks = [
        'mcp-mail-master/dist/index.js',
        'mcp-mail-master/package.json',
        'node.exe',
        'playwright_stealth/js/generate.magic.arrays.js',
    ]

    for check in checks:
        path = os.path.join(meipass, check)
        exists = os.path.exists(path)
        print(f"{'✓' if exists else '✗'} {check}")
        if not exists and check.startswith('mcp-mail-master'):
            # 尝试列出 mcp-mail-master 目录
            mcp_dir = os.path.join(meipass, 'mcp-mail-master')
            if os.path.exists(mcp_dir):
                print(f"  mcp-mail-master 内容: {os.listdir(mcp_dir)}")
else:
    print("未检测到 _MEIPASS，可能是开发环境")

input("\n按回车键退出...")
