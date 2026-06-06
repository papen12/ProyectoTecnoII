from dataclasses import dataclass
from pathlib import Path
from ultralytics import YOLO
import numpy as np
from configs import settings
from services.model_loader import load_model

@dataclass
class Detection:
    class_id: int
    class_name: str
    confidence: float
    bbox: tuple[int, int, int, int]  # (x1, y1, x2, y2)

class TrafficSignDetector:
    """Motor de detección principal para la versión personalizada de YOLOv8s."""
    
    def __init__(self, model_path: str | Path, confidence: float = settings.CONFIDENCE_THRESHOLD, device: str = "auto"):
        self.model = load_model(model_path, device=device)
        self.confidence = confidence
        
    def detect(self, frame: np.ndarray, conf_override: float = None) -> list[Detection]:
        """Ejecuta predicciones sobre un único fotograma y devuelve una lista estructurada de detecciones."""
        threshold = conf_override if conf_override is not None else self.confidence
        results = self.model.predict(source=frame, conf=threshold, verbose=False)
        
        detections = []
        if not results:
            return detections
            
        result = results[0]
        boxes = result.boxes
        
        for box in boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            xyxy = box.xyxy[0].cpu().numpy()
            
            # Mapear el nombre desde el diccionario o usar los nombres predeterminados de YOLO
            cls_name = settings.CLASS_NAMES.get(cls_id, result.names.get(cls_id, f"Clase {cls_id}"))
            
            bbox = (int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3]))
            
            detections.append(Detection(
                class_id=cls_id,
                class_name=cls_name,
                confidence=conf,
                bbox=bbox
            ))
            
        return detections
