#!/bin/bash

# OverPilas Ubuntu Distribution Package Creator
# This script creates a distributable package for Ubuntu users

echo "📦 Creating OverPilas Ubuntu distribution package..."
echo "================================================="

# Check if build exists
if [ ! -f "dist/OverPilas" ]; then
    echo "❌ No built executable found!"
    echo "   Please run './build_ubuntu.sh' first."
    exit 1
fi

# Create package directory
PACKAGE_NAME="OverPilas-Ubuntu-$(date +%Y%m%d)"
PACKAGE_DIR="packages/$PACKAGE_NAME"

echo "📁 Creating package directory: $PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"

# Copy executable
echo "📋 Copying executable..."
cp dist/OverPilas "$PACKAGE_DIR/"

# Copy installation files
echo "📋 Copying installation files..."
cp install_ubuntu.sh "$PACKAGE_DIR/"
cp overpilas.desktop "$PACKAGE_DIR/"

# Copy static assets if they exist separately
if [ -d "static" ]; then
    cp -r static "$PACKAGE_DIR/"
fi

# Copy templates if they exist separately
if [ -d "templates" ]; then
    cp -r templates "$PACKAGE_DIR/"
fi

# Create a simple launcher script for local execution
echo "🚀 Creating launcher script..."
cat > "$PACKAGE_DIR/run_overpilas.sh" << 'EOF'
#!/bin/bash
# OverPilas Local Launcher
# This script runs OverPilas without installing it system-wide

echo "🔋 Starting OverPilas..."

# Get the directory where this script is located
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to that directory
cd "$DIR"

# Make sure the executable is executable
chmod +x OverPilas

# Run the application
./OverPilas
EOF

chmod +x "$PACKAGE_DIR/run_overpilas.sh"

# Create README for the package
echo "📝 Creating package README..."
cat > "$PACKAGE_DIR/README.md" << 'EOF'
# OverPilas - Ubuntu Distribution Package

🔋 **OverPilas** is a battery management application for tracking and organizing battery usage.

## Quick Start

### Option 1: Run without installing (Recommended for testing)
```bash
chmod +x run_overpilas.sh
./run_overpilas.sh
```

### Option 2: Install system-wide
```bash
chmod +x install_ubuntu.sh
sudo ./install_ubuntu.sh
```

After system-wide installation, you can:
- Find OverPilas in your applications menu
- Run from terminal: `overpilas`
- Double-click the application icon

## System Requirements

- Ubuntu 18.04 or newer
- x64 architecture
- No additional dependencies required (all bundled)

## Features

- Battery charge tracking
- Battery resistance monitoring  
- Cooldown period management
- Web-based interface
- Automatic browser launch

## Usage

1. The application will start a local web server
2. Your default browser will open automatically
3. Use the web interface to manage your batteries
4. Close the terminal window to stop the application

## Uninstalling

If you installed system-wide:
```bash
sudo /opt/overpilas/uninstall.sh
```

## Troubleshooting

**Permission denied error:**
```bash
chmod +x OverPilas
chmod +x run_overpilas.sh
```

**Port already in use:**
- Make sure no other OverPilas instance is running
- Check if port 5000 is free: `lsof -i :5000`

**Browser doesn't open:**
- Manually open: http://127.0.0.1:5000

## Support

For issues or questions, please check the main repository documentation.
EOF

# Make all scripts executable
chmod +x "$PACKAGE_DIR"/*.sh

# Create compressed archive
echo "🗜️  Creating compressed archive..."
cd packages
tar -czf "$PACKAGE_NAME.tar.gz" "$PACKAGE_NAME"
cd ..

# Create file size info
ARCHIVE_SIZE=$(du -h "packages/$PACKAGE_NAME.tar.gz" | cut -f1)
FOLDER_SIZE=$(du -sh "$PACKAGE_DIR" | cut -f1)

echo ""
echo "✅ Distribution package created successfully!"
echo ""
echo "📦 Package: packages/$PACKAGE_NAME.tar.gz ($ARCHIVE_SIZE)"
echo "📁 Folder: $PACKAGE_DIR ($FOLDER_SIZE)"
echo ""
echo "🚀 Ready to distribute!"
echo ""
echo "Users can extract and run with:"
echo "  tar -xzf $PACKAGE_NAME.tar.gz"
echo "  cd $PACKAGE_NAME"
echo "  ./run_overpilas.sh"
echo ""
echo "Or install system-wide with:"
echo "  sudo ./install_ubuntu.sh"