from pathlib import Path

import pandas as pd
import streamlit as st

from app_utils.config import DASHBOARD_DATA_PATH


@st.cache_data(
    show_spinner="Loading dashboard data...",
    ttl="1h",
)
def load_dashboard_data(
    path: Path = DASHBOARD_DATA_PATH,
) -> pd.DataFrame:
    """Load and validate the business dashboard dataset."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dashboard dataset not found: {path}. "
            "Run `python dashboard/build_dashboard_dataset.py` first."
        )

    df = pd.read_csv(path)

    required_columns = {
        "timestamp",
        "date",
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
        "weekday_name",
        "price_diff",
    }

    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Dashboard dataset is missing required columns: {missing}"
        )

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce",
    )

    date_text = (
        df["date"]
        .astype("string")
        .str.replace(r"\.0$", "", regex=True)
    )

    compact_date = pd.to_datetime(
        date_text,
        format="%Y%m%d",
        errors="coerce",
    )
    fallback_date = pd.to_datetime(
        date_text,
        errors="coerce",
    )
    df["date"] = compact_date.fillna(fallback_date)

    numeric_columns = [
        "sales",
        "demand_proxy",
        "stock_on_hand",
        "is_stockout",
        "temperature",
        "price",
        "competitor_price",
        "is_promo",
        "hour",
        "price_diff",
    ]

    df[numeric_columns] = df[numeric_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )

    return (
        df.dropna(subset=["date", "sales"])
        .convert_dtypes()
        .reset_index(drop=True)
    )
