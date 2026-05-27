import cv2
import numpy as np

class CameraManager:
    """Wrapper class over cv2.VideoCapture to streamline local webcam management."""
    
    def __init__(self, source: int | str = 0, width: int = 640, height: int = 480):
        self.source = source
        self.cap = cv2.VideoCapture(source)
        
        # Configure frame dimensions
        if isinstance(source, int):
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
    def read_frame(self) -> tuple[bool, np.ndarray]:
        """Reads frame from webcam."""
        if not self.cap.isOpened():
            return False, np.empty((0, 0, 3), dtype=np.uint8)
        return self.cap.read()
        
    def is_opened(self) -> bool:
        """Checks if the video stream is active."""
        return self.cap.isOpened()
        
    def release(self):
        """Releases the camera resource safely."""
        if self.cap.isOpened():
            self.cap.release()
            
    def get_properties(self) -> dict:
        """Returns standard metadata properties of the stream."""
        return {
            "width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": float(self.cap.get(cv2.CAP_PROP_FPS))
        }
