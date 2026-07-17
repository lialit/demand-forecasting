import streamlit as st

from app_utils.charts import (
    competitive_price_chart,
    demand_proxy_chart,
    temperature_sales_chart,
    weekday_sales_chart,
)
from app_utils.components import render_page_header
from app_utils.filters import (
    apply_filters,
    render_sidebar_filters,
)
from app_utils.loader import load_dashboard_data
from app_utils.metrics import (
    calculate_executive_metrics,
    compact_number,
)


try:
    data = load_dashboard_data()
except (FileNotFoundError, ValueError) as error:
    st.error(str(error))
    st.stop()

filters = render_sidebar_filters(data)
filtered = apply_filters(data, filters)

render_page_header(
    "Business Insights",
    "Demand patterns, price position and hidden stock-out demand",
)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

left, right = st.columns(2)

with left:
    st.plotly_chart(
        weekday_sales_chart(filtered),
        width="stretch",
    )

with right:
    st.plotly_chart(
        temperature_sales_chart(filtered),
        width="stretch",
    )

left, right = st.columns(2)

with left:
    st.plotly_chart(
        competitive_price_chart(filtered),
        width="stretch",
    )

with right:
    st.plotly_chart(
        demand_proxy_chart(filtered),
        width="stretch",
    )

metrics = calculate_executive_metrics(filtered)

st.info(
    "Estimated hidden demand during stock-outs in the selected period: "
    f"{compact_number(metrics.hidden_demand)} units."
)
