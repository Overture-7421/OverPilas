@echo off
echo ============================================================
echo Creando Paquete de Distribución de OverPilas
echo ============================================================
echo.

REM Crear carpeta de distribución
if exist "OverPilas_Portable" rmdir /s /q "OverPilas_Portable"
mkdir "OverPilas_Portable"
echo Carpeta de distribución creada...

REM Copiar el ejecutable
if exist "dist\OverPilas.exe" (
    copy "dist\OverPilas.exe" "OverPilas_Portable\"
    echo OverPilas.exe copiado...
) else (
    echo ERROR: No se encontró OverPilas.exe
    echo Por favor ejecuta build_exe.bat primero
    pause
    exit /b 1
)

REM Copiar archivos de configuración iniciales
copy "battery_names.json" "OverPilas_Portable\"
copy "config.json" "OverPilas_Portable\"
if exist "pilas.json" (
    copy "pilas.json" "OverPilas_Portable\"
) else (
    echo {"pilas": [], "pilas_en_uso": [], "pilas_en_cooldown": {}, "pilas_inhabilitadas": []} > "OverPilas_Portable\pilas.json"
)
echo Archivos JSON copiados...

REM Copiar instrucciones
copy "INSTRUCCIONES_EXE.txt" "OverPilas_Portable\"
echo Instrucciones copiadas...

echo.
echo ============================================================
echo Paquete creado exitosamente!
echo ============================================================
echo.
echo La carpeta "OverPilas_Portable" contiene:
echo   - OverPilas.exe (ejecutable principal)
echo   - battery_names.json (configuración de nombres)
echo   - config.json (configuración inicial)
echo   - pilas.json (archivo de datos)
echo   - INSTRUCCIONES_EXE.txt (manual de uso)
echo.
echo Puedes copiar esta carpeta completa a cualquier computadora
echo con Windows y ejecutar OverPilas.exe directamente.
echo.
echo También puedes crear un archivo ZIP de esta carpeta para
echo compartirla más fácilmente.
echo.

pause
