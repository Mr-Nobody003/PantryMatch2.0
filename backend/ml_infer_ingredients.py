"""
Inference utilities for the trained ingredient classifier (ONNX Runtime).

Loads:
  backend/models/ingredients_resnet18.onnx
  backend/models/yolov8n.onnx
  backend/models/class_names.json

Provides:
  - load_model()
  - predict_ingredients_batch_from_bytes(...)
  - predict_boxes_onnx(...) - Lightweight YOLOv8 detection via ONNX
"""

from __future__ import annotations

import io
import json
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
from PIL import Image

try:
    import onnxruntime as ort
except ImportError:
    ort = None

MODELS_DIR = Path(__file__).resolve().parent / "models"
MODEL_PATH = MODELS_DIR / "best_enhanced_5fold_model.onnx"
YOLO_PATH = MODELS_DIR / "yolov8n.onnx"
CLASSES_PATH = MODELS_DIR / "class_names.json"

# Global sessions to avoid reloading
_RESNET_SESS = None
_YOLO_SESS = None

def load_model():
    """
    Load the trained ResNet18 model via ONNX Runtime and class names.
    """
    global _RESNET_SESS
    if ort is None:
        raise ImportError("onnxruntime is not installed. Please add it to requirements.txt")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(f"ONNX model file not found at {MODEL_PATH}")

    if not CLASSES_PATH.exists():
        raise FileNotFoundError(f"Class names file not found at {CLASSES_PATH}")

    with open(CLASSES_PATH, "r") as f:
        class_names = json.load(f)

    if _RESNET_SESS is None:
        sess_options = ort.SessionOptions()
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        # Force single thread for Render stability
        sess_options.intra_op_num_threads = 1
        sess_options.inter_op_num_threads = 1
        _RESNET_SESS = ort.InferenceSession(str(MODEL_PATH), sess_options=sess_options, providers=['CPUExecutionProvider'])

    return _RESNET_SESS, class_names, None

def _preprocess_resnet(image_bytes: bytes) -> np.ndarray:
    """Resize(224), ToTensor, Normalize for ResNet18."""
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224), Image.Resampling.BILINEAR)
    img_data = np.array(img).astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
    img_data = (img_data - mean) / std
    return np.transpose(img_data, (2, 0, 1))

def predict_ingredients_batch_from_bytes(
    model,
    class_names: List[str],
    device,
    image_bytes_list: List[bytes],
    top_k: int = 5,
    max_batch_size: int = 8
) -> List[List[Dict[str, float]]]:
    """Run inference on multiple images using ONNX batching."""
    if not image_bytes_list:
        return []

    all_results = []
    input_name = model.get_inputs()[0].name

    def softmax(x):
        e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return e_x / np.sum(e_x, axis=-1, keepdims=True)

    for i in range(0, len(image_bytes_list), max_batch_size):
        chunk_bytes = image_bytes_list[i : i + max_batch_size]
        tensors = [_preprocess_resnet(img_bytes) for img_bytes in chunk_bytes]
        batch_tensor = np.stack(tensors, axis=0)
        outputs = model.run(None, {input_name: batch_tensor})[0]
        probs = softmax(outputs)
        top_k_curr = min(top_k, len(class_names))
        
        for j in range(len(chunk_bytes)):
            prob_row = probs[j]
            indices = prob_row.argsort()[::-1][:top_k_curr]
            res = [{"name": class_names[idx], "prob": float(prob_row[idx])} for idx in indices]
            all_results.append(res)
            
    return all_results

def predict_ingredients_from_bytes(model, class_names, device, image_bytes, top_k=5):
    res = predict_ingredients_batch_from_bytes(model, class_names, device, [image_bytes], top_k=top_k)
    return res[0] if res else []

def predict_boxes_onnx(image_bytes: bytes, conf_thres=0.4) -> List[Tuple[int, int, int, int]]:
    """
    Lightweight YOLOv8 detection via ONNX Runtime.
    Returns list of [x1, y1, x2, y2] bounding boxes.
    """
    global _YOLO_SESS
    if not YOLO_PATH.exists():
        return []

    if _YOLO_SESS is None:
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = 1
        _YOLO_SESS = ort.InferenceSession(str(YOLO_PATH), sess_options=sess_options, providers=['CPUExecutionProvider'])

    img_raw = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    orig_w, orig_h = img_raw.size
    
    # YOLOv8 input is 640x640
    img = img_raw.resize((640, 640), Image.Resampling.BILINEAR)
    img_data = np.array(img).astype(np.float32) / 255.0
    img_data = np.transpose(img_data, (2, 0, 1))
    img_data = np.expand_dims(img_data, axis=0)

    input_name = _YOLO_SESS.get_inputs()[0].name
    outputs = _YOLO_SESS.run(None, {input_name: img_data})[0] # (1, 84, 8400)
    
    # Current YOLOv8n-ONNX output: [x_center, y_center, width, height, class0_conf, class1_conf, ...]
    output = np.squeeze(outputs) # (84, 8400)
    boxes = output[:4, :] # (4, 8400)
    scores = np.max(output[4:, :], axis=0) # (8400,)
    
    # Filter by confidence
    mask = scores > conf_thres
    boxes = boxes[:, mask]
    scores = scores[mask]
    
    if boxes.shape[1] == 0:
        return []

    # Convert center to corners
    # YOLO box: [cx, cy, w, h]
    results = []
    for i in range(boxes.shape[1]):
        cx, cy, w, h = boxes[:, i]
        x1 = (cx - w/2) * (orig_w / 640)
        y1 = (cy - h/2) * (orig_h / 640)
        x2 = (cx + w/2) * (orig_w / 640)
        y2 = (cy + h/2) * (orig_h / 640)
        results.append((int(x1), int(y1), int(x2), int(y2)))

    # Simple NMS (Non-Maximum Suppression)
    if not results:
        return []
        
    final_boxes = []
    # Sort by score desc
    sorted_idxs = np.argsort(scores)[::-1]
    
    def iou(boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
        boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
        return interArea / float(boxAArea + boxBArea - interArea)

    keep = []
    for i in sorted_idxs:
        box = results[i]
        is_keep = True
        for k in keep:
            if iou(box, results[k]) > 0.45:
                is_keep = False
                break
        if is_keep:
            keep.append(i)
            final_boxes.append(box)
            if len(final_boxes) > 10: # Limit crops for memory
                break
                
    return final_boxes
