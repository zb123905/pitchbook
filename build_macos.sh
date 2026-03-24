#!/bin/bash

# ====================================
# VC/PE PitchBook - macOS 打包脚本
# ====================================

echo "===================================="
echo "  VC/PE PitchBook - macOS 打包"
echo "===================================="
echo ""

# 检查 PyInstaller
if ! pip show pyinstaller &> /dev/null; then
    echo "安装 PyInstaller..."
    pip install pyinstaller
fi

# 激活虚拟环境
if [ -f ".venv/bin/activate" ]; then
    echo "激活虚拟环境..."
    source .venv/bin/activate
fi

# 清理旧文件
echo "清理旧构建..."
rm -rf build dist

# 打包
echo "开始打包..."
echo ""

pyinstaller --onefile --windowed --name "VC_PE_PitchBook" \
    --hidden-import customtkinter \
    --hidden-import PIL \
    --hidden-import playwright_stealth \
    --hidden-import playwright_stealth.stealth \
    --add-data ".venv/Lib/site-packages/playwright_stealth:playwright_stealth" \
    gui_launcher.py

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
echo "可执行文件: dist/VC_PE_PitchBook"

# 创建应用包
echo "创建应用包..."
mkdir -p dist/VC_PE_PitchBook_App
cp dist/VC_PE_PitchBook dist/VC_PE_PitchBook_App/

# 创建启动脚本
cat > dist/VC_PE_PitchBook_App/启动应用.command << 'SCRIPT'
#!/bin/bash
cd "$(dirname "$0")"
./VC_PE_PitchBook
SCRIPT

chmod +x dist/VC_PE_PitchBook_App/启动应用.command

echo ""
echo "✅ 应用包已创建: dist/VC_PE_PitchBook_App/"
echo ""
echo "使用方法:"
echo "  双击 VC_PE_PitchBook 或 启动应用.command"
echo ""
