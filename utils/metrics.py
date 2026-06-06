import pandas as pd
from pathlib import Path
from ultralytics import YOLO
from configs import settings

def compute_metrics(model: YOLO, data_yaml: str | Path) -> dict:
    """Ejecuta la validación sobre el conjunto de validación y obtiene las métricas."""
    print("Iniciando validación sobre el conjunto de pruebas/validación...")
    results = model.val(data=str(data_yaml))
    
    # Extraer métricas
    metrics = {
        "mAP50": results.results_dict.get("metrics/mAP50(B)", 0.0),
        "mAP50-95": results.results_dict.get("metrics/mAP50-95(B)", 0.0),
        "precision": results.results_dict.get("metrics/precision(B)", 0.0),
        "recall": results.results_dict.get("metrics/recall(B)", 0.0)
    }
    return metrics

def generate_metrics_table(results_dict: dict) -> pd.DataFrame:
    """Da formato al diccionario de métricas en un DataFrame de pandas legible."""
    df = pd.DataFrame([results_dict])
    return df
