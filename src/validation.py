import numpy as np
import pandas as pd

from src.metrics import evaluate_predictions


def get_three_month_backtest_split(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    months: int = 3,
):
    """Use the last N months as the backtest period."""
    max_date = df[timestamp_col].max()
    cutoff = max_date - pd.DateOffset(months=months)

    train_df = df[df[timestamp_col] < cutoff].copy()
    test_df = df[df[timestamp_col] >= cutoff].copy()

    return train_df, test_df


def create_naive_baselines(test_df: pd.DataFrame) -> pd.DataFrame:
    """Create naive and seasonal naive forecasts."""
    df = test_df.copy()
    df = df.sort_values(["store_id", "product_id", "timestamp"])

    group_cols = ["store_id", "product_id"]
    grouped_sales = df.groupby(group_cols)["sales"]

    df["naive_forecast_1h"] = grouped_sales.shift(1)
    df["seasonal_naive_24h"] = grouped_sales.shift(24)

    median_sales = df["sales"].median()
    df["naive_forecast_1h"] = df["naive_forecast_1h"].fillna(median_sales)
    df["seasonal_naive_24h"] = df["seasonal_naive_24h"].fillna(median_sales)

    return df


def evaluate_baselines(
    test_df: pd.DataFrame,
    target_col: str = "demand_proxy",
) -> pd.DataFrame:
    """Evaluate naive baseline models."""
    df = create_naive_baselines(test_df)

    rows = [
        {
            "Model": "Naive Forecast (previous hour)",
            **evaluate_predictions(df[target_col], df["naive_forecast_1h"]),
        },
        {
            "Model": "Seasonal Naive Forecast (previous day)",
            **evaluate_predictions(df[target_col], df["seasonal_naive_24h"]),
        },
    ]

    return pd.DataFrame(rows)


def future_permutation_test(
    raw_df: pd.DataFrame,
    feature_builder,
    suspicious_columns: list[str] | None = None,
    random_state: int = 42,
) -> dict:
    """Test whether future target permutation changes historical features."""
    if suspicious_columns is None:
        suspicious_columns = [
            "sales_lag_1h",
            "sales_lag_24h",
            "sales_lag_168h",
            "sales_rolling_mean_24h",
            "sales_rolling_std_24h",
        ]

    df_original = raw_df.sort_values("timestamp").reset_index(drop=True).copy()
    split_index = int(len(df_original) * 0.8)

    original_features = feature_builder(df_original)
    historical_original = original_features.loc[
        : split_index - 1,
        suspicious_columns,
    ].copy()

    df_permuted = df_original.copy()
    rng = np.random.default_rng(random_state)

    future_index = df_permuted.index[split_index:]
    df_permuted.loc[future_index, "sales"] = rng.permutation(
        df_permuted.loc[future_index, "sales"].values
    )

    permuted_features = feature_builder(df_permuted)
    historical_permuted = permuted_features.loc[
        : split_index - 1,
        suspicious_columns,
    ].copy()

    differences = (
        historical_original.fillna(-999999)
        != historical_permuted.fillna(-999999)
    ).sum().sum()

    passed = differences == 0

    return {
        "test_name": "Future Permutation Test",
        "passed": bool(passed),
        "checked_columns": suspicious_columns,
        "changed_values_count": int(differences),
        "explanation": (
            "Historical lag and rolling features remained unchanged after "
            "rebuilding features with permuted future target values."
            if passed
            else "Historical features changed after future target permutation."
        ),
    }