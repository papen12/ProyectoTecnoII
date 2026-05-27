import argparse
import sys
from pathlib import Path
from configs import settings
from services.realtime_detection import RealtimeDetectionSystem

def main():
    parser = argparse.ArgumentParser(description="YOLOv8s Detector de Senales de Transito en Tiempo Real")
    
    parser.add_argument(
        "--model", 
        type=str, 
        default=str(Path(settings.MODELS_DIR) / "best.pt"),
        help="Ruta al modelo entrenado best.pt"
    )
    parser.add_argument(
        "--source", 
        default=settings.CAMERA_INDEX, 
        help="Origen de video: ID de webcam (int) o ruta a video (str)"
    )
    parser.add_argument(
        "--no-voice", 
        action="store_true", 
        help="Desactiva las alertas de voz en español"
    )
    parser.add_argument(
        "--conf", 
        type=float, 
        default=settings.CONFIDENCE_THRESHOLD,
        help="Umbral de confianza para la inferencia"
    )
    
    args = parser.parse_args()
    
    # Parse camera index if numeric
    source = args.source
    if isinstance(source, str) and source.isdigit():
        source = int(source)
        
    # Update configurations dynamically
    settings.CONFIDENCE_THRESHOLD = args.conf
    
    system = RealtimeDetectionSystem(
        model_path=args.model,
        camera_source=source,
        enable_voice=not args.no_voice
    )
    
    try:
        system.run()
    except KeyboardInterrupt:
        print("\nInterrupción manual recibida.")
        system.stop()
        sys.exit(0)

if __name__ == "__main__":
    main()
