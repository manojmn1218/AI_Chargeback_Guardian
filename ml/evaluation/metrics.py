"""
AI Chargeback Guardian — Model Evaluation Metrics

Computes comprehensive classification metrics:
- Precision (Contest Win Accuracy)
- Recall (Fraud / Winnable Case Capture Sensitivity)
- F1 Score (Harmonic mean of precision and recall)
- ROC-AUC & Average Precision (PR-AUC)
- Confusion Matrix breakdown (TP, TN, FP, FN)
- False Positive Rate (FPR) & False Negative Rate (FNR)
"""

from typing import Any, Dict, List, Optional, Union
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
)


def evaluate_model(
    model: Any,
    X: pd.DataFrame,
    y_true: Union[pd.Series, np.ndarray],
    model_name: str = "model",
    threshold: float = 0.50,
) -> Dict[str, Any]:
    """
    Compute rigorous evaluation metrics for a binary classifier on a given dataset.

    Parameters
    ----------
    model : Trained model with predict_proba method.
    X : Feature matrix.
    y_true : Ground truth binary labels.
    model_name : Identifier name for reports.
    threshold : Decision threshold for positive classification.

    Returns
    -------
    dict
        Evaluation metrics dictionary.
    """
    y_true_arr = np.array(y_true)
    y_proba = model.predict_proba(X)[:, 1]
    y_pred = (y_proba >= threshold).astype(int)

    # Core classification metrics
    acc = float(accuracy_score(y_true_arr, y_pred))
    prec = float(precision_score(y_true_arr, y_pred, zero_division=0))
    rec = float(recall_score(y_true_arr, y_pred, zero_division=0))
    f1 = float(f1_score(y_true_arr, y_pred, zero_division=0))

    try:
        roc_auc = float(roc_auc_score(y_true_arr, y_proba))
    except Exception:
        roc_auc = 0.0

    try:
        pr_auc = float(average_precision_score(y_true_arr, y_proba))
    except Exception:
        pr_auc = 0.0

    # Confusion matrix breakdown
    cm = confusion_matrix(y_true_arr, y_pred, labels=[0, 1])
    tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

    # Rates
    fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
    fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

    return {
        "model_name": model_name,
        "threshold": float(threshold),
        "total_samples": int(len(y_true_arr)),
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "pr_auc": round(pr_auc, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "confusion_matrix": {
            "true_negatives": tn,
            "false_positives": fp,
            "false_negatives": fn,
            "true_positives": tp,
        },
    }


def format_confusion_matrix_ascii(cm_dict: Dict[str, int]) -> str:
    """
    Format confusion matrix as an annotated ASCII table.

    Definitions:
    - True Negative (TN): Correctly identified a weak case; avoided paying futile contest fees.
    - False Positive (FP): Incorrectly contested a weak case; incurred contest fee + lost issuer goodwill.
    - False Negative (FN): Failed to contest a winnable case; 100% loss of transaction amount.
    - True Positive (TP): Successfully recommended contest on a winnable case; recovered funds.
    """
    tn = cm_dict["true_negatives"]
    fp = cm_dict["false_positives"]
    fn = cm_dict["false_negatives"]
    tp = cm_dict["true_positives"]

    lines = [
        "+------------------------------------------------------------+",
        "|                 CONFUSION MATRIX BREAKDOWN                 |",
        "+-----------------------------+------------------------------+",
        "| PREDICTED: ACCEPT (0)       | PREDICTED: CONTEST (1)       |",
        "+-----------------------------+------------------------------+",
        f"| TRUE NEGATIVE (TN):  {tn:>5}  | FALSE POSITIVE (FP):  {fp:>5}  |",
        "| (Correctly accepted loss)   | (Futile contest / fee loss)  |",
        "+-----------------------------+------------------------------+",
        f"| FALSE NEGATIVE (FN): {fn:>5}  | TRUE POSITIVE (TP):   {tp:>5}  |",
        "| (Missed valid recovery)     | (Successfully won dispute)   |",
        "+-----------------------------+------------------------------+",
    ]
    return "\n".join(lines)


def compare_models(results: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Format evaluation results into a clean side-by-side comparison DataFrame.

    Parameters
    ----------
    results : List of model evaluation dictionaries.

    Returns
    -------
    pd.DataFrame
        Formatted comparison table.
    """
    rows = []
    for r in results:
        cm = r["confusion_matrix"]
        rows.append({
            "Model": r["model_name"],
            "Threshold": r["threshold"],
            "Accuracy": f"{r['accuracy'] * 100:.1f}%",
            "Precision": f"{r['precision'] * 100:.1f}%",
            "Recall": f"{r['recall'] * 100:.1f}%",
            "F1 Score": f"{r['f1']:.3f}",
            "ROC-AUC": f"{r['roc_auc']:.3f}",
            "PR-AUC": f"{r['pr_auc']:.3f}",
            "FPR": f"{r['false_positive_rate'] * 100:.1f}%",
            "TP": cm["true_positives"],
            "FP": cm["false_positives"],
            "TN": cm["true_negatives"],
            "FN": cm["false_negatives"],
        })
    return pd.DataFrame(rows)


def save_metrics_report(
    metrics_data: Dict[str, Any],
    output_path: Path,
) -> None:
    """Save metrics report as formatted JSON."""
    out_p = Path(output_path)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
