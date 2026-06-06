import queue
import threading
import time
import pyttsx3
import subprocess
import sys
from configs import settings

class VoiceAlertService:
    """Servicio para emitir notificaciones de voz en español sobre señales de tránsito usando un hilo en segundo plano."""
    
    def __init__(self, rate: int = settings.VOICE_RATE, cooldown_seconds: float = settings.VOICE_COOLDOWN_SECONDS, lang: str = settings.VOICE_LANG):
        self.cooldown_seconds = cooldown_seconds
        self.last_alerts = {}
        self.queue = queue.Queue()
        self.running = True
        self.active = True
        self.rate = rate
        
        # Iniciar hilo en segundo plano
        self.thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.thread.start()
        print("Threaded VoiceAlertService inicializado correctamente.")
        
    def _speech_worker(self):
        while self.running:
            try:
                # Obtener solicitud de voz de la cola
                text = self.queue.get(timeout=0.5)
                try:
                    # Ejecutar pyttsx3 en un proceso separado para evitar problemas de COM en Windows
                    cmd = [
                        sys.executable,
                        "-c",
                        "import pyttsx3\n"
                        "engine = pyttsx3.init()\n"
                        f"engine.setProperty('rate', {self.rate})\n"
                        "voices = engine.getProperty('voices')\n"
                        "voice_id = next((v.id for v in voices if any(tag in v.languages for tag in ['es', 'es_ES', 'es_MX']) or 'spanish' in v.name.lower()), None)\n"
                        "if voice_id:\n"
                        "    engine.setProperty('voice', voice_id)\n"
                        f"engine.say({repr(text)})\n"
                        "engine.runAndWait()\n"
                    ]
                    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                except Exception as e:
                    print(f"Error en la ejecución de alerta de voz: {e}")
                finally:
                    self.queue.task_done()
            except queue.Empty:
                continue
                
    def is_on_cooldown(self, label: str) -> bool:
        """Determina si una etiqueta se ha anunciado muy recientemente."""
        now = time.time()
        last_spoken = self.last_alerts.get(label, 0.0)
        return (now - last_spoken) < self.cooldown_seconds
        
    def alert(self, label: str):
        """Añade una notificación de voz a la cola si no está en cooldown."""
        if not self.active or self.is_on_cooldown(label):
            return
            
        text = f"Atención, señal de {label} detectada"
        self.last_alerts[label] = time.time()
        
        # Limpiar notificaciones antiguas
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except queue.Empty:
                break
                
        self.queue.put(text)
            
    def reset_cooldowns(self):
        """Limpia los temporizadores internos."""
        self.last_alerts.clear()
        
    def shutdown(self):
        """Detiene la cola de voz de manera segura."""
        self.running = False
        if self.active:
            try:
                pass
            except Exception:
                pass
        print("VoiceAlertService finalizado.")
