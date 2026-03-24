# QQ 邮箱 MCP 配置指南

本指南将帮助您配置 QQ 邮箱以使用 MCP 协议获取 PitchBook 邮件。

## 📋 前置要求

- ✅ QQ 邮箱账号
- ✅ Python 3.11+
- ✅ Node.js 18.x+
- ✅ 项目已克隆到本地

## 🔧 步骤 1：开启 QQ 邮箱 IMAP 服务

### 1.1 登录 QQ 邮箱网页版

访问：https://mail.qq.com

### 1.2 进入设置页面

点击右上角 **"设置"** → **"账户"**

### 1.3 开启 IMAP/SMTP 服务

找到 **"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"** 部分

1. 点击 **"开启 IMAP/SMTP 服务"**
2. 按照提示发送短信验证
3. 验证成功后会显示 **"已开启"**

## 🔑 步骤 2：获取 16 位授权码

### 2.1 生成授权码

在开启 IMAP/SMTP 服务的页面中：

1. 点击 **"生成授权码"**
2. 通过手机验证
3. 系统会生成一个 **16 位授权码**（例如：`glhziqkekwmpdfdc`）

### 2.2 保存授权码

⚠️ **重要**：
- 请将授权码保存在安全的地方
- 授权码只会显示一次，请妥善保管
- **不要**使用 QQ 密码，必须使用授权码

## ⚙️ 步骤 3：配置 MCP 服务器

### 3.1 编辑配置文件

打开项目中的 `mcp-mail-master/.env` 文件：

```bash
# Windows
notepad mcp-mail-master\.env

# Linux/Mac
nano mcp-mail-master/.env
```

### 3.2 填写配置信息

将以下内容复制到 `.env` 文件中，并替换为您的信息：

```env
# SMTP配置（发送邮件）
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=your_email@qq.com
SMTP_PASS=your_16_char_auth_code

# IMAP配置（接收邮件）
IMAP_HOST=imap.qq.com
IMAP_PORT=993
IMAP_SECURE=true
IMAP_USER=your_email@qq.com
IMAP_PASS=your_16_char_auth_code

# 其他配置
DEFAULT_FROM_NAME=Your Name
DEFAULT_FROM_EMAIL=your_email@qq.com
```

### 3.3 替换说明

| 配置项 | 说明 | 示例 |
|--------|------|------|
| `your_email@qq.com` | 您的 QQ 邮箱地址 | `3185709067@qq.com` |
| `your_16_char_auth_code` | 步骤 2 中获取的 16 位授权码 | `glhziqkekwmpdfdc` |
| `Your Name` | 发件人显示名称 | `张三` |

### 3.4 示例配置

```env
# SMTP配置（发送邮件）
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_SECURE=true
SMTP_USER=3185709067@qq.com
SMTP_PASS=glhziqkekwmpdfdc

# IMAP配置（接收邮件）
IMAP_HOST=imap.qq.com
IMAP_PORT=993
IMAP_SECURE=true
IMAP_USER=3185709067@qq.com
IMAP_PASS=glhziqkekwmpdfdc

# 其他配置
DEFAULT_FROM_NAME=kaka
DEFAULT_FROM_EMAIL=3185709067@qq.com
```

## 🔨 步骤 4：安装依赖并编译

### 4.1 安装 Node.js 依赖

```bash
cd mcp-mail-master
npm install
```

### 4.2 编译 TypeScript 代码

```bash
npm run build
```

✅ 成功后会在 `mcp-mail-master/dist/` 目录下生成 `index.js` 文件

## 🧪 步骤 5：测试连接

### 5.1 运行测试工具

```bash
python test_mcp_qq.py
```

### 5.2 检查测试结果

测试工具会执行以下检查：

1. ✅ **配置文件检查** - 验证 `.env` 文件存在且格式正确
2. ✅ **MCP 服务器连接** - 测试与 MCP 服务器的连接
3. ✅ **邮件搜索功能** - 测试搜索 PitchBook 邮件
4. ✅ **邮件详情获取** - 测试获取邮件详情

### 5.3 预期输出

如果配置正确，您会看到：

```
✅ 配置文件存在: mcp-mail-master/.env
✅ IMAP 服务器: imap.qq.com:993
✅ IMAP 用户: your_email@qq.com
✅ 授权码长度正确 (16 位)
✅ MCP 服务器连接成功
✅ 找到 X 封 PitchBook 邮件
```

## 🚀 步骤 6：运行主程序

### 6.1 使用启动脚本（推荐）

**Windows:**
```batch
start.bat
```

**PowerShell:**
```powershell
.\start.ps1
```

### 6.2 手动运行

```bash
# 激活虚拟环境
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# 运行主程序
python main.py
```

## ❓ 常见问题

### Q1: 授权码获取失败？

**A:** 请确保：
- QQ 邮箱已绑定手机号
- 已开启 IMAP/SMTP 服务
- 使用 QQ 邮箱网页版操作（非客户端）

### Q2: 连接 MCP 服务器失败？

**A:** 请检查：
- Node.js 是否已安装（运行 `node --version`）
- npm 依赖是否已安装（`cd mcp-mail-master && npm install`）
- TypeScript 是否已编译（`cd mcp-mail-master && npm run build`）

### Q3: 授权码长度不是 16 位？

**A:** QQ 邮箱授权码固定为 16 位，如果长度不对，请重新生成。

### Q4: 未找到 PitchBook 邮件？

**A:** 这不是错误！可能原因：
- 收件箱中确实没有 PitchBook 发送的邮件
- 可以先给自己发送一封测试邮件，主题包含 "PitchBook"

### Q5: 编译 TypeScript 时出错？

**A:** 请尝试：
```bash
cd mcp-mail-master
npm install -g typescript
npm run build
```

## 📞 获取帮助

如果遇到问题：

1. 查看测试工具的详细输出：`python test_mcp_qq.py`
2. 查看系统日志：`数据储存/logs/system.log`
3. 检查环境配置：`python check_env.py`

## 🔐 安全提示

- ⚠️ **不要**将 `.env` 文件提交到 Git 仓库
- ⚠️ **不要**在代码中硬编码授权码
- ✅ **建议**将 `.env` 添加到 `.gitignore` 文件
- ✅ **定期**更换授权码以保证安全

## 🎯 下一步

配置完成后：

1. 运行 `python test_mcp_qq.py` 验证配置
2. 运行 `python main.py` 开始使用系统
3. 查看生成的 Word 报告：`数据储存/第二次/`

---

**配置成功后，系统将自动：**
- ✅ 从 QQ 邮箱获取 PitchBook 邮件
- ✅ 提取邮件内容和链接
- ✅ 自动下载报告
- ✅ 分析内容并生成中文 Word 报告

祝使用愉快！🎉
