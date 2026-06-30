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
        import cv2
        threshold = conf_override if conf_override is not None else self.confidence
        
        # Rotar fotograma si está habilitado en la configuración (para dataset rotado 90 grados CCW)
        rotate_ccw = getattr(settings, "ROTATE_INPUT_90_CCW", False)
        
        if rotate_ccw:
            # Rotar 90 grados a la izquierda (antihorario) para coincidir con la orientación del entrenamiento
            pred_frame = cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
            h_orig, w_orig = frame.shape[:2]  # Dimensiones del fotograma vertical original
        else:
            pred_frame = frame
            
        results = self.model.predict(source=pred_frame, conf=threshold, verbose=False)
        
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
            
            if rotate_ccw:
                # Mapear coordenadas rotadas (H x W) de vuelta al marco original (W x H)
                # x_rot = y_orig  => y_orig = x_rot
                # y_rot = w_orig - 1 - x_orig => x_orig = w_orig - 1 - y_rot
                # xyxy = [x1_rot, y1_rot, x2_rot, y2_rot]
                x1_rot, y1_rot, x2_rot, y2_rot = xyxy
                
                x1 = int(w_orig - 1 - y2_rot)
                x2 = int(w_orig - 1 - y1_rot)
                y1 = int(x1_rot)
                y2 = int(x2_rot)
                
                # Asegurar límites correctos
                x1 = max(0, min(x1, w_orig - 1))
                x2 = max(0, min(x2, w_orig - 1))
                y1 = max(0, min(y1, h_orig - 1))
                y2 = max(0, min(y2, h_orig - 1))
                
                bbox = (x1, y1, x2, y2)
            else:
                bbox = (int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3]))
            
            detections.append(Detection(
                class_id=cls_id,
                class_name=cls_name,
                confidence=conf,
                bbox=bbox
            ))
            
        return detections
