import time
import pyttsx3
from configs import settings

class VoiceAlertService:
    """Uses pyttsx3 to emit Spanish voice notifications for detected traffic signs with cooldown periods."""
    
    def __init__(self, rate: int = settings.VOICE_RATE, cooldown_seconds: float = settings.VOICE_COOLDOWN_SECONDS, lang: str = settings.VOICE_LANG):
        self.cooldown_seconds = cooldown_seconds
        self.last_alerts = {}
        
        # Initialize pyttsx3 text-to-speech engine
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            
            # Attempt to set voice properties to Spanish
            voices = self.engine.getProperty('voices')
            spanish_voice_found = False
            for voice in voices:
                if any(tag in voice.languages for tag in ['es', 'es_ES', 'es_MX']) or 'spanish' in voice.name.lower():
                    self.engine.setProperty('voice', voice.id)
                    spanish_voice_found = True
                    break
                    
            if not spanish_voice_found and len(voices) > 0:
                # Fallback to default voice if Spanish profile is missing
                self.engine.setProperty('voice', voices[0].id)
                
            self.active = True
            print("🔊 VoiceAlertService initialized successfully.")
        except Exception as e:
            self.active = False
            print(f"⚠️ Failed to initialize voice alerts (pyttsx3): {e}")
            
    def is_on_cooldown(self, label: str) -> bool:
        """Determines if a given label has been spoken too recently."""
        now = time.time()
        last_spoken = self.last_alerts.get(label, 0.0)
        return (now - last_spoken) < self.cooldown_seconds
        
    def alert(self, label: str):
        """Emits verbal notification using non-blocking voice engine thread calls."""
        if not self.active or self.is_on_cooldown(label):
            return
            
        text = f"Atención, señal de {label} detectada"
        self.last_alerts[label] = time.time()
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            print(f"⚠️ Voice system alert runtime failure: {e}")
            
    def reset_cooldowns(self):
        """Resets the internal timers."""
        self.last_alerts.clear()
        
    def shutdown(self):
        """Safely stops any pending speech queues."""
        if self.active:
            try:
                self.engine.stop()
            except Exception:
                pass
