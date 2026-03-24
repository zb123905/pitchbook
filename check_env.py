#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
环境检查和修复脚本
自动检测 Python 环境、依赖安装情况，并提供修复建议
"""
import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """检查 Python 版本"""
    print("检查 Python 版本...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"✓ Python 版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"✗ Python 版本过低: {version.major}.{version.minor}.{version.micro}")
        print("  需要至少 Python 3.8")
        return False

def check_venv():
    """检查虚拟环境"""
    print("\n检查虚拟环境...")
    venv_python = Path(".venv/Scripts/python.exe")
    if venv_python.exists():
        print(f"✓ 虚拟环境存在: {venv_python.absolute()}")
        return True
    else:
        print("✗ 虚拟环境不存在")
        print("  请运行: python -m venv .venv")
        return False

def check_dependencies():
    """检查依赖安装"""
    print("\n检查依赖安装...")
    required_packages = [
        ("PyPDF2", "3.0.0"),
        ("pdfplumber", "0.10.0"),
        ("requests", "2.0.0"),
        ("beautifulsoup4", "4.0.0"),
        ("python-docx", "0.8.11"),
    ]

    missing_packages = []
    for package, min_version in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✓ {package} 已安装")
        except ImportError:
            print(f"✗ {package} 未安装")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n缺少 {len(missing_packages)} 个依赖包")
        return False
    else:
        print("\n所有依赖已安装")
        return True

def install_dependencies():
    """安装依赖"""
    print("\n正在安装依赖...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True,
            text=True
        )
        print("✓ 依赖安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖安装失败: {e}")
        return False

def main():
    print("=" * 50)
    print("VC/PE 环境检查工具")
    print("=" * 50)

    # 检查 Python 版本
    if not check_python_version():
        sys.exit(1)

    # 检查虚拟环境
    if not check_venv():
        sys.exit(1)

    # 检查依赖
    if not check_dependencies():
        print("\n是否安装缺失的依赖？(y/n): ", end="")
        if input().lower() == 'y':
            if install_dependencies():
                print("\n✓ 环境配置完成！")
                print("  运行命令启动系统: start.bat")
            else:
                print("\n✗ 环境配置失败")
                sys.exit(1)
        else:
            print("\n请手动安装依赖: pip install -r requirements.txt")
            sys.exit(1)

    print("\n" + "=" * 50)
    print("✓ 环境检查通过")
    print("=" * 50)

if __name__ == "__main__":
    main()
