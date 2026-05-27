import os
from pathlib import Path

# Base directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset" / "roboflow"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Model Configurations
MODEL_NAME = "yolov8s.pt"
CONFIDENCE_THRESHOLD = 0.45  # Optimized confidence threshold
IMG_SIZE = 640

# Training Parameters (when training locally)
EPOCHS = 50
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
# Note: You should update this dictionary if your Roboflow class mappings differ!
CLASS_NAMES = {
    0: "Limite de velocidad 30",
    1: "Limite de velocidad 50",
    2: "Limite de velocidad 80",
    3: "Pare",
    4: "Ceda el paso",
    5: "No entrar",
    6: "Paso peatonal",
    7: "Giro obligatorio a la derecha",
    8: "Giro obligatorio a la izquierda",
    9: "Atencion peligro",
    # Add or update classes according to your custom dataset annotations!
}

# Ensure critical folders exist
for folder in [DATASET_DIR, MODELS_DIR, OUTPUTS_DIR, OUTPUTS_DIR / "training", OUTPUTS_DIR / "validation", OUTPUTS_DIR / "detections"]:
    folder.mkdir(parents=True, exist_ok=True)
