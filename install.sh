#!/usr/bin/env bash
# One-command installer for the study-buddy CLI app.
set -euo pipefail

echo "Installing study-buddy..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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
pipx install "$SCRIPT_DIR" --force

echo ""
echo "Done! Open a new terminal window and run: study-buddy <file> -n 5"
