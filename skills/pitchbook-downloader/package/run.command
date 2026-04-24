#!/bin/zsh
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SKILL_DIR"

echo "[1/6] Checking .env"
if [[ ! -f .env ]]; then
  cp references/.env.example .env
  cat <<'MSG'
已为你创建 .env 模板：
  ~/.claude/skills/pitchbook-report-downloader/.env
请先编辑真实信息后再运行本脚本。
MSG
  exit 1
fi

echo "[2/6] 加载资料"
set -a
source .env
set +a

required_vars=(PB_FIRST_NAME PB_LAST_NAME PB_EMAIL PB_COMPANY PB_TITLE)
for v in "${required_vars[@]}"; do
  if [[ -z "${(P)v:-}" ]]; then
    echo "缺少必填字段：$v（请检查 .env）"
    exit 1
  fi
done

# 防止把模板占位符直接提交到网站导致失败
if [[ "${PB_FIRST_NAME}" == "YourFirstName" || "${PB_LAST_NAME}" == "YourLastName" || "${PB_EMAIL}" == "your@email.com" || "${PB_COMPANY}" == "Your Company" || "${PB_TITLE}" == "Your Title" ]]; then
  echo "检测到你还在使用 .env 模板默认值，请先改成真实信息再重试。"
  exit 1
fi

if [[ "${PB_EMAIL}" == *"gmail.com" || "${PB_EMAIL}" == *"qq.com" || "${PB_EMAIL}" == *"outlook.com" || "${PB_EMAIL}" == *"hotmail.com" ]]; then
  echo "提示：PitchBook 通常要求企业邮箱，当前邮箱可能被拒绝：${PB_EMAIL}"
  echo "建议改为公司域名邮箱后再运行。"
fi

echo "[3/6] 检查 npm 依赖"
if [[ ! -d node_modules/playwright ]]; then
  npm install
fi

echo "[4/6] 检查 Playwright 浏览器"
if ! ls "$HOME/Library/Caches/ms-playwright"/chromium-* >/dev/null 2>&1; then
  npm run install:browsers
fi

echo "[5/6] 开始下载（交互模式）"
npm run interactive

echo "[6/6] 完成"
echo "输出目录：$HOME/Downloads/pitchbook-reports"
*** End Patch
#+#+#+#+assistant to=functions.exec_command մեկն_commentary 《凤凰大参考json
{"cmd":"sed -n '1,220p' /Users/a1111/.codex/skills/pitchbook-report-downloader/run.command"}}
 ыҟоуп.functions.exec_command.commentary  qq彩票
Command: /bin/zsh -lc "sed -n '1,220p' /Users/a1111/.codex/skills/pitchbook-report-downloader/run.command"
Chunk ID: c860eb
Wall time: 0.0000 seconds
Process exited with code 0
Original token count: 744
Output:
#!/bin/zsh
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "$0")" && pwd)"

cd "$SKILL_DIR"

echo "[1/6] 检查 .env"
if [[ ! -f .env ]]; then
  cp references/.env.example .env
  cat <<'MSG'
已创建 .env 模板：
  ~/.claude/skills/pitchbook-report-downloader/.env
请先改成你的真实信息，再重新运行。
MSG
  exit 1
fi

echo "[2/6] 加载资料"
set -a
source .env
set +a

required_vars=(PB_FIRST_NAME PB_LAST_NAME PB_EMAIL PB_COMPANY PB_TITLE)
for v in "${required_vars[@]}"; do
  if [[ -z "${(P)v:-}" ]]; then
    echo "缺少必填字段：$v（请检查 .env）"
    exit 1
  fi
done

if [[ "${PB_FIRST_NAME}" == "YourFirstName" || "${PB_LAST_NAME}" == "YourLastName" || "${PB_EMAIL}" == "your@email.com" || "${PB_COMPANY}" == "Your Company" || "${PB_TITLE}" == "Your Title" ]]; then
  echo "检测到你还在使用 .env 模板默认值，请先改成真实信息。"
  exit 1
fi

if [[ "${PB_EMAIL}" == *"gmail.com" || "${PB_EMAIL}" == *"qq.com" || "${PB_EMAIL}" == *"outlook.com" || "${PB_EMAIL}" == *"hotmail.com" ]]; then
  echo "提示：PitchBook 常要求企业邮箱，当前邮箱可能被拒绝：${PB_EMAIL}"
fi

echo "[3/6] 检查 npm 依赖"
if [[ ! -d node_modules/playwright ]]; then
  npm install
fi

echo "[4/6] 检查 Playwright 浏览器"
if ! ls "$HOME/Library/Caches/ms-playwright"/chromium-* >/dev/null 2>&1; then
  npm run install:browsers
fi

echo "[5/6] 开始下载（交互模式）"
npm run interactive

echo "[6/6] 完成"
echo "输出目录：$SKILL_DIR/downloads/pitchbook-reports"
