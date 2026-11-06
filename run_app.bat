@echo off
title Lanzador - Aplicación de Turnos de Sábados
echo ====================================================================
echo   📅 Lanzador de la Aplicación de Turnos de Sábados (Supernumerarios)
echo ====================================================================
echo.

:: Asegurar que el directorio de trabajo sea la carpeta exacta del script
cd /d "%~dp0"

:: Check if python or py launcher works
set PYTHON_CMD=
python --version >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    py -c "import sys" >nul 2>nul
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
    ) else (
        echo [ERROR] No se pudo encontrar Python en el sistema.
        echo Por favor, asegúrate de tener instalado Python en tu equipo.
        pause
        exit /b 1
    )
)

echo [1/2] Verificando dependencias necesarias de Python...
%PYTHON_CMD% -m pip install pandas openpyxl streamlit plotly streamlit-sortables msal requests --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Hubo un problema instalando dependencias. 
    echo Intentando continuar con la ejecución...
) else (
    echo [OK] Dependencias verificadas con éxito.
)

echo.
echo [2/2] Iniciando el servidor local de Streamlit en puerto dedicado 8505...
echo La aplicación web se abrirá automáticamente en tu navegador en http://localhost:8505
echo (Puerto 8505 asignado para evitar conflicto con horas-conexion u otros proyectos)
echo Para cerrar la aplicación, cierra esta ventana negra.
echo.

:: Run Streamlit en puerto 8505 dedicado
%PYTHON_CMD% -m streamlit run app.py --server.port 8505 --server.headless false

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] La aplicación web se detuvo de manera inesperada.
    pause
)
