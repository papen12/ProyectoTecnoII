import cv2
import numpy as np

def draw_detections(frame: np.ndarray, detections: list, class_names: dict = None) -> np.ndarray:
    """Dibuja cajas delimitadoras, etiquetas de confianza y nombres de clase sobre el fotograma."""
    out_frame = frame.copy()
    
    for det in detections:
        x1, y1, x2, y2 = det.bbox
        label = det.class_name
        conf = det.confidence
        
        # Paleta de colores según la clase
        color = (0, 215, 255) if det.class_id == 3 else (255, 140, 0)
        
        # Dibujar caja delimitadora
        cv2.rectangle(out_frame, (x1, y1), (x2, y2), color, 3)
        
        # Formatear el texto de la etiqueta
        tag = f"{label} ({conf:.2f})"
        
        # Dibujar la etiqueta de texto con un rectángulo de fondo
        (w, h), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)
        cv2.rectangle(out_frame, (x1, y1 - 25), (x1 + w + 10, y1), color, -1)
        cv2.putText(out_frame, tag, (x1 + 5, y1 - 7), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        
    return out_frame
    
def draw_fps(frame: np.ndarray, fps_val: float) -> np.ndarray:
    """Muestra el indicador de FPS en la esquina superior derecha."""
    out_frame = frame.copy()
    h, w, _ = frame.shape
    
    fps_text = f"FPS: {fps_val:.1f}"
    
    # Panel de fondo para los FPS
    cv2.rectangle(out_frame, (w - 150, 15), (w - 15, 50), (30, 30, 30), -1)
    cv2.rectangle(out_frame, (w - 150, 15), (w - 15, 50), (0, 215, 255), 1)
    cv2.putText(out_frame, fps_text, (w - 135, 40), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 215, 255), 1, cv2.LINE_AA)
    
    return out_frame
    
def draw_info_panel(frame: np.ndarray, info_dict: dict) -> np.ndarray:
    """Dibuja un panel HUD en la esquina superior izquierda."""
    out_frame = frame.copy()
    
    # Panel de fondo para la información HUD
    cv2.rectangle(out_frame, (15, 15), (320, 135), (20, 20, 20), -1)
    cv2.rectangle(out_frame, (15, 15), (320, 135), (255, 140, 0), 1)
    
    y = 35
    for key, value in info_dict.items():
        text = f"{key}: {value}"
        cv2.putText(out_frame, text, (25, y), cv2.FONT_HERSHEY_DUPLEX, 0.5, (240, 240, 240), 1, cv2.LINE_AA)
        y += 22
        
    return out_frame
