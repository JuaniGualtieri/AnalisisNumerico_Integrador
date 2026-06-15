@echo off
REM ==========================================================================
REM  Genera un EJECUTABLE (.exe) independiente con PyInstaller.
REM  El resultado queda en la carpeta  dist\AnalisisNumerico_Integrador.exe
REM ==========================================================================
title Construir EXE - Analisis Numerico
cd /d "%~dp0"

echo Instalando PyInstaller (si hace falta)...
python -m pip install --upgrade pyinstaller

echo.
echo Generando el ejecutable... (puede tardar unos minutos)
python -m PyInstaller --noconfirm --onefile --windowed ^
  --name "AnalisisNumerico_Integrador" ^
  --collect-all customtkinter ^
  --collect-submodules matplotlib ^
  main.py

echo.
if exist "dist\AnalisisNumerico_Integrador.exe" (
    echo ============================================================
    echo  LISTO!  El ejecutable esta en:
    echo     dist\AnalisisNumerico_Integrador.exe
    echo ============================================================
) else (
    echo Hubo un problema al generar el ejecutable. Revise los mensajes de arriba.
)
pause
