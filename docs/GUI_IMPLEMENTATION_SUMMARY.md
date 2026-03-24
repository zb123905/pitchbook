# VC/PE PitchBook 系统 - GUI 实施完成

## 概述

成功为 VC/PE PitchBook 自动化系统添加了基于 CustomTkinter 的图形化界面，替代命令行操作方式。

## 实施成果

### 新建文件 (15 个)

| 文件 | 行数 | 说明 |
|------|------|------|
| `gui/__init__.py` | 6 | GUI 包初始化 |
| `gui/main.py` | 33 | GUI 入口点 |
| `gui/main_window.py` | 264 | 主窗口类 |
| `gui/models/__init__.py` | 9 | 模型包初始化 |
| `gui/models/config_model.py` | 134 | 配置数据模型 |
| `gui/controllers/__init__.py` | 4 | 控制器包初始化 |
| `gui/controllers/pipeline_controller.py` | 135 | 流程控制器 |
| `gui/views/__init__.py` | 7 | 视图包初始化 |
| `gui/views/config_panel.py` | 307 | 配置面板 |
| `gui/views/progress_panel.py` | 301 | 进度面板 |
| `gui/views/output_panel.py` | 247 | 输出面板 |
| `gui/views/log_panel.py` | 243 | 日志面板 |
| `gui/workers/__init__.py` | 4 | 工作线程包初始化 |
| `gui/workers/pipeline_worker.py` | 499 | 后台工作线程 |
| `gui/utils/__init__.py` | 16 | 工具包初始化 |
| `gui/utils/thread_safe_notifier.py` | 113 | 线程安全通知 |

**总计**: ~2,322 行代码

### 修改的文件

| 文件 | 修改内容 |
|------|---------|
| `requirements.txt` | 添加 `customtkinter>=5.2.0` |
| `start_gui.bat` | 新建 GUI 启动脚本 |
| `gui_launcher.py` | 新建简化启动器 |

## 功能特性

### 1. 配置面板 (标签页 1)

**邮箱配置:**
- 邮箱地址输入
- 密码/授权码输入
- 日期范围设置 (1-30 天)
- 最大邮件数设置 (1-500)

**爬虫配置:**
- 最大链接数 (0=全部)
- 延迟范围设置
- 内容日期过滤

**分析配置:**
- NLP 实体识别开关
- LLM 智能分析开关
- 可视化图表开关
- 报告格式选择 (Word/PDF)

**功能:**
- 保存配置到文件
- 重置为默认值
- 配置验证反馈

### 2. 运行监控 (标签页 2)

**整体进度:**
- 总体进度条
- 百分比显示

**步骤状态 (8 步):**
1. 连接MCP服务器
2. 读取PitchBook邮件
3. 提取邮件内容和链接
4. 自动下载报告
5. Web爬取内容
6. 提取报告内容
7. 综合分析
8. 生成报告

**状态图标:**
- ⏳ 等待中
- 🔄 运行中
- ✅ 成功
- ❌ 失败
- ⏭️ 跳过

**实时统计:**
- 处理邮件数
- 提取链接数
- PitchBook 链接数
- 下载报告数
- 网页爬取数
- 内容分析数

**时间信息:**
- 已用时间
- 预计剩余时间

### 3. 输出预览 (标签页 3)

**文件列表:**
- 显示最新生成的文件
- 按修改时间排序
- 文件类型图标
- 文件大小和日期

**快捷操作:**
- 打开文件
- 打开目录

**快捷访问目录:**
- Word 报告目录
- PDF 报告目录
- 提取邮件目录
- Markdown 目录

### 4. 日志查看 (标签页 4)

**日志显示:**
- 实时日志滚动
- 彩色日志级别
- 时间戳显示

**日志过滤:**
- 全部 / INFO / WARNING / ERROR

**功能:**
- 自动滚动开关
- 清空日志
- 导出日志

## 架构设计

```
┌─────────────────────────────────────┐
│         MainWindow (主窗口)          │
│  ┌───────────────────────────────┐  │
│  │   TabView (4个标签页)          │  │
│  │  ┌─────────────────────────┐  │  │
│  │  │ ConfigPanel             │  │  │
│  │  │ ProgressPanel           │  │  │
│  │  │ OutputPanel             │  │  │
│  │  │ LogPanel                │  │  │
│  │  └─────────────────────────┘  │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │   PipelineController          │  │
│  └───────────────┬───────────────┘  │
└──────────────────┼───────────────────┘
                   │ Queue
┌──────────────────▼───────────────────┐
│   PipelineWorker (后台线程)          │
│  ┌───────────────────────────────┐  │
│  │  7步流程执行                  │  │
│  │  - MCP连接                    │  │
│  │  - 邮件读取                   │  │
│  │  - 链接提取                   │  │
│  │  - 报告下载                   │  │
│  │  - 网页爬取                   │  │
│  │  - 内容分析                   │  │
│  │  - 报告生成                   │  │
│  └───────────────────────────────┘  │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│  现有模块                           │
│  - MCPClient                        │
│  - EmailProcessor                   │
│  - VCPEContentAnalyzer              │
│  - WeeklyReportGenerator            │
│  - PitchBookScraper                 │
└─────────────────────────────────────┘
```

## 线程安全通信

使用 **Queue + after()** 模式:

```python
# 工作线程发送通知
self.notifier.notify('progress', (step, status, message))

# 主线程通过 after() 处理
def _on_progress(self, data):
    self.main_window.after(0, lambda: callback(data))
```

## 使用方法

### 方式 1: 启动脚本 (推荐)
```batch
start_gui.bat
```

### 方式 2: 直接运行
```bash
python gui_launcher.py
```

### 方式 3: 命令行 (保留)
```bash
python main.py
```

## 配置文件

配置保存在: `data/gui_config.json`

```json
{
  "email": {
    "email_address": "your@email.com",
    "password": "your-password",
    "fetch_days": 7,
    "max_emails": 50
  },
  "scraper": {
    "max_scrape_links": 0,
    "scrape_delay_min": 5,
    "scrape_delay_max": 12,
    "date_filter_days": 7
  },
  "analysis": {
    "enable_nlp": true,
    "enable_llm": false,
    "enable_charts": true,
    "generate_pdf": false,
    "report_format": "word"
  }
}
```

## 依赖安装

```bash
pip install customtkinter>=5.2.0
```

## 验证测试

### 导入测试
```bash
python -c "from gui.models import PipelineConfig; print('OK')"
```

### 配置模型测试
```bash
python -c "
from gui.models import PipelineConfig
config = PipelineConfig()
config.email.email_address = 'test@test.com'
config.email.password = 'test'
print('Valid:', config.is_valid())
"
```

## 主题支持

支持三种主题模式:
- System (跟随系统)
- Light (浅色)
- Dark (深色)

可通过界面右上角的选项菜单切换。

## 已知限制

1. GUI 运行时不能关闭窗口，会终止整个程序
2. 后台任务不支持暂停，只能停止
3. 日志文件加载时只显示最后 100 行
4. 文件列表最多显示 50 个文件

## 后续改进建议

1. 添加任务历史记录功能
2. 支持批量处理多个日期范围
3. 添加计划任务功能
4. 支持更多主题和自定义颜色
5. 添加数据统计图表
6. 支持配置导入/导出

## 技术要点

1. **线程安全**: 所有 UI 更新通过 `after()` 在主线程执行
2. **状态管理**: 使用 PipelineConfig 数据类统一管理配置
3. **错误处理**: 所有异常都通过日志和 UI 反馈给用户
4. **模块化**: GUI 与现有业务逻辑完全分离
5. **可扩展**: 标签页和面板可轻松添加新功能

---

**实施日期**: 2026-03-20
**版本**: 1.0.0
**状态**: ✅ 完成
