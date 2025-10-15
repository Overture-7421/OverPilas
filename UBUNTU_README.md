# OverPilas - Ubuntu Executable Guide

🔋 **OverPilas** is a battery management application that helps you track battery charges, resistance, and cooldown periods through an intuitive web interface.

## 🚀 Quick Setup for Ubuntu

### Prerequisites
- Ubuntu 18.04 or newer
- x64 architecture
- Internet connection (for initial setup only)

### Step 1: Download and Extract
```bash
# Download the latest Ubuntu package
# Extract the package
tar -xzf OverPilas-Ubuntu-*.tar.gz
cd OverPilas-Ubuntu-*
```

### Step 2: Choose Installation Method

#### Option A: Quick Run (No Installation Required)
```bash
# Make scripts executable
chmod +x run_overpilas.sh

# Run the application
./run_overpilas.sh
```

#### Option B: System-Wide Installation (Recommended)
```bash
# Make installation script executable
chmod +x install_ubuntu.sh

# Install system-wide (requires admin password)
sudo ./install_ubuntu.sh
```

## 🔧 Building from Source (Advanced Users)

If you have the source code and want to build the executable yourself:

### Prerequisites
```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Optional: Install development tools
sudo apt install build-essential
```

### Build Process
```bash
# Make build script executable
chmod +x build_ubuntu.sh

# Run the build process
./build_ubuntu.sh

# Create distribution package
chmod +x create_ubuntu_package.sh
./create_ubuntu_package.sh
```

## 📱 Using OverPilas

### Starting the Application

**After System Installation:**
- Find "OverPilas" in your applications menu (Activities → OverPilas)
- Or run from terminal: `overpilas`
- Or run directly: `/opt/overpilas/OverPilas`

**Without Installation:**
- Run `./run_overpilas.sh` from the extracted folder

### Using the Interface

1. **Automatic Browser Launch**: The application automatically opens your default browser
2. **Manual Access**: If browser doesn't open, go to `http://127.0.0.1:5000`
3. **Adding Battery Data**: Use the form to input battery name, charge, and resistance
4. **Managing Batteries**: Mark batteries as "in use" or "received" to track their status
5. **Cooldown Tracking**: Batteries automatically enter 30-minute cooldown after being received

### Features

- **Battery Tracking**: Monitor charge levels and internal resistance
- **Smart Sorting**: Batteries sorted by charge (highest first) and resistance (lowest first)
- **Cooldown Management**: Automatic 30-minute cooldown period tracking
- **Usage Status**: Track which batteries are currently in use
- **Data Persistence**: All data saved automatically in `pilas.json`
- **Reset Function**: Clear all data when needed

## 🛠️ Troubleshooting

### Common Issues

**"Permission denied" Error:**
```bash
chmod +x OverPilas
chmod +x run_overpilas.sh
chmod +x install_ubuntu.sh
```

**"Port 5000 already in use" Error:**
```bash
# Check what's using port 5000
sudo lsof -i :5000

# Kill any existing OverPilas processes
pkill -f OverPilas
```

**Browser Doesn't Open Automatically:**
- Manually open your browser and go to: `http://127.0.0.1:5000`
- Check if you have a default browser set

**Application Won't Start:**
```bash
# Check if executable has proper permissions
ls -la OverPilas

# Try running with verbose output
./OverPilas --help
```

**"No such file or directory" Error:**
- Make sure you're in the correct directory
- Verify the executable exists: `ls -la OverPilas`
- Check if you're on a compatible system: `uname -m` (should show x86_64)

### System Compatibility

**Supported Ubuntu Versions:**
- Ubuntu 20.04 LTS ✅
- Ubuntu 22.04 LTS ✅
- Ubuntu 18.04 LTS ✅ (may require additional dependencies)

**Architecture Requirements:**
- x64/x86_64 only
- ARM-based systems not supported in this build

## 🗑️ Uninstalling

### If Installed System-Wide:
```bash
sudo /opt/overpilas/uninstall.sh
```

### If Running Locally:
Simply delete the extracted folder:
```bash
rm -rf OverPilas-Ubuntu-*
```

## 🔒 Security Notes

- The application runs a local web server on `127.0.0.1:5000`
- No network access required after initial setup
- Data is stored locally in `pilas.json`
- No external connections or data transmission

## 📋 File Structure

```
OverPilas-Ubuntu-YYYYMMDD/
├── OverPilas                 # Main executable
├── run_overpilas.sh         # Local launcher script
├── install_ubuntu.sh        # System installation script
├── overpilas.desktop        # Desktop entry file
├── static/                  # Web assets (if separate)
├── templates/               # HTML templates (if separate)
└── README.md               # This documentation
```

## 🔄 Updates

To update OverPilas:
1. Download the latest package
2. Uninstall the current version (if installed system-wide)
3. Install the new version

## 📞 Support

If you encounter issues:
1. Check this troubleshooting guide
2. Verify system compatibility
3. Try running from terminal to see error messages
4. Check the main repository for known issues

## 🎯 Pro Tips

- **Multiple Instances**: Don't run multiple instances simultaneously
- **Data Backup**: Back up your `pilas.json` file to preserve battery data
- **Performance**: Close unused browser tabs for better performance
- **Automation**: Add to startup applications for automatic launching

---

*This executable package contains all necessary dependencies and should work on most Ubuntu systems without additional installations.*