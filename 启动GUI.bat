@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM Check if virtual environment exists
if exist ".venv\Scripts\python.exe" (
    set "PYTHON_CMD=.venv\Scripts\python.exe"
) else if exist ".venv\bin\python.exe" (
    set "PYTHON_CMD=.venv\bin\python.exe"
) else (
    set "PYTHON_CMD=python"
)

echo.
echo ========================================
echo   VC/PE PitchBook 自动化系统
echo ========================================
echo.
echo 正在启动可视化界面...
echo.

"%PYTHON_CMD%" gui_launcher.py

if errorlevel 1 (
    echo.
    echo ========================================
    echo   程序异常退出
    echo ========================================
    echo.
    echo 请检查以下事项：
    echo   1. Python 是否已安装
    echo   2. 虚拟环境是否已创建 (.venv)
    echo   3. 依赖包是否已安装
    echo.
    echo 如需帮助，请运行 check_env.py 检查环境
    echo.
    pause
)
