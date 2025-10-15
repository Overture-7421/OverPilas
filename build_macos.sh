#!/bin/bash

echo "🔋 Building OverPilas Executable for macOS..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed or not in PATH"
    echo "Please install Python 3 and try again"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed or not in PATH"
    exit 1
fi

echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "🏗️  Building executable with PyInstaller..."
pyinstaller OverPilas.spec --clean

if [ $? -ne 0 ]; then
    echo "❌ Failed to build executable"
    exit 1
fi

echo ""
echo "✅ Build completed successfully!"
echo "📁 Executable is located in: dist/OverPilas"
echo ""
echo "🚀 You can now copy the OverPilas executable to any macOS computer and run it!"
echo "   The executable includes all dependencies and files needed."
echo ""
echo "📝 To make it easier to run, you can:"
echo "   1. Right-click on OverPilas and select 'Make Alias'"
echo "   2. Drag the alias to your Desktop or Applications folder"
echo ""
read -p "Press Enter to continue..."