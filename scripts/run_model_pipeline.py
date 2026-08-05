from __future__ import annotations

import json
from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data_loading import load_data, validate_schema
from src.decensoring import create_demand_proxy
from src.features import build_features
from src.metrics import calculate_improvement
from src.preprocessing import add_stockout_flag, clean_data, sort_time_series
from src.training import train_and_evaluate
from src.validation import (
    evaluate_baselines,
    future_permutation_test,
    get_three_month_backtest_split,
)

RAW_DATA_PATH = PROJECT_ROOT / "data" / "demand_train_val_1.5years.csv"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
PREDICTIONS_PATH = ARTIFACTS_DIR / "model_predictions.csv"
METRICS_PATH = ARTIFACTS_DIR / "model_metrics.json"


def prepare_model_data(path: Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load source data and run the current feature pipeline."""
    df = load_data(path)
    validate_schema(df)
    df = clean_data(df)
    df = sort_time_series(df)
    df = add_stockout_flag(df)
    df = build_features(df)
    return create_demand_proxy(df)


def run_model_pipeline() -> tuple[pd.DataFrame, dict]:
    """Train, evaluate and persist dashboard-ready model artifacts."""
    df = prepare_model_data()
    train_df, test_df = get_three_month_backtest_split(df)

    _, model_metrics, predictions = train_and_evaluate(
        train_df,
        test_df,
        target_col="demand_proxy",
    )

    baseline_results = evaluate_baselines(
        test_df,
        target_col="demand_proxy",
    )

    best_baseline = baseline_results.sort_values("MAE").iloc[0]
    leakage_result = future_permutation_test(df, build_features)

    metrics_payload = {
        "model_name": "LightGBM",
        "validation_method": "Three-month time-based holdout",
        "target": "demand_proxy",
        "test_start": test_df["timestamp"].min().isoformat(),
        "test_end": test_df["timestamp"].max().isoformat(),
        "test_rows": int(len(test_df)),
        "model_metrics": model_metrics,
        "baseline_results": baseline_results.to_dict(orient="records"),
        "best_baseline": str(best_baseline["Model"]),
        "mae_improvement_pct": calculate_improvement(
            float(best_baseline["MAE"]),
            float(model_metrics["MAE"]),
        ),
        "rmse_improvement_pct": calculate_improvement(
            float(best_baseline["RMSE"]),
            float(model_metrics["RMSE"]),
        ),
        "leakage_test": leakage_result,
    }

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(PREDICTIONS_PATH, index=False)
    METRICS_PATH.write_text(
        json.dumps(metrics_payload, indent=2),
        encoding="utf-8",
    )

    return predictions, metrics_payload


if __name__ == "__main__":
    prediction_rows, metrics = run_model_pipeline()
    print(f"Predictions saved to: {PREDICTIONS_PATH}")
    print(f"Metrics saved to: {METRICS_PATH}")
    print(f"Prediction rows: {len(prediction_rows):,}")
    print(
        "Model metrics: "
        f"MAE={metrics['model_metrics']['MAE']}, "
        f"RMSE={metrics['model_metrics']['RMSE']}"
    )
