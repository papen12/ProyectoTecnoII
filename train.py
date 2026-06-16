import sys
from pathlib import Path
from ultralytics import YOLO
from configs import settings
from utils.helpers import get_device

def main():
    print("=" * 60)
    print("INICIANDO ENTRENAMIENTO COMPLETO DE YOLOv8s EN GPU/CUDA")
    print("=" * 60)
    
    data_yaml_path = settings.DATASET_DIR / "data.yaml"
    if not data_yaml_path.exists():
        print(f"Error: No se encontro el archivo data.yaml en: {data_yaml_path}")
        sys.exit(1)
        
    device = get_device()
    print(f"Dispositivo de entrenamiento: {device.upper()}")
    if device == "cpu":
        print("ADVERTENCIA: No se detecto CUDA. El entrenamiento en CPU sera extremadamente lento.")
        
    print(f"Cargando modelo base: {settings.MODEL_NAME}")
    model = YOLO(settings.MODEL_NAME)
    
    print(f"\nIniciando entrenamiento optimizado por {settings.EPOCHS} epocas con batch size {settings.BATCH_SIZE}...")
    model.train(
        data=str(data_yaml_path.resolve()),
        epochs=settings.EPOCHS,
        imgsz=settings.IMG_SIZE,
        batch=settings.BATCH_SIZE,
        project=str(settings.OUTPUTS_DIR / 'training'),
        name='yolov8s_traffic_signs',
        device=device,
        workers=2,             # Evitar problemas de memoria en Windows
        cos_lr=True,
        label_smoothing=0.1,
        cls=1.5,               # Distinguir límites de velocidad
        fliplr=0.0,            # No voltear para evitar reflejar señales de tránsito
        flipud=0.0
    )
    
    print("\n[OK] Entrenamiento finalizado con exito.")
    
    # Copiar los pesos de best.pt a models/
    training_dir = settings.OUTPUTS_DIR / 'training'
    run_folders = list(training_dir.glob("yolov8s_traffic_signs*"))
    
    if run_folders:
        run_folders.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        latest_run_dir = run_folders[0]
        best_weights_path = latest_run_dir / 'weights' / 'best.pt'
        
        if best_weights_path.exists():
            import shutil
            settings.MODELS_DIR.mkdir(parents=True, exist_ok=True)
            shutil.copy(best_weights_path, settings.MODELS_DIR / 'best.pt')
            print(f"Pesos optimos guardados exitosamente desde {latest_run_dir.name} en: {settings.MODELS_DIR / 'best.pt'}")
        else:
            print(f"No se encontraron los pesos best.pt en {latest_run_dir / 'weights'}")
    else:
        print("No se encontraron carpetas de entrenamiento en la ruta de salida.")
    print("=" * 60)

if __name__ == "__main__":
    main()
