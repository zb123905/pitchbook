# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VC/PE Industry Information Automation System - Automatically fetches PitchBook emails from Outlook, extracts content and links, analyzes them, and generates Word reports in Chinese.

## Quick Start (推荐)

### 一键启动 (Windows)
```batch
# 双击运行或在命令行中执行
start.bat

# 或使用 PowerShell
.\start.ps1
```

### 环境检查
```bash
# 检查环境和依赖
python check_env.py

# 测试 MCP 连接
python test_mcp_connection.py
```

### 手动运行 (开发模式)
```bash
# 激活虚拟环境
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# 运行主程序
python main.py
```

### 开发命令
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 创建虚拟环境
python -m venv .venv

# 测试 IMAP 连接 (备用)
python test_imap_login.py

# 测试环境变量
python test_env_variables.py
```

## Architecture

### MCP-Mode Email Fetching System

The system uses **MCP Mode** (recommended) for fetching emails:

1. **MCP Mode** (Primary): Uses `DirectMCPClient` in `mcp_client.py` - a simplified IMAP wrapper optimized for Outlook
2. **Legacy modes** (available but not recommended): IMAP mode and local file mode for fallback purposes

### Core Modules

- **`main.py`**: Entry point with mode selection and orchestration of the full pipeline
- **`imap_email_fetcher.py`**: `IMAPEmailFetcher` class - direct IMAP connection to Outlook (server: `outlook.office365.com:993`)
- **`mcp_client.py`**: Contains `MCPClient` (for Node.js MCP server) and `DirectMCPClient` (simplified IMAP wrapper)
- **`email_processor.py`**: `EmailProcessor` - processes and saves email data
- **`content_analyzer.py`**: `VCPEContentAnalyzer` - analyzes VC/PE industry content, extracts topics and metrics
- **`report_generator.py`**: `WeeklyReportGenerator` - generates Word reports using `python-docx`
- **`config.py`**: Centralized configuration for directory paths

### Data Flow

```
Email Source → Email Fetcher (MCP/IMAP/Local) → EmailProcessor → VCPEContentAnalyzer → WeeklyReportGenerator → Word Report
```

### Key Directories

- `data/emails/` - Local email files for fallback mode
- `data/reports/` - Analysis reports (JSON)
- `数据储存/提取邮件/` - Extracted email storage (user-specified)
- `数据储存/汇总总结/` - Summary reports (user-specified)
- `数据储存/第二次/` - Word reports (user-specified)
- `mcp-mail-master/` - Node.js MCP email server

## Configuration

### Email Credentials

Edit `email_credentials.py` to configure IMAP settings:

```python
IMAP_CONFIG = {
    'email_address': 'your-email@outlook.com',
    'password': 'your-password',
    'fetch_days': 7,
    'max_emails': 20
}
```

### Environment Variables (Optional)

The system supports `.env` file for credentials:
- `EMAIL_ADDRESS` - Outlook email address
- `EMAIL_PASSWORD` - Email password

### MCP Server Configuration

The MCP server in `mcp-mail-master/` requires:
- `.env` file with email credentials
- Built TypeScript code in `dist/` directory
- Configured in `C:\Users\HUAWEI\.claude\mcp.json` for Claude Code integration

## Important Notes

### IMAP Connection Details
- Server: `outlook.office365.com`
- Port: `993` (SSL)
- Uses direct email password (not app-specific password)

### Email Processing
- Searches for emails containing "PitchBook" in subject or sender
- Extracts links from both HTML and plain text content
- Handles multipart emails with attachments

### Content Analysis
The `VCPEContentAnalyzer` class:
- Classifies content types (deals, fundraising, market trends, etc.)
- Extracts key topics using keyword matching
- Categorizes by industry sectors, regions, deal stages
- Generates market sentiment overview

### Report Generation
The `WeeklyReportGenerator` class:
- Creates formatted Word documents with `python-docx`
- Includes market overview, key topics, deal summaries
- Outputs to user-specified directories in Chinese

### Startup Scripts
The project includes automated startup scripts for one-click execution:
- **`start.bat`** - Windows batch script for automated startup
- **`start.ps1`** - PowerShell script with enhanced error handling
- **`check_env.py`** - Environment validation and dependency checker
- **`test_mcp_connection.py`** - MCP connection testing script

### IDE Configuration
- **VS Code**: Configuration files in `.vscode/` for correct Python interpreter
- **`.python-version`**: Specifies Python 3.11
- **`.env.example`**: Template for environment variables

### Dependencies
- `requests` - HTTP requests
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML processing
- `pandas` - Data manipulation
- `openpyxl` - Excel file handling
- `python-dotenv` - Environment variable loading
- `python-docx` - Word document generation
- `PyPDF2` - PDF text extraction
- `pdfplumber` - Advanced PDF processing

### Troubleshooting
1. **ModuleNotFoundError**: Run `check_env.py` to verify dependencies
2. **Connection issues**: Run `test_mcp_connection.py` to test email connectivity
3. **Path issues**: Use `start.bat` to ensure correct Python interpreter
4. **Encoding issues**: Startup scripts automatically set UTF-8 encoding

### Language
Most user-facing content, reports, and documentation are in Chinese. Code comments and variable names are in English.
