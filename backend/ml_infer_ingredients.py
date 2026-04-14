"""
Inference utilities for the trained ingredient classifier (ONNX Runtime).

Loads:
  backend/models/ingredients_resnet18.onnx
  backend/models/class_names.json

Provides:
  - load_model()
  - predict_ingredients_batch_from_bytes(model, class_names, dummy_device, image_bytes_list, top_k=5)
  - predict_ingredients_from_bytes(...) (legacy wrapper)

Usage example (from Python, after training):

  from ml_infer_ingredients import load_model, predict_ingredients_from_bytes

  model, class_names, _ = load_model()
  with open("some_image.jpg", "rb") as f:
      image_bytes = f.read()
  preds = predict_ingredients_from_bytes(model, class_names, None, image_bytes, top_k=5)
  print(preds)  # List[{"name": ..., "prob": ...}, ...]
"""

from __future__ import annotations

import io
import json
import numpy as np
from pathlib import Path
from typing import List, Dict
from PIL import Image

try:
    import onnxruntime as ort
except ImportError:
    ort = None

MODELS_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODELS_DIR / "ingredients_resnet18.onnx"
CLASSES_PATH = MODELS_DIR / "class_names.json"


def load_model():
    """
    Load the trained ResNet18 model via ONNX Runtime and class names.
    This eliminates PyTorch module bloat completely, making memory usage tiny and safe for Render Free Tier.

    Returns:
      model: onnxruntime.InferenceSession
      class_names: List[str]
      device: None (maintained for backwards compatibility with app.py)
    """
    if ort is None:
        raise ImportError("onnxruntime is not installed. Please add it to requirements.txt")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"ONNX model file not found at {MODEL_PATH}. Convert the model first."
        )

    if not CLASSES_PATH.exists():
        raise FileNotFoundError(
            f"Class names file not found at {CLASSES_PATH}. Export the model first."
        )

    with open(CLASSES_PATH, "r") as f:
        class_names = json.load(f)

    # Initialize ONNX inference session
    sess_options = ort.SessionOptions()
    sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    model = ort.InferenceSession(str(MODEL_PATH), sess_options=sess_options, providers=['CPUExecutionProvider'])

    # Device is None since ONNX implicitly handles CPU/GPU execution via providers
    device = None

    return model, class_names, device


def _preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Replicates torchvision Transforms (Resize(224), ToTensor, Normalize) in pure Numpy + Pillow.
    Returns array of shape (1, 3, 224, 224) as float32.
    """
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    
    # 1. Resize to (224, 224)
    img = img.resize((224, 224), Image.Resampling.BILINEAR)
    
    # 2. ToTensor (convert to float32 and scale 0-1)
    img_data = np.array(img).astype(np.float32) / 255.0
    
    # 3. Normalize using ImageNet means/stds
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_data = (img_data - mean) / std
    
    # 4. HWC (Height, Width, Channels) to CHW (Channels, Height, Width)
    img_data = np.transpose(img_data, (2, 0, 1))
    
    return img_data


def predict_ingredients_from_bytes(
    model,
    class_names: List[str],
    device,
    image_bytes: bytes,
    top_k: int = 5,
) -> List[Dict[str, float]]:
    """
    Run inference on a single image given as raw bytes.

    Returns:
      List of dicts: [{"name": ingredient_name, "prob": probability}, ...] sorted by prob desc.
    """
    # Simply wrap the batch version
    res = predict_ingredients_batch_from_bytes(
        model, class_names, device, [image_bytes], top_k=top_k, max_batch_size=1
    )
    return res[0] if res else []


def predict_ingredients_batch_from_bytes(
    model,
    class_names: List[str],
    device,
    image_bytes_list: List[bytes],
    top_k: int = 5,
    max_batch_size: int = 8
) -> List[List[Dict[str, float]]]:
    """
    Run inference on multiple images using ONNX batching to speed up processing
    and avoid worker timeouts on Render.
    """
    if not image_bytes_list:
        return []

    all_results = []
    
    input_name = model.get_inputs()[0].name

    def softmax(x):
        e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return e_x / np.sum(e_x, axis=-1, keepdims=True)

    # Process in chunks to prevent memory spikes on large numbers of crops
    for i in range(0, len(image_bytes_list), max_batch_size):
        chunk_bytes = image_bytes_list[i : i + max_batch_size]
        tensors = []
        for img_bytes in chunk_bytes:
            tensors.append(_preprocess_image(img_bytes))
            
        # Stack into (N, C, H, W)
        batch_tensor = np.stack(tensors, axis=0)
        
        # ONNX inference
        outputs = model.run(None, {input_name: batch_tensor})[0]
        
        probs = softmax(outputs)
            
        top_k_curr = min(top_k, len(class_names))
        
        for j in range(len(chunk_bytes)):
            prob_row = probs[j]
            indices = prob_row.argsort()[::-1][:top_k_curr]
            
            res = []
            for idx in indices:
                res.append({
                    "name": class_names[idx],
                    "prob": float(prob_row[idx]),
                })
            all_results.append(res)
            
    return all_results
