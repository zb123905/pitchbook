# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller 配置文件 - macOS 版本
用于将 VC/PE PitchBook 系统打包成独立的 macOS 应用程序
"""

import os
import sys

block_cipher = None

# 项目根目录
project_root = os.path.dirname(os.path.abspath(SPEC))

# 数据文件
datas = []

# 添加 playwright_stealth
stealth_path = os.path.join('.venv', 'Lib', 'site-packages', 'playwright_stealth')
if os.path.exists(stealth_path):
    for root, dirs, files in os.walk(stealth_path):
        for file in files:
            src = os.path.join(root, file)
            rel_path = os.path.relpath(root, stealth_path)
            dst_dir = os.path.join('playwright_stealth', rel_path) if rel_path != '.' else 'playwright_stealth'
            datas.append((src, dst_dir))

# MCP 服务器文件
mcp_files = [
    ('mcp-mail-master/dist', 'mcp-mail-master/dist'),
    ('mcp-mail-master/node_modules', 'mcp-mail-master/node_modules'),
    ('mcp-mail-master/package.json', 'mcp-mail-master'),
    ('mcp-mail-master/.env.example', 'mcp-mail-master'),
]
for src, dst in mcp_files:
    if os.path.exists(src):
        datas.append((src, dst))

# Workaround: package.json 备份
package_json_src = 'mcp-mail-master/package.json'
package_json_bak = 'mcp-mail-master/mcp-package.json.bak'
if os.path.exists(package_json_src):
    import shutil
    shutil.copy(package_json_src, package_json_bak)
    datas.append((package_json_bak, 'mcp-mail-master'))

# Node.js 运行时 (macOS 使用系统 node 或打包的)
node_exe = os.path.join('resources', 'node', 'node')
if os.path.exists(node_exe):
    datas.append((node_exe, '.'))

# 隐藏导入
hidden_imports = [
    'customtkinter',
    'PIL',
    'tkinter',
    'queue',
    'threading',
    'asyncio',
    'bs4',
    'lxml',
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
    'playwright_stealth',
    'nlp.entity_extractor',
    'nlp.relation_extractor',
    'llm.deepseek_client',
    'llm.prompts',
    'llm.response_parser',
    'pdf.pdf_report_generator',
]

a = Analysis(
    ['gui_launcher.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['pyi_rth_restore_mcp_package.py'],
    excludes=['matplotlib', 'scipy', 'IPython'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VC_PE_PitchBook',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VC_PE_PitchBook',
)
