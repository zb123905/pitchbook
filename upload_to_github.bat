@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ═══════════════════════════════════════════════════════════
echo          VC/PE PitchBook - GitHub 自动构建
echo ═══════════════════════════════════════════════════════════
echo.

REM 检查 git
where git >nul 2>nul
if errorlevel 1 (
    echo ❌ 未找到 git，请先安装 Git
    echo 下载地址: https://git-scm.com/downloads
    pause
    exit /b 1
)

REM 输入信息
set /p GITHUB_USER="GitHub 用户名: "
set /p REPO_NAME="仓库名称 (默认: pitchbook): "
if "%REPO_NAME%"=="" set REPO_NAME=pitchbook

set /p VERSION="版本号 (默认: 1.0.0): "
if "%VERSION%"=="" set VERSION=1.0.0

echo.
echo 配置信息：
echo   用户名: %GITHUB_USER%
echo   仓库: %REPO_NAME%
echo   版本: v%VERSION%
echo.

REM 初始化 git
if not exist ".git" (
    echo 初始化 Git 仓库...
    git init
    git branch -M main
)

REM 添加文件
echo 添加文件到 Git...
git add .

REM 提交
echo 创建提交...
git commit -m "Release v%VERSION%" 2>nul
if errorlevel 1 (
    echo 没有新文件需要提交
)

REM 添加 remote
git remote get-url origin >nul 2>nul
if errorlevel 1 (
    set REPO_URL=https://github.com/%GITHUB_USER%/%REPO_NAME%.git
    echo 添加远程仓库: !REPO_URL!
    git remote add origin !REPO_URL!
)

REM 推送
echo.
echo 推送代码到 GitHub...
echo （可能需要输入 GitHub 用户名和密码/token）
echo.
git push -u origin main
if errorlevel 1 (
    git push
)

echo.
echo ═══════════════════════════════════════════════════════════
echo                     上传完成！
echo ═══════════════════════════════════════════════════════════
echo.
echo 下一步：
echo.
echo 1. 打开 GitHub 网页
echo    https://github.com/%GITHUB_USER%/%REPO_NAME%
echo.
echo 2. 点击「Releases」→「Create a new release」
echo.
echo 3. 填写：
echo    - Tag: v%VERSION%
echo    - Title: Release v%VERSION%
echo    - 点击「Publish release」
echo.
echo 4. 等待构建完成（约 10-15 分钟）
echo.
echo 5. 构建完成后，在 Releases 页面下载：
echo    ✅ VC_PE_PitchBook_Windows.zip
echo    ✅ VC_PE_PitchBook_macOS.zip
echo.
echo ═══════════════════════════════════════════════════════════

pause
