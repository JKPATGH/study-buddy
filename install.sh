#!/usr/bin/env bash
# One-command installer for the study-buddy CLI app.
# Usage (local):  bash install.sh
# Usage (remote): curl -fsSL https://raw.githubusercontent.com/JKPATGH/study-buddy/main/install.sh | bash
set -euo pipefail

echo "Installing study-buddy..."

REPO_URL="https://github.com/JKPATGH/study-buddy.git"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" 2>/dev/null && pwd || true)"

if ! command -v brew >/dev/null 2>&1; then
  echo "Error: Homebrew is required. Install it from https://brew.sh first." >&2
  exit 1
fi

if ! command -v tesseract >/dev/null 2>&1; then
  echo "Installing tesseract (OCR engine)..."
  brew install tesseract
fi

if ! command -v pipx >/dev/null 2>&1; then
  echo "Installing pipx (Python app installer)..."
  brew install pipx
  pipx ensurepath
fi

echo "Installing study-buddy app..."
if [[ -n "$SCRIPT_DIR" && -f "$SCRIPT_DIR/pyproject.toml" ]]; then
  pipx install "$SCRIPT_DIR" --force
else
  pipx install "git+$REPO_URL" --force
fi

echo ""
echo "Done! Open a new terminal window and run: study-buddy <file> -n 5"
