#!/bin/bash

# ====================================
# 一键上传到 GitHub 并自动构建
# ====================================

set -e

echo "═══════════════════════════════════════════════════════════"
echo "         VC/PE PitchBook - GitHub 自动构建"
echo "═══════════════════════════════════════════════════════════"
echo ""

# 检查 git
if ! command -v git &> /dev/null; then
    echo "❌ 未找到 git，请先安装 Git"
    exit 1
fi

# 询问 GitHub 仓库信息
read -p "GitHub 用户名: " GITHUB_USER
read -p "仓库名称 (默认: pitchbook): " REPO_NAME
REPO_NAME=${REPO_NAME:-pitchbook}

read -p "版本号 (默认: 1.0.0): " VERSION
VERSION=${VERSION:-1.0.0}

echo ""
echo "配置信息："
echo "  用户名: $GITHUB_USER"
echo "  仓库: $REPO_NAME"
echo "  版本: v$VERSION"
echo ""

# 初始化 git（如果还没有）
if [ ! -d ".git" ]; then
    echo "初始化 Git 仓库..."
    git init
    git branch -M main
fi

# 添加所有文件
echo "添加文件到 Git..."
git add .

# 提交
echo "创建提交..."
git commit -m "Release v$VERSION" || echo "没有新文件需要提交"

# 添加 remote（如果还没有）
if ! git remote get-url origin &> /dev/null; then
    REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"
    echo "添加远程仓库: $REPO_URL"
    git remote add origin "$REPO_URL"
fi

# 推送到 GitHub
echo ""
echo "推送代码到 GitHub..."
echo "（可能需要输入 GitHub 用户名和密码/token）"
git push -u origin main || git push

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "                    上传完成！"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "下一步："
echo ""
echo "1. 打开 GitHub 网页"
echo "   https://github.com/$GITHUB_USER/$REPO_NAME"
echo ""
echo "2. 点击「Releases」→「Create a new release」"
echo ""
echo "3. 填写："
echo "   - Tag: v$VERSION"
echo "   - Title: Release v$VERSION"
echo "   - 点击「Publish release」"
echo ""
echo "4. 等待构建完成（约 10-15 分钟）"
echo ""
echo "5. 构建完成后，在 Releases 页面下载："
echo "   ✅ VC_PE_PitchBook_Windows.zip"
echo "   ✅ VC_PE_PitchBook_macOS.zip"
echo ""
echo "═══════════════════════════════════════════════════════════"
