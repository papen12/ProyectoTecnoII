import sys
import importlib

# Force UTF-8 stdout if possible, or just use plain ASCII
packages_to_test = [
    "torch",
    "torchvision",
    "ultralytics",
    "transformers",
    "numpy",
    "pandas",
    "scipy",
    "sklearn",
    "matplotlib",
    "seaborn",
    "tabulate"
]

print("=" * 60)
print(f"Python Version: {sys.version}")
print(f"Executable: {sys.executable}")
print("=" * 60)

all_successful = True

for package in packages_to_test:
    try:
        mod = importlib.import_module(package)
        version = getattr(mod, "__version__", "unknown version")
        print(f"[OK] {package:<15} version: {version}")
    except ImportError as e:
        print(f"[FAIL] {package:<15} - Error: {e}")
        all_successful = False

print("=" * 60)
if all_successful:
    print("All imports are verified and working perfectly!")
else:
    print("Some packages failed to import. Please check details above.")
print("=" * 60)

# PyTorch specific verification
if "torch" in sys.modules:
    import torch
    print(f"CUDA Available: {torch.cuda.is_available()}")
    if torch.cuda.is_available():
        print(f"CUDA Device: {torch.cuda.get_device_name(0)}")
    print("=" * 60)
