from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from app_utils.charts import apply_chart_theme


def actual_vs_predicted_chart(
    df: pd.DataFrame,
    aggregation: str = "Hourly",
) -> go.Figure:
    """Plot actual and predicted demand on the same time axis."""
    chart_df = df.copy().sort_values("timestamp")

    if aggregation == "Daily":
        chart_df = (
            chart_df.assign(period=chart_df["timestamp"].dt.floor("D"))
            .groupby("period", as_index=False)
            .agg(
                actual_demand=("actual_demand", "sum"),
                predicted_demand=("predicted_demand", "sum"),
            )
            .rename(columns={"period": "timestamp"})
        )

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=chart_df["timestamp"],
            y=chart_df["actual_demand"],
            name="Actual demand",
            mode="lines",
            line=dict(width=2.5),
        )
    )
    figure.add_trace(
        go.Scatter(
            x=chart_df["timestamp"],
            y=chart_df["predicted_demand"],
            name="Predicted demand",
            mode="lines",
            line=dict(width=2.2, dash="dash"),
        )
    )
    figure.update_layout(
        title=f"Actual vs Predicted Demand ({aggregation})",
        hovermode="x unified",
    )
    figure.update_xaxes(title="Time")
    figure.update_yaxes(title="Demand, product units")

    return apply_chart_theme(figure, height=440)
