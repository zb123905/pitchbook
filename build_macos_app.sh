#!/bin/bash

# ====================================
# VC/PE PitchBook - macOS 完整打包脚本
# ====================================

set -e

echo "===================================="
echo "  VC/PE PitchBook - macOS 打包"
echo "===================================="
echo ""

# 检查系统
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ 此脚本只能在 macOS 上运行"
    echo "   Windows 用户请运行 build_app.bat"
    exit 1
fi

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 Python3，请先安装 Python"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "创建虚拟环境..."
    python3 -m venv .venv
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 安装依赖
echo "检查依赖..."
pip install -q pyinstaller customtkinter pillow requests beautifulsoup4 lxml pandas openpyxl python-docx PyPDF2 pdfplumber markdownify fake-useragent
pip install -q playwright playwright-stealth
pip install -q openai python-dotenv

# 安装 Playwright 浏览器
playwright install chromium

# 清理旧文件
echo "清理旧构建..."
rm -rf build dist

# 创建 package.json 备份
echo "准备 MCP 服务器文件..."
if [ -f "mcp-mail-master/package.json" ]; then
    cp mcp-mail-master/package.json mcp-mail-master/mcp-package.json.bak
fi

# 打包
echo "开始打包..."
echo ""

pyinstaller build_macos.spec

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 打包失败！"
    exit 1
fi

echo ""
echo "===================================="
echo "  ✅ 打包完成！"
echo "===================================="
echo ""

# 创建发布包
echo "创建发布包..."
RELEASE_DIR="dist/release_macos"
APP_DIR="dist/VC_PE_PitchBook"

rm -rf "$RELEASE_DIR"
mkdir -p "$RELEASE_DIR"

# 复制应用
cp -R "$APP_DIR" "$RELEASE_DIR/"

# 创建数据目录
mkdir -p "$RELEASE_DIR/数据储存"

# 创建启动脚本
cat > "$RELEASE_DIR/启动应用.command" << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
./VC_PE_PitchBook/VC_PE_PitchBook
SCRIPT

chmod +x "$RELEASE_DIR/启动应用.command"

# 创建使用说明
cat > "$RELEASE_DIR/使用说明.txt" << 'EOF'
═══════════════════════════════════════════════════════════
         VC/PE PitchBook 行业信息自动化系统
                    macOS 版本 v1.0
═══════════════════════════════════════════════════════════

【快速开始】
1. 双击运行：启动应用.command
   或者在终端中运行：./VC_PE_PitchBook/VC_PE_PitchBook
2. 首次运行会自动创建数据储存目录
3. 在界面中配置邮箱信息后点击开始

【系统要求】
- macOS 10.15 (Catalina) 或更高版本
- 无需安装 Python 或其他依赖

【首次运行提示】
如果看到"无法打开因为来自身份不明开发者"：
1. 右键点击应用 -> 打开
2. 或者在系统偏好设置 -> 安全性与性中允许

【输出目录】
程序会在当前目录创建以下文件夹：
  - 数据储存/供人阅读使用/汇总总结/  (分析报告)
  - 数据储存/供人阅读使用/提取邮件/  (提取的邮件)
  - 数据储存/供人阅读使用/PDF报告/    (PDF报告)
  - 数据储存/ai分析使用/              (AI分析数据)
  - VC_PE_PitchBook/data/              (日志和缓存)

【常见问题】
Q: 提示 MCP 连接失败？
A: 检查网络连接，确保能访问邮箱服务器

Q: 找不到邮件？
A: 检查邮箱收件箱是否有 PitchBook 邮件

Q: 报告生成失败？
A: 确保有足够的磁盘空间

【技术支持】
如遇问题请检查：VC_PE_PitchBook/data/logs/ 目录下的日志文件

═══════════════════════════════════════════════════════════
EOF

# 创建 .zip 压缩包
cd dist
zip -r -q "VC_PE_PitchBook_macOS.zip" "release_macos"
cd ..

echo ""
echo "===================================="
echo "  📦 发布包已创建"
echo "===================================="
echo ""
echo "位置：dist/release_macos/"
echo "压缩包：dist/VC_PE_PitchBook_macOS.zip"
echo ""
echo "文件内容："
ls -lh "$RELEASE_DIR"
echo ""
echo "使用方法："
echo "  1. 解压 VC_PE_PitchBook_macOS.zip"
echo "  2. 双击 启动应用.command"
echo ""
