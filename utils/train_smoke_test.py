import sys
from pathlib import Path

# Add project root to python path to resolve configs and utils imports
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT))

from ultralytics import YOLO
from configs import settings

DATA_YAML_PATH = PROJECT_ROOT / "dataset" / "roboflow" / "data.yaml"
MODEL_SAVE_DIR = PROJECT_ROOT / "models"

def run_smoke_test():
    print("=" * 60)
    print("INICIANDO PRUEBA DE ENTRENAMIENTO RAPIDO (SMOKE TEST) EN CPU")
    print("=" * 60)
    
    if not DATA_YAML_PATH.exists():
        print(f"Error: No se encontro el archivo data.yaml en: {DATA_YAML_PATH}")
        sys.exit(1)
        
    print(f"Cargando modelo base: {settings.MODEL_NAME}")
    model = YOLO(settings.MODEL_NAME)
    
    print("\nIniciando entrenamiento para 3 epocas...")
    print("Esto comprobara de forma completa que el dataset y las dependencias estan listos.")
    
    from utils.helpers import get_device
    device = get_device()
    print(f"Dispositivo de entrenamiento detectado: {device.upper()}")
    
    results = model.train(
        data=str(DATA_YAML_PATH.resolve()),
        epochs=3,
        imgsz=settings.IMG_SIZE,
        batch=8,
        project=str(settings.OUTPUTS_DIR / 'training'),
        name='yolov8s_traffic_signs',
        device=device,
        workers=2
    )
    
    print("\n[OK] Entrenamiento corto finalizado con exito.")
    
    # Look for the trained best.pt
    train_runs_dir = settings.OUTPUTS_DIR / 'training' / 'yolov8s_traffic_signs' / 'weights'
    best_weights_path = train_runs_dir / 'best.pt'
    
    if best_weights_path.exists():
        print(f"Copiando el mejor modelo entrenado (best.pt) a: {MODEL_SAVE_DIR}")
        MODEL_SAVE_DIR.mkdir(parents=True, exist_ok=True)
        shutil_copy = Path(shutil_copy_path(best_weights_path, MODEL_SAVE_DIR / 'best.pt'))
        print(f"[OK] Modelo guardado con exito en: {shutil_copy.resolve()}")
    else:
        print("[WARN] Advertencia: No se encontro el archivo best.pt en los resultados de entrenamiento.")
        
    print("=" * 60)

def shutil_copy_path(src, dst):
    import shutil
    return shutil.copy(src, dst)

if __name__ == "__main__":
    run_smoke_test()
