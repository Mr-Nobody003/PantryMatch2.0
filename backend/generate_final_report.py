"""
Generate final 5-fold cross-validation report from existing trained models.
This script skips training and just creates the final report and best model selection.
"""

import os
import json
import numpy as np
from pathlib import Path
import torch
import shutil
from collections import Counter

def load_fold_metrics():
    """Load metrics from existing trained fold models."""
    models_dir = Path("models")
    fold_metrics = []
    
    print("Loading existing fold models...")
    
    for fold_idx in range(1, 6):
        model_path = models_dir / f"fold_{fold_idx}_ingredients_resnet18.pt"
        
        if model_path.exists():
            try:
                checkpoint = torch.load(model_path, map_location='cpu')
                
                # Extract metrics from checkpoint
                fold_metric = {
                    'fold': fold_idx,
                    'best_val_acc': checkpoint.get('val_acc', 0.0),
                    'best_f1': checkpoint.get('val_f1', 0.0),
                    'best_precision': checkpoint.get('val_precision', 0.0),
                    'best_recall': checkpoint.get('val_recall', 0.0),
                    'class_names': checkpoint.get('class_names', [])
                }
                fold_metrics.append(fold_metric)
                print(f"Fold {fold_idx}: Val Acc = {fold_metric['best_val_acc']:.4f}, F1 = {fold_metric['best_f1']:.4f}")
                
            except Exception as e:
                print(f"Error loading fold {fold_idx}: {e}")
        else:
            print(f"Model not found: {model_path}")
    
    return fold_metrics

def generate_final_report(fold_metrics):
    """Generate final 5-fold cross-validation report."""
    models_dir = Path("models")
    
    if not fold_metrics:
        print("No fold metrics found!")
        return
    
    # Calculate overall metrics
    val_accs = [fold['best_val_acc'] for fold in fold_metrics]
    val_f1s = [fold['best_f1'] for fold in fold_metrics]
    mean_acc = np.mean(val_accs)
    std_acc = np.std(val_accs)
    mean_f1 = np.mean(val_f1s)
    std_f1 = np.std(val_f1s)
    
    # Find best fold
    best_fold_idx = np.argmax(val_accs)
    best_fold = fold_metrics[best_fold_idx]
    
    # Generate report
    report = f"""
ENHANCED 5-FOLD CROSS-VALIDATION REPORT
==========================================

OVERALL RESULTS:
  Mean Validation Accuracy: {mean_acc:.4f} ± {std_acc:.4f}
  Mean F1-Score: {mean_f1:.4f} ± {std_f1:.4f}
  Best Fold: {best_fold_idx + 1} (Acc: {best_fold['best_val_acc']:.4f}, F1: {best_fold['best_f1']:.4f})
  Worst Fold: {np.argmin(val_accs) + 1} (Acc: {np.min(val_accs):.4f})

PER-FOLD RESULTS:
"""
    
    for i, fold in enumerate(fold_metrics):
        report += f"""
Fold {i + 1}:
  Best Val Acc: {fold['best_val_acc']:.4f}
  Best F1-Score: {fold['best_f1']:.4f}
  Best Precision: {fold['best_precision']:.4f}
  Best Recall: {fold['best_recall']:.4f}
"""
    
    # Save report
    report_path = models_dir / "enhanced_5fold_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    # Save metrics as JSON
    metrics_dict = {
        'config': {
            'folds': 5,
            'epochs': 15,
            'batch_size': 32,
            'learning_rate': 0.001,
            'num_classes': len(best_fold['class_names'])
        },
        'results': {
            'mean_val_acc': float(mean_acc),
            'std_val_acc': float(std_acc),
            'mean_f1': float(mean_f1),
            'std_f1': float(std_f1),
            'best_fold': int(best_fold_idx + 1),
            'best_val_acc': float(best_fold['best_val_acc']),
            'best_f1': float(best_fold['best_f1']),
            'fold_val_accs': [float(acc) for acc in val_accs],
            'fold_f1s': [float(f1) for f1 in val_f1s]
        },
        'fold_metrics': fold_metrics
    }
    
    json_path = models_dir / "enhanced_5fold_metrics.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_dict, f, indent=2)
    
    # Copy best model
    best_model_path = models_dir / f"fold_{best_fold_idx + 1}_ingredients_resnet18.pt"
    ensemble_model_path = models_dir / "best_enhanced_5fold_model.pt"
    
    if best_model_path.exists():
        shutil.copy2(best_model_path, ensemble_model_path)
        print(f"Best model copied to: {ensemble_model_path}")
    
    print(f"\nEnhanced 5-fold cross-validation complete!")
    print(f"Mean validation accuracy: {mean_acc:.4f} ± {std_acc:.4f}")
    print(f"Mean F1-score: {mean_f1:.4f} ± {std_f1:.4f}")
    print(f"Best performing fold: {best_fold_idx + 1} (Acc: {best_fold['best_val_acc']:.4f}, F1: {best_fold['best_f1']:.4f})")
    print(f"Reports saved to: {report_path} and {json_path}")

if __name__ == "__main__":
    fold_metrics = load_fold_metrics()
    generate_final_report(fold_metrics)
