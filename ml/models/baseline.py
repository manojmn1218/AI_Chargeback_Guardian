"""
AI Chargeback Guardian — Baseline Model (Logistic Regression)

Provides a standard, interpretable linear benchmark with L2 regularization
and balanced class weighting to compare against non-linear tree models.
"""

from typing import Any, Dict, Optional, Union
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

from ml.config import RANDOM_STATE, BASELINE_MODEL_NAME


def train_baseline(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    C: float = 1.0,
    max_iter: int = 1000,
    random_state: int = RANDOM_STATE,
    class_weight: Optional[str] = "balanced",
) -> LogisticRegression:
    """
    Train a Logistic Regression baseline model with L2 penalty.

    Parameters
    ----------
    X_train : pd.DataFrame
        Preprocessed training feature matrix.
    y_train : pd.Series
        Binary training labels (1 = Merchant Win, 0 = Merchant Lost).
    C : float
        Inverse regularization strength.
    max_iter : int
        Maximum iterations for solver convergence.
    random_state : int
        Seed for reproducibility.
    class_weight : Optional[str]
        Class weighting strategy to balance positive and negative classes.

    Returns
    -------
    LogisticRegression
        Fitted sklearn LogisticRegression instance.
    """
    model = LogisticRegression(
        C=C,
        solver="lbfgs",
        max_iter=max_iter,
        random_state=random_state,
        class_weight=class_weight,
    )
    model.fit(X_train, y_train)
    return model


def predict_baseline(
    model: LogisticRegression,
    X: pd.DataFrame,
    threshold: float = 0.50,
) -> pd.DataFrame:
    """
    Generate probabilities and binary contest predictions using the baseline model.

    Parameters
    ----------
    model : LogisticRegression
        Fitted baseline model.
    X : pd.DataFrame
        Preprocessed feature matrix.
    threshold : float
        Classification decision boundary threshold.

    Returns
    -------
    pd.DataFrame
        DataFrame with 'probability' (win likelihood) and 'prediction' (binary 0/1).
    """
    # Probability of class 1 (Merchant Win)
    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    return pd.DataFrame({
        "probability": np.round(probabilities, 4),
        "prediction": predictions,
    }, index=X.index)
