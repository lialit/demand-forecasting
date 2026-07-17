from pathlib import Path
import sys

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from src.data_loading import load_data, validate_schema
from src.preprocessing import clean_data, sort_time_series, add_stockout_flag
from src.features import build_features
from src.decensoring import create_demand_proxy


RAW_DATA_PATH = PROJECT_ROOT / "data" / "demand_train_val_1.5years.csv"
OUTPUT_PATH = PROJECT_ROOT / "dashboard" / "demand_dashboard.csv"


def build_dashboard_dataset() -> pd.DataFrame:
    """Prepare clean business-friendly dataset for Looker Studio."""
    df = load_data(RAW_DATA_PATH)
    validate_schema(df)

    df = clean_data(df)
    df = sort_time_series(df)
    df = add_stockout_flag(df)
    df = build_features(df)
    df = create_demand_proxy(df)

    dashboard_df = df[
        [
            "timestamp",
            "store_id",
            "product_id",
            "sales",
            "demand_proxy",
            "stock_on_hand",
            "is_stockout",
            "temperature",
            "price",
            "competitor_price",
            "is_promo",
            "hour",
            "day_of_week",
            "month",
        ]
    ].copy()

    # Looker Studio works more reliably with YYYYMMDD date format from CSV.
    dashboard_df["date"] = dashboard_df["timestamp"].dt.strftime("%Y%m%d")

    # Keep timestamp as text for display / optional datetime parsing.
    dashboard_df["timestamp"] = dashboard_df["timestamp"].dt.strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    dashboard_df["year"] = pd.to_datetime(
        dashboard_df["date"], format="%Y%m%d"
    ).dt.year

    dashboard_df["quarter"] = pd.to_datetime(
        dashboard_df["date"], format="%Y%m%d"
    ).dt.quarter

    dashboard_df["week"] = pd.to_datetime(
        dashboard_df["date"], format="%Y%m%d"
    ).dt.isocalendar().week.astype(int)

    dashboard_df["weekday_name"] = pd.to_datetime(
        dashboard_df["date"], format="%Y%m%d"
    ).dt.day_name()

    dashboard_df["month_name"] = pd.to_datetime(
        dashboard_df["date"], format="%Y%m%d"
    ).dt.month_name()

    dashboard_df["price_diff"] = (
        dashboard_df["price"] - dashboard_df["competitor_price"]
    )

    dashboard_df["stockout_label"] = dashboard_df["is_stockout"].map(
        {0: "In stock", 1: "Stock-out"}
    )

    dashboard_df["promo_label"] = dashboard_df["is_promo"].map(
        {0: "No promo", 1: "Promo"}
    )

    dashboard_df.to_csv(OUTPUT_PATH, index=False)

    return dashboard_df


if __name__ == "__main__":
    result = build_dashboard_dataset()
    print(f"Dashboard dataset saved to: {OUTPUT_PATH}")
    print(f"Shape: {result.shape}")
    print("\nColumns:")
    for column in result.columns:
        print(f"- {column}")