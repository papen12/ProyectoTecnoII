import queue
import threading
import time
import pyttsx3
import subprocess
import sys
from configs import settings

class VoiceAlertService:
    """Uses a background thread and a queue to emit Spanish voice notifications for traffic signs without blocking the main OpenCV frame loop."""
    
    def __init__(self, rate: int = settings.VOICE_RATE, cooldown_seconds: float = settings.VOICE_COOLDOWN_SECONDS, lang: str = settings.VOICE_LANG):
        self.cooldown_seconds = cooldown_seconds
        self.last_alerts = {}
        self.queue = queue.Queue()
        self.running = True
        self.active = True
        self.rate = rate
        
        # Start background thread
        self.thread = threading.Thread(target=self._speech_worker, daemon=True)
        self.thread.start()
        print("🔊 Threaded VoiceAlertService initialized successfully.")
        
    def _speech_worker(self):
        while self.running:
            try:
                # Retrieve voice request from queue (non-blocking with timeout to check running status)
                text = self.queue.get(timeout=0.5)
                try:
                    # Run pyttsx3 in a separate python process to avoid COM apartment threading issues on Windows
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
                    print(f"⚠️ Voice system alert runtime failure: {e}")
                finally:
                    self.queue.task_done()
            except queue.Empty:
                continue
                
    def is_on_cooldown(self, label: str) -> bool:
        """Determines if a given label has been spoken too recently."""
        now = time.time()
        last_spoken = self.last_alerts.get(label, 0.0)
        return (now - last_spoken) < self.cooldown_seconds
        
    def alert(self, label: str):
        """Adds verbal notification to the queue if not on cooldown, clearing any old queued alerts."""
        if not self.active or self.is_on_cooldown(label):
            return
            
        text = f"Atención, señal de {label} detectada"
        self.last_alerts[label] = time.time()
        
        # Empty the queue first so we never speak stale/old notifications
        while not self.queue.empty():
            try:
                self.queue.get_nowait()
                self.queue.task_done()
            except queue.Empty:
                break
                
        self.queue.put(text)
            
    def reset_cooldowns(self):
        """Resets the internal timers."""
        self.last_alerts.clear()
        
    def shutdown(self):
        """Safely stops any pending speech queues."""
        self.running = False
        if self.active:
            try:
                # We could call engine.stop() here, but since it is running in thread it is safer to let worker thread exit.
                pass
            except Exception:
                pass
        print("🔌 VoiceAlertService shutdown.")

