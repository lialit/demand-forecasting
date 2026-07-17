from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class ExecutiveMetrics:
    total_sales: float
    average_sales: float
    stockout_rate: float
    promotion_rate: float
    average_temperature: float
    hidden_demand: float


def calculate_executive_metrics(
    df: pd.DataFrame,
) -> ExecutiveMetrics:
    """Calculate headline metrics for the executive dashboard."""
    stockout_rows = df.loc[df["is_stockout"].eq(1)]

    hidden_demand = (
        stockout_rows["demand_proxy"]
        .sub(stockout_rows["sales"])
        .clip(lower=0)
        .sum()
    )

    return ExecutiveMetrics(
        total_sales=float(df["sales"].sum()),
        average_sales=float(df["sales"].mean()),
        stockout_rate=float(df["is_stockout"].mean()),
        promotion_rate=float(df["is_promo"].mean()),
        average_temperature=float(df["temperature"].mean()),
        hidden_demand=float(hidden_demand),
    )


def compact_number(value: float) -> str:
    """Format a number using K and M suffixes."""
    absolute_value = abs(value)

    if absolute_value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if absolute_value >= 1_000:
        return f"{value / 1_000:.1f}K"

    return f"{value:,.0f}"



def daily_metric_series(
    df: pd.DataFrame,
    column: str,
    aggregation: str = "sum",
    periods: int = 30,
) -> list[float]:
    """Return a compact daily series for a metric sparkline."""
    grouped = df.groupby("date")[column]

    if aggregation == "mean":
        series = grouped.mean()
    else:
        series = grouped.sum()

    return (
        series.sort_index()
        .tail(periods)
        .astype(float)
        .tolist()
    )


def period_delta(
    df: pd.DataFrame,
    column: str,
    aggregation: str = "sum",
) -> float | None:
    """Compare the latest half of the period with the preceding half."""
    daily = df.groupby("date")[column]

    if aggregation == "mean":
        series = daily.mean().sort_index()
    else:
        series = daily.sum().sort_index()

    if len(series) < 4:
        return None

    midpoint = len(series) // 2
    previous = float(series.iloc[:midpoint].mean())
    current = float(series.iloc[midpoint:].mean())

    if previous == 0:
        return None

    return (current - previous) / previous
