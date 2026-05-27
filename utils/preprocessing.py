from pathlib import Path
import pandas as pd
from configs import settings

def validate_dataset(dataset_dir: str | Path) -> dict:
    """Verifies that every image has a corresponding label file in the YOLO dataset structure."""
    dataset_path = Path(dataset_dir)
    results = {}
    
    for split in ['train', 'val', 'test']:
        img_dir = dataset_path / split / "images"
        lbl_dir = dataset_path / split / "labels"
        
        if not img_dir.exists():
            continue
            
        images = {p.stem: p for p in img_dir.iterdir() if p.suffix.lower() in ('.jpg', '.png', '.jpeg', '.bmp')}
        labels = {p.stem: p for p in lbl_dir.iterdir() if p.suffix.lower() == '.txt'} if lbl_dir.exists() else {}
        
        missing_labels = []
        for stem in images:
            if stem not in labels:
                missing_labels.append(images[stem].name)
                
        results[split] = {
            "total_images": len(images),
            "total_labels": len(labels),
            "missing_labels": missing_labels
        }
    return results

def verify_yolo_format(label_file: str | Path) -> bool:
    """Verifies that bounding boxes inside a .txt label file conform to the [class x y w h] normalizations."""
    file_path = Path(label_file)
    if not file_path.exists() or file_path.stat().st_size == 0:
        # Empty text file is valid for background images in YOLO
        return True
        
    try:
        with open(file_path, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 5:
                    return False
                cls_id = int(parts[0])
                coords = [float(x) for x in parts[1:]]
                for val in coords:
                    if not (0.0 <= val <= 1.0):
                        return False
        return True
    except Exception:
        return False

def get_class_distribution(dataset_dir: str | Path) -> pd.DataFrame:
    """Counts the occurrences of each class index across splits in the dataset."""
    dataset_path = Path(dataset_dir)
    counts = []
    
    for split in ['train', 'val', 'test']:
        lbl_dir = dataset_path / split / "labels"
        if not lbl_dir.exists():
            continue
            
        for file in lbl_dir.glob("*.txt"):
            try:
                with open(file, 'r') as f:
                    for line in f:
                        parts = line.strip().split()
                        if len(parts) > 0:
                            cls_id = int(parts[0])
                            counts.append({"split": split, "class_id": cls_id})
            except Exception:
                pass
                
    df = pd.DataFrame(counts)
    if df.empty:
        return pd.DataFrame(columns=["split", "class_id", "count"])
    return df.groupby(["split", "class_id"]).size().reset_index(name="count")
