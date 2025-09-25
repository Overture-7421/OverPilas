@echo off
echo 🔋 Building OverPilas Executable for Windows...
echo.

REM Set the full path to MS Store Python
set PYTHON_PATH=%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python.exe
set PIP_CMD=%PYTHON_PATH% -m pip

REM Check if Python is installed
echo Checking for Python installation...
"%PYTHON_PATH%" --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not found at expected location
    echo Please install Python from Microsoft Store
    pause
    exit /b 1
) else (
    echo ✅ Found Python at MS Store location
    "%PYTHON_PATH%" --version
)

echo.
echo 📦 Installing dependencies...
"%PYTHON_PATH%" -m pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo 🏗️  Building executable with PyInstaller...
"%PYTHON_PATH%" -m pip install pyinstaller
"%PYTHON_PATH%" -m PyInstaller OverPilas.spec --clean

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