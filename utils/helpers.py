import sys
import torch
from pathlib import Path
from configs import settings

def ensure_dirs(*paths):
    """Asegura que los directorios existan de forma recursiva."""
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)

def get_device() -> str:
    """Devuelve 'cuda' si la GPU está disponible, de lo contrario 'cpu'."""
    return "cuda" if torch.cuda.is_available() else "cpu"

def print_system_info():
    """Imprime información de diagnóstico del sistema sobre Python, el entorno y la GPU."""
    print("=" * 60)
    print("INFORMACIÓN DE DIAGNÓSTICO DEL SISTEMA Y ENTORNO")
    print("=" * 60)
    print(f"Versión de Python: {sys.version}")
    print(f"Raíz del Proyecto: {settings.PROJECT_ROOT}")
    print(f"Dispositivo Objetivo: {get_device().upper()}")
    if torch.cuda.is_available():
        print(f"Modelo de GPU: {torch.cuda.get_device_name(0)}")
    print(f"Base del Modelo YOLOv8: {settings.MODEL_NAME}")
    print(f"Umbral de Confianza: {settings.CONFIDENCE_THRESHOLD}")
    print(f"Ruta del Dataset: {settings.DATASET_DIR}")
    print("=" * 60)

def list_images(directory: Path, extensions=(".jpg", ".jpeg", ".png", ".bmp")) -> list[Path]:
    """Función de ayuda para encontrar todas las imágenes dentro de una carpeta."""
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    return [p for p in dir_path.rglob("*") if p.suffix.lower() in extensions]
