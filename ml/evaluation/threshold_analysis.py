"""
AI Chargeback Guardian — Threshold Analysis & Asymmetric Financial Cost Matrix

Evaluates classifier behavior across decision thresholds ($0.10 to $0.90) and computes
expected business cost under asymmetric false-positive vs false-negative penalties:

- False Positive Penalty: Submitting an ungrounded or weak dispute incurring gateway fees ($15)
  and network contest ratio degradation.
- False Negative Penalty: Failing to contest a legitimately winnable dispute, resulting in
  100% loss of the disputed transaction value (Avg $489.00).
"""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from sklearn.metrics import precision_score, recall_score, f1_score, confusion_matrix

from ml.config import (
    DEFAULT_FALSE_POSITIVE_COST,
    DEFAULT_FALSE_NEGATIVE_COST,
    DEFAULT_CONTEST_THRESHOLD,
)


def analyze_thresholds(
    y_true: np.ndarray,
    y_proba: np.ndarray,
    thresholds: Optional[List[float]] = None,
    fp_cost: float = DEFAULT_FALSE_POSITIVE_COST,
    fn_cost: float = DEFAULT_FALSE_NEGATIVE_COST,
) -> pd.DataFrame:
    """
    Perform multi-threshold sweep and financial cost optimization.

    Parameters
    ----------
    y_true : Ground truth binary array (1 = Win, 0 = Lost).
    y_proba : Predicted positive class probabilities.
    thresholds : List of probability cutoffs to analyze (default: 0.10 to 0.90).
    fp_cost : Configurable financial cost per False Positive (in USD).
    fn_cost : Configurable financial cost per False Negative (in USD).

    Returns
    -------
    pd.DataFrame
        Threshold comparison table with precision, recall, F1, FPR, FNR,
        confusion matrix counts, and expected financial loss.
    """
    if thresholds is None:
        thresholds = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90]

    y_true = np.array(y_true)
    y_proba = np.array(y_proba)

    rows = []
    for tau in thresholds:
        y_pred = (y_proba >= tau).astype(int)

        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        tn, fp, fn, tp = int(cm[0, 0]), int(cm[0, 1]), int(cm[1, 0]), int(cm[1, 1])

        prec = float(precision_score(y_true, y_pred, zero_division=0))
        rec = float(recall_score(y_true, y_pred, zero_division=0))
        f1 = float(f1_score(y_true, y_pred, zero_division=0))

        fpr = float(fp / (fp + tn)) if (fp + tn) > 0 else 0.0
        fnr = float(fn / (fn + tp)) if (fn + tp) > 0 else 0.0

        # Asymmetric business cost function
        total_expected_cost = float(fp * fp_cost + fn * fn_cost)
        avg_cost_per_case = float(total_expected_cost / len(y_true))

        rows.append({
            "threshold": round(tau, 2),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1_score": round(f1, 4),
            "false_positive_rate": round(fpr, 4),
            "false_negative_rate": round(fnr, 4),
            "true_positives": tp,
            "false_positives": fp,
            "true_negatives": tn,
            "false_negatives": fn,
            "fp_cost_total": round(fp * fp_cost, 2),
            "fn_cost_total": round(fn * fn_cost, 2),
            "total_expected_cost": round(total_expected_cost, 2),
            "avg_cost_per_case": round(avg_cost_per_case, 2),
        })

    df_results = pd.DataFrame(rows)
    return df_results


def find_optimal_threshold(
    threshold_df: pd.DataFrame,
    criterion: str = "min_cost",
) -> Dict[str, Any]:
    """
    Select the optimal decision threshold based on business criteria.

    Parameters
    ----------
    threshold_df : Output of analyze_thresholds.
    criterion : 'min_cost' (minimize expected dollar loss) or 'max_f1' (maximize F1).

    Returns
    -------
    dict
        Selected optimal threshold details and rationale.
    """
    if criterion == "min_cost":
        best_idx = threshold_df["total_expected_cost"].idxmin()
        reason = "Minimizes net financial loss considering asymmetric FP ($15) vs FN ($489) penalties."
    else:
        best_idx = threshold_df["f1_score"].idxmax()
        reason = "Maximizes harmonic mean of precision and recall."

    best_row = threshold_df.loc[best_idx].to_dict()
    best_row["criterion"] = criterion
    best_row["selection_reason"] = reason

    return best_row
