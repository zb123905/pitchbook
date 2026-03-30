@echo off
REM VC/PE PitchBook Report Automation System - GUI Launcher
REM 直接启动图形界面

title VC/PE PitchBook GUI

echo ======================================
echo VC/PE PitchBook 自动化系统 - GUI模式
echo ======================================
echo.

REM Switch to script directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please run: python -m venv .venv
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check Python dependencies
echo [1/3] 检查Python依赖...
python -c "import customtkinter" 2>/dev/null
if errorlevel 1 (
    echo [INFO] 安装GUI依赖...
    pip install customtkinter pillow
)

echo [2/3] 启动GUI界面...
echo.

set PYTHONIOENCODING=utf-8
python start_gui.py

echo.
pause
