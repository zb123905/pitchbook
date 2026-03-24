@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ====================================
REM VC/PE PitchBook 系统 - 打包脚本
REM ====================================

echo ====================================
echo   VC/PE PitchBook 应用打包工具
echo ====================================
echo.

REM 检查 PyInstaller
echo [1/4] 检查 PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 安装 PyInstaller...
    pip install pyinstaller
)

REM 激活虚拟环境
if exist ".venv\Scripts\activate.bat" (
    echo [2/4] 激活虚拟环境...
    call .venv\Scripts\activate.bat
)

REM 检查并构建 MCP 服务器
if exist "mcp-mail-master\package.json" (
    if not exist "mcp-mail-master\dist\index.js" (
        echo [2.5/4] MCP 服务器未构建，开始构建...
        cd mcp-mail-master
        call npm run build
        cd ..
        if errorlevel 1 (
            echo ⚠️  MCP 服务器构建失败，但继续打包...
        )
    )
)

REM 清理旧的构建
echo [3/4] 清理旧构建...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM 开始打包
echo [4/4] 开始打包...
echo 这可能需要几分钟，请耐心等待...
echo.

pyinstaller --clean build_exe.spec

if errorlevel 1 (
    echo.
    echo ❌ 打包失败！
    pause
    exit /b 1
)

echo.
echo ====================================
echo   ✅ 打包完成！
echo ====================================
echo.
echo 输出位置: dist\VC_PE_PitchBook.exe
echo.
echo 文件大小:
for %%I in (dist\VC_PE_PitchBook.exe) do echo   %%~zI 字节 (约 %%~zI:~0,-3% KB)
echo.

REM 创建快捷方式
echo 创建快捷方式...
powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('dist\VC_PE PitchBook.lnk'); $s.TargetPath = '%CD%\dist\VC_PE_PitchBook.exe'; $s.Save()"

echo.
echo ✅ 完成！可执行文件已保存在 dist 目录
echo.
echo 使用说明:
echo   1. 将 dist 目录中的所有文件复制到目标位置
echo   2. 双击 VC_PE_PitchBook.exe 启动应用
echo   3. 首次运行会在程序目录创建必要的子目录
echo.
pause
