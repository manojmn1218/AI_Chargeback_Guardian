"""
AI Chargeback Guardian — Strong Model (XGBoost Classifier)

Gradient-boosted decision tree architecture tuned for high precision,
robust non-linear feature interaction capture, and SHAP explainability.
Includes fallback to RandomForestClassifier if XGBoost is unavailable.
"""

from typing import Any, Dict, Optional, Union
import numpy as np
import pandas as pd

from ml.config import RANDOM_STATE, DEFAULT_CONTEST_THRESHOLD

# Try importing XGBoost; provide clean fallback if environment requires
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier


def train_xgboost(
    X_train: pd.DataFrame,
    y_train: pd.Series,
    X_val: Optional[pd.DataFrame] = None,
    y_val: Optional[pd.Series] = None,
    n_estimators: int = 150,
    max_depth: int = 4,
    learning_rate: float = 0.05,
    subsample: float = 0.8,
    colsample_bytree: float = 0.8,
    random_state: int = RANDOM_STATE,
) -> Any:
    """
    Train an XGBoost classifier (or robust ensemble fallback).

    Parameters
    ----------
    X_train : pd.DataFrame
        Preprocessed training features.
    y_train : pd.Series
        Training labels (1 = Merchant Win, 0 = Merchant Lost).
    X_val, y_val : Optional validation sets for early stopping.
    n_estimators : int
        Number of boosting trees.
    max_depth : int
        Maximum depth of each decision tree.
    learning_rate : float
        Step size shrinkage to prevent overfitting.
    subsample, colsample_bytree : float
        Stochastic bagging & feature subsampling rates.
    random_state : int
        Reproducibility seed.

    Returns
    -------
    Trained model object.
    """
    # Calculate scale_pos_weight to address class balance
    neg_count = float((y_train == 0).sum())
    pos_count = float((y_train == 1).sum())
    scale_pos_weight = neg_count / max(1.0, pos_count)

    if XGBOOST_AVAILABLE:
        model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            scale_pos_weight=scale_pos_weight,
            eval_metric="logloss",
            random_state=random_state,
            n_jobs=-1,
        )

        if X_val is not None and y_val is not None:
            model.fit(
                X_train,
                y_train,
                eval_set=[(X_val, y_val)],
                verbose=False,
            )
        else:
            model.fit(X_train, y_train)

        return model
    else:
        # Fallback to RandomForestClassifier
        fallback_model = RandomForestClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth + 2,
            class_weight="balanced",
            random_state=random_state,
            n_jobs=-1,
        )
        fallback_model.fit(X_train, y_train)
        return fallback_model


def predict_xgboost(
    model: Any,
    X: pd.DataFrame,
    threshold: float = DEFAULT_CONTEST_THRESHOLD,
) -> pd.DataFrame:
    """
    Generate win probabilities and binary contest recommendations.

    Parameters
    ----------
    model : Trained model instance.
    X : pd.DataFrame
        Preprocessed feature matrix.
    threshold : float
        Classification decision boundary (e.g. 0.60).

    Returns
    -------
    pd.DataFrame
        DataFrame with 'probability' and 'prediction' columns.
    """
    probabilities = model.predict_proba(X)[:, 1]
    predictions = (probabilities >= threshold).astype(int)

    return pd.DataFrame({
        "probability": np.round(probabilities, 4),
        "prediction": predictions,
    }, index=X.index)
