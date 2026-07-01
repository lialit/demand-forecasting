
import pandas as pd


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["temperature"] = df["temperature"].fillna(df["temperature"].median())
    df["competitor_price"] = df["competitor_price"].fillna(df["price"])
    df["app_clicks"] = df["app_clicks"].fillna(0)

    return df


def sort_time_series(df: pd.DataFrame) -> pd.DataFrame:
    return df.sort_values(["store_id", "product_id", "timestamp"]).reset_index(drop=True)
