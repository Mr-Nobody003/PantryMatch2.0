import torch
import json
from pathlib import Path
from ml_infer_ingredients import load_model

def convert():
    print("Loading PyTorch model...")
    model, class_names, device = load_model()
    
    MODELS_DIR = Path("models")
    MODELS_DIR.mkdir(exist_ok=True)
    
    print("Saving class names...")
    with open(MODELS_DIR / "class_names.json", "w") as f:
        json.dump(class_names, f)
        
    print("Exporting to ONNX...")
    # Dynamic axes allows for batching
    dummy_input = torch.randn(1, 3, 224, 224, device=device)
    onnx_path = MODELS_DIR / "ingredients_resnet18.onnx"
    
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
