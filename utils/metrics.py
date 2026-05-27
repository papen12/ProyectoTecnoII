import pandas as pd
from pathlib import Path
from ultralytics import YOLO
from configs import settings

def compute_metrics(model: YOLO, data_yaml: str | Path) -> dict:
    """Executes validation mode on validation set and retrieves metrics."""
    print("Iniciando validación sobre el conjunto de pruebas/validación...")
    results = model.val(data=str(data_yaml))
    
    # Extract metrics
    metrics = {
        "mAP50": results.results_dict.get("metrics/mAP50(B)", 0.0),
        "mAP50-95": results.results_dict.get("metrics/mAP50-95(B)", 0.0),
        "precision": results.results_dict.get("metrics/precision(B)", 0.0),
        "recall": results.results_dict.get("metrics/recall(B)", 0.0)
    }
    return metrics

def generate_metrics_table(results_dict: dict) -> pd.DataFrame:
    """Formats metrics dictionary into a readable pandas DataFrame."""
    df = pd.DataFrame([results_dict])
    return df
