import os
import shutil
import random
from pathlib import Path
import yaml

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATASET_DIR = PROJECT_ROOT / "dataset" / "dataset_bolivia"
SETTINGS_PATH = PROJECT_ROOT / "configs" / "settings.py"

def main():
    print("=" * 60)
    print("PREPARANDO EL DATASET DE BOLIVIA PARA YOLOv8")
    print("=" * 60)

    # 1. Leer las clases de classes.txt
    classes_file = DATASET_DIR / "classes.txt"
    if not classes_file.exists():
        print(f"Error: No se encontro el archivo classes.txt en {classes_file}")
        return

    with open(classes_file, "r", encoding="utf-8") as f:
        classes = [line.strip() for line in f if line.strip()]

    print(f"Se detectaron {len(classes)} clases en classes.txt:")
    for idx, name in enumerate(classes):
        print(f"  {idx}: {name}")

    # 2. Encontrar imagenes y sus correspondientes etiquetas
    src_images_dir = DATASET_DIR / "images"
    src_labels_dir = DATASET_DIR / "labels"

    if not src_images_dir.exists() or not src_labels_dir.exists():
        print("Error: Asegurate de que existan las carpetas 'images' y 'labels' dentro de dataset_bolivia")
        return

    # Buscar imagenes con extensiones comunes
    valid_exts = {".jpg", ".jpeg", ".png", ".jpg", ".png", ".jpeg", ".bmp", ".JPG", ".PNG", ".JPEG", ".BMP"}
    image_files = [p for p in src_images_dir.iterdir() if p.is_file() and p.suffix in valid_exts]
    
    dataset_pairs = []
    missing_labels = 0

    for img_path in image_files:
        lbl_path = src_labels_dir / f"{img_path.stem}.txt"
        if lbl_path.exists():
            dataset_pairs.append((img_path, lbl_path))
        else:
            missing_labels += 1

    print(f"Imagenes encontradas: {len(image_files)}")
    print(f"Parejas validas (imagen + etiqueta): {len(dataset_pairs)}")
    if missing_labels > 0:
        print(f"Advertencia: {missing_labels} imagenes no tienen un archivo de etiqueta correspondientes.")

    if len(dataset_pairs) == 0:
        print("Error: No se encontraron parejas de imagen y etiqueta validas.")
        return

    # 3. Crear directorios para train y val
    train_img_dir = DATASET_DIR / "train" / "images"
    train_lbl_dir = DATASET_DIR / "train" / "labels"
    val_img_dir = DATASET_DIR / "val" / "images"
    val_lbl_dir = DATASET_DIR / "val" / "labels"

    for d in [train_img_dir, train_lbl_dir, val_img_dir, val_lbl_dir]:
        d.mkdir(parents=True, exist_ok=True)

    # 4. Mezclar y dividir (85% train, 15% val)
    random.seed(42)  # Para reproducibilidad
    random.shuffle(dataset_pairs)

    split_idx = int(len(dataset_pairs) * 0.85)
    train_pairs = dataset_pairs[:split_idx]
    val_pairs = dataset_pairs[split_idx:]

    print(f"Dividiendo dataset:")
    print(f"  - Entrenamiento (85%): {len(train_pairs)} imagenes")
    print(f"  - Validacion (15%): {len(val_pairs)} imagenes")

    # Mover archivos a sus respectivas carpetas
    print("\nMoviendo archivos de Entrenamiento...")
    for img_p, lbl_p in train_pairs:
        shutil.move(str(img_p), str(train_img_dir / img_p.name))
        shutil.move(str(lbl_p), str(train_lbl_dir / lbl_p.name))

    print("Moviendo archivos de Validacion...")
    for img_p, lbl_p in val_pairs:
        shutil.move(str(img_p), str(val_img_dir / img_p.name))
        shutil.move(str(lbl_p), str(val_lbl_dir / lbl_p.name))

    # Limpiar las carpetas originales si quedaron vacias
    try:
        if src_images_dir.exists() and not any(src_images_dir.iterdir()):
            src_images_dir.rmdir()
        if src_labels_dir.exists() and not any(src_labels_dir.iterdir()):
            src_labels_dir.rmdir()
    except Exception as e:
        print(f"Nota al limpiar carpetas vacias: {e}")

    # 5. Generar data.yaml
    data_yaml_path = DATASET_DIR / "data.yaml"
    names_dict = {i: name for i, name in enumerate(classes)}
    
    yaml_data = {
        "path": str(DATASET_DIR.resolve()).replace("\\", "/"),
        "train": "train/images",
        "val": "val/images",
        "nc": len(classes),
        "names": names_dict
    }

    with open(data_yaml_path, "w", encoding="utf-8") as f:
        yaml.dump(yaml_data, f, default_flow_style=False, sort_keys=False)
    print(f"\n[OK] data.yaml creado y guardado en: {data_yaml_path}")

    # 6. Modificar configs/settings.py
    if SETTINGS_PATH.exists():
        print("\nActualizando configs/settings.py...")
        with open(SETTINGS_PATH, "r", encoding="utf-8") as sf:
            content = sf.read()

        # Reemplazar DATASET_DIR line
        # DATASET_DIR = PROJECT_ROOT / "dataset" / "gtsdb" -> DATASET_DIR = PROJECT_ROOT / "dataset" / "dataset_bolivia"
        import re
        content_new, count = re.subn(
            r'DATASET_DIR\s*=\s*PROJECT_ROOT\s*/\s*["\']dataset["\']\s*/\s*["\'][^"\']+["\']',
            'DATASET_DIR = PROJECT_ROOT / "dataset" / "dataset_bolivia"',
            content
        )
        if count > 0:
            print("  - DATASET_DIR actualizado a 'dataset_bolivia'.")
        else:
            print("  - Advertencia: No se pudo actualizar automaticamente DATASET_DIR en settings.py")

        # Formatear el diccionario CLASS_NAMES
        class_dict_str = "CLASS_NAMES = {\n"
        for k, v in names_dict.items():
            class_dict_str += f"    {k}: \"{v}\",\n"
        class_dict_str += "}"

        # Reemplazar el bloque CLASS_NAMES en settings.py
        pattern = r'CLASS_NAMES\s*=\s*\{.*?\}'
        content_new, count = re.subn(pattern, class_dict_str, content_new, flags=re.DOTALL)
        if count > 0:
            print("  - CLASS_NAMES actualizado con las clases de Bolivia.")
        else:
            # Intentar otra forma si la primera fallo
            lines = content_new.splitlines()
            new_lines = []
            in_class_block = False
            for line in lines:
                if line.strip().startswith("CLASS_NAMES = {"):
                    in_class_block = True
                    new_lines.append(class_dict_str)
                    continue
                if in_class_block:
                    if line.strip().startswith("}"):
                        in_class_block = False
                    continue
                new_lines.append(line)
            content_new = "\n".join(new_lines) + "\n"
            print("  - CLASS_NAMES actualizado con metodos de linea.")

        with open(SETTINGS_PATH, "w", encoding="utf-8") as sf:
            sf.write(content_new)
        print("[OK] configs/settings.py actualizado con exito.")

    print("=" * 60)
    print("PROCESO DE PREPARACION COMPLETADO CON EXITO.")
    print("El dataset esta listo para entrenar.")
    print("=" * 60)

if __name__ == "__main__":
    main()
