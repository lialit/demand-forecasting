import pandas as pd
import plotly.express as px
import streamlit as st

from app_utils.common import apply_app_style, chart_layout


st.set_page_config(
    page_title="Model Performance",
    page_icon="🤖",
    layout="wide",
)

apply_app_style()

st.markdown(
    '<p class="dashboard-title">Model Performance</p>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p class="dashboard-subtitle">'
    "LightGBM evaluation, baseline comparison and leakage validation"
    "</p>",
    unsafe_allow_html=True,
)

results = pd.DataFrame(
    {
        "Model": [
            "Naive Forecast (previous hour)",
            "Seasonal Naive Forecast (previous day)",
            "LightGBM improved model",
        ],
        "MAE": [8.72, 7.66, 2.13],
        "RMSE": [17.07, 15.07, 6.23],
    }
)

columns = st.columns(4)
columns[0].metric("LightGBM MAE", "2.13")
columns[1].metric("LightGBM RMSE", "6.23")
columns[2].metric("MAE Improvement", "72.15%")
columns[3].metric("RMSE Improvement", "58.63%")

st.markdown("")

left, right = st.columns(2)

with left:
    fig = px.bar(
        results,
        x="Model",
        y="MAE",
        title="Mean Absolute Error Comparison",
        text_auto=".2f",
    )
    fig.update_xaxes(tickangle=-18)
    st.plotly_chart(
        chart_layout(fig),
        use_container_width=True,
    )

with right:
    fig = px.bar(
        results,
        x="Model",
        y="RMSE",
        title="Root Mean Squared Error Comparison",
        text_auto=".2f",
    )
    fig.update_xaxes(tickangle=-18)
    st.plotly_chart(
        chart_layout(fig),
        use_container_width=True,
    )

st.success(
    "Future Permutation Test: PASSED. Historical lag and rolling features "
    "remained unchanged after future target values were permuted."
)

st.markdown(
    """
    ### Validation design

    - The final evaluation uses the last three months as a time-based backtest.
    - LightGBM is compared with previous-hour and previous-day baselines.
    - MAE expresses average error directly in product units.
    - RMSE penalizes large errors more strongly because they create greater
      stock-out or overstock risk.
    """
)
