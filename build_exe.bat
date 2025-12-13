@echo off
echo ============================================================
echo Building OverPilas Executable
echo ============================================================
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
echo.

REM Build the executable
echo Building executable with PyInstaller...
pyinstaller --clean OverPilas.spec
echo.

if exist "dist\OverPilas.exe" (
    echo ============================================================
    echo Build successful!
    echo ============================================================
    echo.
    echo Executable location: dist\OverPilas.exe
    echo.
    echo You can now copy the OverPilas.exe file to any Windows laptop
    echo and run it without needing Python installed.
    echo.
    echo IMPORTANT: The following files will be created/used by the app:
    echo   - battery_names.json (battery names configuration)
    echo   - config.json (competition mode configuration)
    echo   - pilas.json (battery data)
    echo.
    echo These files will be created in the same folder as the EXE.
    echo.
) else (
    echo ============================================================
    echo Build failed! Check the output above for errors.
    echo ============================================================
)

pause
