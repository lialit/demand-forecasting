import pandas as pd


def create_time_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.dayofweek
    df["month"] = df["timestamp"].dt.month
    df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

    return df


def create_price_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["price_diff"] = df["price"] - df["competitor_price"]
    df["price_ratio"] = df["price"] / df["competitor_price"]

    return df


def create_lag_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    group_cols = ["store_id", "product_id"]

    df["sales_lag_1h"] = df.groupby(group_cols)["sales"].shift(1)
    df["sales_lag_24h"] = df.groupby(group_cols)["sales"].shift(24)
    df["sales_lag_168h"] = df.groupby(group_cols)["sales"].shift(168)

    df["sales_rolling_mean_24h"] = (
        df.groupby(group_cols)["sales"]
        .shift(1)
        .rolling(24)
        .mean()
    )

    df["sales_rolling_std_24h"] = (
        df.groupby(group_cols)["sales"]
        .shift(1)
        .rolling(24)
        .std()
    )

    return df
