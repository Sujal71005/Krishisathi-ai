"""Train and evaluate crop recommendation classifiers.

The script is intentionally self-contained and uses paths relative to the
repository root, so it can be run from any working directory:

    python backend/scripts/train_model.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "Crop_recommendation.csv"
MODEL_DIR = PROJECT_ROOT / "backend" / "models"
MODEL_PATH = MODEL_DIR / "crop_model.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"
REPORT_PATH = PROJECT_ROOT / "docs" / "model-evaluation.md"

FEATURE_NAMES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
TARGET_NAME = "label"
RANDOM_SEED = 42
TEST_SIZE = 0.20
CV_SPLITS = 5
MODEL_VERSION = "1.0.0"


def validate_dataset(df: pd.DataFrame) -> None:
    """Validate the exact expected input and target schema."""
    expected = FEATURE_NAMES + [TARGET_NAME]
    if list(df.columns) != expected:
        raise ValueError(
            f"Unexpected dataset columns. Expected {expected}, got {list(df.columns)}"
        )
    if df.empty:
        raise ValueError("Dataset is empty")
    if df[FEATURE_NAMES].isna().any().any() or df[TARGET_NAME].isna().any():
        raise ValueError("Dataset contains missing values")
    if not np.isfinite(df[FEATURE_NAMES].to_numpy(dtype=float)).all():
        raise ValueError("Dataset contains non-finite feature values")
    if df[TARGET_NAME].nunique() < 2:
        raise ValueError("Dataset must contain at least two target classes")


def build_models() -> dict[str, Any]:
    """Return deterministic baseline classifiers.

    KNN is the only model requiring feature scaling here, and the scaler is
    inside its Pipeline so each CV fold learns preprocessing from its fold's
    training portion only.
    """
    return {
        "Decision Tree": DecisionTreeClassifier(random_state=RANDOM_SEED),
        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            random_state=RANDOM_SEED,
            n_jobs=-1,
        ),
        "K-Nearest Neighbors": Pipeline(
            steps=[
                ("scaler", StandardScaler()),
                ("classifier", KNeighborsClassifier(n_neighbors=5)),
            ]
        ),
    }


def _json_value(value: Any) -> Any:
    """Convert NumPy/scikit-learn values into JSON-compatible values."""
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, np.ndarray)):
        return [_json_value(v) for v in value]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def _format_pct(value: float) -> str:
    return f"{value:.4f}"


def _error_rows(confusion: np.ndarray, class_names: list[str]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for actual_index, actual in enumerate(class_names):
        for predicted_index, predicted in enumerate(class_names):
            count = int(confusion[actual_index, predicted_index])
            if actual != predicted and count:
                errors.append(
                    {"actual": actual, "predicted": predicted, "count": count}
                )
    return sorted(errors, key=lambda row: (-row["count"], row["actual"], row["predicted"]))


def _write_report(metadata: dict[str, Any]) -> None:
    selected = metadata["selected_model"]
    test = metadata["evaluation_metrics"]
    comparisons = metadata["model_comparison"]
    errors = metadata["classification_errors"]
    lines = [
        "# Model evaluation — Phase 2",
        "",
        f"Training timestamp: `{metadata['training_timestamp']}`",
        "",
        "## Dataset and procedure",
        "",
        f"The actual `data/Crop_recommendation.csv` was loaded with {metadata['dataset_row_count']:,} rows, {metadata['dataset_class_count']} target classes, and the seven validated features: `{'`, `'.join(metadata['feature_names'])}`.",
        "",
        f"A stratified {int((1 - metadata['test_size']) * 100)}/{int(metadata['test_size'] * 100)} train/test split used random seed `{metadata['random_seed']}`. Model selection used only the {metadata['train_sample_count']:,}-row training split with {metadata['cross_validation']['splits']}-fold stratified cross-validation. The test set was held out until after selection.",
        "",
        "## Algorithms compared",
        "",
        "- **Decision Tree Classifier:** an interpretable tree-based baseline.",
        "- **Random Forest Classifier:** an ensemble of randomized decision trees.",
        "- **K-Nearest Neighbors Classifier:** uses `StandardScaler` inside a scikit-learn Pipeline so scaling is fitted separately within each training fold.",
        "",
        "## Cross-validation comparison",
        "",
        "| Model | Fold macro F1 scores | Mean macro F1 | Std. dev. |",
        "|---|---|---:|---:|",
    ]
    for row in comparisons:
        folds = ", ".join(_format_pct(score) for score in row["fold_macro_f1"])
        lines.append(
            f"| {row['model_name']} | {folds} | {_format_pct(row['cv_macro_f1_mean'])} | {_format_pct(row['cv_macro_f1_std'])} |"
        )
    lines += [
        "",
        f"**Selection:** `{selected}` was selected because it had the highest mean cross-validation macro F1. The criterion was evaluated before using the held-out test set.",
        "",
        "## Selected-model held-out test results",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Accuracy | {_format_pct(test['accuracy'])} |",
        f"| Macro precision | {_format_pct(test['macro_precision'])} |",
        f"| Macro recall | {_format_pct(test['macro_recall'])} |",
        f"| Macro F1 | {_format_pct(test['macro_f1'])} |",
        "",
        "### Per-class metrics",
        "",
        "| Class | Precision | Recall | F1 | Support |",
        "|---|---:|---:|---:|---:|",
    ]
    for class_name in metadata["target_classes"]:
        row = test["per_class"][class_name]
        lines.append(
            f"| {class_name} | {_format_pct(row['precision'])} | {_format_pct(row['recall'])} | {_format_pct(row['f1_score'])} | {row['support']} |"
        )
    lines += [
        "",
        "### Confusion matrix",
        "",
        "Rows are actual classes and columns are predicted classes, in the order shown in the header.",
        "",
        "| Actual \\ Predicted | " + " | ".join(metadata["target_classes"]) + " |",
        "|---|" + "---:|" * len(metadata["target_classes"]),
    ]
    for class_name, row in zip(metadata["target_classes"], test["confusion_matrix"]):
        lines.append(f"| {class_name} | " + " | ".join(str(value) for value in row) + " |")
    lines += ["", "## Observed classification errors", ""]
    if errors:
        lines.append("The selected model's held-out errors were:")
        lines.append("")
        lines.append("| Actual class | Predicted class | Count |")
        lines.append("|---|---|---:|")
        lines.extend(f"| {row['actual']} | {row['predicted']} | {row['count']} |" for row in errors)
    else:
        lines.append("No off-diagonal errors were observed in the held-out test set.")
    lines += [
        "",
        "## Limitations",
        "",
        "- Results describe this supplied dataset and its sampled conditions; they are not universal agronomic guarantees.",
        "- A balanced benchmark does not establish real-world performance across farms, regions, seasons, measurement error, or crops outside these 22 classes.",
        "- Probability-like outputs must be interpreted as model confidence, not calibrated agronomic risk, unless calibration is evaluated separately.",
        "",
        "## Reproduction",
        "",
        "From the project root, run:",
        "",
        "```powershell",
        "python backend/scripts/train_model.py",
        "python -m unittest discover -s tests -v",
        "```",
        "The script recreates `backend/models/crop_model.joblib`, `backend/models/model_metadata.json`, and this report from the unchanged CSV.",
    ]
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def train_and_evaluate() -> dict[str, Any]:
    """Train, select, evaluate, and persist the selected crop model."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    validate_dataset(df)

    X = df[FEATURE_NAMES]
    y = df[TARGET_NAME]
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_SEED,
        stratify=y,
    )

    cv = StratifiedKFold(n_splits=CV_SPLITS, shuffle=True, random_state=RANDOM_SEED)
    model_comparison: list[dict[str, Any]] = []
    models = build_models()
    for name, estimator in models.items():
        scores = cross_val_score(
            estimator,
            X_train,
            y_train,
            cv=cv,
            scoring="f1_macro",
            n_jobs=None,
        )
        model_comparison.append(
            {
                "model_name": name,
                "fold_macro_f1": scores.tolist(),
                "cv_macro_f1_mean": float(scores.mean()),
                "cv_macro_f1_std": float(scores.std()),
            }
        )

    selected_row = max(
        enumerate(model_comparison),
        key=lambda item: (item[1]["cv_macro_f1_mean"], -item[0]),
    )[1]
    selected_name = selected_row["model_name"]
    selected_model = clone(models[selected_name])
    selected_model.fit(X_train, y_train)

    target_classes = sorted(y.unique().tolist())
    predictions = selected_model.predict(X_test)
    report = classification_report(
        y_test,
        predictions,
        labels=target_classes,
        output_dict=True,
        zero_division=0,
    )
    matrix = confusion_matrix(y_test, predictions, labels=target_classes)
    test_metrics = {
        "accuracy": float(report["accuracy"]),
        "macro_precision": float(report["macro avg"]["precision"]),
        "macro_recall": float(report["macro avg"]["recall"]),
        "macro_f1": float(report["macro avg"]["f1-score"]),
        "per_class": {
            name: {
                "precision": float(report[name]["precision"]),
                "recall": float(report[name]["recall"]),
                "f1_score": float(report[name]["f1-score"]),
                "support": int(report[name]["support"]),
            }
            for name in target_classes
        },
        "confusion_matrix": matrix.tolist(),
    }

    metadata: dict[str, Any] = {
        "model_name": selected_name,
        "selected_model": selected_name,
        "model_version": MODEL_VERSION,
        "feature_names": FEATURE_NAMES,
        "target_name": TARGET_NAME,
        "target_classes": target_classes,
        "dataset_path": str(DATA_PATH.relative_to(PROJECT_ROOT)),
        "dataset_row_count": int(len(df)),
        "dataset_class_count": int(y.nunique()),
        "train_sample_count": int(len(X_train)),
        "test_sample_count": int(len(X_test)),
        "random_seed": RANDOM_SEED,
        "test_size": TEST_SIZE,
        "cross_validation": {
            "strategy": "StratifiedKFold",
            "splits": CV_SPLITS,
            "shuffle": True,
            "random_seed": RANDOM_SEED,
            "scoring": "f1_macro",
        },
        "model_selection_criterion": "highest mean cross-validation macro F1 on the training split",
        "model_comparison": model_comparison,
        "selected_model_cv": selected_row,
        "evaluation_metrics": test_metrics,
        "classification_errors": _error_rows(matrix, target_classes),
        "training_timestamp": datetime.now(timezone.utc).isoformat(),
        "sklearn_version": __import__("sklearn").__version__,
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(selected_model, MODEL_PATH)
    METADATA_PATH.write_text(
        json.dumps(_json_value(metadata), indent=2) + "\n", encoding="utf-8"
    )
    _write_report(metadata)

    print(f"Selected model: {selected_name}")
    print(f"Artifacts: {MODEL_PATH}, {METADATA_PATH}")
    print("\nCross-validation comparison:")
    for row in model_comparison:
        print(
            f"  {row['model_name']}: mean macro F1={row['cv_macro_f1_mean']:.6f} "
            f"(std={row['cv_macro_f1_std']:.6f})"
        )
    print("\nHeld-out test metrics for selected model:")
    for key in ("accuracy", "macro_precision", "macro_recall", "macro_f1"):
        print(f"  {key}: {test_metrics[key]:.6f}")
    print(f"Classification error pairs: {len(metadata['classification_errors'])}")
    return metadata


if __name__ == "__main__":
    try:
        train_and_evaluate()
    except Exception as exc:  # pragma: no cover - command-line diagnostic
        print(f"Training failed: {exc}", file=sys.stderr)
        raise
