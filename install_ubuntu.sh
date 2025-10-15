#!/bin/bash

# OverPilas Ubuntu Installation Script
# This script installs OverPilas system-wide for easy access

echo "🔋 Installing OverPilas for Ubuntu..."
echo "===================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    echo "   sudo ./install_ubuntu.sh"
    exit 1
fi

# Check if executable exists
if [ ! -f "dist/OverPilas" ]; then
    echo "❌ OverPilas executable not found!"
    echo "   Please run './build_ubuntu.sh' first to build the application."
    exit 1
fi

# Create installation directory
echo "📁 Creating installation directory..."
mkdir -p /opt/overpilas

# Copy executable and resources
echo "📋 Copying application files..."
cp dist/OverPilas /opt/overpilas/
cp -r templates /opt/overpilas/ 2>/dev/null || echo "   Templates already included in executable"
cp -r static /opt/overpilas/ 2>/dev/null || echo "   Static files already included in executable"

# Copy logo if it exists
if [ -f "static/logo.png" ]; then
    cp static/logo.png /opt/overpilas/
else
    echo "⚠️  Logo not found, creating placeholder..."
    # Create a simple placeholder icon
    touch /opt/overpilas/logo.png
fi

# Set proper permissions
echo "🔒 Setting permissions..."
chmod +x /opt/overpilas/OverPilas
chmod -R 755 /opt/overpilas/

# Create symbolic link for command line access
echo "🔗 Creating symbolic link..."
ln -sf /opt/overpilas/OverPilas /usr/local/bin/overpilas

# Install desktop entry
echo "🖥️  Installing desktop entry..."
cp overpilas.desktop /usr/share/applications/
chmod 644 /usr/share/applications/overpilas.desktop

# Update desktop database
if command -v update-desktop-database &> /dev/null; then
    echo "🔄 Updating desktop database..."
    update-desktop-database /usr/share/applications/
fi

# Create uninstall script
echo "🗑️  Creating uninstall script..."
cat > /opt/overpilas/uninstall.sh << 'EOF'
#!/bin/bash
echo "🗑️  Uninstalling OverPilas..."
rm -rf /opt/overpilas
rm -f /usr/local/bin/overpilas
rm -f /usr/share/applications/overpilas.desktop
update-desktop-database /usr/share/applications/ 2>/dev/null || true
echo "✅ OverPilas has been uninstalled."
EOF

chmod +x /opt/overpilas/uninstall.sh

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🎉 OverPilas is now installed and ready to use!"
echo ""
echo "How to use:"
echo "  • Double-click the OverPilas icon in the applications menu"
echo "  • Or run from terminal: overpilas"
echo "  • Or run directly: /opt/overpilas/OverPilas"
echo ""
echo "To uninstall:"
echo "  sudo /opt/overpilas/uninstall.sh"
echo ""
echo "📍 Installation location: /opt/overpilas/"
echo "🖥️  Desktop entry: /usr/share/applications/overpilas.desktop"