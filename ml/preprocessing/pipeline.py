"""
AI Chargeback Guardian — Data Validation, Feature Engineering & Preprocessing Pipeline

Provides:
1. Robust data validation with data-quality reporting.
2. Leakage-free feature engineering.
3. Stratified Train / Validation / Test splitting (70% / 15% / 15%).
4. ColumnTransformer-based preprocessor for numeric scaling, categorical one-hot encoding,
   and binary passthrough.
"""

from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator, TransformerMixin

from ml.config import (
    BASE_FEATURES,
    NUMERIC_FEATURES,
    BINARY_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_COLUMN,
    TOTAL_NUMERIC_FEATURES,
    TOTAL_BINARY_FEATURES,
    ALL_ENGINEERED_FEATURES,
    TRAIN_RATIO,
    VAL_RATIO,
    TEST_RATIO,
    RANDOM_STATE,
)

# Valid categories for categorical feature checks
VALID_DISPUTE_REASONS = {
    "GOODS_NOT_RECEIVED",
    "UNAUTHORIZED_TRANSACTION",
    "GOODS_NOT_AS_DESCRIBED",
    "DUPLICATE_TRANSACTION",
    "REFUND_NOT_RECEIVED",
}

VALID_PAYMENT_METHODS = {
    "CREDIT_CARD",
    "DEBIT_CARD",
    "DIGITAL_WALLET",
    "BANK_TRANSFER",
}


def validate_data(df: pd.DataFrame, is_training: bool = True) -> Dict[str, Any]:
    """
    Validate dataset quality, schema conformance, range validity, and target distribution.

    Parameters
    ----------
    df : pd.DataFrame
        Dataset to validate.
    is_training : bool
        If True, validates target column presence and distribution.

    Returns
    -------
    dict
        Structured validation report containing status, statistics, and any errors.
    """
    errors: List[str] = []
    warnings: List[str] = []

    # 1. Required column check
    required_cols = list(BASE_FEATURES)
    if is_training:
        required_cols.append(TARGET_COLUMN)

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        errors.append(f"Missing required columns: {missing_cols}")

    if errors:
        return {
            "is_valid": False,
            "errors": errors,
            "warnings": warnings,
            "row_count": len(df),
            "feature_count": len(df.columns),
            "report": f"Validation FAILED: Missing columns {missing_cols}",
        }

    # 2. Missing / NaN values
    null_counts = df[required_cols].isnull().sum()
    total_nulls = int(null_counts.sum())
    if total_nulls > 0:
        null_breakdown = null_counts[null_counts > 0].to_dict()
        errors.append(f"Found {total_nulls} missing/NaN values across columns: {null_breakdown}")

    # 3. Duplicate records
    duplicate_count = int(df.duplicated(subset=BASE_FEATURES).sum())
    if duplicate_count > 0:
        warnings.append(f"Found {duplicate_count} duplicate feature rows.")

    # 4. Numeric validity checks
    if (df["transaction_amount"] <= 0).any():
        errors.append("Found non-positive values in 'transaction_amount'.")
    if (df["transaction_age"] < 0).any():
        errors.append("Found negative values in 'transaction_age'.")
    if (df["customer_account_age"] < 0).any():
        errors.append("Found negative values in 'customer_account_age'.")
    if (df["evidence_count"] < 0).any() or (df["evidence_count"] > 7).any():
        errors.append("Values in 'evidence_count' must be between 0 and 7.")
    if ((df["merchant_dispute_rate"] < 0) | (df["merchant_dispute_rate"] > 1)).any():
        errors.append("Values in 'merchant_dispute_rate' must be between 0.0 and 1.0.")

    # 5. Binary validity checks
    for b_col in BINARY_FEATURES:
        unique_vals = set(df[b_col].dropna().unique())
        if not unique_vals.issubset({0, 1, True, False}):
            errors.append(f"Binary column '{b_col}' contains non-binary values: {unique_vals}")

    # 6. Categorical validity checks
    invalid_reasons = set(df["dispute_reason"].unique()) - VALID_DISPUTE_REASONS
    if invalid_reasons:
        errors.append(f"Invalid dispute_reason categories found: {invalid_reasons}")

    invalid_payments = set(df["payment_method"].unique()) - VALID_PAYMENT_METHODS
    if invalid_payments:
        errors.append(f"Invalid payment_method categories found: {invalid_payments}")

    # 7. Target distribution check (if training)
    target_stats: Dict[str, Any] = {}
    if is_training and TARGET_COLUMN in df.columns:
        target_vals = set(df[TARGET_COLUMN].dropna().unique())
        if not target_vals.issubset({0, 1}):
            errors.append(f"Target column '{TARGET_COLUMN}' contains invalid values: {target_vals}")
        else:
            pos_count = int((df[TARGET_COLUMN] == 1).sum())
            neg_count = int((df[TARGET_COLUMN] == 0).sum())
            pos_pct = round((pos_count / len(df)) * 100, 2)
            neg_pct = round((neg_count / len(df)) * 100, 2)
            target_stats = {
                "positive_count": pos_count,
                "negative_count": neg_count,
                "positive_percentage": pos_pct,
                "negative_percentage": neg_pct,
            }

    is_valid = len(errors) == 0

    # Build human-readable data quality report
    report_lines = [
        "=" * 50,
        "DATA QUALITY & VALIDATION REPORT",
        "=" * 50,
        f"Status:            {'PASSED' if is_valid else 'FAILED'}",
        f"Total Rows:        {len(df):,}",
        f"Total Features:    {len(BASE_FEATURES)} base",
        f"Missing Values:    {total_nulls}",
        f"Duplicate Rows:    {duplicate_count}",
    ]
    if target_stats:
        report_lines.extend([
            f"Positive Class (1): {target_stats['positive_count']} ({target_stats['positive_percentage']}%) [Merchant Won/Contest Succeeded]",
            f"Negative Class (0): {target_stats['negative_count']} ({target_stats['negative_percentage']}%) [Merchant Lost/Dispute Upheld]",
        ])
    if warnings:
        report_lines.append(f"Warnings ({len(warnings)}): " + "; ".join(warnings))
    if errors:
        report_lines.append(f"Errors ({len(errors)}): " + "; ".join(errors))
    report_lines.append("=" * 50)

    report_str = "\n".join(report_lines)

    return {
        "is_valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "row_count": len(df),
        "feature_count": len(BASE_FEATURES),
        "target_stats": target_stats,
        "report": report_str,
    }


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute derived, leakage-free features from base dispute/transaction features.

    Engineered Features:
    --------------------
    1. successful_transaction_ratio:
       Ratio of prior successful orders to total prior activity (orders + disputes).
       Reflects historical customer loyalty and chargeback risk.
    2. customer_dispute_ratio:
       Ratio of previous disputes to prior transactions.
       Flags habitual or abusive dispute history.
    3. evidence_completeness:
       Normalized score of evidence availability (0.0 to 1.0) out of 7 mandatory categories.
    4. amount_deviation_score:
       Scaled interaction of amount deviation multiplied by transaction amount.
    5. txn_age_vs_account_age:
       Relative age of transaction against total customer tenure.
    6. delivery_confirmation_flag:
       Compound binary indicator: 1 if delivery is confirmed AND customer acknowledged.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with base features.

    Returns
    -------
    pd.DataFrame
        New DataFrame containing both base and engineered features.
    """
    out = df.copy()

    # 1. successful_transaction_ratio
    prev_txns = out["previous_successful_transactions"].astype(float)
    prev_disp = out["previous_disputes"].astype(float)
    out["successful_transaction_ratio"] = np.round(
        prev_txns / (prev_txns + prev_disp + 1.0), 4
    )

    # 2. customer_dispute_ratio
    out["customer_dispute_ratio"] = np.round(
        prev_disp / (prev_txns + 1.0), 4
    )

    # 3. evidence_completeness (out of 7 mandatory categories)
    out["evidence_completeness"] = np.round(
        out["evidence_count"].astype(float) / 7.0, 4
    )

    # 4. amount_deviation_score
    out["amount_deviation_score"] = np.round(
        (out["amount_deviation"].astype(float) * out["transaction_amount"].astype(float)) / 100.0, 4
    )

    # 5. txn_age_vs_account_age
    out["txn_age_vs_account_age"] = np.round(
        out["transaction_age"].astype(float) / (out["customer_account_age"].astype(float) + 1.0), 4
    )

    # 6. delivery_confirmation_flag
    deliv_conf = out["delivery_confirmed"].astype(int)
    cust_ack = out["customer_acknowledged"].astype(int)
    out["delivery_confirmation_flag"] = (deliv_conf * cust_ack).astype(int)

    return out


def split_data(
    df: pd.DataFrame,
    train_ratio: float = TRAIN_RATIO,
    val_ratio: float = VAL_RATIO,
    test_ratio: float = TEST_RATIO,
    random_state: int = RANDOM_STATE,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split dataset into Stratified Train (70%), Validation (15%), and Test (15%) sets.

    Parameters
    ----------
    df : pd.DataFrame
        Full preprocessed dataset.
    train_ratio, val_ratio, test_ratio : float
        Split proportions (must sum to 1.0).
    random_state : int
        Seed for strict reproducibility.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        (train_df, val_df, test_df)
    """
    assert abs((train_ratio + val_ratio + test_ratio) - 1.0) < 1e-6, "Split ratios must sum to 1.0"

    stratify_target = df[TARGET_COLUMN] if TARGET_COLUMN in df.columns else None

    # First split: Train vs Temp (Val + Test)
    temp_ratio = val_ratio + test_ratio
    train_df, temp_df = train_test_split(
        df,
        test_size=temp_ratio,
        random_state=random_state,
        stratify=stratify_target,
    )

    # Second split: Validation vs Test (50/50 split of the remaining 30%)
    temp_stratify = temp_df[TARGET_COLUMN] if TARGET_COLUMN in temp_df.columns else None
    val_share_of_temp = val_ratio / temp_ratio  # 0.15 / 0.30 = 0.50

    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1.0 - val_share_of_temp),
        random_state=random_state,
        stratify=temp_stratify,
    )

    return train_df.reset_index(drop=True), val_df.reset_index(drop=True), test_df.reset_index(drop=True)


class MLPreprocessor:
    """
    ColumnTransformer preprocessor:
    - Scales numeric features with StandardScaler
    - Encodes categorical features with OneHotEncoder (handle_unknown='ignore')
    - Passes binary features as passthrough
    """

    def __init__(self):
        self.numeric_features = TOTAL_NUMERIC_FEATURES
        self.binary_features = TOTAL_BINARY_FEATURES
        self.categorical_features = CATEGORICAL_FEATURES
        self.transformer: Optional[ColumnTransformer] = None
        self.feature_names_: List[str] = []

    def fit(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> "MLPreprocessor":
        """Fit preprocessor only on training data to prevent information leakage."""
        self.transformer = ColumnTransformer(
            transformers=[
                (
                    "num",
                    StandardScaler(),
                    self.numeric_features,
                ),
                (
                    "bin",
                    "passthrough",
                    self.binary_features,
                ),
                (
                    "cat",
                    OneHotEncoder(handle_unknown="ignore", sparse_output=False),
                    self.categorical_features,
                ),
            ],
            remainder="drop",
        )
        self.transformer.fit(X)

        # Build feature names
        num_names = list(self.numeric_features)
        bin_names = list(self.binary_features)
        cat_encoder = self.transformer.named_transformers_["cat"]
        cat_names = list(cat_encoder.get_feature_names_out(self.categorical_features))
        self.feature_names_ = num_names + bin_names + cat_names

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """Transform input features into preprocessed DataFrame."""
        if self.transformer is None:
            raise RuntimeError("MLPreprocessor has not been fitted yet. Call fit() first.")

        arr = self.transformer.transform(X)
        return pd.DataFrame(arr, columns=self.feature_names_, index=X.index)

    def fit_transform(self, X: pd.DataFrame, y: Optional[pd.Series] = None) -> pd.DataFrame:
        """Fit on X and transform X in one step."""
        return self.fit(X, y).transform(X)

    def get_feature_names_out(self) -> List[str]:
        """Return list of transformed feature column names."""
        return list(self.feature_names_)
