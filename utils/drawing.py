import cv2
import numpy as np

def draw_detections(frame: np.ndarray, detections: list, class_names: dict = None) -> np.ndarray:
    """Draws bounding boxes, confidence tags, and class names onto a frame."""
    out_frame = frame.copy()
    
    for det in detections:
        x1, y1, x2, y2 = det.bbox
        label = det.class_name
        conf = det.confidence
        
        # Color palette depending on bounding boxes (custom HSL to BGR matching)
        # Using a sleek orange/cyan color palette for premium design aesthetics
        color = (0, 215, 255) if det.class_id == 3 else (255, 140, 0) # Gold/Orange
        
        # Draw bounding box
        cv2.rectangle(out_frame, (x1, y1), (x2, y2), color, 3)
        
        # Format label text
        tag = f"{label} ({conf:.2f})"
        
        # Render text tag with background rectangle for sleek legibility
        (w, h), _ = cv2.getTextSize(tag, cv2.FONT_HERSHEY_DUPLEX, 0.6, 1)
        cv2.rectangle(out_frame, (x1, y1 - 25), (x1 + w + 10, y1), color, -1)
        cv2.putText(out_frame, tag, (x1 + 5, y1 - 7), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1, cv2.LINE_AA)
        
    return out_frame

def draw_fps(frame: np.ndarray, fps_val: float) -> np.ndarray:
    """Renders FPS indicator box in the top-right corner."""
    out_frame = frame.copy()
    h, w, _ = frame.shape
    
    fps_text = f"FPS: {fps_val:.1f}"
    
    # Premium glassmorphic background plate for FPS
    cv2.rectangle(out_frame, (w - 150, 15), (w - 15, 50), (30, 30, 30), -1)
    cv2.rectangle(out_frame, (w - 150, 15), (w - 15, 50), (0, 215, 255), 1)
    cv2.putText(out_frame, fps_text, (w - 135, 40), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 215, 255), 1, cv2.LINE_AA)
    
    return out_frame

def draw_info_panel(frame: np.ndarray, info_dict: dict) -> np.ndarray:
    """Draws a premium HUD overlay in the top-left corner."""
    out_frame = frame.copy()
    
    # Backdrop
    cv2.rectangle(out_frame, (15, 15), (280, 110), (20, 20, 20), -1)
    cv2.rectangle(out_frame, (15, 15), (280, 110), (255, 140, 0), 1)
    
    y = 35
    for key, value in info_dict.items():
        text = f"{key}: {value}"
        cv2.putText(out_frame, text, (25, y), cv2.FONT_HERSHEY_DUPLEX, 0.5, (240, 240, 240), 1, cv2.LINE_AA)
        y += 22
        
    return out_frame
