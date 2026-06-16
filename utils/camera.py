import cv2
import numpy as np

class CameraManager:
    """Clase de envoltura sobre cv2.VideoCapture para simplificar la gestión de la cámara web local."""
    
    def __init__(self, source: int | str = 0, width: int = 640, height: int = 480):
        self.source = source
        
        # Optimizar el backend de video de OpenCV para transmisión IP (usar FFMPEG explícitamente para transmisiones de red)
        if isinstance(source, str) and source.startswith("http"):
            self.cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
            # Minimizar el tamaño del búfer para reducir la latencia y evitar desfase en la transmisión
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        else:
            self.cap = cv2.VideoCapture(source)
            
        # Configurar dimensiones del fotograma
        if isinstance(source, int):
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
    def read_frame(self) -> tuple[bool, np.ndarray]:
        """Lee un fotograma de la cámara."""
        if not self.cap.isOpened():
            return False, np.empty((0, 0, 3), dtype=np.uint8)
        return self.cap.read()
        
    def is_opened(self) -> bool:
        """Verifica si la transmisión de video está activa."""
        return self.cap.isOpened()
        
    def release(self):
        """Libera el recurso de la cámara de forma segura."""
        if self.cap.isOpened():
            self.cap.release()
            
    def get_properties(self) -> dict:
        """Devuelve las propiedades de metadatos estándar de la transmisión."""
        return {
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": float(self.cap.get(cv2.CAP_PROP_FPS))
        }
