"""
PyInstaller Runtime Hook: Restore MCP package.json

PyInstaller filters out package.json files. This hook copies the backup
(mcp-package.json.bak) to package.json in _MEIPASS at runtime.

The Node.js server will run from _MEIPASS where node_modules exists.
"""

import os
import sys
import shutil

def restore_mcp_package_json():
    """
    Restore mcp-package.json.bak to package.json in _MEIPASS

    _MEIPASS is writable during runtime (temp extraction directory).
    Node.js will run from here where node_modules exists.
    """
    if not (getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')):
        return

    meipass_dir = sys._MEIPASS
    mcp_dir = os.path.join(meipass_dir, 'mcp-mail-master')

    # Source and destination both in _MEIPASS
    backup_file = os.path.join(mcp_dir, 'mcp-package.json.bak')
    target_file = os.path.join(mcp_dir, 'package.json')

    if not os.path.exists(backup_file):
        return

    try:
        # Only copy if target doesn't exist
        if not os.path.exists(target_file):
            shutil.copy(backup_file, target_file)
            print(f"[MCP Hook] Restored package.json to {target_file}")
    except Exception as e:
        print(f"[MCP Hook] Warning: {e}")

# Execute on import
restore_mcp_package_json()
