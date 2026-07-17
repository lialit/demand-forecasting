from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BusinessInsight:
    icon: str
    title: str
    message: str
    tone: str = "neutral"


def _safe_change(current: float, baseline: float) -> float:
    if baseline == 0:
        return 0.0
    return (current - baseline) / baseline


def generate_business_insights(
    df: pd.DataFrame,
) -> list[BusinessInsight]:
    """Generate deterministic business observations from filtered data."""
    insights: list[BusinessInsight] = []

    promo_means = (
        df.groupby("is_promo")["sales"]
        .mean()
        .to_dict()
    )
    no_promo_sales = float(promo_means.get(0, 0.0))
    promo_sales = float(promo_means.get(1, 0.0))
    promo_uplift = _safe_change(
        promo_sales,
        no_promo_sales,
    )

    if 0 in promo_means and 1 in promo_means:
        direction = "higher" if promo_uplift >= 0 else "lower"
        insights.append(
            BusinessInsight(
                icon="🎁",
                title="Promotion effect",
                message=(
                    "Average sales during promotions are "
                    f"{abs(promo_uplift):.1%} {direction} than "
                    "non-promotion sales."
                ),
                tone="positive" if promo_uplift >= 0 else "warning",
            )
        )

    stockout_by_store = (
        df.groupby("store_id")["is_stockout"]
        .mean()
        .sort_values(ascending=False)
    )
    if not stockout_by_store.empty:
        highest_store = str(stockout_by_store.index[0])
        highest_rate = float(stockout_by_store.iloc[0])
        insights.append(
            BusinessInsight(
                icon="⚠️",
                title="Inventory risk",
                message=(
                    f"Store {highest_store} has the highest selected "
                    f"stock-out rate at {highest_rate:.2%}."
                ),
                tone="warning",
            )
        )

    hourly_sales = (
        df.groupby("hour")["sales"]
        .mean()
        .sort_values(ascending=False)
    )
    if not hourly_sales.empty:
        peak_hour = int(hourly_sales.index[0])
        peak_sales = float(hourly_sales.iloc[0])
        insights.append(
            BusinessInsight(
                icon="🕒",
                title="Peak demand",
                message=(
                    f"Peak average demand occurs around {peak_hour:02d}:00 "
                    f"with {peak_sales:.2f} units per observation."
                ),
            )
        )

    stockout_rows = df.loc[df["is_stockout"].eq(1)]
    hidden_demand = (
        stockout_rows["demand_proxy"]
        .sub(stockout_rows["sales"])
        .clip(lower=0)
        .sum()
    )
    insights.append(
        BusinessInsight(
            icon="📦",
            title="Hidden demand",
            message=(
                "Estimated demand not visible in observed sales during "
                f"stock-outs is {hidden_demand:,.0f} units."
            ),
            tone="warning" if hidden_demand > 0 else "positive",
        )
    )

    return insights
