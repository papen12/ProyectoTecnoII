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
                
            # Perform inference
            detections = self.detector.detect(frame)
            self.fps_counter.tick()
            
            # Draw overlays
            annotated_frame = draw_detections(frame, detections)
            annotated_frame = draw_fps(annotated_frame, self.fps_counter.get_fps())
            annotated_frame = draw_info_panel(annotated_frame, info)
            
            # Emit voice alerts for detections
            if self.enable_voice and self.voice_service:
                for det in detections:
                    self.voice_service.alert(det.class_name)
                    
            cv2.imshow("Detector de Senales de Transito (YOLOv8s)", annotated_frame)
            
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
