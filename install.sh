#!/usr/bin/env bash
# One-command installer for the Zero Study CLI + desktop app.
# Usage (local):  bash install.sh
# Usage (remote): curl -fsSL https://raw.githubusercontent.com/JKPATGH/zero-study/main/install.sh | bash
set -euo pipefail

echo "Installing Zero Study..."

REPO_URL="https://github.com/JKPATGH/zero-study.git"
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

echo "Installing Zero Study app..."
if [[ -n "$SCRIPT_DIR" && -f "$SCRIPT_DIR/pyproject.toml" ]]; then
  pipx install "$SCRIPT_DIR" --force
else
  pipx install "git+$REPO_URL" --force
fi

echo "Installing python-tk (needed for the desktop app window)..."
if ! "$(pipx environment --value PIPX_LOCAL_VENVS 2>/dev/null || echo "$HOME/Library/Application Support/pipx/venvs")/zero-study/bin/python3" -c "import tkinter" >/dev/null 2>&1; then
  brew install python-tk@3.14 2>/dev/null || brew install python-tk
fi

echo "Creating the Zero Study desktop app..."
VENV_BIN="$HOME/Library/Application Support/pipx/venvs/zero-study/bin"
APP_DIR="$HOME/Applications/Zero Study.app"
mkdir -p "$APP_DIR/Contents/MacOS" "$APP_DIR/Contents/Resources"

if [[ -n "$SCRIPT_DIR" && -f "$SCRIPT_DIR/study_buddy/icon.icns" ]]; then
  cp "$SCRIPT_DIR/study_buddy/icon.icns" "$APP_DIR/Contents/Resources/icon.icns"
else
  "$VENV_BIN/python3" - << 'ICONPY'
from study_buddy.make_icon import main
main()
ICONPY
  cp "$("$VENV_BIN/python3" -c "import study_buddy, os; print(os.path.join(os.path.dirname(study_buddy.__file__), 'icon.icns'))")" "$APP_DIR/Contents/Resources/icon.icns" 2>/dev/null || true
fi

cat > "$APP_DIR/Contents/Info.plist" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleName</key>
    <string>Zero Study</string>
    <key>CFBundleDisplayName</key>
    <string>Zero Study</string>
    <key>CFBundleIdentifier</key>
    <string>com.zerostudy.app</string>
    <key>CFBundleVersion</key>
    <string>0.1.0</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleExecutable</key>
    <string>ZeroStudyLauncher</string>
    <key>CFBundleIconFile</key>
    <string>icon.icns</string>
    <key>LSMinimumSystemVersion</key>
    <string>11.0</string>
    <key>NSHighResolutionCapable</key>
    <true/>
</dict>
</plist>
PLIST

cat > "$APP_DIR/Contents/MacOS/ZeroStudyLauncher" << LAUNCHER
#!/usr/bin/env bash
exec "$VENV_BIN/zero-study-gui"
LAUNCHER
chmod +x "$APP_DIR/Contents/MacOS/ZeroStudyLauncher"

echo ""
echo "Done!"
echo "- Terminal command: zero-study <file> -n 5"
echo "- Desktop app: open ~/Applications, double-click 'Zero Study'"
