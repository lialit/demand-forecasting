import pandas as pd


def create_demand_proxy(df: pd.DataFrame) -> pd.DataFrame:
    """Create conservative demand proxy for stock-out observations."""
    df = df.copy()

    if "is_stockout" not in df.columns:
        raise ValueError("Column 'is_stockout' is required.")

    if "sales_rolling_mean_24h" not in df.columns:
        raise ValueError("Column 'sales_rolling_mean_24h' is required.")

    df["demand_proxy"] = df["sales"].astype(float)

    stockout_mask = df["is_stockout"] == 1
    recent_demand = df["sales_rolling_mean_24h"].fillna(df["sales"]).astype(float)

    adjusted_demand = pd.concat(
        [
            df.loc[stockout_mask, "sales"].astype(float),
            recent_demand.loc[stockout_mask],
        ],
        axis=1,
    ).max(axis=1)

    df.loc[stockout_mask, "demand_proxy"] = adjusted_demand

    return df


def summarize_censoring(df: pd.DataFrame) -> dict:
    """Summarize stock-out observations."""
    total_rows = len(df)
    stockout_rows = int(df["is_stockout"].sum())

    return {
        "total_rows": total_rows,
        "stockout_rows": stockout_rows,
        "stockout_share": round(stockout_rows / total_rows, 4)
        if total_rows
        else 0,
    }