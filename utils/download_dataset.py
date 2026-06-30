import os
import shutil
import urllib.request
import zipfile
import yaml
from pathlib import Path

# Base directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset" / "roboflow"
ZIP_URL = "https://github.com/Boggartfly/Indian-Expressway-Traffic-Sign-Dataset/archive/refs/heads/main.zip"
ZIP_TEMP = PROJECT_ROOT / "dataset" / "irtsd-temp.zip"
EXTRACT_TEMP = PROJECT_ROOT / "dataset" / "temp_extract"

def download_and_extract():
    print("=" * 60)
    print("DESCARGA Y ORGANIZACION DE DATASET REAL: MUMBAY-PUNE EXPRESSWAY")
    print("=" * 60)
    
    # 1. Clean previous folders
    if DATASET_DIR.exists():
        print(f"Limpiando carpeta de dataset existente: {DATASET_DIR}")
        shutil.rmtree(DATASET_DIR)
    DATASET_DIR.parent.mkdir(parents=True, exist_ok=True)
    
    if EXTRACT_TEMP.exists():
        shutil.rmtree(EXTRACT_TEMP)
    EXTRACT_TEMP.mkdir(parents=True, exist_ok=True)

    # 2. Download ZIP
    print(f"Descargando dataset desde: {ZIP_URL}")
    try:
        urllib.request.urlretrieve(ZIP_URL, ZIP_TEMP)
        print("Descarga completa con exito.")
    except Exception as e:
        print(f"Error al descargar el dataset: {e}")
        return False

    # 3. Unzip
    print("Extrayendo archivos...")
    try:
        with zipfile.ZipFile(ZIP_TEMP, 'r') as zip_ref:
            zip_ref.extractall(EXTRACT_TEMP)
        print("Extraccion completa.")
    except Exception as e:
        print(f"Error al descomprimir el archivo: {e}")
        return False
    finally:
        if ZIP_TEMP.exists():
            ZIP_TEMP.unlink()

    # 4. Locate repo root folder inside extracted files
    root_extracted = list(EXTRACT_TEMP.glob("Indian-Expressway-Traffic-Sign-Dataset-*"))
    if not root_extracted:
        print("Error: No se localizo la carpeta raiz del dataset extraido.")
        return False
    
    src_dir = root_extracted[0]
    print(f"Carpeta del repositorio localizada en: {src_dir.resolve()}")
    
    # 5. Move and structure dataset splits into train/images, train/labels, etc.
    print("Estructurando dataset para compatibilidad estandar con YOLOv8...")
    DATASET_DIR.mkdir(parents=True, exist_ok=True)
    
    # Move data.yaml
    src_yaml = src_dir / "data.yaml"
    if src_yaml.exists():
        shutil.copy(str(src_yaml), str(DATASET_DIR / "data.yaml"))
        
    for split in ["train", "val", "test"]:
        src_split_dir = src_dir / split
        if not src_split_dir.exists():
            continue
            
        # Target folders
        dst_img_dir = DATASET_DIR / split / "images"
        dst_lbl_dir = DATASET_DIR / split / "labels"
        dst_img_dir.mkdir(parents=True, exist_ok=True)
        dst_lbl_dir.mkdir(parents=True, exist_ok=True)
        
        # Sort files into images and labels
        print(f"  Organizando split: {split.upper()}...")
        for item in src_split_dir.iterdir():
            if item.is_file():
                ext = item.suffix.lower()
                if ext in [".jpg", ".png", ".jpeg", ".bmp"]:
                    shutil.move(str(item), str(dst_img_dir / item.name))
                elif ext == ".txt":
                    shutil.move(str(item), str(dst_lbl_dir / item.name))
                    
    # Clean up temp folder
    if EXTRACT_TEMP.exists():
        shutil.rmtree(EXTRACT_TEMP)
    print("Dataset estructurado con exito.")

    # 6. Read data.yaml and dynamically update configs/settings.py
    data_yaml_path = DATASET_DIR / "data.yaml"
    if data_yaml_path.exists():
        print("Sincronizando configuraciones de clase con configs/settings.py...")
        try:
            with open(data_yaml_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            names = data.get("names", {})
            if isinstance(names, list):
                names = {i: name for i, name in enumerate(names)}
                
            print(f"Se detectaron {len(names)} clases reales de senales de transito.")
            
            # Format CLASS_NAMES dictionary as python code
            class_dict_str = "CLASS_NAMES = {\n"
            for k, v in names.items():
                class_dict_str += f"    {k}: \"{v}\",\n"
            class_dict_str += "}"
            
            settings_path = PROJECT_ROOT / "configs" / "settings.py"
            if settings_path.exists():
                with open(settings_path, 'r', encoding='utf-8') as sf:
                    lines = sf.readlines()
                
                # Replace CLASS_NAMES block
                new_lines = []
                in_class_block = False
                for line in lines:
                    if line.strip().startswith("CLASS_NAMES = {"):
                        in_class_block = True
                        new_lines.append(class_dict_str + "\n")
                        continue
                    if in_class_block:
                        if line.strip().startswith("}"):
                            in_class_block = False
                        continue
                    new_lines.append(line)
                
                with open(settings_path, 'w', encoding='utf-8') as sf:
                    sf.writelines(new_lines)
                print("configs/settings.py actualizado exitosamente.")
                
                # Correct data.yaml paths with absolute path compatibility
                print("Actualizando data.yaml con rutas absolutas locales...")
                data['path'] = str(DATASET_DIR.resolve()).replace("\\", "/")
                data['train'] = "train/images"
                data['val'] = "val/images"
                if 'test' in data or (DATASET_DIR / "test").exists():
                    data['test'] = "test/images"
                
                with open(data_yaml_path, 'w', encoding='utf-8') as f:
                    yaml.dump(data, f, default_flow_style=False)
                print("data.yaml actualizado con rutas absolutas locales.")
        except Exception as e:
            print(f"Error al actualizar settings.py o data.yaml: {e}")
            
    print("=" * 60)
    print("Proceso finalizado. Dataset estructurado y listo.")
    print("=" * 60)
    return True

if __name__ == "__main__":
    download_and_extract()
