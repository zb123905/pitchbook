# VC/PE PitchBook 自动化系统 - macOS 版本

> 基于 Python 的 VC/PE 行业信息自动化处理系统 - 图形化界面版本

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 系统要求

- macOS 10.15 (Catalina) 或更高版本
- Python 3.8 或更高版本
- 至少 500MB 可用磁盘空间
- 稳定的网络连接

## 快速开始

### 方式 1: 使用已打包的应用（推荐）

1. **下载应用**
   ```bash
   # 解压 VC_PE_PitchBook_App.zip
   unzip VC_PE_PitchBook_App.zip
   ```

2. **启动应用**
   ```bash
   cd VC_PE_PitchBook_App
   ./启动应用.command
   ```
   或直接双击 `VC_PE_PitchBook` 图标

3. **首次运行**
   - 如遇安全提示：右键点击 → 打开 → 仍要打开
   - 应用会自动创建必要的目录结构

### 方式 2: 从源码运行

```bash
# 克隆或下载项目
cd pitch

# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动 GUI
python gui_launcher.py
```

### 方式 3: 自行打包

```bash
# 安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 运行打包脚本
chmod +x build_macos.sh
./build_macos.sh

# 应用位置: dist/VC_PE_PitchBook_App/
```

## 功能说明

### 📊 四个功能面板

| 面板 | 功能 |
|------|------|
| **配置** | 设置邮箱、爬虫、分析参数 |
| **运行监控** | 实时查看 8 步处理流程 |
| **输出预览** | 查看生成的报告文件 |
| **日志查看** | 查看运行日志和错误信息 |

### 🔄 处理流程

```
1. 连接 MCP 邮件服务器
2. 读取 PitchBook 邮件
3. 提取邮件内容和链接
4. 自动下载报告
5. Web 爬取网页内容
6. 提取报告内容
7. 综合分析（支持 NLP/LLM）
8. 生成报告（Word/PDF）
```

## 配置说明

### 邮箱配置

```yaml
邮箱地址: your-email@example.com
密码: 邮箱密码或应用专用密码
日期范围: 7 天（建议 1-30 天）
最大邮件数: 50 封
```

### 爬虫配置

```yaml
爬取链接数: 0（全部）或指定数量
延迟范围: 5-12 秒（避免被封）
内容日期: 7 天内
```

### 分析配置

```yaml
NLP 实体识别: 启用
LLM 智能分析: 可选（需配置 API）
可视化图表: 启用
报告格式: Word 或 PDF
```

## 数据存储

```
~/Library/Application Support/VC_PE_PitchBook/
├── data/
│   ├── gui_config.json      # GUI 配置
│   └── logs/                # 日志文件
└── 数据储存/
    ├── 提取邮件/             # 邮件数据
    ├── 汇总总结/             # 分析报告
    ├── PDF报告/              # PDF 输出
    └── ai分析使用/           # AI 数据
```

## Playwright 浏览器

首次使用爬虫功能时，会自动下载 Chromium 浏览器：

```bash
# 手动安装（可选）
playwright install chromium
```

## LLM 智能分析（可选）

如需启用 LLM 增强分析，配置环境变量：

```bash
# 创建 .env 文件
LLM_ENABLED=true
DEEPSEEK_API_KEY=your_api_key
DEEPSEEK_BASE_URL=https://openrouter.fans/v1
```

## 故障排除

### 应用无法打开

```bash
# 问题：macOS 安全限制
# 解决：右键点击应用 → 打开 → 仍要打开

# 或在终端运行
xattr -cr VC_PE_PitchBook
```

### Playwright 浏览器下载失败

```bash
# 手动安装
source .venv/bin/activate
playwright install chromium
```

### 依赖安装失败

```bash
# 更新 pip
pip install --upgrade pip

# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 网页爬取失败

- 检查网络连接
- 某些网站需要登录（系统会自动跳过）
- 可增加延迟时间避免被拦截

## 快捷键

| 快捷键 | 功能 |
|--------|------|
| ⌘ + Q | 退出应用 |
| ⌘ + , | 打开配置（未实现） |
| ⌘ + L | 打开日志面板 |

## 与 Windows 版本的区别

| 特性 | Windows | macOS |
|------|---------|-------|
| 可执行文件 | .exe | 专用二进制 |
| 配置文件 | 不兼容 | 不兼容 |
| 文件路径 | `\` 分隔 | `/` 分隔 |
| 系统命令 | `os.startfile()` | `open` 命令 |

**注意**: 配置文件不能跨平台共用，需要在各平台单独配置。

## 技术支持

- 查看日志：`数据储存/logs/gui_system.log`
- GitHub Issues: [项目地址]
- 文档: `docs/` 目录

## 更新日志

### v1.0.0 (2026-03-20)
- ✅ 图形化界面
- ✅ 8 步自动化流程
- ✅ NLP 实体识别
- ✅ LLM 智能分析
- ✅ PDF/Word 报告生成
- ✅ Web 爬虫功能

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 致谢

- CustomTkinter - 现代化 GUI 框架
- Playwright - 网页自动化
- OpenAI/DeepSeek - LLM 分析

---

**开发**: VC/PE PitchBook Team
**版本**: 1.0.0
**平台**: macOS 10.15+
