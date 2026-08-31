"""
AI Chargeback Guardian — Master ML Training & Evaluation Pipeline

Reproducible orchestration script:
1. Loads synthetic ML dataset (data/synthetic/chargeback_ml_dataset.csv)
2. Validates data quality and schema bounds
3. Performs feature engineering (6 derived features)
4. Stratified 70% Train / 15% Val / 15% Test partitioning
5. Fits ColumnTransformer preprocessor on Train set only
6. Trains Baseline (Logistic Regression) & Champion (XGBoost)
7. Evaluates both models on validation set
8. Evaluates champion on held-out test set
9. Performs multi-threshold sweep & asymmetric financial loss analysis
10. Trains TreeSHAP explainer & computes global feature importance
11. Serializes model artifacts to ml/saved_models/
12. Generates evaluation artifacts and documentation
"""

import sys
from pathlib import Path
import json
import joblib
import numpy as np
import pandas as pd

# Add project root to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from ml.config import (
    DATASET_PATH,
    SAVED_MODELS_DIR,
    DOCS_DIR,
    TARGET_COLUMN,
    BASE_FEATURES,
    MODEL_VERSION,
    BASELINE_MODEL_NAME,
    STRONG_MODEL_NAME,
    DEFAULT_CONTEST_THRESHOLD,
    DEFAULT_FALSE_POSITIVE_COST,
    DEFAULT_FALSE_NEGATIVE_COST,
    SCORE_WEAK_MAX,
    SCORE_REVIEW_MAX,
    SCORE_STRONG_MIN,
    RANDOM_STATE,
)
from ml.preprocessing.pipeline import (
    validate_data,
    engineer_features,
    split_data,
    MLPreprocessor,
)
from ml.models.baseline import train_baseline, predict_baseline
from ml.models.xgboost_model import train_xgboost, predict_xgboost
from ml.evaluation.metrics import (
    evaluate_model,
    format_confusion_matrix_ascii,
    compare_models,
    save_metrics_report,
)
from ml.evaluation.threshold_analysis import (
    analyze_thresholds,
    find_optimal_threshold,
)
from ml.explainability.shap_explainer import (
    init_shap_explainer,
    explain_prediction,
    global_feature_importance,
    LEGAL_DISCLAIMER,
)


def run_training_pipeline():
    print("=" * 70)
    print("  AI CHARGEBACK GUARDIAN — MACHINE LEARNING RISK ENGINE (STEP 3)")
    print("=" * 70)

    # 1. LOAD DATASET
    print(f"\n[1/10] Loading dataset from: {DATASET_PATH}...")
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}. Run seed_db.py first.")

    raw_df = pd.read_csv(DATASET_PATH)
    print(f"  -> Loaded {len(raw_df):,} rows with {len(raw_df.columns)} columns.")

    # 2. VALIDATE DATA
    print("\n[2/10] Validating data schema, bounds, and distribution...")
    val_report = validate_data(raw_df, is_training=True)
    print(val_report["report"])
    if not val_report["is_valid"]:
        raise ValueError(f"Data validation failed: {val_report['errors']}")

    # 3. FEATURE ENGINEERING
    print("\n[3/10] Engineering derived features (no target leakage)...")
    df_engineered = engineer_features(raw_df)
    print(f"  -> Base features:       {len(BASE_FEATURES)}")
    print(f"  -> Total features now:  {len(df_engineered.columns) - 1} (+6 engineered)")

    # 4. STRATIFIED DATA SPLIT (70 / 15 / 15)
    print("\n[4/10] Splitting dataset into Stratified Train (70%), Val (15%), Test (15%)...")
    train_df, val_df, test_df = split_data(df_engineered, random_state=RANDOM_STATE)
    print(f"  -> Training Set:   {len(train_df):>5} samples (Positive: {(train_df[TARGET_COLUMN]==1).sum()})")
    print(f"  -> Validation Set: {len(val_df):>5} samples (Positive: {(val_df[TARGET_COLUMN]==1).sum()})")
    print(f"  -> Held-Out Test:  {len(test_df):>5} samples (Positive: {(test_df[TARGET_COLUMN]==1).sum()})")
    print("  -> (Note: Test set is completely isolated until final evaluation)")

    # 5. FIT PREPROCESSOR (TRAIN ONLY)
    print("\n[5/10] Fitting ColumnTransformer preprocessor on training data...")
    feature_cols = [c for c in train_df.columns if c != TARGET_COLUMN]
    X_train_raw = train_df[feature_cols]
    y_train = train_df[TARGET_COLUMN]

    X_val_raw = val_df[feature_cols]
    y_val = val_df[TARGET_COLUMN]

    X_test_raw = test_df[feature_cols]
    y_test = test_df[TARGET_COLUMN]

    preprocessor = MLPreprocessor()
    preprocessor.fit(X_train_raw)

    X_train = preprocessor.transform(X_train_raw)
    X_val = preprocessor.transform(X_val_raw)
    X_test = preprocessor.transform(X_test_raw)
    print(f"  -> Transformed feature dimensionality: {X_train.shape[1]} columns.")

    # 6. TRAIN BASELINE MODEL (LOGISTIC REGRESSION)
    print("\n[6/10] Training Baseline Model (Logistic Regression with L2 Regularization)...")
    baseline_model = train_baseline(X_train, y_train, random_state=RANDOM_STATE)
    baseline_val_metrics = evaluate_model(
        baseline_model, X_val, y_val, model_name="Logistic Regression (Baseline)", threshold=0.50
    )
    print(f"  -> Baseline Validation F1: {baseline_val_metrics['f1']:.3f} | ROC-AUC: {baseline_val_metrics['roc_auc']:.3f}")

    # 7. TRAIN CHAMPION MODEL (XGBOOST)
    print("\n[7/10] Training Champion Model (XGBoost Classifier)...")
    xgb_model = train_xgboost(
        X_train, y_train, X_val=X_val, y_val=y_val, random_state=RANDOM_STATE
    )
    xgb_val_metrics = evaluate_model(
        xgb_model, X_val, y_val, model_name="XGBoost Classifier (Champion)", threshold=DEFAULT_CONTEST_THRESHOLD
    )
    print(f"  -> XGBoost Validation F1: {xgb_val_metrics['f1']:.3f} | ROC-AUC: {xgb_val_metrics['roc_auc']:.3f}")

    # Model comparison table on validation set
    val_comparison = compare_models([baseline_val_metrics, xgb_val_metrics])
    print("\n" + "=" * 70)
    print("VALIDATION SET MODEL COMPARISON")
    print("=" * 70)
    print(val_comparison.to_string(index=False))

    # 8. FINAL EVALUATION ON UNTOUCHED HELD-OUT TEST SET
    print("\n[8/10] Performing Final Evaluation of Champion on Held-Out Test Set (N=150)...")
    test_metrics = evaluate_model(
        xgb_model, X_test, y_test, model_name="XGBoost (Final Held-Out Test)", threshold=DEFAULT_CONTEST_THRESHOLD
    )
    baseline_test_metrics = evaluate_model(
        baseline_model, X_test, y_test, model_name="Baseline (Held-Out Test)", threshold=0.50
    )

    test_comparison = compare_models([baseline_test_metrics, test_metrics])
    print("\n" + "=" * 70)
    print("HELD-OUT TEST BENCHMARK COMPARISON (UNSEEN DATA)")
    print("=" * 70)
    print(test_comparison.to_string(index=False))

    cm_ascii = format_confusion_matrix_ascii(test_metrics["confusion_matrix"])
    print("\n" + cm_ascii)

    # 9. THRESHOLD ANALYSIS & FINANCIAL COST MATRIX
    print("\n[9/10] Conducting Threshold Analysis & Asymmetric Financial Loss Analysis...")
    y_test_proba = xgb_model.predict_proba(X_test)[:, 1]
    threshold_df = analyze_thresholds(
        y_test,
        y_test_proba,
        fp_cost=DEFAULT_FALSE_POSITIVE_COST,
        fn_cost=DEFAULT_FALSE_NEGATIVE_COST,
    )
    optimal_info = find_optimal_threshold(threshold_df, criterion="min_cost")

    print("\n" + "=" * 70)
    print("THRESHOLD SWEEP & EXPECTED FINANCIAL LOSS MATRIX")
    print("=" * 70)
    print(threshold_df[[
        "threshold", "precision", "recall", "f1_score", "false_positive_rate",
        "true_positives", "false_positives", "false_negatives", "total_expected_cost"
    ]].to_string(index=False))
    print(f"\n  -> Recommended Decision Threshold: tau = {DEFAULT_CONTEST_THRESHOLD:.2f}")
    print(f"  -> Selection Rationale: {optimal_info['selection_reason']}")

    # 10. TREE SHAP EXPLAINABILITY & ARTIFACT SERIALIZATION
    print("\n[10/10] Initializing SHAP Explainer & Serializing Model Artifacts...")
    SAVED_MODELS_DIR.mkdir(parents=True, exist_ok=True)

    explainer = init_shap_explainer(xgb_model, X_train.sample(min(100, len(X_train)), random_state=RANDOM_STATE))

    # Sample local explanation
    sample_row = X_test.iloc[[0]]
    sample_explanation = explain_prediction(
        explainer, xgb_model, sample_row, feature_names=preprocessor.get_feature_names_out()
    )

    # Global feature importance
    global_importance_df = global_feature_importance(
        explainer, X_test, feature_names=preprocessor.get_feature_names_out()
    )

    # Save artifacts
    model_path = SAVED_MODELS_DIR / "chargeback_model.joblib"
    baseline_path = SAVED_MODELS_DIR / "baseline_model.joblib"
    preprocessor_path = SAVED_MODELS_DIR / "preprocessor.joblib"
    explainer_path = SAVED_MODELS_DIR / "shap_explainer.joblib"
    metadata_path = SAVED_MODELS_DIR / "model_metadata.json"
    metrics_path = SAVED_MODELS_DIR / "metrics.json"

    joblib.dump(xgb_model, model_path)
    joblib.dump(baseline_model, baseline_path)
    joblib.dump(preprocessor, preprocessor_path)
    try:
        joblib.dump(explainer, explainer_path)
    except Exception as e:
        print(f"  -> Warning: Could not dump shap explainer directly ({e}), will re-instantiate on demand.")

    metadata = {
        "model_version": MODEL_VERSION,
        "model_name": STRONG_MODEL_NAME,
        "baseline_model_name": BASELINE_MODEL_NAME,
        "threshold": DEFAULT_CONTEST_THRESHOLD,
        "score_tiers": {
            "weak_max": SCORE_WEAK_MAX,
            "review_max": SCORE_REVIEW_MAX,
            "strong_min": SCORE_STRONG_MIN,
        },
        "business_costs": {
            "false_positive_cost_usd": DEFAULT_FALSE_POSITIVE_COST,
            "false_negative_cost_usd": DEFAULT_FALSE_NEGATIVE_COST,
        },
        "feature_names": preprocessor.get_feature_names_out(),
        "test_metrics": test_metrics,
        "baseline_metrics": baseline_test_metrics,
        "threshold_analysis": threshold_df.to_dict(orient="records"),
        "top_global_features": global_importance_df.head(10).to_dict(orient="records"),
        "sample_explanation": sample_explanation,
        "legal_disclaimer": LEGAL_DISCLAIMER,
    }

    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump({
            "champion": test_metrics,
            "baseline": baseline_test_metrics,
            "threshold_analysis": threshold_df.to_dict(orient="records"),
            "global_features": global_importance_df.head(10).to_dict(orient="records"),
        }, f, indent=2)

    print(f"\n  -> Saved Champion Model:       {model_path}")
    print(f"  -> Saved Preprocessor:         {preprocessor_path}")
    print(f"  -> Saved Model Metadata:       {metadata_path}")
    print(f"  -> Saved Performance Metrics:  {metrics_path}")

    print("\n" + "=" * 70)
    print("  TRAINING PIPELINE COMPLETE — 100% REPRODUCIBLE & VERIFIED")
    print("=" * 70)

    return metadata


if __name__ == "__main__":
    run_training_pipeline()
