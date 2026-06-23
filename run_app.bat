@echo off
title Lanzador - Aplicación de Turnos de Sábados
echo ====================================================================
echo   📅 Lanzador de la Aplicación de Turnos de Sábados (Supernumerarios)
echo ====================================================================
echo.

:: Check if the python launcher exists
where py >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] No se pudo encontrar el lanzador 'py' de Python.
    echo Por favor, asegúrate de tener instalado Python en tu equipo.
    pause
    exit /b 1
)

echo [1/2] Verificando dependencias necesarias de Python...
py -m pip install pandas openpyxl streamlit plotly streamlit-sortables --quiet
if %errorlevel% neq 0 (
    echo [WARNING] Hubo un problema instalando dependencias. 
    echo Intentando continuar con la ejecución...
) else (
    echo [OK] Dependencias verificadas con éxito.
)

echo.
echo [2/2] Iniciando el servidor local de Streamlit...
echo La aplicación web se abrirá automáticamente en tu navegador.
echo Para cerrar la aplicación, cierra esta ventana negra.
echo.

:: Run Streamlit
py -m streamlit run app.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] La aplicación web se detuvo de manera inesperada.
    pause
)
