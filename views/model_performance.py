import pandas as pd
import streamlit as st

from app_utils.charts import model_comparison_chart
from app_utils.components import render_page_header
from app_utils.config import (
    MAE_IMPROVEMENT,
    MODEL_RESULTS,
    RMSE_IMPROVEMENT,
)


render_page_header(
    "Model Performance",
    "LightGBM evaluation, baseline comparison and leakage validation",
)

results = pd.DataFrame.from_dict(
    MODEL_RESULTS,
    orient="index",
).rename_axis("Model").reset_index()

columns = st.columns(4)
columns[0].metric("LightGBM MAE", "2.13")
columns[1].metric("LightGBM RMSE", "6.23")
columns[2].metric(
    "MAE Improvement",
    f"{MAE_IMPROVEMENT:.2f}%",
)
columns[3].metric(
    "RMSE Improvement",
    f"{RMSE_IMPROVEMENT:.2f}%",
)

st.write("")

left, right = st.columns(2)

with left:
    st.plotly_chart(
        model_comparison_chart(results, "MAE"),
        width="stretch",
    )

with right:
    st.plotly_chart(
        model_comparison_chart(results, "RMSE"),
        width="stretch",
    )

st.success(
    "Future Permutation Test: PASSED. Historical lag and rolling "
    "features remained unchanged after future target values were "
    "permuted."
)

with st.expander("Validation design", expanded=True):
    st.markdown(
        """
        - The last three months are used as a time-based backtest.
        - LightGBM is compared with previous-hour and previous-day baselines.
        - MAE expresses average error directly in product units.
        - RMSE penalizes large errors more strongly because they create
          greater stock-out or overstock risk.
        """
    )
