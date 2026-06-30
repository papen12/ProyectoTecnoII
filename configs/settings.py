import os
from pathlib import Path

# Directorios base
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset" / "dataset_bolivia"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

MODEL_NAME = "yolov8s.pt"
CONFIDENCE_THRESHOLD = 0.40
IMG_SIZE = 640

# Parámetros de entrenamiento
EPOCHS = 150
BATCH_SIZE = 8

# Propiedades de la cámara web
CAMERA_INDEX = "http://192.168.21.227:8080/video"
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Configuración de alertas de voz
VOICE_RATE = 150
VOICE_COOLDOWN_SECONDS = 4
VOICE_LANG = "es"

# Corregir rotación de la cámara (rotar 90 grados a la izquierda para el modelo)
ROTATE_INPUT_90_CCW = True

# Mapa de IDs de clases a nombres descriptivos en español
CLASS_NAMES = {
    0: "Caja de Salud de Caminos a 100 metros",
    1: "Calle de doble sentido",
    2: "Calle de un solo sentido",
    3: "Doble circulación",
    4: "Giro en U permitido",
    5: "Paso de peatones",
    6: "Prohibido camiones",
    7: "Prohibido estacionar, servicio rápido",
    8: "Prohibido estacionar en toda la cuadra",
    9: "Prohibido giro en U",
    10: "Prohibido peatones",
    11: "Rompemuelles a 50 metros",
    12: "Servicio rápido Sucre",
    13: "Solo peatones",
    14: "Velocidad máxima 40",
    15: "Zona escolar",
}


# Asegurar que existan las carpetas críticas
for folder in [DATASET_DIR, MODELS_DIR, OUTPUTS_DIR, OUTPUTS_DIR / "training", OUTPUTS_DIR / "validation", OUTPUTS_DIR / "detections"]:
    folder.mkdir(parents=True, exist_ok=True)
