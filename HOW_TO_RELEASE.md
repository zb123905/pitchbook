# 如何分发给 Mac 用户

## 方法一：使用 GitHub Actions（推荐，最简单）

### 步骤：

1. **上传代码到 GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/你的用户名/pitchbook.git
   git push -u origin main
   ```

2. **创建 Release 并自动构建**

   在 GitHub 网页上操作：
   - 进入你的仓库
   - 点击 "Releases" → "Draft a new release"
   - 标签版本：`v1.0.0`
   - 点击 "Publish release"

   构建完成后（约10分钟），Release 页面会有两个下载链接：
   - `VC_PE_PitchBook_Windows.zip` - Windows 版
   - `VC_PE_PitchBook_macOS.zip` - macOS 版

3. **发送链接给 Mac 用户**
   ```
   https://github.com/你的用户名/pitchbook/releases/download/v1.0.0/VC_PE_PitchBook_macOS.zip
   ```

---

## 方法二：手动触发构建

在 GitHub 网页上：
1. 进入 "Actions" 标签页
2. 选择 "Build VC_PE_PitchBook"
3. 点击 "Run workflow"
4. 输入版本号，点击运行
5. 构建完成后在 "Artifacts" 下载

---

## 方法三：给 Mac 用户源代码

如果用户懂一点技术，可以给ta：

```
pitchbook/
├── build_macos_app.sh          # 构建脚本
├── README_MACOS.md              # Mac 构建说明
└── (其他项目文件)
```

用户在 Mac 终端运行：
```bash
cd pitchbook
bash build_macos_app.sh
```

---

## 当前可发送的文件

### Windows 用户（立即可用）
```
E:\pitch\dist\VC_PE_PitchBook_Windows.zip
(140MB，解压即用)
```

### Mac 用户（选择以下方式）

1. **最推荐**：上传 GitHub，让ta下载 Release
2. **备选**：发送整个项目文件夹，ta在 Mac 上运行构建脚本

---

## 快速对比

| 方法 | 需要什么 | 适合谁 |
|------|----------|--------|
| GitHub Actions | GitHub 账号 | 所有人，最简单 |
| 手动构建 | Mac 电脑 | 懂技术的用户 |
| 发送源码 | Mac 电脑 + 技术能力 | 开发者 |

**推荐：使用 GitHub Actions，一次构建，两个平台的用户都能下载。**
