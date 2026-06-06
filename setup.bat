@echo off
setlocal enabledelayedexpansion

echo ============================================================
echo      CONFIGURACION AUTOMATICA - PROYECTO TECNO II
echo ============================================================
echo.

:: 1. Verificar si 'uv' esta instalado y definir comando
set "UV_CMD=uv"
where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [INFO] 'uv' no esta en el PATH del sistema. Buscando en ubicaciones por defecto...
    if exist "%USERPROFILE%\.local\bin\uv.exe" (
        set "UV_CMD=%USERPROFILE%\.local\bin\uv.exe"
        echo [OK] Se encontro 'uv' en: !UV_CMD!
    ) else if exist "%APPDATA%\local\bin\uv.exe" (
        set "UV_CMD=%APPDATA%\local\bin\uv.exe"
        echo [OK] Se encontro 'uv' en: !UV_CMD!
    ) else (
        echo [INFO] 'uv' no esta instalado. Procediendo con la instalacion automatica...
        powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
        
        :: Buscar de nuevo tras la instalacion
        if exist "%USERPROFILE%\.local\bin\uv.exe" (
            set "UV_CMD=%USERPROFILE%\.local\bin\uv.exe"
        ) else if exist "%APPDATA%\local\bin\uv.exe" (
            set "UV_CMD=%APPDATA%\local\bin\uv.exe"
        ) else (
            echo [ERROR] La instalacion de 'uv' finalizo, pero no se encontro el ejecutable.
            echo Por favor, instala 'uv' manualmente desde https://astral.sh/uv e intenta de nuevo.
            pause
            exit /b 1
        )
        echo [OK] 'uv' instalado y configurado correctamente en: !UV_CMD!
    )
) else (
    echo [OK] 'uv' ya esta instalado en el PATH.
)

echo.
echo ============================================================
echo [INFO] Sincronizando entorno virtual y dependencias con 'uv'...
echo ============================================================
echo.

:: 2. Ejecutar sync para crear el .venv e instalar paquetes segun uv.lock y pyproject.toml
call "!UV_CMD!" sync
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Hubo un problema al sincronizar las dependencias.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [OK] Entorno virtual sincronizado correctamente.
echo.
echo ============================================================
echo [INFO] Verificando importaciones y soporte CUDA...
echo ============================================================
echo.

:: 3. Ejecutar pruebas de importacion para asegurar funcionamiento
call "!UV_CMD!" run test_imports.py
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Algunas importaciones fallaron. Revisa el reporte de arriba.
)

:: 4. Validar existencia del modelo entrenado
echo ============================================================
echo [INFO] Verificando archivo de modelo...
echo ============================================================
if exist "models\best.pt" (
    echo [OK] El modelo entrenado 'models\best.pt' esta en su lugar.
) else (
    echo [WARNING] No se encontro 'models\best.pt'.
    echo Asegurate de que el modelo este ubicado en la carpeta 'models/' para ejecutar la deteccion.
)

echo.
echo ============================================================
echo         CONFIGURACION COMPLETADA CON EXITO
echo ============================================================
echo.
echo Para lanzar el sistema de deteccion en tiempo real, ejecuta:
echo    uv run main.py
echo.
echo Para desactivar alertas de voz:
echo    uv run main.py --no-voice
echo.
echo ============================================================
pause
