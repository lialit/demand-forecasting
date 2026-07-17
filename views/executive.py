import streamlit as st

from app_utils.charts import (
    hourly_sales_chart,
    promotion_impact_chart,
    sales_trend_chart,
    stockout_by_store_chart,
)
from app_utils.components import (
    render_insight_cards,
    render_page_header,
)
from app_utils.filters import (
    apply_filters,
    render_sidebar_filters,
)
from app_utils.insights import generate_business_insights
from app_utils.loader import load_dashboard_data
from app_utils.metrics import (
    calculate_executive_metrics,
    daily_metric_series,
    period_delta,
)


try:
    data = load_dashboard_data()
except (FileNotFoundError, ValueError) as error:
    st.error(str(error))
    st.stop()

filters = render_sidebar_filters(data)
filtered = apply_filters(data, filters)

render_page_header(
    "Retail Demand Forecasting Dashboard",
    "Executive overview of demand, promotions and inventory risk",
)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

metrics = calculate_executive_metrics(filtered)
sales_delta = period_delta(filtered, "sales", "sum")
stockout_delta = period_delta(
    filtered,
    "is_stockout",
    "mean",
)

columns = st.columns(5)

columns[0].metric(
    label="💰 Total Sales",
    value=metrics.total_sales,
    delta=sales_delta,
    delta_description="selected-period trend",
    format="compact",
    chart_data=daily_metric_series(
        filtered,
        "sales",
        "sum",
    ),
    chart_type="area",
    border=True,
    width="stretch",
    height="stretch",
)

columns[1].metric(
    label="📈 Average Sales",
    value=metrics.average_sales,
    format="%.2f",
    chart_data=daily_metric_series(
        filtered,
        "sales",
        "mean",
    ),
    chart_type="line",
    border=True,
    width="stretch",
    height="stretch",
)

columns[2].metric(
    label="⚠️ Stock-out Rate",
    value=metrics.stockout_rate,
    delta=stockout_delta,
    delta_description="selected-period trend",
    delta_color="inverse",
    format="percent",
    chart_data=daily_metric_series(
        filtered,
        "is_stockout",
        "mean",
    ),
    chart_type="line",
    border=True,
    width="stretch",
    height="stretch",
)

columns[3].metric(
    label="🎁 Promotion Rate",
    value=metrics.promotion_rate,
    format="percent",
    chart_data=daily_metric_series(
        filtered,
        "is_promo",
        "mean",
    ),
    chart_type="bar",
    border=True,
    width="stretch",
    height="stretch",
)

columns[4].metric(
    label="🌡️ Average Temperature",
    value=metrics.average_temperature,
    format="%.1f °C",
    chart_data=daily_metric_series(
        filtered,
        "temperature",
        "mean",
    ),
    chart_type="line",
    border=True,
    width="stretch",
    height="stretch",
)

st.write("")

left, right = st.columns(2)

with left:
    st.plotly_chart(
        sales_trend_chart(filtered),
        width="stretch",
    )

with right:
    st.plotly_chart(
        hourly_sales_chart(filtered),
        width="stretch",
    )

left, right = st.columns(2)

with left:
    st.plotly_chart(
        promotion_impact_chart(filtered),
        width="stretch",
    )

with right:
    st.plotly_chart(
        stockout_by_store_chart(filtered),
        width="stretch",
    )

st.subheader("Key observations")
render_insight_cards(
    generate_business_insights(filtered)
)
