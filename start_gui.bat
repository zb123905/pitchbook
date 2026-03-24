@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM VC/PE PitchBook 系统 - GUI 启动脚本
echo ====================================
echo VC/PE PitchBook 自动化系统
echo 图形化界面启动器
echo ====================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 Python
    echo 请安装 Python 3.8 或更高版本
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist ".venv\Scripts\activate.bat" (
    echo 创建虚拟环境...
    python -m venv .venv
    if errorlevel 1 (
        echo 错误: 创建虚拟环境失败
        pause
        exit /b 1
    )
)

REM 激活虚拟环境
echo 激活虚拟环境...
call .venv\Scripts\activate.bat

REM 检查依赖
echo 检查依赖...
pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo 安装 GUI 依赖...
    pip install -r requirements.txt
)

REM 启动 GUI
echo.
echo 启动图形化界面...
echo.
python gui_launcher.py

REM 如果出错，暂停以查看错误信息
if errorlevel 1 (
    echo.
    echo 程序异常退出
    pause
)
