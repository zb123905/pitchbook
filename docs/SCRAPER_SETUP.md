# PitchBook 网页爬虫系统设置指南

## 系统概述

本系统使用 **Playwright + Stealth Mode** 技术，能够绕过常见的反爬虫检测，从 PitchBook 网站自动获取文章内容，并保存为两种格式：

- **Markdown 格式** - 存储在 `数据储存/ai分析使用`，用于 AI 分析
- **PDF 格式** - 存储在 `供人阅读使用`，供人工阅读

## 核心特性

- ✅ Playwright Stealth 反检测技术
- ✅ 随机 User-Agent 轮换
- ✅ 真实浏览器行为模拟（滚动、延迟）
- ✅ 智能错误处理和重试机制
- ✅ 支持 403/429/CAPTCHA 处理
- ✅ 批量爬取能力
- ✅ 双格式输出（Markdown + PDF）

## 系统要求

### 必需软件

1. **Python 3.11+**
   ```bash
   python --version
   ```

2. **Node.js 18+** (用于 Playwright)
   ```bash
   node --version
   ```

3. **wkhtmltopdf** (用于 PDF 生成，可选)
   - Windows: https://wkhtmltopdf.org/downloads.html
   - 安装后添加到系统 PATH

### Python 依赖

所有依赖已添加到 `requirements.txt`：
```txt
playwright>=1.48.0
playwright-stealth>=1.0.6
markdownify>=0.11.6
pdfkit>=1.0.0
fake-useragent>=1.5.1
```

## 安装步骤

### 1. 安装 Python 依赖

```bash
# 激活虚拟环境
.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
python -m playwright install chromium
```

### 2. 验证安装

```bash
# 检查 Playwright
python -m playwright --version

# 检查 Chromium
python -m playwright install --dry-run chromium

# 检查 wkhtmltopdf (可选)
wkhtmltopdf --version
```

### 3. 创建必要的目录

系统会自动创建以下目录：
```
E:\pitch\数据储存\ai分析使用\    # Markdown 输出
E:\pitch\供人阅读使用\            # PDF 输出
E:\pitch\data\scraper_cache\      # 缓存目录
E:\pitch\data\logs\scraper\       # 日志目录
```

## 使用方法

### 方式 1：集成到主系统

爬虫已集成到 `main.py`，运行主程序会自动执行爬取：

```bash
python main.py
```

爬取步骤会在"步骤 4.5"自动执行，从邮件中提取的 PitchBook 链接会被爬取。

### 方式 2：独立使用爬虫

#### 单个 URL 爬取

```python
import asyncio
from pitchbook_scraper import scrape_single_url

async def main():
    url = "https://pitchbook.com/news/article-123"
    result = await scrape_single_url(url, headless=True)

    if result:
        print(f"标题: {result['title']}")
        print(f"作者: {result['author']}")
        print(f"字数: {result['word_count']}")

asyncio.run(main())
```

#### 批量 URL 爬取

```python
import asyncio
from pitchbook_scraper import scrape_multiple_urls

async def main():
    urls = [
        "https://pitchbook.com/news/article-1",
        "https://pitchbook.com/news/article-2",
        "https://pitchbook.com/news/article-3",
    ]

    results = await scrape_multiple_urls(urls, headless=True)

    for result in results:
        print(f"✅ {result['title'][:50]}...")

asyncio.run(main())
```

#### 使用转换器

```python
from markdown_converter import MarkdownConverter
from pdf_converter import PDFConverter

# 假设已有 scraped_data
md_converter = MarkdownConverter()
pdf_converter = PDFConverter()

# 转换为 Markdown
md_path = md_converter.convert(scraped_data)

# 转换为 PDF
pdf_path = pdf_converter.convert(scraped_data)

print(f"Markdown: {md_path}")
print(f"PDF: {pdf_path}")
```

## 测试

### 运行单元测试

```bash
# 测试爬虫
python test_pitchbook_scraper.py

# 测试 Markdown 转换器
python test_markdown_converter.py

# 测试 PDF 转换器
python test_pdf_converter.py
```

### 运行集成测试

```bash
python test_scraper_integration.py
```

## 配置选项

### 爬虫配置

在 `pitchbook_scraper.py` 中可以调整：

```python
# 视口尺寸（随机选择）
VIEWPORT_SIZES = [
    {'width': 1920, 'height': 1080},
    {'width': 1366, 'height': 768},
]

# 最大重试次数
scraper = PitchBookScraper(max_retries=3)

# 是否使用无头模式
scraper = PitchBookScraper(headless=True)
```

### 反爬虫策略

系统自动实施以下反爬虫措施：

1. **浏览器指纹混淆**
   - 随机 User-Agent
   - 随机视口尺寸
   - 禁用自动化标志

2. **行为模拟**
   - 随机延迟（3-7 秒）
   - 随机滚动
   - 真实鼠标移动

3. **错误处理**
   - 403: 切换 User-Agent
   - 429: 指数退避（60s → 120s → 240s）
   - CAPTCHA: 等待用户处理（2 分钟）

## 性能指标

- **爬取速度**: 8-12 秒/页面（包括延迟）
- **内存占用**: <500MB/浏览器实例
- **成功率目标**: >80%（首次尝试）

## 故障排除

### 问题 1: Playwright 浏览器未安装

**错误**: `Executable doesn't exist`

**解决方案**:
```bash
python -m playwright install chromium
```

### 问题 2: PDF 生成失败

**错误**: `OSError: No wkhtmltopdf executable found`

**解决方案**:
1. 下载并安装 wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
2. 添加到系统 PATH
3. 或跳过 PDF 生成（只使用 Markdown）

### 问题 3: 403 Forbidden 错误

**原因**: 被检测为机器人

**解决方案**:
1. 增加延迟时间（修改 `scrape_url` 中的 delay）
2. 减少并发数量
3. 考虑使用代理服务

### 问题 4: 429 Rate Limited

**原因**: 请求过于频繁

**解决方案**:
- 系统会自动进行指数退避
- 考虑增加请求间隔
- 限制同时爬取的 URL 数量

## 注意事项

### 法律合规

- ✅ 仅爬取公开可访问的内容
- ✅ 遵守 robots.txt（如有限制）
- ✅ 添加适当的来源标注
- ❌ 不要用于商业目的（除非获得授权）

### 使用建议

1. **首次使用**：每天测试 1-2 个 URL
2. **第二周**：如无问题，增加到每天 5 个 URL
3. **第三周**：增加到每天 10-15 个 URL
4. **第四周**：全量生产模式（每天 20-30 个 URL）

### 避免被封

- 🚫 不要短时间内大量请求
- 🚫 不要忽略错误响应继续请求
- ✅ 使用合理的延迟
- ✅ 监控成功率

## 系统架构

```
邮件 (MCP)
  ↓
提取链接
  ↓
Web 爬虫 (PitchBookScraper)
  ↓
内容提取
  ├→ Markdown 转换器 (MarkdownConverter)
  │   ↓
  │   Markdown 文件 (AI 分析使用)
  │
  └→ PDF 转换器 (PDFConverter)
      ↓
      PDF 文件 (人工阅读)
```

## 输出示例

### Markdown 文件格式

```markdown
# 文章标题

**Author:** John Doe
**Date:** 2024-03-15
**Tags:** VC, PE, Startup
**Word Count:** 1,234

---

[文章内容 Markdown]

---

*Scraped from: https://pitchbook.com/news/article-123*
*Scraped at: 2024-03-15T10:30:00*
```

### PDF 文件特性

- 专业的页面布局
- 元数据头部（标题、作者、日期、标签）
- 优化的字体和间距
- 页脚信息（来源 URL、爬取时间）

## 技术支持

如遇问题：

1. 查看日志文件：`data/logs/scraper/`
2. 运行测试脚本诊断：`test_scraper_integration.py`
3. 检查依赖安装：`python check_env.py`

## 更新日志

### v1.0.0 (2024-03-16)

- ✅ 初始版本发布
- ✅ Playwright + Stealth 反检测
- ✅ Markdown 和 PDF 双格式输出
- ✅ 集成到主系统
- ✅ 完整的测试套件
