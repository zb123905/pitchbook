# 跨平台使用指南

## 支持的平台

| 平台 | 支持状态 | 打包文件 |
|------|----------|----------|
| Windows 10/11 | ✅ 完全支持 | `.exe` |
| macOS 10.15+ | ✅ 完全支持 | 专用二进制 |
| Linux | ✅ 完全支持 | 专用二进制 |

## macOS 使用

### 方式 1: 在 Mac 上打包（推荐）

1. **克隆项目到 Mac**
2. **安装依赖**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **运行打包脚本**
   ```bash
   ./build_macos.sh
   ```

4. **输出位置**: `dist/VC_PE_PitchBook_App/`

### 方式 2: 直接在 Mac 上运行源码

不需要打包，直接运行：
```bash
source .venv/bin/activate
python gui_launcher.py
```

## macOS 特殊说明

### 文件路径差异

代码已自动处理：
```python
# Windows: E:\pitch\数据储存\
# macOS: /Users/username/pitch/数据储存/
# 使用 os.path.join() 自动适配
```

### 系统命令差异

```python
# Windows: os.startfile(path)
# macOS: subprocess.run(['open', path])
# 代码已自动处理
```

### Playwright 浏览器

首次使用会自动下载 macOS 版本的浏览器：
```bash
playwright install chromium
```

## Linux 使用

类似 macOS：
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python gui_launcher.py
```

## 文件共享

**配置和数据文件不跨平台兼容！**

- Windows 配置不能直接在 macOS 使用
- 每个平台需要单独配置

建议只共享源代码，配置文件各自生成。

## 总结

| 需求 | 解决方案 |
|------|----------|
| Windows 用户 | 使用已打包的 `.exe` |
| Mac 用户 | 在 Mac 上运行 `build_macos.sh` |
| 源码共享 | 三个平台都可以直接运行 `python gui_launcher.py` |

---

**重要**: PyInstaller 打包的二进制文件是平台特定的，不能跨平台使用。
