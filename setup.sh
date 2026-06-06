#!/bin/bash

# Colores para salida elegante en terminal
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0;2m' # Sin color
BOLD='\033[1m'

echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}${BOLD}      CONFIGURACIÓN AUTOMÁTICA - PROYECTO TECNO II${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 1. Verificar si 'uv' está instalado
UV_CMD="uv"
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}[INFO] 'uv' no está en el PATH del sistema. Buscando en ubicaciones por defecto...${NC}"
    if [ -f "$HOME/.local/bin/uv" ]; then
        UV_CMD="$HOME/.local/bin/uv"
        echo -e "${GREEN}[OK] Se encontró 'uv' en: $UV_CMD${NC}"
    else
        echo -e "${YELLOW}[INFO] 'uv' no está instalado. Procediendo con la instalación automática...${NC}"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        
        # Cargar entorno de uv
        if [ -f "$HOME/.local/bin/env" ]; then
            source "$HOME/.local/bin/env"
        fi
        
        # Comprobar de nuevo tras instalación
        if [ -f "$HOME/.local/bin/uv" ]; then
            UV_CMD="$HOME/.local/bin/uv"
        elif command -v uv &> /dev/null; then
            UV_CMD="uv"
        else
            echo -e "${RED}[ERROR] La instalación de 'uv' finalizó, pero no se encontró el ejecutable.${NC}"
            echo "Por favor, instala 'uv' manualmente desde https://astral.sh/uv e intenta de nuevo."
            exit 1
        fi
        echo -e "${GREEN}[OK] 'uv' instalado y configurado correctamente.${NC}"
    fi
else
    echo -e "${GREEN}[OK] 'uv' ya está instalado en el PATH.${NC}"
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}[INFO] Sincronizando entorno virtual y dependencias con 'uv'...${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 2. Ejecutar sync para crear el .venv e instalar paquetes
$UV_CMD sync
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR] Hubo un problema al sincronizar las dependencias.${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}[OK] Entorno virtual sincronizado correctamente.${NC}"
echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}[INFO] Verificando importaciones y soporte CUDA...${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""

# 3. Ejecutar pruebas de importación
$UV_CMD run test_imports.py
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}[WARNING] Algunas importaciones fallaron. Revisa el reporte de arriba.${NC}"
fi

# 4. Validar existencia del modelo entrenado
echo -e "${BLUE}============================================================${NC}"
echo -e "${BLUE}[INFO] Verificando archivo de modelo...${NC}"
echo -e "${BLUE}============================================================${NC}"
if [ -f "models/best.pt" ]; then
    echo -e "${GREEN}[OK] El modelo entrenado 'models/best.pt' está en su lugar.${NC}"
else
    echo -e "${YELLOW}[WARNING] No se encontró 'models/best.pt'.${NC}"
    echo "Asegúrate de que el modelo esté ubicado en la carpeta 'models/' para ejecutar la detección."
fi

echo ""
echo -e "${BLUE}============================================================${NC}"
echo -e "${GREEN}${BOLD}         CONFIGURACIÓN COMPLETADA CON ÉXITO${NC}"
echo -e "${BLUE}============================================================${NC}"
echo ""
echo "Para lanzar el sistema de detección en tiempo real, ejecuta:"
echo -e "   ${GREEN}uv run main.py${NC}"
echo ""
echo "Para desactivar alertas de voz:"
echo -e "   ${GREEN}uv run main.py --no-voice${NC}"
echo ""
echo -e "${BLUE}============================================================${NC}"
