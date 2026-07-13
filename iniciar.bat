@echo off
title Deposito Inteligente - Lanzador
echo.
echo ===================================================
echo    INICIANDO EL SISTEMA DE STOCK DE DEPOSITO
echo ===================================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python no esta instalado o no se encuentra en las variables de entorno (PATH).
    echo Por favor, instala Python 3.10 o superior y marca la opcion "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b %errorlevel%
)

:: Run launcher script
python "%~dp0run.py"
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Hubo un fallo en la ejecucion del programa.
    echo Detalle del codigo de salida: %errorlevel%
    echo.
    pause
)
