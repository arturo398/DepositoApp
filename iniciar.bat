@echo off
title Deposito Inteligente - Lanzador
echo.
echo ===================================================
echo    INICIANDO EL SISTEMA DE STOCK DE DEPOSITO
echo ===================================================
echo.

:: 1. Intentar usar el Python del entorno virtual si ya existe
if exist "%~dp0.venv\Scripts\python.exe" (
    "%~dp0.venv\Scripts\python.exe" "%~dp0run.py"
    goto check_error
)

:: 2. Si no existe .venv, buscar python global
python --version >nul 2>&1
if %errorlevel% equ 0 (
    python "%~dp0run.py"
    goto check_error
)

:: 3. Si no, buscar py launcher
py --version >nul 2>&1
if %errorlevel% equ 0 (
    py "%~dp0run.py"
    goto check_error
)

:: 4. Error si no se encuentra nada
echo ERROR: Python no esta instalado o no se encuentra en las variables de entorno (PATH).
echo Por favor, instala Python 3.10 o superior y marca la opcion "Add Python to PATH" durante la instalacion.
echo.
pause
exit /b 1

:check_error
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Hubo un fallo en la ejecucion del programa.
    echo Detalle del codigo de salida: %errorlevel%
    echo.
    pause
)
