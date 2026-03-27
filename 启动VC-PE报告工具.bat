@echo off
chcp 65001 >/dev/null
cd /d "%~dp0"
title VC/PE PitchBook 报告自动化系统

if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe gui_launcher.py
) else if exist "python.exe" (
    python gui_launcher.py
) else (
    echo 错误: 找不到 Python 环境
    echo 请确保虚拟环境已安装
    pause
)
