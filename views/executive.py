import streamlit as st

from app_utils.charts import (
    hourly_sales_chart,
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
    compact_number,
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
    "Business Overview",
    "A quick view of demand volume, stock-out risk and demand timing",
)

if filtered.empty:
    st.warning("No records match the selected filters.")
    st.stop()

metrics = calculate_executive_metrics(filtered)
sales_delta = period_delta(filtered, "sales", "sum")
stockout_delta = period_delta(filtered, "is_stockout", "mean")

sales_delta_text = f"{sales_delta:+.1%}" if sales_delta is not None else None
stockout_delta_text = (
    f"{stockout_delta:+.1%}" if stockout_delta is not None else None
)

st.markdown("### What is happening now?")
columns = st.columns(3)

columns[0].metric(
    label="Total demand served",
    value=f"{compact_number(metrics.total_sales)} units",
    delta=sales_delta_text,
    delta_description="versus the previous comparable period",
    chart_data=daily_metric_series(filtered, "sales", "sum"),
    chart_type="area",
    border=True,
    width="stretch",
)

columns[1].metric(
    label="Typical demand per record",
    value=f"{metrics.average_sales:.2f} units",
    help=(
        "Average observed sales for one store-product-hour record in the "
        "selected period."
    ),
    chart_data=daily_metric_series(filtered, "sales", "mean"),
    chart_type="line",
    border=True,
    width="stretch",
)

columns[2].metric(
    label="Stock-out risk",
    value=f"{metrics.stockout_rate:.2%}",
    delta=stockout_delta_text,
    delta_description="versus the previous comparable period",
    delta_color="inverse",
    help=(
        "Share of records where stock on hand was zero or below. Lower is "
        "better because stock-outs may hide unmet demand."
    ),
    chart_data=daily_metric_series(filtered, "is_stockout", "mean"),
    chart_type="line",
    border=True,
    width="stretch",
)

st.markdown("### Where should attention go?")
left, right = st.columns([1.35, 1])

with left:
    st.plotly_chart(
        sales_trend_chart(filtered),
        width="stretch",
    )

with right:
    st.plotly_chart(
        stockout_by_store_chart(filtered),
        width="stretch",
    )

st.markdown("### When does demand occur?")
st.plotly_chart(
    hourly_sales_chart(filtered),
    width="stretch",
)

st.markdown("### Recommended reading")
render_insight_cards(generate_business_insights(filtered)[:3])

with st.expander("Additional context", expanded=False):
    st.markdown(
        f"""
        - Promotion share in the selected period: **{metrics.promotion_rate:.2%}**
        - Average temperature: **{metrics.average_temperature:.1f} °C**
        - These figures describe the selected historical period; they are not
          themselves future forecasts.
        """
    )
