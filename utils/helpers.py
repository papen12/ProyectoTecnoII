import sys
import torch
from pathlib import Path
from configs import settings

def ensure_dirs(*paths):
    """Ensures directories exist recursively."""
    for path in paths:
        Path(path).mkdir(parents=True, exist_ok=True)

def get_device() -> str:
    """Returns 'cuda' if GPU is available, else 'cpu'."""
    return "cuda" if torch.cuda.is_available() else "cpu"

def print_system_info():
    """Prints diagnostic system information about python, env and gpu."""
    print("=" * 60)
    print("SYSTEM AND ENVIRONMENT DIAGNOSTIC INFO")
    print("=" * 60)
    print(f"Python Version: {sys.version}")
    print(f"Project Root: {settings.PROJECT_ROOT}")
    print(f"Target Device: {get_device().upper()}")
    if torch.cuda.is_available():
        print(f"GPU Model: {torch.cuda.get_device_name(0)}")
    print(f"YOLOv8 Model base: {settings.MODEL_NAME}")
    print(f"Confidence Threshold: {settings.CONFIDENCE_THRESHOLD}")
    print(f"Dataset target path: {settings.DATASET_DIR}")
    print("=" * 60)

def list_images(directory: Path, extensions=(".jpg", ".jpeg", ".png", ".bmp")) -> list[Path]:
    """Helper to find all images inside a folder."""
    dir_path = Path(directory)
    if not dir_path.exists():
        return []
    return [p for p in dir_path.rglob("*") if p.suffix.lower() in extensions]
