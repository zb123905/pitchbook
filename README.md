# VC/PE 行业信息自动化系统

## 项目简介

本项目是一个基于 **Python + MCP (Model Context Protocol)** 架构的 VC/PE（风险投资/私募股权）行业信息自动化处理系统，能够自动从邮箱中提取 PitchBook 邮件，利用 Web 爬虫获取相关报告，并通过 AI 分析生成中文行业周报。

**核心特点**：
- 🔹 自动邮件获取（支持 QQ 邮箱 IMAP）
- 🔹 智能日期过滤（只处理最近 7 天内容）
- 🔹 反检测 Web 爬虫（Playwright + Stealth）
- 🔹 VC/PE 内容自动分析
- 🔹 自动生成 Word 周报

---

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 16+ （用于 MCP 邮件服务器）
- Windows / Linux / macOS

### 安装步骤

#### 1. 创建 Python 虚拟环境

```bash
python -m venv .venv

# 激活虚拟环境
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate
```

#### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

#### 3. 安装 Playwright 浏览器

```bash
playwright install chromium
```

#### 4. 配置邮箱（重要！）

编辑 `email_credentials.py`，配置您的 QQ 邮箱：

```python
IMAP_CONFIG = {
    'email_address': 'your-email@qq.com',  # 修改为您的邮箱
    'password': 'your-authorization-code',  # 修改为您的授权码
    'fetch_days': 7,           # 只读取最近 7 天的邮件
    'max_emails': 50,          # 最多读取 50 封邮件
    'max_scrape_links': 0,     # 0 = 爬取所有符合条件的链接
    'date_filter_days': 7,     # 只爬取最近 7 天发布的内容
}
```

**如何获取 QQ 邮箱授权码**：
1. 登录 https://mail.qq.com
2. 设置 → 账户 → 开启 IMAP 服务
3. 生成 16 位授权码（不是 QQ 密码！）

#### 5. 安装 Node.js 依赖

```bash
cd mcp-mail-master
npm install
cd ..
```

### 运行程序

```bash
# 方式 1：直接运行
python main.py

# 方式 2：使用启动脚本（Windows）
start.bat
```

---

## 项目结构

```
pitch/
├── main.py                      # 主程序入口
├── mcp_client.py               # MCP 邮件客户端
├── pitchbook_scraper.py        # 反检测爬虫
├── content_analyzer.py         # VC/PE 分析引擎
├── report_generator.py         # Word 报告生成器
├── email_processor.py          # 邮件处理器
├── email_credentials.py        # 配置文件 ⚠️ 需要修改
├── config.py                   # 路径配置
├── requirements.txt            # Python 依赖
├── start.bat                   # Windows 启动脚本
├── mcp-mail-master/            # MCP 邮件服务器
│   ├── dist/                   # 编译后的服务器
│   ├── src/                    # TypeScript 源代码
│   ├── package.json            # Node.js 依赖
│   └── .env                    # 环境配置 ⚠️ 需要创建
├── 数据储存/                   # 数据输出目录
│   ├── 提取邮件/               # 处理后的邮件数据
│   ├── 汇总总结/               # Word 周报
│   ├── ai分析使用/             # Markdown 文件
│   └── downloads/              # 下载的报告
└── 供人阅读使用/               # PDF 文件
```

---

## 核心功能

### 1. 智能邮件获取

- **技术**：MCP 协议 + IMAP
- **功能**：自动搜索、筛选、提取 PitchBook 邮件
- **特点**：支持大邮件分批获取，日期自动过滤

### 2. Web 反检测爬虫

- **技术**：Playwright + Stealth Mode
- **功能**：爬取 PitchBook 网页内容
- **特点**：
  - 随机 User-Agent 轮换
  - 真实浏览器行为模拟
  - 三层日期过滤机制
  - 智能错误处理和重试

### 3. VC/PE 内容分析

- **功能**：自动识别交易类型、提取关键主题
- **分类**：按行业、地区、交易阶段自动分类
- **输出**：市场情绪概览、趋势分析

### 4. 自动报告生成

- **格式**：Word 文档（.docx）
- **内容**：市场概览、关键主题、交易摘要
- **语言**：中文

---

## 配置说明

### 邮件日期范围

在 `email_credentials.py` 中配置：

```python
'fetch_days': 7,           # 只读取最近 N 天的邮件
'date_filter_days': 7,     # 只爬取最近 N 天发布的内容
```

### 爬取限制

```python
'max_scrape_links': 0,     # 0 = 爬取所有，>0 = 限制数量
'scrape_delay_min': 5,     # 最小延迟（秒）
'scrape_delay_max': 12,    # 最大延迟（秒）
```

---

## 输出文件

运行后会在以下目录生成文件：

| 目录 | 内容 |
|------|------|
| `数据储存/提取邮件/` | JSON 格式的邮件数据 |
| `数据储存/汇总总结/` | Word 周报（VC_PE_Weekly_YYYYMMDD.docx） |
| `数据储存/ai分析使用/` | Markdown 格式的网页内容 |
| `供人阅读使用/` | PDF 格式的网页内容 |
| `数据储存/downloads/` | 下载的报告文件 |

---

## 常见问题

### 1. ModuleNotFoundError

```bash
# 重新安装依赖
pip install -r requirements.txt
```

### 2. MCP 连接失败

- 检查 `mcp-mail-master/.env` 是否配置正确
- 确保 Node.js 依赖已安装：`cd mcp-mail-master && npm install`
- 确保 MCP 服务器编译成功：`dist/index.js` 存在

### 3. 邮箱连接失败

- 确认 QQ 邮箱已开启 IMAP 服务
- 确认使用的是**授权码**，不是 QQ 密码
- 检查网络连接

### 4. 爬虫失败

- 某些 PitchBook 链接可能已过期（邮件中的跟踪链接）
- 这是正常现象，系统会自动跳过失效链接
- 可以增加 `max_emails` 数量获取更多邮件

---

## 技术栈

| 类别 | 技术 |
|------|------|
| 编程语言 | Python 3.11+ |
| 邮件协议 | IMAP (QQ 邮箱) |
| 通信协议 | MCP (Model Context Protocol) |
| 服务器 | Node.js + TypeScript |
| 爬虫框架 | Playwright 1.58+ |
| 反检测 | playwright-stealth |
| 文档生成 | python-docx |
| 数据处理 | BeautifulSoup4, pandas |

---

## 创新点

1. **MCP 协议应用**：通过 Node.js 中间层统一处理邮件协议
2. **三层日期过滤**：确保只处理时效性内容
3. **反检测爬虫**：Stealth Mode + 真实行为模拟
4. **全量爬取**：可配置无限制爬取所有符合条件的内容
5. **完整闭环**：邮件 → 爬取 → 分析 → 报告生成

---

## 许可证

本项目仅用于学习和研究目的。

---

**最后更新**：2026-03-16
