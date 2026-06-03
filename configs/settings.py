import os
from pathlib import Path

# Base directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset" / "gtsdb"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

MODEL_NAME = "yolov8s.pt"
CONFIDENCE_THRESHOLD = 0.40  # Set to 0.40 since the model has been trained for 50 epochs
IMG_SIZE = 640

# Training Parameters (when training locally)
EPOCHS = 80
BATCH_SIZE = 8  # Safe default for local CPU/GPU limits

# Webcam properties
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# Voice Alert Configuration
VOICE_RATE = 150
VOICE_COOLDOWN_SECONDS = 4
VOICE_LANG = "es"  # Spanish voice alerts

# Dictionary maps class IDs to Spanish descriptive names
CLASS_NAMES = {
    0: "Limite de velocidad (20km/h)",
    1: "Limite de velocidad (30km/h)",
    2: "Limite de velocidad (50km/h)",
    3: "Limite de velocidad (60km/h)",
    4: "Limite de velocidad (70km/h)",
    5: "Limite de velocidad (80km/h)",
    6: "Fin de limite de velocidad (80km/h)",
    7: "Limite de velocidad (100km/h)",
    8: "Limite de velocidad (120km/h)",
    9: "Prohibido adelantar",
    10: "Prohibido adelantar camiones",
    11: "Interseccion con prioridad",
    12: "Calzada con prioridad",
    13: "Ceda el paso",
    14: "Pare",
    15: "Circulacion prohibida",
    16: "Prohibido camiones",
    17: "Direccion prohibida",
    18: "Peligro",
    19: "Curva peligrosa a la izquierda",
    20: "Curva peligrosa a la derecha",
    21: "Curvas peligrosas",
    22: "Perfil irregular o rompemuelles",
    23: "Calzada deslizante",
    24: "Estrechamiento de calzada por la derecha",
    25: "Obras",
    26: "Semaforo",
    27: "Peatones",
    28: "Ninos o zona escolar",
    29: "Ciclistas",
    30: "Hielo o nieve",
    31: "Paso de animales salvajes",
    32: "Fin de todas las prohibiciones",
    33: "Giro obligatorio a la derecha",
    34: "Giro obligatorio a la izquierda",
    35: "Siga de frente",
    36: "Siga de frente o derecha",
    37: "Siga de frente o izquierda",
    38: "Pase por la derecha",
    39: "Pase por la izquierda",
    40: "Rotonda obligatoria",
    41: "Fin de prohibicion de adelantar",
    42: "Fin de prohibicion de adelantar camiones"
}


# Ensure critical folders exist
for folder in [DATASET_DIR, MODELS_DIR, OUTPUTS_DIR, OUTPUTS_DIR / "training", OUTPUTS_DIR / "validation", OUTPUTS_DIR / "detections"]:
    folder.mkdir(parents=True, exist_ok=True)
