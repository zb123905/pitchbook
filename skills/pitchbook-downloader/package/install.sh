#!/usr/bin/env bash
set -euo pipefail

SKILL_NAME="pitchbook-report-downloader"
SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FORCE="${FORCE:-0}"

TARGETS=()
TARGETS+=("$HOME/.claude/skills/${SKILL_NAME}")
TARGETS+=("${CODEX_HOME:-$HOME/.codex}/skills/${SKILL_NAME}")
BIN_DIR="$HOME/.local/bin"

sync_to_target() {
  local target_dir="$1"
  local target_root
  target_root="$(dirname "$target_dir")"

  mkdir -p "${target_root}"

  if [[ -d "${target_dir}" ]]; then
    if [[ "${FORCE}" == "1" ]]; then
      rm -rf "${target_dir}"
      mkdir -p "${target_dir}"
    else
      echo "Target already exists: ${target_dir}"
      echo "Update in place (use FORCE=1 for clean reinstall)."
    fi
  else
    mkdir -p "${target_dir}"
  fi

  if command -v rsync >/dev/null 2>&1; then
    rsync -a --delete \
      --exclude ".git" \
      --exclude ".DS_Store" \
      --exclude "node_modules" \
      --exclude "downloads" \
      --exclude ".env" \
      "${SRC_DIR}/" "${target_dir}/"
  else
    cp -R "${SRC_DIR}/." "${target_dir}/"
    rm -rf "${target_dir}/.git" "${target_dir}/node_modules" "${target_dir}/downloads" || true
  fi

  chmod +x "${target_dir}/scripts/download_pitchbook_reports.mjs" || true
  chmod +x "${target_dir}/scripts/interactive_download.mjs" || true
  chmod +x "${target_dir}/scripts/retry_failed_from_run.mjs" || true
  chmod +x "${target_dir}/run.command" || true
  chmod +x "${target_dir}/bootstrap.sh" || true
  chmod +x "${target_dir}/install.sh" || true

  (
    cd "${target_dir}"
    npm install
    npm run install:browsers
  )

  if [[ ! -f "${target_dir}/.env" ]]; then
    cp "${target_dir}/references/.env.example" "${target_dir}/.env"
  fi

  return 0
}

echo "Installing skill: ${SKILL_NAME}"
echo "Source: ${SRC_DIR}"

OK_COUNT=0
for t in "${TARGETS[@]}"; do
  echo "Target: ${t}"
  if sync_to_target "${t}"; then
    OK_COUNT=$((OK_COUNT + 1))
  fi
done

if [[ "${OK_COUNT}" -eq 0 ]]; then
  echo "No targets updated."
  exit 1
fi

echo "Install complete (${OK_COUNT} target(s))."

mkdir -p "${BIN_DIR}"
cat > "${BIN_DIR}/pitchbook-report-download" <<'SH'
#!/usr/bin/env bash
set -euo pipefail
TARGET="$HOME/.claude/skills/pitchbook-report-downloader/run.command"
if [[ ! -x "$TARGET" ]]; then
  TARGET="${CODEX_HOME:-$HOME/.codex}/skills/pitchbook-report-downloader/run.command"
fi
exec "$TARGET" "$@"
SH
chmod +x "${BIN_DIR}/pitchbook-report-download"

echo "Try:"
echo "  ~/.claude/skills/${SKILL_NAME}/run.command"
echo "  pitchbook-report-download"
