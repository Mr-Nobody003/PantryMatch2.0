import torch
import json
from pathlib import Path
from torchvision import models

def convert():
    MODELS_DIR = Path("models")
    MODEL_PATH = MODELS_DIR / "best_enhanced_5fold_model.pt"
    
    if not MODEL_PATH.exists():
        print(f"Error: Could not find {MODEL_PATH}")
        print("Please ensure you have run: git checkout main -- backend/models/best_enhanced_5fold_model.pt backend/models/ingredients_classes.txt")
        return
        
    print(f"Loading PyTorch model from {MODEL_PATH}...")
    checkpoint = torch.load(MODEL_PATH, map_location="cpu")
    class_names = checkpoint.get("class_names")
    
    if class_names is None:
        raise ValueError("class_names not found in checkpoint.")
        
    num_classes = len(class_names)
    model = models.resnet18(weights=None)
    in_features = model.fc.in_features
    model.fc = torch.nn.Linear(in_features, num_classes)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    
    MODELS_DIR.mkdir(exist_ok=True)
    
    print("Saving class names...")
    with open(MODELS_DIR / "class_names.json", "w") as f:
        json.dump(class_names, f)
        
    print("Exporting to ONNX...")
    # Dynamic axes allows for batching
    dummy_input = torch.randn(1, 3, 224, 224)
    onnx_path = MODELS_DIR / "best_enhanced_5fold_model.onnx"
    
    torch.onnx.export(
        model, 
        dummy_input, 
        str(onnx_path),
        export_params=True,
        opset_version=14,
        do_constant_folding=True,
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
    )
    print(f"Exported successfully to {onnx_path}!")

if __name__ == "__main__":
    convert()
