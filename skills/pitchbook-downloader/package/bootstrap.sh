#!/bin/zsh
set -euo pipefail

cd "$(dirname "$0")"

echo "[1/4] Installing npm dependencies"
npm install

echo "[2/4] Installing Playwright Chromium"
npm run install:browsers

echo "[3/4] Preparing .env"
if [[ ! -f .env ]]; then
  cp references/.env.example .env
  echo "Created .env from template. Please edit: $(pwd)/.env"
else
  echo ".env already exists, keeping your values"
fi

echo "[4/4] Bootstrap complete"
echo "Run: ./run.command"
