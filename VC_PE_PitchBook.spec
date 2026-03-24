# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['gui_launcher.py'],
    pathex=[],
    binaries=[],
    datas=[('.venv/Lib/site-packages/playwright_stealth', 'playwright_stealth'), ('mcp-mail-master/dist', 'mcp-mail-master/dist'), ('mcp-mail-master/node_modules', 'mcp-mail-master/node_modules'), ('mcp-mail-master/package.json', 'mcp-mail-master'), ('resources/node/node.exe', '.')],
    hiddenimports=['customtkinter', 'PIL', 'playwright_stealth', 'playwright_stealth.stealth', 'path_utils'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='VC_PE_PitchBook',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
