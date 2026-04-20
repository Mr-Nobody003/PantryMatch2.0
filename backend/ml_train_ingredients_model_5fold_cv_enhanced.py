"""
Train a ResNet-based ingredient classifier using 5-fold cross-validation with enhanced metrics.

This script implements 5-fold cross-validation with F1-measures,
and comprehensive evaluation metrics for your imbalanced dataset.

Usage (from backend/ directory, inside venv):
  pip install torch torchvision scikit-learn matplotlib
  python ml_train_ingredients_model_4fold_cv_enhanced.py --epochs 15 --batch-size 32
"""

import argparse
import os
import numpy as np
import matplotlib.pyplot as plt

# import seaborn as sns  # Confusion matrix generation disabled
from pathlib import Path
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)
import json

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import datasets, models, transforms
from collections import Counter
import warnings

warnings.filterwarnings("ignore")


def get_transforms():
    """Get training and validation transforms."""
    mean = [0.485, 0.456, 0.406]
    std = [0.229, 0.224, 0.225]

    train_transforms = transforms.Compose(
        [
            transforms.Resize((256, 256)),
            transforms.RandomResizedCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ColorJitter(
                brightness=0.2, contrast=0.2, saturation=0.2, hue=0.05
            ),
            transforms.RandomRotation(10),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ]
    )

    val_transforms = transforms.Compose(
        [
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean, std),
        ]
    )

    return train_transforms, val_transforms


def build_model(num_classes: int):
    """Build a ResNet18 model for classification."""
    model = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)
    return model


def train_one_epoch(model, loader, criterion, optimizer, device):
    """Train model for one epoch."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    for inputs, labels in loader:
        inputs = inputs.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * inputs.size(0)
        _, preds = torch.max(outputs, 1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

    epoch_loss = running_loss / total if total > 0 else 0.0
    epoch_acc = correct / total if total > 0 else 0.0
    return epoch_loss, epoch_acc


def evaluate_enhanced(model, loader, criterion, device, class_names):
    """Evaluate model and return detailed metrics including F1 and confusion matrix."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in loader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, labels)

            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    epoch_loss = running_loss / total if total > 0 else 0.0
    epoch_acc = correct / total if total > 0 else 0.0

    # Calculate detailed metrics
    precision = precision_score(
        all_labels, all_preds, average="weighted", zero_division=0
    )
    recall = recall_score(all_labels, all_preds, average="weighted", zero_division=0)
    f1 = f1_score(all_labels, all_preds, average="weighted", zero_division=0)

    # Per-class metrics
    per_class_precision = precision_score(
        all_labels,
        all_preds,
        average=None,
        zero_division=0,
        labels=range(len(class_names)),
    )
    per_class_recall = recall_score(
        all_labels,
        all_preds,
        average=None,
        zero_division=0,
        labels=range(len(class_names)),
    )
    per_class_f1 = f1_score(
        all_labels,
        all_preds,
        average=None,
        zero_division=0,
        labels=range(len(class_names)),
    )

    # Confusion matrix
    cm = confusion_matrix(all_labels, all_preds, labels=range(len(class_names)))

    return {
        "loss": epoch_loss,
        "accuracy": epoch_acc,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "per_class_precision": per_class_precision,
        "per_class_recall": per_class_recall,
        "per_class_f1": per_class_f1,
        "confusion_matrix": cm,
        "predictions": all_preds,
        "labels": all_labels,
    }


def create_5fold_splits(dataset):
    """Create stratified 5-fold cross-validation splits."""
    targets = [dataset.targets[i] for i in range(len(dataset))]

    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

    splits = []
    for fold_idx, (train_idx, val_idx) in enumerate(
        skf.split(np.zeros(len(targets)), targets)
    ):
        splits.append((train_idx, val_idx))

    return splits


def train_fold_enhanced(fold_idx, train_dataset, val_dataset, class_names, args):
    """Train model for a single fold with enhanced metrics."""
    print(f"\n{'='*60}")
    print(f"Training Fold {fold_idx + 1}/5")
    print(f"Train samples: {len(train_dataset)}, Val samples: {len(val_dataset)}")
    print(f"{'='*60}")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Create data loaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=args.num_workers,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=args.num_workers,
        pin_memory=True,
    )

    # Build model
    model = build_model(num_classes=len(class_names)).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=2
    )

    # Training loop
    best_val_acc = 0.0
    fold_metrics = {
        "fold": fold_idx + 1,
        "train_losses": [],
        "train_accs": [],
        "val_losses": [],
        "val_accs": [],
        "val_precisions": [],
        "val_recalls": [],
        "val_f1s": [],
        "best_val_acc": 0.0,
        "best_metrics": None,
    }

    for epoch in range(args.epochs):
        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device
        )
        val_metrics = evaluate_enhanced(
            model, val_loader, criterion, device, class_names
        )

        scheduler.step(val_metrics["loss"])

        fold_metrics["train_losses"].append(train_loss)
        fold_metrics["train_accs"].append(train_acc)
        fold_metrics["val_losses"].append(val_metrics["loss"])
        fold_metrics["val_accs"].append(val_metrics["accuracy"])
        fold_metrics["val_precisions"].append(val_metrics["precision"])
        fold_metrics["val_recalls"].append(val_metrics["recall"])
        fold_metrics["val_f1s"].append(val_metrics["f1"])

        print(
            f"Epoch {epoch + 1:2d} | "
            f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc*100:6.2f}% | "
            f"Val Loss: {val_metrics['loss']:.4f} | Val Acc: {val_metrics['accuracy']*100:6.2f}% | "
            f"F1: {val_metrics['f1']:.4f}"
        )

        # Save best model for this fold
        if val_metrics["accuracy"] > best_val_acc:
            best_val_acc = val_metrics["accuracy"]
            fold_metrics["best_val_acc"] = best_val_acc
            fold_metrics["best_metrics"] = val_metrics

            # Save model
            models_dir = Path(__file__).resolve().parent / "models"
            models_dir.mkdir(exist_ok=True)
            model_path = models_dir / f"fold_{fold_idx + 1}_ingredients_resnet18.pt"

            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "class_names": class_names,
                    "fold_idx": fold_idx + 1,
                    "val_acc": best_val_acc,
                    "val_f1": val_metrics["f1"],
                    "val_precision": val_metrics["precision"],
                    "val_recall": val_metrics["recall"],
                },
                model_path,
            )

            print(
                f"Saved new best model for fold {fold_idx + 1} (val_acc={best_val_acc:.4f}, f1={val_metrics['f1']:.4f})"
            )

    return fold_metrics


def save_confusion_matrix(cm, class_names, fold_idx, models_dir):
    """Save confusion matrix as image."""
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        cm,
        annot=True,
        fmt="d",
        cmap="Blues",
        xticklabels=class_names,
        yticklabels=class_names,
    )
    plt.title(f"Confusion Matrix - Fold {fold_idx + 1}")
    plt.ylabel("True Label")
    plt.xlabel("Predicted Label")
    plt.tight_layout()

    cm_path = models_dir / f"confusion_matrix_fold_{fold_idx + 1}.png"
    plt.savefig(cm_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved confusion matrix: {cm_path}")


def generate_enhanced_5fold_report(all_fold_metrics, class_names, class_counts, args):
    """Generate comprehensive 5-fold cross-validation report with F1 and confusion matrix."""
    models_dir = Path(__file__).resolve().parent / "models"

    # Calculate overall metrics
    val_accs = [fold["best_val_acc"] for fold in all_fold_metrics]
    val_f1s = [
        fold["best_metrics"]["f1"] if fold["best_metrics"] else 0
        for fold in all_fold_metrics
    ]
    mean_acc = np.mean(val_accs)
    std_acc = np.std(val_accs)
    mean_f1 = np.mean(val_f1s)
    std_f1 = np.std(val_f1s)

    # Find best fold
    best_fold_idx = np.argmax(val_accs)
    best_fold = all_fold_metrics[best_fold_idx]

    # Generate text report
    report = f"""
ENHANCED 4-FOLD CROSS-VALIDATION REPORT
==========================================

Dataset Analysis:
- Total classes: {len(class_names)}
- Samples per class range: {min(class_counts.values())} - {max(class_counts.values())}
- Small classes (<50): {sum(1 for c in class_counts.values() if c < 50)}
- Medium classes (50-70): {sum(1 for c in class_counts.values() if 50 <= c < 70)}
- Large classes (>70): {sum(1 for c in class_counts.values() if c >= 70)}

Configuration:
- Folds: 4 (fixed)
- Epochs per fold: {args.epochs}
- Batch size: {args.batch_size}
- Learning rate: {args.lr}

EPOCH-WISE PERFORMANCE SUMMARY:
"""

    # Add epoch-wise performance table for best fold
    if best_fold["best_metrics"]:
        report += f"""
Best Fold ({best_fold_idx + 1}) Epoch-wise Performance:
{'Epoch':<6} {'Train Loss':<12} {'Train Acc (%)':<15} {'Val Loss':<12} {'Val Acc (%)':<15} {'F1-Score':<10}
"""
        for epoch in range(args.epochs):
            train_loss = best_fold["train_losses"][epoch]
            train_acc = best_fold["train_accs"][epoch] * 100
            val_loss = best_fold["val_losses"][epoch]
            val_acc = best_fold["val_accs"][epoch] * 100
            f1_score = best_fold["val_f1s"][epoch]
            report += f"{epoch+1:<6} {train_loss:<12.4f} {train_acc:<15.2f} {val_loss:<12.4f} {val_acc:<15.2f} {f1_score:<10.4f}\n"

    report += f"""
OVERALL RESULTS:
  Mean Validation Accuracy: {mean_acc:.4f} ± {std_acc:.4f}
  Mean F1-Score: {mean_f1:.4f} ± {std_f1:.4f}
  Best Fold: {best_fold_idx + 1} (Acc: {best_fold['best_val_acc']:.4f}, F1: {best_fold['best_metrics']['f1']:.4f})
  Worst Fold: {np.argmin(val_accs) + 1} (Acc: {np.min(val_accs):.4f})

PER-FOLD RESULTS:
"""

    for i, fold in enumerate(all_fold_metrics):
        best_f1 = fold["best_metrics"]["f1"] if fold["best_metrics"] else 0
        report += f"""
Fold {i + 1}:
  Best Val Acc: {fold['best_val_acc']:.4f}
  Best F1-Score: {best_f1:.4f}
  Final Train Acc: {fold['train_accs'][-1]*100:.2f}%
  Final Val Acc: {fold['val_accs'][-1]*100:.2f}%
"""

    # Add per-class metrics for best fold
    if best_fold["best_metrics"]:
        report += "\nBEST FOLD - PER-CLASS METRICS:\n"
        report += f"{'Class':<20} {'Precision':<10} {'Recall':<10} {'F1-Score':<10} {'Support':<8}\n"

        for i, class_name in enumerate(class_names):
            precision = best_fold["best_metrics"]["per_class_precision"][i]
            recall = best_fold["best_metrics"]["per_class_recall"][i]
            f1 = best_fold["best_metrics"]["per_class_f1"][i]

            # Count support (number of true samples)
            support = sum(
                1 for label in best_fold["best_metrics"]["labels"] if label == i
            )

            report += f"{class_name:<20} {precision:<10.4f} {recall:<10.4f} {f1:<10.4f} {support:<8}\n"

    # Save detailed classification report for best fold
    if best_fold["best_metrics"]:
        report += "\nDETAILED CLASSIFICATION REPORT (Best Fold):\n"
        report += classification_report(
            best_fold["best_metrics"]["labels"],
            best_fold["best_metrics"]["predictions"],
            target_names=class_names,
            digits=4,
        )

    # Save report
    report_path = models_dir / "enhanced_5fold_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)

    # Confusion matrix generation disabled - no image output
    # Confusion matrix generation removed as requested

    # Save metrics as JSON
    metrics_dict = {
        "config": {
            "folds": 5,
            "epochs": args.epochs,
            "batch_size": args.batch_size,
            "learning_rate": args.lr,
            "num_classes": len(class_names),
        },
        "dataset_stats": {
            "total_classes": len(class_names),
            "min_samples": min(class_counts.values()),
            "max_samples": max(class_counts.values()),
            "small_classes": sum(1 for c in class_counts.values() if c < 50),
            "medium_classes": sum(1 for c in class_counts.values() if 50 <= c < 70),
            "large_classes": sum(1 for c in class_counts.values() if c >= 70),
        },
        "results": {
            "mean_val_acc": float(mean_acc),
            "std_val_acc": float(std_acc),
            "mean_f1": float(mean_f1),
            "std_f1": float(std_f1),
            "best_fold": int(best_fold_idx + 1),
            "best_val_acc": float(best_fold["best_val_acc"]),
            "best_f1": float(best_fold["best_metrics"]["f1"]),
            "fold_val_accs": [float(acc) for acc in val_accs],
            "fold_f1s": [float(f1) for f1 in val_f1s],
        },
        "fold_metrics": all_fold_metrics,
    }

    json_path = models_dir / "enhanced_5fold_metrics.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(metrics_dict, f, indent=2)

    print(f"\nEnhanced 5-fold cross-validation complete!")
    print(f"Mean validation accuracy: {mean_acc:.4f} ± {std_acc:.4f}")
    print(f"Mean F1-score: {mean_f1:.4f} ± {std_f1:.4f}")
    print(
        f"Best performing fold: {best_fold_idx + 1} (Acc: {best_fold['best_val_acc']:.4f}, F1: {best_fold['best_metrics']['f1']:.4f})"
    )
    print(f"Reports saved to: {report_path} and {json_path}")

    return best_fold_idx


def main(args):
    backend_dir = Path(__file__).resolve().parent
    data_dir = backend_dir / "data"
    train_dir = data_dir / "Train"

    if not train_dir.exists():
        raise FileNotFoundError(f"Training directory not found: {train_dir}")

    print(f"Loading data from: {train_dir}")

    # Load full dataset
    train_transforms, val_transforms = get_transforms()
    full_dataset = datasets.ImageFolder(train_dir, transform=train_transforms)

    # Get class names and counts
    class_names = full_dataset.classes
    num_classes = len(class_names)

    # Calculate class counts
    class_counts = Counter([full_dataset.targets[i] for i in range(len(full_dataset))])
    class_name_counts = {class_names[i]: count for i, count in class_counts.items()}

    print(f"Detected {num_classes} ingredient classes")
    print(f"Total samples: {len(full_dataset)}")
    print(f"Sample range: {min(class_counts.values())} - {max(class_counts.values())}")
    print(f"Using enhanced 5-fold cross-validation with F1-measures")

    # Create 5-fold splits
    splits = create_5fold_splits(full_dataset)
    print(f"Created {len(splits)} 5-fold cross-validation splits")

    # Train each fold
    all_fold_metrics = []
    for fold_idx, (train_idx, val_idx) in enumerate(splits):
        # Create datasets for this fold
        train_dataset = Subset(full_dataset, train_idx)
        val_dataset = Subset(full_dataset, val_idx)

        # Apply validation transforms to validation set
        val_dataset.dataset.transform = val_transforms

        # Train this fold
        fold_metrics = train_fold_enhanced(
            fold_idx, train_dataset, val_dataset, class_names, args
        )
        all_fold_metrics.append(fold_metrics)

    # Generate comprehensive report
    best_fold_idx = generate_enhanced_5fold_report(
        all_fold_metrics, class_names, class_name_counts, args
    )

    # Copy best model as ensemble model
    models_dir = backend_dir / "models"
    best_model_path = models_dir / f"fold_{best_fold_idx + 1}_ingredients_resnet18.pt"
    ensemble_model_path = models_dir / "best_enhanced_5fold_model.pt"

    if best_model_path.exists():
        import shutil

        shutil.copy2(best_model_path, ensemble_model_path)
        print(f"Best model copied to: {ensemble_model_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Train ResNet ingredient classifier with enhanced 4-fold cross-validation."
    )
    parser.add_argument(
        "--epochs", type=int, default=15, help="Number of training epochs per fold."
    )
    parser.add_argument("--batch-size", type=int, default=32, help="Batch size.")
    parser.add_argument(
        "--lr", type=float, default=1e-3, help="Learning rate for Adam optimizer."
    )
    parser.add_argument(
        "--num-workers",
        type=int,
        default=2,
        help="Number of DataLoader worker processes.",
    )
    args = parser.parse_args()
    main(args)
