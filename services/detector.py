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
    """Core detection engine for custom trained YOLOv8s."""
    
    def __init__(self, model_path: str | Path, confidence: float = settings.CONFIDENCE_THRESHOLD, device: str = "auto"):
        self.model = load_model(model_path, device=device)
        self.confidence = confidence
        
    def detect(self, frame: np.ndarray) -> list[Detection]:
        """Runs predictions over a single frame and returns structured Detections list."""
        results = self.model.predict(source=frame, conf=self.confidence, verbose=False)
        
        detections = []
        if not results:
            return detections
            
        result = results[0]
        boxes = result.boxes
        
        for box in boxes:
            cls_id = int(box.cls[0].item())
            conf = float(box.conf[0].item())
            xyxy = box.xyxy[0].cpu().numpy()
            
            # Map name from dictionary or fallback to YOLO names
            cls_name = settings.CLASS_NAMES.get(cls_id, result.names.get(cls_id, f"Clase {cls_id}"))
            
            bbox = (int(xyxy[0]), int(xyxy[1]), int(xyxy[2]), int(xyxy[3]))
            
            detections.append(Detection(
                class_id=cls_id,
                class_name=cls_name,
                confidence=conf,
                bbox=bbox
            ))
            
        return detections
