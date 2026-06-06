import time
from collections import deque

class FPSCounter:
    """Clase de utilidad para rastrear fotogramas por segundo sobre una ventana promedio."""
    
    def __init__(self, avg_window: int = 30):
        self.times = deque(maxlen=avg_window)
        
    def tick(self):
        """Registra la marca de tiempo actual para denotar una iteración de fotograma finalizada."""
        self.times.append(time.time())
        
    def get_fps(self) -> float:
        """Devuelve el promedio de FPS calculado dentro de la ventana móvil."""
        if len(self.times) < 2:
            return 0.0
        
        # Calcular la diferencia de tiempo entre el fotograma más antiguo y el más reciente
        total_time = self.times[-1] - self.times[0]
        if total_time == 0:
            return 0.0
            
        return (len(self.times) - 1) / total_time
        
    def reset(self):
        """Limpia la cola de marcas de tiempo."""
        self.times.clear()
        
    def get_latency_ms(self) -> float:
        """Devuelve la latencia en milisegundos basada en el procesamiento del último fotograma."""
        if len(self.times) < 2:
            return 0.0
        return (self.times[-1] - self.times[-2]) * 1000.0
