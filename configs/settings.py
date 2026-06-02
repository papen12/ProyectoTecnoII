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
    0: "Ahead only",
    1: "Bump",
    2: "Car Speed 100",
    3: "Danger",
    4: "Go Slow",
    5: "Lane sign",
    6: "Left Curve",
    7: "No Passing",
    8: "No Stopping",
    9: "No U Turn",
    10: "No Waiting",
    11: "Phone",
    12: "Right Curve",
    13: "Speed 100",
    14: "Speed 30",
    15: "Speed 50",
    16: "Speed 80",
    17: "Steep decent",
    18: "Truck Speed 80",
    19: "Tunnel",
    20: "Work in Progress",
}

# Ensure critical folders exist
for folder in [DATASET_DIR, MODELS_DIR, OUTPUTS_DIR, OUTPUTS_DIR / "training", OUTPUTS_DIR / "validation", OUTPUTS_DIR / "detections"]:
    folder.mkdir(parents=True, exist_ok=True)
