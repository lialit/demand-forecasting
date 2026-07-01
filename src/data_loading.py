from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = {
    "timestamp",
    "store_id",
    "product_id",
    "temperature",
    "local_event_factor",
    "price",
    "is_promo",
    "competitor_price",
    "delivery_delay_hours",
    "holiday_factor",
    "app_clicks",
    "stock_on_hand",
    "sales",
}


def load_data(path: str | Path) -> pd.DataFrame:
    """Load source CSV data and parse timestamp column."""
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Data file not found: {path}")

    df = pd.read_csv(path)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    return df


def validate_schema(df: pd.DataFrame) -> None:
    """Validate that all expected source columns are available."""
    missing_columns = REQUIRED_COLUMNS.difference(df.columns)

    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing}")

    if df["timestamp"].isna().any():
        raise ValueError("Column 'timestamp' contains invalid datetime values.")
