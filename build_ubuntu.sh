#!/bin/bash

# OverPilas Ubuntu Build Script
# This script creates a standalone executable for Ubuntu Linux

echo "🔋 Building OverPilas for Ubuntu Linux..."
echo "======================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 is not installed. Please install Python3 first:"
    echo "   sudo apt update && sudo apt install python3 python3-pip"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first:"
    echo "   sudo apt install python3-pip"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Install additional Linux-specific dependencies
echo "🐧 Installing Linux-specific dependencies..."
pip install --upgrade pyinstaller

# Clean previous build
if [ -d "dist" ]; then
    echo "🧹 Cleaning previous build..."
    rm -rf dist
fi

if [ -d "build" ]; then
    rm -rf build
fi

# Build the executable
echo "🛠️  Building executable with PyInstaller..."
pyinstaller OverPilas_linux.spec

# Check if build was successful
if [ -f "dist/OverPilas" ]; then
    echo "✅ Build successful!"
    echo "📁 Executable created at: dist/OverPilas"
    
    # Make executable
    chmod +x dist/OverPilas
    
    echo "🎉 OverPilas Ubuntu executable is ready!"
    echo ""
    echo "To run the application:"
    echo "  ./dist/OverPilas"
    echo ""
    echo "To install system-wide, run:"
    echo "  sudo ./install_ubuntu.sh"
    
else
    echo "❌ Build failed! Check the output above for errors."
    exit 1
fi

# Deactivate virtual environment
deactivate

echo ""
echo "🏁 Build process completed!"