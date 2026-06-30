@echo off
setlocal enabledelayedexpansion

:: Titulo y colores
title Detector de Senales de Transito - Tiempo Real
color 0B
cls

echo =================================================================
echo         SISTEMA DE DETECCION DE SENALES DE TRANSITO
echo =================================================================
echo.
echo [INFO] Configurando directorio de trabajo...

:: Moverse a la carpeta del script
cd /d "%~dp0"

:: Validar si el modelo existe
if not exist "models\best.pt" (
    color 0C
    echo [ERROR] No se encontro el archivo del modelo 'models\best.pt'.
    echo Asegurate de que el entrenamiento haya finalizado y el archivo existe.
    echo.
    pause
    exit /b 1
)

:: Intentar detectar uv
set "RUN_CMD="
where uv >nul 2>nul
if %ERRORLEVEL% equ 0 (
    set "RUN_CMD=uv run python main.py"
) else (
    if exist "%USERPROFILE%\.local\bin\uv.exe" (
        set "RUN_CMD="%USERPROFILE%\.local\bin\uv.exe" run python main.py"
    ) else if exist "%APPDATA%\local\bin\uv.exe" (
        set "RUN_CMD="%APPDATA%\local\bin\uv.exe" run python main.py"
    ) else if exist ".venv\Scripts\python.exe" (
        set "RUN_CMD=.venv\Scripts\python.exe main.py"
    )
)

if "%RUN_CMD%"=="" (
    color 0C
    echo [ERROR] No se pudo encontrar 'uv' ni el entorno virtual '.venv'.
    echo Por favor, ejecuta primero 'setup.bat' para configurar el entorno.
    echo.
    pause
    exit /b 1
)

echo [OK] Entorno de ejecucion configurado correctamente.
echo.
echo =================================================================
echo Opciones de Ejecucion:
echo =================================================================
echo  1. Ejecutar detector CON Alertas de Voz (Recomendado)
echo  2. Ejecutar detector SIN Alertas de Voz (--no-voice)
echo  3. Ejecutar detector con una Camara/Video personalizado
echo  4. Salir
echo =================================================================
echo.

set /p opcion="Seleccione una opcion (1-4): "

if "%opcion%"=="1" (
    cls
    echo [INFO] Iniciando deteccion en tiempo real con alertas de voz...
    echo Presione 'q' en la ventana del video para salir o Ctrl+C en la consola.
    echo.
    call !RUN_CMD!
) else if "%opcion%"=="2" (
    cls
    echo [INFO] Iniciando deteccion en tiempo real SIN alertas de voz...
    echo Presione 'q' en la ventana del video para salir o Ctrl+C en la consola.
    echo.
    call !RUN_CMD! --no-voice
) else if "%opcion%"=="3" (
    cls
    echo =================================================================
    echo Configurar Origen de Video Personalizado
    echo =================================================================
    echo.
    echo Ejemplos:
    echo  - 0 (Camara web local integrada/USB)
    echo  - http://192.168.1.100:8080/video (Otra camara IP)
    echo  - ruta/al/video.mp4 (Un archivo de video grabado)
    echo.
    set /p custom_source="Ingrese el origen de video: "
    
    echo.
    echo Desea activar las alertas de voz? (S/N): 
    set /p con_voz=""
    
    cls
    if /i "!con_voz!"=="N" (
        echo [INFO] Iniciando deteccion en "!custom_source!" SIN alertas de voz...
        call !RUN_CMD! --source "!custom_source!" --no-voice
    ) else (
        echo [INFO] Iniciando deteccion en "!custom_source!" con alertas de voz...
        call !RUN_CMD! --source "!custom_source!"
    )
) else if "%opcion%"=="4" (
    echo Saliendo...
    exit /b 0
) else (
    echo Opcion invalida. Iniciando por defecto (Con alertas de voz)...
    timeout /t 2 >nul
    cls
    call !RUN_CMD!
)

echo.
echo =================================================================
echo Programa terminado.
echo =================================================================
pause
