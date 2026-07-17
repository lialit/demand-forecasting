import streamlit as st

from app_utils.components import render_page_header


render_page_header(
    "About the Project",
    "Production-oriented demand forecasting for a dark store network",
)

st.markdown(
    """
    ### Business objective

    Forecast hourly product demand for each store-product pair to support
    15-minute delivery, replenishment planning and inventory optimization.

    ### Solution

    - Modular Python pipeline
    - Leakage-safe lag and rolling features
    - Stock-out / censored demand adjustment
    - LightGBM regression
    - Three-month time-based backtest
    - Future Permutation Test
    - Interactive Streamlit analytics application

    ### Main results

    | Model | MAE | RMSE |
    |---|---:|---:|
    | Naive Forecast | 8.72 | 17.07 |
    | Seasonal Naive Forecast | 7.66 | 15.07 |
    | LightGBM | 2.13 | 6.23 |

    The improved model reduced MAE by **72.15%** and RMSE by **58.63%**
    relative to the best naive baseline.
    """
)
