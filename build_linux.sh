#!/bin/bash
set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=== OverPilas Linux Build ==="
echo "Project: $PROJECT_DIR"

# Create a clean venv
echo ">> Setting up venv..."
python3 -m venv .venv_linux
source .venv_linux/bin/activate

# Install only what's needed
echo ">> Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet flask==2.3.3 werkzeug==2.3.7 pyinstaller==6.1.0

# Build
echo ">> Running PyInstaller..."
pyinstaller \
    --onefile \
    --name OverPilas \
    --add-data "templates:templates" \
    --add-data "static:static" \
    app.py

deactivate

echo ""
echo "=== Done! ==="
echo "Binary: $PROJECT_DIR/dist/OverPilas"
echo ""
echo "To run on the target machine:"
echo "  chmod +x dist/OverPilas"
echo "  ./dist/OverPilas"
echo "  Then open browser: http://127.0.0.1:5000"
