# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller 配置文件
用于将 VC/PE PitchBook 系统打包成独立的 Windows 应用程序
"""

import os
import sys

block_cipher = None

# 项目根目录
project_root = os.path.dirname(os.path.abspath(SPEC))

# 数据文件 - 收集所有需要的数据文件
datas = []

# 添加 playwright_stealth 的所有文件
stealth_path = os.path.join('.venv', 'Lib', 'site-packages', 'playwright_stealth')
if os.path.exists(stealth_path):
    for root, dirs, files in os.walk(stealth_path):
        for file in files:
            src = os.path.join(root, file)
            # 计算相对于 playwright_stealth 目录的路径
            rel_path = os.path.relpath(root, stealth_path)
            # 目标路径保持 playwright_stealth/js/... 结构
            dst_dir = os.path.join('playwright_stealth', rel_path) if rel_path != '.' else 'playwright_stealth'
            datas.append((src, dst_dir))

# MCP 服务器文件 (邮件获取核心组件)
mcp_files = [
    ('mcp-mail-master/dist', 'mcp-mail-master/dist'),
    ('mcp-mail-master/node_modules', 'mcp-mail-master/node_modules'),
    ('mcp-mail-master/package.json', 'mcp-mail-master'),
    ('mcp-mail-master/.env.example', 'mcp-mail-master'),
]
for src, dst in mcp_files:
    if os.path.exists(src):
        datas.append((src, dst))

# Workaround: PyInstaller 会过滤 package.json，创建备份副本
# 同时在 binaries 和 datas 中指定可确保文件被正确包含
package_json_src = 'mcp-mail-master/package.json'
package_json_bak = 'mcp-mail-master/mcp-package.json.bak'
if os.path.exists(package_json_src):
    import shutil
    shutil.copy(package_json_src, package_json_bak)
    datas.append((package_json_bak, 'mcp-mail-master'))

# Node.js 运行时 (MCP 服务器需要)
node_exe = os.path.join('resources', 'node', 'node.exe')
if os.path.exists(node_exe):
    datas.append((node_exe, '.'))

# 隐藏导入（PyInstaller 可能无法自动检测的模块）
hidden_imports = [
    'customtkinter',
    'PIL',
    'PIL._tkinter_finder',
    'tkinter',
    'queue',
    'threading',
    'asyncio',
    'bs4',
    'lxml',
    'lxml._elementpath',
    'pandas',
    'openpyxl',
    'openai',
    'dotenv',
    'docx',
    'PyPDF2',
    'pdfplumber',
    'markdownify',
    'fake_useragent',
    'playwright',
    'playwright.async_api',
    'playwright_stealth',
    'playwright_stealth.stealth',
    # NLP 模块
    'nlp.entity_extractor',
    'nlp.relation_extractor',
    # LLM 模块
    'llm.deepseek_client',
    'llm.prompts',
    'llm.response_parser',
    # PDF 报告模块
    'pdf.pdf_report_generator',
    # 可视化模块
    'visualization.charts',
]

# 强制包含 package.json (PyInstaller 可能会自动排除该文件)
binaries = [
    ('mcp-mail-master/package.json', 'mcp-mail-master'),
]

a = Analysis(
    ['gui_launcher.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_restore_mcp_package.py'],
    excludes=[
        # 排除不需要的模块以减小体积
        'matplotlib',
        'scipy',
        'IPython',
        'jupyter',
        'notebook',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='VC_PE_PitchBook',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # 不显示控制台窗口
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 可以添加 .ico 图标文件
)
