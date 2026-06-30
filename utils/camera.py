import cv2
import numpy as np
import threading
import time

class CameraManager:
    """Clase de envoltura optimizada sobre cv2.VideoCapture para gestionar cámaras web e IP de forma asíncrona usando hilos."""
    
    def __init__(self, source: int | str = 0, width: int = 640, height: int = 480):
        self.source = source
        
        # Optimizar el backend de video de OpenCV para transmisión IP (usar FFMPEG explícitamente para transmisiones de red)
        if isinstance(source, str) and (source.startswith("http") or source.startswith("rtsp")):
            self.cap = cv2.VideoCapture(source, cv2.CAP_FFMPEG)
            # Minimizar el tamaño del búfer para reducir la latencia y evitar desfase en la transmisión
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        else:
            self.cap = cv2.VideoCapture(source)
            
        # Configurar dimensiones del fotograma
        if isinstance(source, int):
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
        self.ret = False
        self.frame = np.empty((0, 0, 3), dtype=np.uint8)
        self.running = False
        
        if self.cap.isOpened():
            self.running = True
            # Iniciar hilo de lectura asíncrona para maximizar FPS y eliminar lag de red
            self.thread = threading.Thread(target=self._update_frame, daemon=True)
            self.thread.start()
            
            # Esperar a que se capture el primer fotograma (máximo 3.0 segundos) para evitar fallos de lectura inmediatos
            start_time = time.time()
            while not self.ret and (time.time() - start_time) < 3.0:
                time.sleep(0.05)
            
    def _update_frame(self):
        """Bucle en segundo plano para actualizar constantemente el último fotograma disponible."""
        while self.running:
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret:
                    self.ret = ret
                    self.frame = frame
                else:
                    time.sleep(0.01)
            else:
                time.sleep(0.01)
                
    def read_frame(self) -> tuple[bool, np.ndarray]:
        """Devuelve el último fotograma capturado por el hilo asíncrono sin bloquear el bucle principal."""
        return self.ret, self.frame
        
    def is_opened(self) -> bool:
        """Verifica si la transmisión de video está activa."""
        return self.cap.isOpened()
        
    def release(self):
        """Libera el recurso de la cámara y detiene el hilo de lectura."""
        self.running = False
        if hasattr(self, 'thread'):
            self.thread.join(timeout=1.0)
        if self.cap.isOpened():
            self.cap.release()
            
    def get_properties(self) -> dict:
        """Devuelve las propiedades de metadatos estándar de la transmisión."""
        return {
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": float(self.cap.get(cv2.CAP_PROP_FPS))
        }
