import os
import sys

print("Building caches for Render deployment...")


try:
    print("Building Matplotlib font cache...")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots()
    ax.text(0.5, 0.5, "test")
    plt.close(fig)
    print("Matplotlib font cache built successfully.")
except ImportError:
    print("Matplotlib is not installed. Skipping font cache.")

try:
    print("Downloading YOLOv8n model...")
    from ultralytics import YOLO
    model = YOLO("yolov8n.pt")
    print("YOLOv8n model downloaded successfully.")
except ImportError:
    print("Ultralytics is not installed. Skipping YOLO download.")
except Exception as e:
    print(f"Error during YOLO model download: {e}")

try:
    print("Pre-loading PyTorch models (ResNet)...")
    from ml_infer_ingredients import load_model
    # load_model() initializes the PyTorch topology
    model, class_names, device = load_model()
    print("PyTorch model loaded successfully.")
except FileNotFoundError:
    print("ingredients_resnet18.pt not found. Skipping PyTorch ResNet load.")
except ImportError:
    print("PyTorch or ml_infer_ingredients not found. Skipping PyTorch load.")
except Exception as e:
    print(f"Error during ResNet load: {e}")

print("Pre-build cache population complete!")
