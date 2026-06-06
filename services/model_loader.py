from pathlib import Path
from ultralytics import YOLO
import torch
from configs import settings
from utils.helpers import get_device

def load_model(model_path: str | Path, device: str = "auto") -> YOLO:
    """Carga un modelo de detección YOLOv8 y verifica su existencia."""
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"El archivo del modelo no existe en: {path.resolve()}")
        
    target_device = get_device() if device == "auto" else device
    print(f"Cargando modelo YOLO desde {path.name} en el dispositivo: {target_device.upper()}")
    
    # Cargar el modelo
    model = YOLO(str(path))
    model.to(target_device)
    return model

def load_pretrained(model_name: str = settings.MODEL_NAME) -> YOLO:
    """Descarga y carga una arquitectura YOLOv8 preentrenada oficial."""
    target_device = get_device()
    print(f"Cargando arquitectura YOLOv8 preentrenada: {model_name} en {target_device.upper()}")
    model = YOLO(model_name)
    model.to(target_device)
    return model

def get_model_info(model: YOLO) -> dict:
    """Obtiene los nombres y las características estructurales de la instancia YOLO cargada."""
    return {
        "names": model.names,
        "device": str(model.device),
        "task": model.task
    }
