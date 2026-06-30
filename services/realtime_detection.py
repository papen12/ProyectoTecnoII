import cv2
from pathlib import Path
from configs import settings
from services.detector import TrafficSignDetector
from services.voice_service import VoiceAlertService
from utils.camera import CameraManager
from utils.drawing import draw_detections, draw_fps, draw_info_panel
from utils.fps import FPSCounter

class RealtimeDetectionSystem:
    """Motor unificado que combina el detector, la cámara, los dibujos y los servicios de alerta de voz."""
    
    def __init__(self, model_path: str | Path, camera_source: int | str = 0, enable_voice: bool = True):
        self.model_path = Path(model_path)
        self.camera_source = camera_source
        self.enable_voice = enable_voice
        
        # Instanciar dependencias
        self.detector = TrafficSignDetector(
            model_path=self.model_path if self.model_path.exists() else settings.MODEL_NAME
        )
        self.camera = CameraManager(
            source=self.camera_source,
            width=settings.FRAME_WIDTH,
            height=settings.FRAME_HEIGHT
        )
        self.fps_counter = FPSCounter()
        self.voice_service = VoiceAlertService() if enable_voice else None
        self.running = False
        
    def run(self):
        """Inicia el bucle que muestra la ventana con la detección y las alertas."""
        if not self.camera.is_opened():
            print("Error: No se pudo abrir la fuente de la cámara.")
            return
            
        self.running = True
        self.fps_counter.reset()
        print("Sistema de detección en tiempo real en ejecución. Presione 'q' para detener.")
        
        # Configurar detalles del panel de información
        info = {
            "Modelo": self.model_path.name,
            "Conf": settings.CONFIDENCE_THRESHOLD,
            "Camara": self.camera_source,
            "Voz": "Activa" if self.enable_voice else "Inactiva"
        }
        
        while self.running and self.camera.is_opened():
            ret, frame = self.camera.read_frame()
            if not ret:
                print("Advertencia: Fallo en la adquisición del fotograma.")
                break
                
            # Realizar inferencia
            detections = self.detector.detect(frame)
            self.fps_counter.tick()
            
            # Determinar la última señal detectada para el HUD
            last_sign = "Ninguna"
            if len(detections) > 0:
                det = detections[0]
                last_sign = f"{det.class_name} ({det.confidence*100:.1f}%)"
            
            # Configurar detalles del panel de información en tiempo real
            current_info = {
                "Modelo": settings.MODEL_NAME,
                "Conf": settings.CONFIDENCE_THRESHOLD,
                "Camara": "Camara IP" if "http" in str(self.camera_source) else self.camera_source,
                "Voz": "Activa" if self.enable_voice else "Inactiva",
                "Ultima": last_sign
            }
            
            # Dibujar superposiciones
            annotated_frame = draw_detections(frame, detections)
            annotated_frame = draw_fps(annotated_frame, self.fps_counter.get_fps())
            annotated_frame = draw_info_panel(annotated_frame, current_info)
            
            # Emitir alertas de voz y registrar detecciones en consola
            if len(detections) > 0:
                import datetime
                now_str = datetime.datetime.now().strftime("%H:%M:%S")
                for det in detections:
                    print(f"[DETECCIÓN] Señal Encontrada: {det.class_name} - Confianza: {det.confidence*100:.1f}% - Hora: {now_str}")
                    if self.enable_voice and self.voice_service:
                        self.voice_service.alert(det.class_name)
                        
            # Crear ventana redimensionable
            window_name = "Detector de Senales de Transito (YOLOv8s)"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 800, 600)
            cv2.imshow(window_name, annotated_frame)
            
            # Manejar eventos de teclado
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                
        self.stop()
        
    def stop(self):
        """Libera de forma segura los componentes del sistema."""
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()
        if self.voice_service:
            self.voice_service.shutdown()
        print("Sistema de detección en tiempo real detenido.")
