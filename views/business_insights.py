import streamlit as st

from app_utils.charts import (
    competitive_price_chart,
    demand_proxy_chart,
    promotion_impact_chart,
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
    "Demand Drivers",
    "Explore when demand changes and which business factors are associated with it",
)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

metrics = calculate_executive_metrics(filtered)

st.info(
    "Estimated demand not directly observed during stock-outs: "
    f"**{compact_number(metrics.hidden_demand)} units** in the selected period. "
    "This is a conservative proxy, not confirmed lost sales."
)

st.markdown("### When is demand stronger?")
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

st.markdown("### Which commercial factors are associated with demand?")
left, right = st.columns(2)

with left:
    st.plotly_chart(
        promotion_impact_chart(filtered),
        width="stretch",
    )

with right:
    st.plotly_chart(
        competitive_price_chart(filtered),
        width="stretch",
    )

st.markdown("### How much demand may be hidden by stock-outs?")
st.plotly_chart(
    demand_proxy_chart(filtered),
    width="stretch",
)

with st.expander("How to use these charts", expanded=False):
    st.markdown(
        """
        - These charts show **associations**, not proof of causation.
        - Promotion and price effects may also reflect product mix, seasonality
          or store differences.
        - The demand proxy estimates possible unmet demand when inventory was
          unavailable; it should be validated against operational data.
        - Use these views to identify segments for deeper analysis, not as an
          automatic pricing or replenishment rule.
        """
    )
