from pathlib import Path
from ultralytics import YOLO
import torch
from configs import settings
from utils.helpers import get_device

def load_model(model_path: str | Path, device: str = "auto") -> YOLO:
    """Carga un modelo de detección YOLOv8 y verifica su existencia, con fallback a CPU si falla CUDA."""
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"El archivo del modelo no existe en: {path.resolve()}")
        
    target_device = get_device() if device == "auto" else device
    print(f"Cargando modelo YOLO desde {path.name} en el dispositivo: {target_device.upper()}")
    
    # Cargar el modelo
    model = YOLO(str(path))
    try:
        model.to(target_device)
    except Exception as e:
        if "cuda" in str(target_device).lower():
            print(f"Advertencia: Fallo al cargar el modelo en GPU CUDA ({e}). Reintentando fallback en CPU...")
            try:
                model.to("cpu")
                print("OK: Modelo cargado exitosamente en CPU.")
            except Exception as cpu_err:
                print(f"Error crítico al cargar el modelo en CPU: {cpu_err}")
                raise cpu_err
        else:
            raise e
    return model

def load_pretrained(model_name: str = settings.MODEL_NAME) -> YOLO:
    """Descarga y carga una arquitectura YOLOv8 preentrenada oficial con fallback a CPU."""
    target_device = get_device()
    print(f"Cargando arquitectura YOLOv8 preentrenada: {model_name} en {target_device.upper()}")
    model = YOLO(model_name)
    try:
        model.to(target_device)
    except Exception as e:
        if "cuda" in str(target_device).lower():
            print(f"Advertencia: Fallo al mover modelo preentrenado a CUDA ({e}). Usando CPU.")
            model.to("cpu")
        else:
            raise e
    return model

def get_model_info(model: YOLO) -> dict:
    """Obtiene los nombres y las características estructurales de la instancia YOLO cargada."""
    return {
        "names": model.names,
        "device": str(model.device),
        "task": model.task
    }
