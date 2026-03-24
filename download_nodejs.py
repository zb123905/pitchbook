#!/usr/bin/env python3
"""
Node.js 便携版下载助手

自动下载 Node.js Windows 便携版并提取 node.exe 到 resources/node/ 目录
"""
import os
import sys
import urllib.request
import zipfile
import tempfile
import shutil

# Node.js LTS 版本配置
NODE_VERSION = "v20.11.1"
NODE_URL = f"https://nodejs.org/dist/{NODE_VERSION}/node-{NODE_VERSION}-win-x64.zip"
TARGET_DIR = os.path.join(os.path.dirname(__file__), "resources", "node")
TARGET_FILE = os.path.join(TARGET_DIR, "node.exe")


def download_with_progress(url: str, dest_path: str) -> bool:
    """下载文件并显示进度"""
    print(f"正在下载: {url}")
    print(f"保存到: {dest_path}")

    try:
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('content-length', 0))
            block_size = 8192
            downloaded = 0

            with open(dest_path, 'wb') as f:
                while True:
                    block = response.read(block_size)
                    if not block:
                        break
                    downloaded += len(block)
                    f.write(block)

                    # 显示进度
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        mb_downloaded = downloaded / (1024 * 1024)
                        mb_total = total_size / (1024 * 1024)
                        print(f"\r进度: {percent:.1f}% ({mb_downloaded:.1f} MB / {mb_total:.1f} MB)", end='')

        print("\n下载完成!")
        return True
    except Exception as e:
        print(f"\n下载失败: {e}")
        return False


def extract_node_exe(zip_path: str, dest_dir: str) -> bool:
    """从 ZIP 文件中提取 node.exe"""
    print(f"\n正在解压: {zip_path}")

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # node.exe 在 ZIP 中的路径
            node_exe_path = f"node-{NODE_VERSION}-win-x64/node.exe"

            if node_exe_path not in zip_ref.namelist():
                print(f"错误: 在 ZIP 文件中找不到 {node_exe_path}")
                return False

            # 提取 node.exe
            with zip_ref.open(node_exe_path) as source, open(dest_dir, 'wb') as target:
                shutil.copyfileobj(source, target)

        print(f"提取完成: {dest_dir}")
        return True
    except Exception as e:
        print(f"解压失败: {e}")
        return False


def main():
    """主函数"""
    print("=" * 60)
    print("Node.js 便携版下载助手")
    print("=" * 60)
    print(f"版本: {NODE_VERSION}")
    print(f"目标: {TARGET_FILE}")
    print()

    # 检查是否已存在
    if os.path.exists(TARGET_FILE):
        size_mb = os.path.getsize(TARGET_FILE) / (1024 * 1024)
        response = input(f"node.exe 已存在 ({size_mb:.1f} MB)，是否重新下载？(y/N): ")
        if response.lower() != 'y':
            print("取消下载")
            return

    # 确保目标目录存在
    os.makedirs(TARGET_DIR, exist_ok=True)

    # 创建临时目录
    with tempfile.TemporaryDirectory() as temp_dir:
        zip_path = os.path.join(temp_dir, "node.zip")

        # 下载 ZIP 文件
        if not download_with_progress(NODE_URL, zip_path):
            print("\n下载失败，请手动下载:")
            print(f"  URL: {NODE_URL}")
            print(f"  解压后复制 node.exe 到: {TARGET_DIR}")
            sys.exit(1)

        # 提取 node.exe
        if not extract_node_exe(zip_path, TARGET_FILE):
            print("\n解压失败，请手动操作")
            sys.exit(1)

    # 验证
    if os.path.exists(TARGET_FILE):
        size_mb = os.path.getsize(TARGET_FILE) / (1024 * 1024)
        print(f"\n成功! node.exe 已保存到: {TARGET_FILE}")
        print(f"文件大小: {size_mb:.1f} MB")
        print()
        print("下一步:")
        print("  1. 确保 VC_PE_PitchBook.spec 中的 node.exe 配置已取消注释")
        print("  2. 运行打包命令: python build_app.bat")
    else:
        print("\n错误: node.exe 未成功创建")
        sys.exit(1)


if __name__ == "__main__":
    main()
