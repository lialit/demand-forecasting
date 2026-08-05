import streamlit as st

from app_utils.components import render_page_header


render_page_header(
    "How It Works",
    "A plain-language guide to the current forecasting solution",
)

st.markdown(
    """
    ### What the solution does

    The model estimates hourly demand for each **dark store-product pair**.
    The output is intended to support replenishment and inventory planning by
    showing how much demand is expected and where forecast risk is higher.

    ### How the data moves through the solution

    1. **Load and validate data** — required columns and timestamps are checked.
    2. **Clean the inputs** — missing values are handled with rules specific to
       each field.
    3. **Build historical features** — the model uses recent sales, daily and
       weekly lags, rolling statistics, calendar variables, prices, promotions,
       weather and inventory information.
    4. **Estimate hidden demand** — stock-out observations receive a conservative
       demand proxy based on recent sales history.
    5. **Train the model** — LightGBM learns relationships between the features
       and the demand proxy.
    6. **Evaluate the model** — the last three months are held out and compared
       with simple previous-hour and previous-day forecasts.
    7. **Publish artifacts** — predictions and metrics are saved for the
       dashboard.

    ### What the main metrics mean

    - **MAE: 2.13 units** — the forecast differs from actual demand by about two
      units on average for one store-product-hour record.
    - **RMSE: 6.23 units** — occasional large misses still occur, especially in
      more difficult periods.
    - **72.15% lower MAE than the best simple baseline** — the model materially
      improves on repeating recent demand patterns.

    These results are from the current project dataset. They do not directly
    quantify profit, lost sales or inventory savings because unit economics are
    not available.

    ### Current limitations

    - The validation is one three-month time-based holdout, not multi-fold
      walk-forward backtesting.
    - The demand proxy is an estimation rule, not observed ground truth.
    - The current dataset is synthetic, so production performance may differ.
    - Drift monitoring, automatic retraining and deployment are not yet
      implemented.

    ### Where to look in the repository

    | Question | Location |
    |---|---|
    | Where is the model trained? | `src/training.py` |
    | Where are features created? | `src/features.py` |
    | Where is demand adjusted for stock-outs? | `src/decensoring.py` |
    | Where are metrics calculated? | `src/metrics.py` |
    | Where is validation defined? | `src/validation.py` |
    | Where are predictions generated? | `src/inference.py` |
    | Where is the full architecture documented? | `docs/CURRENT_SOLUTION_GUIDE.md` |
    """
)
