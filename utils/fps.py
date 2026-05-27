import time
from collections import deque

class FPSCounter:
    """Utility class to track frames per second over an average window."""
    
    def __init__(self, avg_window: int = 30):
        self.times = deque(maxlen=avg_window)
        
    def tick(self):
        """Logs present timestamp to denote a finished frame iteration."""
        self.times.append(time.time())
        
    def get_fps(self) -> float:
        """Returns computed average FPS inside the moving window."""
        if len(self.times) < 2:
            return 0.0
        
        # Calculate time delta between oldest frame and most recent frame
        total_time = self.times[-1] - self.times[0]
        if total_time == 0:
            return 0.0
            
        return (len(self.times) - 1) / total_time
        
    def reset(self):
        """Clears times deque."""
        self.times.clear()
        
    def get_latency_ms(self) -> float:
        """Returns latency in milliseconds based on last frame processing."""
        if len(self.times) < 2:
            return 0.0
        return (self.times[-1] - self.times[-2]) * 1000.0
