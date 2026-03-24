@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

REM ====================================
REM 完整打包脚本 - 包含 Node.js 下载
REM ====================================

echo ====================================
echo   VC/PE PitchBook - 完整打包工具
echo ====================================
echo.

REM ====================================
REM Step 1: 检查 Node.js 便携版
REM ====================================
echo [步骤 1/4] 检查 Node.js 运行时...
echo.

if exist "resources\node\node.exe" (
    for %%A in ("resources\node\node.exe") do set SIZE=%%~zA
    set /a SIZE_MB=!SIZE! / 1048576
    echo ✓ 找到便携版 Node.js (!SIZE_MB! MB)
) else (
    echo ✗ 未找到便携版 Node.js
    echo.
    echo ====================================
    echo   选项
    echo ====================================
    echo.
    echo A. 自动下载 Node.js 便携版 (推荐)
    echo B. 跳过 (使用系统 Node.js)
    echo C. 取消
    echo.
    choice /C ABC /N /M "请选择 [A/B/C]: "
    if errorlevel 3 (
        echo 已取消
        pause
        exit /b 1
    )
    if errorlevel 2 (
        echo 跳过 Node.js 下载，将使用系统安装的 Node.js
    ) else (
        echo.
        echo 正在下载 Node.js 便携版...
        python download_nodejs.py
        if errorlevel 1 (
            echo 下载失败，请手动下载或使用系统 Node.js
            pause
            exit /b 1
        )
    )
)

REM ====================================
REM Step 2: 检查依赖
REM ====================================
echo.
echo [步骤 2/4] 检查依赖...

pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 安装 PyInstaller...
    pip install pyinstaller
)

REM 激活虚拟环境
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM ====================================
REM Step 3: 准备 MCP 服务器
REM ====================================
echo.
echo [步骤 3/4] 准备 MCP 服务器...

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
REM Step 4: 打包
REM ====================================
echo.
echo [步骤 4/4] 开始打包...
echo.

REM 清理旧文件
if exist "build" rmdir /s /q build 2>nul
if exist "dist" rmdir /s /q dist 2>nul

REM 收集数据文件
set DATA_FILES=.venv/Lib/site-packages/playwright_stealth;playwright_stealth

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
    echo ✓ 已包含 Node.js 运行时
) else (
    echo ⚠ 未包含 Node.js 运行时，将使用系统 node
)

echo.
echo 数据文件: !DATA_FILES!
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

REM 创建应用包
mkdir dist\VC_PE_PitchBook_App 2>nul
copy /Y dist\VC_PE_PitchBook.exe dist\VC_PE_PitchBook_App\ >nul

echo [Launcher] > dist\VC_PE_PitchBook_App\启动应用.bat
echo start "" "VC_PE_PitchBook.exe" >> dist\VC_PE_PitchBook_App\启动应用.bat

REM 显示文件信息
echo 可执行文件: dist\VC_PE_PitchBook_App\VC_PE_PitchBook.exe
for %%A in ("dist\VC_PE_PitchBook_App\VC_PE_PitchBook.exe") do (
    set SIZE=%%~zA
    set /a SIZE_MB=!SIZE! / 1048576
)
echo 文件大小: !SIZE_MB! MB
echo.

if exist "resources\node\node.exe" (
    echo ✓ 已包含 Node.js 运行时，可离线使用 MCP 邮件功能
) else (
    echo ⚠ 未包含 Node.js 运行时，需要系统安装 Node.js 才能使用 MCP 邮件功能
)

echo.
echo ====================================
echo   使用说明
echo ====================================
echo.
echo 1. 首次运行时，程序会在用户文档目录创建数据文件夹：
echo    %%USERPROFILE%%\Documents\VC_PE_PitchBook\
echo.
echo 2. 如需使用 MCP 邮件功能，请在应用中配置邮箱信息。
echo.
echo 3. 应用包位置: dist\VC_PE_PitchBook_App\
echo.
pause
