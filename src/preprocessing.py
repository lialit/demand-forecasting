import pandas as pd


def sort_time_series(df: pd.DataFrame) -> pd.DataFrame:
    """Sort data chronologically for each store-product pair."""
    return (
        df.sort_values(["store_id", "product_id", "timestamp"])
        .reset_index(drop=True)
    )


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean missing values without using future target information."""
    df = df.copy()

    df["temperature"] = df["temperature"].fillna(df["temperature"].median())
    df["competitor_price"] = df["competitor_price"].fillna(df["price"])
    df["app_clicks"] = df["app_clicks"].fillna(0)
    df["holiday_factor"] = df["holiday_factor"].fillna(0)
    df["delivery_delay_hours"] = df["delivery_delay_hours"].fillna(0)
    df["local_event_factor"] = df["local_event_factor"].fillna(1)

    return df


def add_stockout_flag(df: pd.DataFrame) -> pd.DataFrame:
    """Mark observations where demand may be censored due to stock-out."""
    df = df.copy()
    df["is_stockout"] = (df["stock_on_hand"] <= 0).astype(int)
    return df


def time_based_split(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
    test_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split dataset by time to avoid data leakage."""
    df = df.sort_values(timestamp_col).reset_index(drop=True)
    split_index = int(len(df) * (1 - test_size))

    train_df = df.iloc[:split_index].copy()
    test_df = df.iloc[split_index:].copy()

    return train_df, test_df