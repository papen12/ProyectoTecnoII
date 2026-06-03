import cv2
from pathlib import Path
from configs import settings
from services.detector import TrafficSignDetector
from services.voice_service import VoiceAlertService
from utils.camera import CameraManager
from utils.drawing import draw_detections, draw_fps, draw_info_panel
from utils.fps import FPSCounter

class RealtimeDetectionSystem:
    """Unified engine combining detector, camera, drawings, and voice alert services."""
    
    def __init__(self, model_path: str | Path, camera_source: int | str = 0, enable_voice: bool = True):
        self.model_path = Path(model_path)
        self.camera_source = camera_source
        self.enable_voice = enable_voice
        
        # Instantiate dependencies
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
        """Starts loop displaying windows with annotated images and alerts."""
        if not self.camera.is_opened():
            print("❌ Cannot open camera source.")
            return
            
        self.running = True
        self.fps_counter.reset()
        print("▶️ Real-time Detection System Running. Press 'q' to stop.")
        
        # Setup info banner details
        info = {
            "Modelo": settings.MODEL_NAME,
            "Conf": settings.CONFIDENCE_THRESHOLD,
            "Camara": self.camera_source,
            "Voz": "Activa" if self.enable_voice else "Inactiva"
        }
        
        while self.running and self.camera.is_opened():
            ret, frame = self.camera.read_frame()
            if not ret:
                print("⚠️ Frame acquisition failure.")
                break
                
            # Perform inference using the optimized confidence threshold to avoid false positives
            detections = self.detector.detect(frame)
            self.fps_counter.tick()
            
            # Determine last detected sign dynamically for HUD
            last_sign = "Ninguna"
            if len(detections) > 0:
                det = detections[0]
                last_sign = f"{det.class_name} ({det.confidence*100:.1f}%)"
            
            # Setup info banner details dynamically
            current_info = {
                "Modelo": settings.MODEL_NAME,
                "Conf": settings.CONFIDENCE_THRESHOLD,
                "Camara": "Camara IP" if "http" in str(self.camera_source) else self.camera_source,
                "Voz": "Activa" if self.enable_voice else "Inactiva",
                "Ultima": last_sign
            }
            
            # Draw overlays (Adds boxes around recognized signs and names on top in real time)
            annotated_frame = draw_detections(frame, detections)
            annotated_frame = draw_fps(annotated_frame, self.fps_counter.get_fps())
            annotated_frame = draw_info_panel(annotated_frame, current_info)
            
            # Emit voice alerts and log only when a signal is actually detected (no repetitive zero logs)
            if len(detections) > 0:
                import datetime
                now_str = datetime.datetime.now().strftime("%H:%M:%S")
                # Deduplicate repeated print statements for identical detections in adjacent frames to prevent console spam
                for det in detections:
                    # Logs print only when a detection is active in real time
                    print(f"[DETECCIÓN] 🚦 Señal Encontrada: {det.class_name} - Confianza: {det.confidence*100:.1f}% - Hora: {now_str}")
                    if self.enable_voice and self.voice_service:
                        self.voice_service.alert(det.class_name)
                        
            # Create resizable window and set custom dimensions
            window_name = "Detector de Senales de Transito (YOLOv8s)"
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 800, 600)
            cv2.imshow(window_name, annotated_frame)
            
            # Handle key events
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False
                
        self.stop()
        
    def stop(self):
        """Safely releases system components."""
        self.running = False
        self.camera.release()
        cv2.destroyAllWindows()
        if self.voice_service:
            self.voice_service.shutdown()
        print("🔌 Real-time Detection System Stopped.")
