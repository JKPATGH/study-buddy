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

echo "Installing python-tk (needed for the desktop app window)..."
if ! "$(pipx environment --value PIPX_LOCAL_VENVS 2>/dev/null || echo "$HOME/Library/Application Support/pipx/venvs")/study-buddy/bin/python3" -c "import tkinter" >/dev/null 2>&1; then
  brew install python-tk@3.14 2>/dev/null || brew install python-tk
fi

echo "Creating the Study Buddy desktop app..."
VENV_BIN="$HOME/Library/Application Support/pipx/venvs/study-buddy/bin"
APP_DIR="$HOME/Applications/Study Buddy.app"
mkdir -p "$APP_DIR/Contents/MacOS"

cat > "$APP_DIR/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Study Buddy</string>
    <key>CFBundleDisplayName</key>
    <string>Study Buddy</string>
    <key>CFBundleIdentifier</key>
    <string>com.studybuddy.app</string>
    <key>CFBundleVersion</key>
    <string>0.1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleExecutable</key>
    <string>StudyBuddyLauncher</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

cat > "$APP_DIR/Contents/MacOS/StudyBuddyLauncher" << LAUNCHER
#!/usr/bin/env bash
exec "$VENV_BIN/study-buddy-gui"
LAUNCHER
chmod +x "$APP_DIR/Contents/MacOS/StudyBuddyLauncher"

echo ""
echo "Done!"
echo "- Terminal command: study-buddy <file> -n 5"
echo "- Desktop app: open ~/Applications, double-click 'Study Buddy'"
