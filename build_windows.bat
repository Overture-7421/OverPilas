@echo off
echo 🔋 Building OverPilas Executable for Windows...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

REM Check if pip is available
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip is not installed or not in PATH
    pause
    exit /b 1
)

echo 📦 Installing dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo 🏗️  Building executable with PyInstaller...
pyinstaller OverPilas.spec --clean

if errorlevel 1 (
    echo ❌ Failed to build executable
    pause
    exit /b 1
)

echo.
echo ✅ Build completed successfully!
echo 📁 Executable is located in: dist\OverPilas.exe
echo.
echo 🚀 You can now copy OverPilas.exe to any Windows computer and run it!
echo    The executable includes all dependencies and files needed.
echo.
pause