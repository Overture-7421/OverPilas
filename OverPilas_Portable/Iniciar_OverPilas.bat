@echo off
chcp 65001 >nul
cls
echo ================================================================================
echo                     OverPilas - Sistema de Gestión de Baterías
echo ================================================================================
echo.
echo Iniciando OverPilas...
echo.
echo 1. Se abrirá una ventana de consola (no la cierres)
echo 2. Tu navegador se abrirá automáticamente en unos segundos
echo 3. Si el navegador no se abre, ve a: http://127.0.0.1:5000
echo.
echo Para detener la aplicación, cierra esta ventana o presiona Ctrl+C
echo.
echo ================================================================================
echo.

start "" "%~dp0OverPilas.exe"
