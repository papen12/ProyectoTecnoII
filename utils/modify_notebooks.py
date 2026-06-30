import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

def modify_exploration_notebook():
    notebook_path = PROJECT_ROOT / "notebooks" / "02_dataset_exploration.ipynb"
    print(f"Modificando notebook de exploracion: {notebook_path.name}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for cell in data["cells"]:
        if cell["cell_type"] == "code" and any("Asegúrate de colocar tu exportación de Roboflow" in line for line in cell["source"]):
            new_source = [
                "dataset_path = Path(settings.DATASET_DIR)\n",
                "print(f\"Ruta del dataset: {dataset_path.resolve()}\")\n",
                "\n",
                "if not dataset_path.exists():\n",
                "    print(\"ATENCION: La carpeta del dataset no existe. Iniciando descarga automatizada...\")\n",
                "    from utils.download_dataset import download_and_extract\n",
                "    success = download_and_extract()\n",
                "    if success:\n",
                "        import importlib\n",
                "        import configs.settings\n",
                "        importlib.reload(configs.settings)\n",
                "        print(\"Dataset descargado e inicializado correctamente.\")\n",
                "    else:\n",
                "        print(\"Error durante la descarga del dataset.\")\n",
                "else:\n",
                "    # Listar subdirectorios para comprobar la estructura\n",
                "    for child in dataset_path.iterdir():\n",
                "        print(f\"  - {child.name} ({'Directorio' if child.is_dir() else 'Archivo'})\")"
            ]
            cell["source"] = new_source
            print("Celda de verificacion de dataset modificada con exito.")
            break
            
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)

def modify_training_notebook():
    notebook_path = PROJECT_ROOT / "notebooks" / "04_training_yolo.ipynb"
    print(f"Modificando notebook de entrenamiento: {notebook_path.name}")
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    for cell in data["cells"]:
        if cell["cell_type"] == "code" and any("results = model.train(" in line for line in cell["source"]):
            new_source = [
                "# 2. Iniciar el entrenamiento\n",
                "# Asegúrate de tener tu archivo dataset/roboflow/data.yaml listo\n",
                "data_yaml_path = Path(settings.DATASET_DIR) / \"data.yaml\"\n",
                "\n",
                "print(f\"Buscando configuración del dataset en: {data_yaml_path.resolve()}\")\n",
                "if not data_yaml_path.exists():\n",
                "    print(\"dataset/roboflow/data.yaml no se encuentra. Coloca tu exportación antes de entrenar.\")\n",
                "else:\n",
                "    print(\"Iniciando entrenamiento local de prueba (3 épocas)...\\n\")\n",
                "    results = model.train(\n",
                "        data=str(data_yaml_path.resolve()),\n",
                "        epochs=3,  # 3 épocas para una verificación rápida local en CPU\n",
                "        imgsz=settings.IMG_SIZE,\n",
                "        batch=settings.BATCH_SIZE,\n",
                "        project=str(settings.OUTPUTS_DIR / 'training'),\n",
                "        name='yolov8s_traffic_signs',\n",
                "        device='cpu'  # Forzar CPU para compatibilidad garantizada\n",
                "    )"
            ]
            cell["source"] = new_source
            print("Celda de entrenamiento de YOLO modificada con exito.")
            break
            
    with open(notebook_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)

if __name__ == "__main__":
    modify_exploration_notebook()
    modify_training_notebook()
