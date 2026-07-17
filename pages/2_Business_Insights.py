import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app_utils.common import (
    apply_app_style,
    chart_layout,
    compact_number,
    filter_data,
    load_dashboard_data,
)


st.set_page_config(
    page_title="Business Insights",
    page_icon="💡",
    layout="wide",
)

apply_app_style()

try:
    data = load_dashboard_data()
except FileNotFoundError as error:
    st.error(str(error))
    st.stop()

filtered = filter_data(data)

st.markdown(
    '<p class="dashboard-title">Business Insights</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="dashboard-subtitle">'
    "Demand patterns, price position and hidden stock-out demand"
    "</p>",
    unsafe_allow_html=True,
)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

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
    filtered.groupby("weekday_name", as_index=False)["sales"]
    .mean()
)
weekday_sales["weekday_name"] = pd.Categorical(
    weekday_sales["weekday_name"],
    categories=weekday_order,
    ordered=True,
)
weekday_sales = weekday_sales.sort_values("weekday_name")

temperature_impact = (
    filtered.assign(
        temperature_range=pd.cut(
            filtered["temperature"],
            bins=8,
            duplicates="drop",
        ).astype(str)
    )
    .groupby(
        "temperature_range",
        as_index=False,
        observed=False,
    )["sales"]
    .mean()
)

price_effect = (
    filtered.assign(
        price_position=pd.cut(
            filtered["price_diff"],
            bins=[-float("inf"), -0.01, 0.01, float("inf")],
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
    )["sales"]
    .mean()
)

demand_comparison = (
    filtered.groupby("date", as_index=False)[
        ["sales", "demand_proxy"]
    ]
    .sum()
    .sort_values("date")
)

left, right = st.columns(2)

with left:
    fig = px.bar(
        weekday_sales,
        x="weekday_name",
        y="sales",
        title="Average Sales by Weekday",
        labels={
            "weekday_name": "Weekday",
            "sales": "Average Sales",
        },
    )
    st.plotly_chart(
        chart_layout(fig),
        use_container_width=True,
    )

with right:
    fig = px.bar(
        temperature_impact,
        x="temperature_range",
        y="sales",
        title="Average Sales by Temperature Range",
        labels={
            "temperature_range": "Temperature Range",
            "sales": "Average Sales",
        },
    )
    fig.update_xaxes(tickangle=-25)
    st.plotly_chart(
        chart_layout(fig),
        use_container_width=True,
    )

left, right = st.columns(2)

with left:
    fig = px.bar(
        price_effect,
        x="price_position",
        y="sales",
        title="Sales by Competitive Price Position",
        labels={
            "price_position": "",
            "sales": "Average Sales",
        },
    )
    st.plotly_chart(
        chart_layout(fig),
        use_container_width=True,
    )

with right:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=demand_comparison["date"],
            y=demand_comparison["sales"],
            name="Observed Sales",
            mode="lines",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=demand_comparison["date"],
            y=demand_comparison["demand_proxy"],
            name="Demand Proxy",
            mode="lines",
        )
    )
    fig.update_layout(title="Observed Sales vs Demand Proxy")
    st.plotly_chart(
        chart_layout(fig),
        use_container_width=True,
    )

stockout_rows = filtered[filtered["is_stockout"] == 1]
hidden_demand = (
    stockout_rows["demand_proxy"] - stockout_rows["sales"]
).clip(lower=0).sum()

st.info(
    "Estimated hidden demand during stock-outs in the selected period: "
    f"{compact_number(hidden_demand)} units."
)
