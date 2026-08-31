"""
AI Chargeback Guardian — ML Configuration

Central configuration for the Machine Learning Risk Engine:
paths, feature lists, engineered feature names, target column,
split ratios, hyperparameter defaults, threshold settings, and business cost weights.
"""

from pathlib import Path

# ---- Paths ----
ML_ROOT = Path(__file__).resolve().parent
DATA_DIR = ML_ROOT.parent / "data" / "synthetic"
DATASET_PATH = DATA_DIR / "chargeback_ml_dataset.csv"
SAVED_MODELS_DIR = ML_ROOT / "saved_models"
OUTPUTS_DIR = ML_ROOT / "outputs"
DOCS_DIR = ML_ROOT.parent / "docs"

# ---- Target Variable ----
# outcome = 1 -> Merchant successfully contested the dispute (Win)
# outcome = 0 -> Merchant did not successfully contest the dispute (Chargeback Upheld / Loss)
TARGET_COLUMN = "outcome"

# ---- Base Features ----
NUMERIC_FEATURES = [
    "transaction_amount",
    "transaction_age",
    "customer_account_age",
    "previous_disputes",
    "previous_successful_transactions",
    "previous_refunds",
    "evidence_count",
    "merchant_dispute_rate",
    "transaction_frequency",
    "amount_deviation",
]

BINARY_FEATURES = [
    "delivery_confirmed",
    "customer_acknowledged",
    "refund_processed",
    "communication_available",
]

CATEGORICAL_FEATURES = [
    "dispute_reason",
    "payment_method",
]

BASE_FEATURES = NUMERIC_FEATURES + BINARY_FEATURES + CATEGORICAL_FEATURES

# ---- Engineered Features ----
ENGINEERED_NUMERIC_FEATURES = [
    "successful_transaction_ratio",
    "customer_dispute_ratio",
    "evidence_completeness",
    "amount_deviation_score",
    "txn_age_vs_account_age",
]

ENGINEERED_BINARY_FEATURES = [
    "delivery_confirmation_flag",
]

ALL_ENGINEERED_FEATURES = ENGINEERED_NUMERIC_FEATURES + ENGINEERED_BINARY_FEATURES

# All numeric features after engineering
TOTAL_NUMERIC_FEATURES = NUMERIC_FEATURES + ENGINEERED_NUMERIC_FEATURES
TOTAL_BINARY_FEATURES = BINARY_FEATURES + ENGINEERED_BINARY_FEATURES

# ---- Split Ratios (Stratified) ----
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15
RANDOM_STATE = 42

# ---- Model Names & Version ----
MODEL_VERSION = "v1.0"
BASELINE_MODEL_NAME = "logistic_regression"
STRONG_MODEL_NAME = "xgboost"

# ---- Decision Thresholds & Risk Tiers ----
# Case Strength Score Calibration:
# 0–39: WEAK (Low contest probability, consider accepting chargeback)
# 40–69: NEEDS_REVIEW (Moderate contest probability, manual investigator review required)
# 70–100: STRONG (High contest probability, recommend automated contest packet submission)
SCORE_WEAK_MAX = 39
SCORE_REVIEW_MAX = 69
SCORE_STRONG_MIN = 70

DEFAULT_CONTEST_THRESHOLD = 0.60
HIGH_CONFIDENCE_THRESHOLD = 0.70
LOW_CONFIDENCE_THRESHOLD = 0.40

# ---- Business Cost Assumptions (Synthetic / Configurable) ----
# False Positive Cost ($15.00 gateway contest fee + lost issuer goodwill on weak claims)
DEFAULT_FALSE_POSITIVE_COST = 15.0
# False Negative Cost ($489.00 average synthetic transaction loss when failing to contest winnable cases)
DEFAULT_FALSE_NEGATIVE_COST = 489.0
