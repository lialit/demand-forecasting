import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def apply_chart_theme(
    figure: go.Figure,
    *,
    height: int = 370,
) -> go.Figure:
    """Apply shared styling to a Plotly figure."""
    figure.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=58, b=18),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#334155",
        ),
        title_font=dict(
            size=17,
            color="#102348",
        ),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#FFFFFF"),
    )
    figure.update_xaxes(
        gridcolor="#E8EDF4",
        zeroline=False,
    )
    figure.update_yaxes(
        gridcolor="#E8EDF4",
        zeroline=False,
    )
    return figure


def sales_trend_chart(df: pd.DataFrame) -> go.Figure:
    daily_sales = (
        df.groupby("date", as_index=False)
        .agg(total_sales=("sales", "sum"))
        .sort_values("date")
    )

    figure = px.line(
        daily_sales,
        x="date",
        y="total_sales",
        title="Sales Trend (Daily)",
        labels={
            "date": "Date",
            "total_sales": "Total Sales",
        },
    )
    figure.update_traces(
        line=dict(width=2.5),
        fill="tozeroy",
    )
    return apply_chart_theme(figure)


def hourly_sales_chart(df: pd.DataFrame) -> go.Figure:
    hourly_sales = (
        df.groupby("hour", as_index=False)
        .agg(average_sales=("sales", "mean"))
        .sort_values("hour")
    )

    figure = px.bar(
        hourly_sales,
        x="hour",
        y="average_sales",
        title="Average Sales by Hour of Day",
        labels={
            "hour": "Hour",
            "average_sales": "Average Sales",
        },
    )
    return apply_chart_theme(figure)


def promotion_impact_chart(df: pd.DataFrame) -> go.Figure:
    promotion_impact = (
        df.assign(
            promotion_status=df["is_promo"].map(
                {0: "No Promotion", 1: "With Promotion"}
            )
        )
        .groupby("promotion_status", as_index=False)
        .agg(average_sales=("sales", "mean"))
    )

    figure = px.bar(
        promotion_impact,
        x="promotion_status",
        y="average_sales",
        title="Promotion Impact on Average Sales",
        text_auto=".2f",
        labels={
            "promotion_status": "",
            "average_sales": "Average Sales",
        },
    )
    return apply_chart_theme(figure)


def stockout_by_store_chart(df: pd.DataFrame) -> go.Figure:
    stockout_by_store = (
        df.groupby("store_id", as_index=False)
        .agg(stockout_rate=("is_stockout", "mean"))
        .assign(
            stockout_rate_pct=lambda frame: (
                frame["stockout_rate"] * 100
            )
        )
        .nlargest(10, "stockout_rate_pct")
        .sort_values("stockout_rate_pct")
    )

    figure = px.bar(
        stockout_by_store,
        x="stockout_rate_pct",
        y=stockout_by_store["store_id"].astype("string"),
        orientation="h",
        title="Stock-out Rate by Store (Top 10)",
        text="stockout_rate_pct",
        labels={
            "stockout_rate_pct": "Stock-out Rate (%)",
            "y": "Store",
        },
    )
    figure.update_traces(
        texttemplate="%{text:.2f}%",
    )
    return apply_chart_theme(figure)


def model_comparison_chart(
    results: pd.DataFrame,
    metric: str,
) -> go.Figure:
    figure = px.bar(
        results,
        x="Model",
        y=metric,
        title=f"{metric} Comparison",
        text_auto=".2f",
    )
    figure.update_xaxes(tickangle=-18)
    return apply_chart_theme(figure)


def weekday_sales_chart(df: pd.DataFrame) -> go.Figure:
    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]

    weekday_sales = (
        df.groupby("weekday_name", as_index=False)
        .agg(average_sales=("sales", "mean"))
    )
    weekday_sales["weekday_name"] = pd.Categorical(
        weekday_sales["weekday_name"],
        categories=weekday_order,
        ordered=True,
    )
    weekday_sales = weekday_sales.sort_values("weekday_name")

    figure = px.bar(
        weekday_sales,
        x="weekday_name",
        y="average_sales",
        title="Average Sales by Weekday",
        labels={
            "weekday_name": "Weekday",
            "average_sales": "Average Sales",
        },
    )
    return apply_chart_theme(figure)


def temperature_sales_chart(df: pd.DataFrame) -> go.Figure:
    temperature_impact = (
        df.assign(
            temperature_range=pd.cut(
                df["temperature"],
                bins=8,
                duplicates="drop",
            ).astype("string")
        )
        .groupby(
            "temperature_range",
            as_index=False,
            observed=False,
        )
        .agg(average_sales=("sales", "mean"))
    )

    figure = px.bar(
        temperature_impact,
        x="temperature_range",
        y="average_sales",
        title="Average Sales by Temperature Range",
        labels={
            "temperature_range": "Temperature Range",
            "average_sales": "Average Sales",
        },
    )
    figure.update_xaxes(tickangle=-25)
    return apply_chart_theme(figure)


def competitive_price_chart(df: pd.DataFrame) -> go.Figure:
    price_effect = (
        df.assign(
            price_position=pd.cut(
                df["price_diff"],
                bins=[
                    -float("inf"),
                    -0.01,
                    0.01,
                    float("inf"),
                ],
                labels=[
                    "Cheaper than competitor",
                    "Price parity",
                    "More expensive",
                ],
            )
        )
        .groupby(
            "price_position",
            as_index=False,
            observed=False,
        )
        .agg(average_sales=("sales", "mean"))
    )

    figure = px.bar(
        price_effect,
        x="price_position",
        y="average_sales",
        title="Sales by Competitive Price Position",
        labels={
            "price_position": "",
            "average_sales": "Average Sales",
        },
    )
    return apply_chart_theme(figure)


def demand_proxy_chart(df: pd.DataFrame) -> go.Figure:
    comparison = (
        df.groupby("date", as_index=False)
        .agg(
            sales=("sales", "sum"),
            demand_proxy=("demand_proxy", "sum"),
        )
        .sort_values("date")
    )

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=comparison["date"],
            y=comparison["sales"],
            name="Observed Sales",
            mode="lines",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=comparison["date"],
            y=comparison["demand_proxy"],
            name="Demand Proxy",
            mode="lines",
        )
    )
    figure.update_layout(
        title="Observed Sales vs Demand Proxy"
    )
    return apply_chart_theme(figure)
