@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ====================================
REM 简单打包脚本 - 单文件版本（支持 MCP 和 Node.js）
REM ====================================

echo ====================================
REM   VC/PE PitchBook - 单文件打包
REM ====================================
echo.

REM 检查 PyInstaller
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 安装 PyInstaller...
    pip install pyinstaller
)

REM 激活虚拟环境
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM 清理旧文件
echo 清理旧构建...
if exist "build" rmdir /s /q build 2>nul
if exist "dist" rmdir /s /q dist 2>nul

REM ====================================
REM 准备 MCP 服务器
REM ====================================
echo.
echo ====================================
echo   准备 MCP 服务器
echo ====================================
echo.

if exist "mcp-mail-master\package.json" (
    echo 检查 MCP 服务器构建状态...
    if not exist "mcp-mail-master\dist\index.js" (
        echo MCP 服务器未编译，正在构建...
        cd mcp-mail-master
        call npm run build
        cd ..
        if errorlevel 1 (
            echo 警告: MCP 服务器构建失败，可能影响邮件功能
        ) else (
            echo ✓ MCP 服务器构建完成
        )
    ) else (
        echo ✓ MCP 服务器已编译
    )
) else (
    echo 警告: 未找到 mcp-mail-master 目录
)

REM ====================================
REM 检查 Node.js 便携版
REM ====================================
echo.
echo 检查 Node.js 运行时...
if exist "resources\node\node.exe" (
    echo ✓ 找到便携版 Node.js
) else (
    echo 提示: 未找到便携版 Node.js (resources\node\node.exe)
    echo     程序将使用系统安装的 Node.js
    echo     如需离线运行，请从 https://nodejs.org 下载 Windows 便携版
    echo     并将 node.exe 放入 resources\node\ 目录
)

REM ====================================
REM 添加数据文件
REM ====================================
echo.
echo 收集数据文件...
set DATA_FILES=.venv/Lib/site-packages/playwright_stealth;playwright_stealth

REM 添加 MCP 服务器文件
if exist "mcp-mail-master\dist" (
    set DATA_FILES=!DATA_FILES! mcp-mail-master/dist;mcp-mail-master/dist
)
if exist "mcp-mail-master\node_modules" (
    set DATA_FILES=!DATA_FILES! mcp-mail-master/node_modules;mcp-mail-master/node_modules
)
if exist "mcp-mail-master\package.json" (
    set DATA_FILES=!DATA_FILES! mcp-mail-master/package.json;mcp-mail-master
)
if exist "mcp-mail-master\.env.example" (
    set DATA_FILES=!DATA_FILES! mcp-mail-master/.env.example;mcp-mail-master
)

REM 添加 Node.js 运行时
if exist "resources\node\node.exe" (
    set DATA_FILES=!DATA_FILES! resources/node/node.exe;.
)

REM ====================================
REM 打包成单文件
REM ====================================
echo.
echo 开始打包（单文件版本）...
echo 这可能需要几分钟，请耐心等待...
echo.

pyinstaller --onefile --windowed --name "VC_PE_PitchBook" ^
    --hidden-import customtkinter ^
    --hidden-import PIL ^
    --hidden-import playwright_stealth ^
    --hidden-import playwright_stealth.stealth ^
    --hidden-import path_utils ^
    --add-data "!DATA_FILES!" ^
    gui_launcher.py

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
echo 可执行文件: dist\VC_PE_PitchBook.exe
echo.

REM 创建应用包
echo 创建应用包...
mkdir dist\VC_PE_PitchBook_App 2>nul
copy /Y dist\VC_PE_PitchBook.exe dist\VC_PE_PitchBook_App\ >nul

echo [Launcher] > dist\VC_PE_PitchBook_App\启动应用.bat
echo start "" "VC_PE_PitchBook.exe" >> dist\VC_PE_PitchBook_App\启动应用.bat

echo.
echo ✅ 应用包已创建: dist\VC_PE_PitchBook_App\
echo.
echo ====================================
echo   使用说明
echo ====================================
echo.
echo 首次运行时，程序会在用户文档目录创建数据文件夹：
echo   %%USERPROFILE%%\Documents\VC_PE_PitchBook\
echo.
echo 如需使用 MCP 邮件功能，请在应用中配置邮箱信息。
echo.
pause
