@echo off
REM ==========================================================================
REM  Lanzador del Trabajo Final Integrador - Analisis Numerico
REM  Ejecuta la aplicacion desde el codigo fuente con Python.
REM ==========================================================================
title Analisis Numerico - Trabajo Integrador
cd /d "%~dp0"

echo Iniciando la aplicacion...
python main.py
if errorlevel 1 (
    echo.
    echo Hubo un problema al iniciar. Verifique que Python y las dependencias
    echo esten instaladas con:   pip install -r requirements.txt
    echo.
    pause
)
