"""
直接从 PitchBook 官网抓取并下载报告

独立脚本，不依赖 GUI 配置
"""
import os
import subprocess
import sys
from datetime import datetime

# 设置 UTF-8 编码输出（Windows 兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def main():
    skill_dir = r"E:\pitch\skills\pitchbook-downloader\package"
    output_dir = r"E:\pitch\数据储存\文件抓取"

    # 检查 Skill 目录是否存在
    if not os.path.exists(skill_dir):
        print(f"❌ 错误: Playwright Skill 目录不存在: {skill_dir}")
        print("请确保已安装 PitchBook 报告下载 Skill")
        return 1

    # 加载 .env 文件中的环境变量
    env_path = os.path.join(skill_dir, ".env")
    env = os.environ.copy()
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # 移除引号
                    value = value.strip('"').strip("'")
                    env[key] = value
        print("✅ 已加载环境配置")
    else:
        print("⚠️ 警告: .env 文件不存在")

    # 使用 Playwright Skill 的列表页下载功能
    script_path = os.path.join(skill_dir, "scripts", "download_pitchbook_reports.mjs")
    if not os.path.exists(script_path):
        print(f"❌ 错误: 下载脚本不存在: {script_path}")
        return 1

    cmd = [
        "node",
        script_path,
        "--listing-url", "https://pitchbook.com/news/reports",
        "--max-from-listing", "10",
        "--retries", "2"
    ]

    print("=" * 60)
    print("🔍 PitchBook 报告直接下载工具")
    print("=" * 60)
    print(f"📁 输出目录: {output_dir}")
    print(f"📋 最大下载数量: 10")
    print(f"🌐 源网址: https://pitchbook.com/news/reports")
    print("=" * 60)
    print()

    print("🚀 开始下载...")
    result = subprocess.run(
        cmd,
        cwd=skill_dir,
        capture_output=True,
        text=True,
        encoding='utf-8',
        env=env  # 传递环境变量
    )

    # 输出结果
    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print("⚠️ 错误输出:")
        print(result.stderr)

    print()
    print("=" * 60)
    if result.returncode == 0:
        print("✅ 下载完成！")
        print(f"📁 请查看输出目录: {output_dir}")
    else:
        print(f"❌ 下载失败，返回码: {result.returncode}")
    print("=" * 60)

    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
