import os
import shutil
import urllib.request
import zipfile
import cv2
import yaml
from pathlib import Path

# Configuración de directorios
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset" / "gtsdb"
ZIP_URL = "https://sid.erda.dk/public/archives/ff17dc924eba88d5d01a807357d6614c/FullIJCNN2013.zip"
ZIP_TEMP = PROJECT_ROOT / "dataset" / "gtsdb_temp.zip"
EXTRACT_TEMP = PROJECT_ROOT / "dataset" / "gtsdb_temp_extract"

# Progreso de descarga
def download_progress(count, block_size, total_size):
    percent = int(count * block_size * 100 / total_size)
    if percent % 10 == 0:
        print(f"\rDescargando... {percent}% ({total_size / 1024 / 1024:.2f} MB totales)", end="")

def download_and_prepare():
    print("=" * 60)
    print("DESCARGA Y PREPARACION DEL DATASET PUBLICO GTSDB")
    print("=" * 60)
    
    # 1. Limpiar carpetas anteriores
    if DATASET_DIR.exists():
        print(f"Limpiando carpeta de dataset existente: {DATASET_DIR}")
        shutil.rmtree(DATASET_DIR)
    DATASET_DIR.parent.mkdir(parents=True, exist_ok=True)
    
    if EXTRACT_TEMP.exists():
        shutil.rmtree(EXTRACT_TEMP)
    EXTRACT_TEMP.mkdir(parents=True, exist_ok=True)
    
    # 2. Descargar ZIP
    print(f"Descargando dataset desde: {ZIP_URL}")
    print("Esto podria tardar unos minutos (1.6 GB)...")
    try:
        urllib.request.urlretrieve(ZIP_URL, ZIP_TEMP, reporthook=download_progress)
        print("\nDescarga completa con exito.")
    except Exception as e:
        print(f"\nError al descargar el dataset: {e}")
        return False
        
    # 3. Descomprimir
    print("Extrayendo archivos...")
    try:
        with zipfile.ZipFile(ZIP_TEMP, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_TEMP)
        print("Extraccion completa.")
    except Exception as e:
        print(f"Error al descomprimir: {e}")
        return False
    finally:
        if ZIP_TEMP.exists():
            ZIP_TEMP.unlink()
            
    # 4. Localizar la carpeta FullIJCNN2013
    gtsdb_root = EXTRACT_TEMP / "FullIJCNN2013"
    if not gtsdb_root.exists():
        print("Error: No se encontro la carpeta FullIJCNN2013 en el archivo extraido.")
        return False
        
    gt_file = gtsdb_root / "gt.txt"
    if not gt_file.exists():
        print("Error: No se encontro gt.txt.")
        return False
        
    # 5. Parsear anotaciones de gt.txt
    print("Parseando anotaciones y procesando imagenes...")
    # Formato: image_name.ppm;x1;y1;x2;y2;class_id
    annotations = {}
    with open(gt_file, 'r') as f:
        for line in f:
            parts = line.strip().split(';')
            if len(parts) == 6:
                img_name, x1, y1, x2, y2, class_id = parts
                if img_name not in annotations:
                    annotations[img_name] = []
                annotations[img_name].append({
                    'x1': float(x1), 'y1': float(y1),
                    'x2': float(x2), 'y2': float(y2),
                    'class_id': int(class_id)
                })
                
    # Obtener todas las imagenes .ppm (900 imagenes)
    ppm_files = sorted(list(gtsdb_root.glob("*.ppm")))
    print(f"Se encontraron {len(ppm_files)} imagenes PPM.")
    
    # Estructura de carpetas YOLO
    for split in ['train', 'val']:
        (DATASET_DIR / split / "images").mkdir(parents=True, exist_ok=True)
        (DATASET_DIR / split / "labels").mkdir(parents=True, exist_ok=True)
        
    # Procesar imagenes y generar labels YOLO
    # Split 80/20 determinista
    train_count = int(len(ppm_files) * 0.8)
    
    processed_count = 0
    for idx, ppm_path in enumerate(ppm_files):
        split = "train" if idx < train_count else "val"
        img_name = ppm_path.name
        jpg_name = img_name.replace(".ppm", ".jpg")
        
        # Leer imagen
        img = cv2.imread(str(ppm_path))
        if img is None:
            continue
            
        height, width, _ = img.shape
        
        # Guardar en formato JPG
        out_img_path = DATASET_DIR / split / "images" / jpg_name
        cv2.imwrite(str(out_img_path), img)
        
        # Generar archivo de labels
        out_lbl_path = DATASET_DIR / split / "labels" / img_name.replace(".ppm", ".txt")
        with open(out_lbl_path, 'w') as f:
            if img_name in annotations:
                for ann in annotations[img_name]:
                    # Convertir a coordenadas YOLO normalizadas
                    x_center = (ann['x1'] + ann['x2']) / 2.0 / width
                    y_center = (ann['y1'] + ann['y2']) / 2.0 / height
                    w = (ann['x2'] - ann['x1']) / width
                    h = (ann['y2'] - ann['y1']) / height
                    # Clampear valores entre 0 y 1 por seguridad
                    x_center = max(0.0, min(1.0, x_center))
                    y_center = max(0.0, min(1.0, y_center))
                    w = max(0.0, min(1.0, w))
                    h = max(0.0, min(1.0, h))
                    f.write(f"{ann['class_id']} {x_center:.6f} {y_center:.6f} {w:.6f} {h:.6f}\n")
        
        processed_count += 1
        if processed_count % 100 == 0:
            print(f"Procesadas {processed_count}/{len(ppm_files)} imagenes...")
            
    # 6. Crear data.yaml
    yaml_content = {
        'path': str(DATASET_DIR.resolve()).replace("\\", "/"),
        'train': "train/images",
        'val': "val/images",
        'test': "val/images",
        'nc': 43,
        'names': {
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
    }
    
    yaml_path = DATASET_DIR / "data.yaml"
    with open(yaml_path, 'w', encoding='utf-8') as f:
        yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)
        
    print(f"data.yaml creado en: {yaml_path}")
    
    # 7. Limpieza
    if EXTRACT_TEMP.exists():
        shutil.rmtree(EXTRACT_TEMP)
        
    print("=" * 60)
    print("GTSDB procesado y listo para entrenamiento en formato YOLOv8.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    download_and_prepare()
