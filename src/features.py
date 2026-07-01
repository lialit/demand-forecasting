import numpy as np
import pandas as pd


GROUP_COLUMNS = ["store_id", "product_id"]


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create calendar-based features."""
    df = df.copy()

    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    return df


def create_price_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create price-related features."""
    df = df.copy()

    df["price_diff"] = df["price"] - df["competitor_price"]
    df["price_ratio"] = np.where(
        df["competitor_price"] > 0,
        df["price"] / df["competitor_price"],
        1.0,
    )

    return df


def create_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    """Create leakage-safe lag and rolling features."""
    df = df.copy()
    df = df.sort_values(GROUP_COLUMNS + ["timestamp"]).reset_index(drop=True)

    grouped_sales = df.groupby(GROUP_COLUMNS)["sales"]

    df["sales_lag_1h"] = grouped_sales.shift(1)
    df["sales_lag_24h"] = grouped_sales.shift(24)
    df["sales_lag_168h"] = grouped_sales.shift(168)

    df["sales_rolling_mean_24h"] = grouped_sales.transform(
        lambda s: s.shift(1).rolling(window=24, min_periods=3).mean()
    )
    df["sales_rolling_std_24h"] = grouped_sales.transform(
        lambda s: s.shift(1).rolling(window=24, min_periods=3).std()
    )

    lag_columns = [
        "sales_lag_1h",
        "sales_lag_24h",
        "sales_lag_168h",
        "sales_rolling_mean_24h",
        "sales_rolling_std_24h",
    ]

    df[lag_columns] = df[lag_columns].fillna(0)

    return df


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Run complete feature engineering pipeline."""
    df = create_time_features(df)
    df = create_price_features(df)
    df = create_lag_features(df)

    return df