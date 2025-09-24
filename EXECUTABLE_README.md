# OverPilas - Desktop Executable Guide

This guide explains how to create a single-click executable version of OverPilas that works on Windows and macOS without requiring Python installation.

## 🚀 Quick Start (For End Users)

If someone has already built the executable for you:

### Windows
1. Copy `OverPilas.exe` to your computer
2. Double-click `OverPilas.exe` to run
3. The app will automatically open in your browser at `http://127.0.0.1:5000`

### macOS
1. Copy the `OverPilas` executable to your computer
2. Double-click `OverPilas` to run
3. The app will automatically open in your browser at `http://127.0.0.1:5000`

## 🏗️ Building the Executable (For Developers)

### Prerequisites
- Python 3.7 or higher
- pip (Python package manager)

### Windows Build Instructions

1. **Open Command Prompt or PowerShell** in the project directory
2. **Run the build script:**
   ```batch
   build_windows.bat
   ```
   
   Or manually:
   ```batch
   pip install -r requirements.txt
   pyinstaller OverPilas.spec --clean
   ```

3. **Find your executable:** `dist\OverPilas.exe`

### macOS Build Instructions

1. **Open Terminal** in the project directory
2. **Make the script executable (first time only):**
   ```bash
   chmod +x build_macos.sh
   ```
3. **Run the build script:**
   ```bash
   ./build_macos.sh
   ```
   
   Or manually:
   ```bash
   pip3 install -r requirements.txt
   pyinstaller OverPilas.spec --clean
   ```

4. **Find your executable:** `dist/OverPilas`

## 📁 Files Explained

- **`launcher.py`** - Modified version of app.py that handles executable packaging
- **`OverPilas.spec`** - PyInstaller configuration file
- **`build_windows.bat`** - Windows build script
- **`build_macos.sh`** - macOS build script
- **`OverPilas_Launcher.bat`** - Optional Windows launcher for desktop shortcuts
- **`requirements.txt`** - Updated with PyInstaller dependencies

## 🖥️ Creating Desktop Shortcuts

### Windows
1. Right-click on `OverPilas.exe`
2. Select "Create shortcut"
3. Drag the shortcut to your Desktop
4. Optionally rename it to "OverPilas"

### macOS
1. Right-click on `OverPilas` executable
2. Select "Make Alias"
3. Drag the alias to your Desktop or Applications folder
4. Optionally rename it to "OverPilas"

## 📦 Distribution

The built executable is completely self-contained and includes:
- Python runtime
- All Python packages (Flask, etc.)
- Your application code
- Templates and static files
- Data files (pilas.json will be created in the same directory)

**For Windows:** Distribute the single `OverPilas.exe` file
**For macOS:** Distribute the single `OverPilas` executable file

## 🔧 Troubleshooting

### Build Issues
- **"Python not found"**: Install Python 3.7+ and ensure it's in your PATH
- **"pip not found"**: Install pip or use `python -m pip` instead
- **"PyInstaller failed"**: Try running `pip install --upgrade pyinstaller`

### Runtime Issues
- **Port already in use**: Make sure no other application is using port 5000
- **Browser doesn't open**: Manually navigate to `http://127.0.0.1:5000`
- **Files not found**: Ensure templates and static folders are in the same directory as the executable

### Antivirus Warnings
Some antivirus software may flag PyInstaller executables as suspicious. This is a false positive common with packaged Python applications. You may need to:
- Add an exception for the executable
- Temporarily disable real-time protection during build
- Use code signing certificates for distribution (advanced)

## 🔄 Updating the Application

To update the executable with new features:
1. Modify the source code as needed
2. Run the build script again
3. Replace the old executable with the new one

The `pilas.json` data file will be preserved between updates as long as it's in the same directory as the executable.

## 📝 Advanced Configuration

### Adding an Icon
1. Create or find an `.ico` file (Windows) or `.icns` file (macOS)
2. Update the `OverPilas.spec` file:
   ```python
   icon='path/to/your/icon.ico'  # Windows
   icon='path/to/your/icon.icns'  # macOS
   ```
3. Rebuild the executable

### Creating a Windowed Application (No Console)
To hide the console window on Windows, change in `OverPilas.spec`:
```python
console=False  # Instead of console=True
```

## 🌐 Network Access

The application runs locally on `127.0.0.1:5000` and is only accessible from the same computer. To allow access from other devices on the network, modify the launcher.py file to change the host from `'127.0.0.1'` to `'0.0.0.0'`, but be aware of security implications.

## 🛡️ Security Notes

- The executable includes your source code, but it's compiled/packaged
- Data is stored locally in `pilas.json`
- No external network connections are made
- The application only accepts local connections by default

---

**Need help?** Contact the development team or check the project repository for updates and support.