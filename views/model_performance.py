import numpy as np
import pandas as pd
import streamlit as st

from app_utils.charts import model_comparison_chart
from app_utils.components import render_page_header
from app_utils.config import (
    MAE_IMPROVEMENT,
    MODEL_RESULTS,
    RMSE_IMPROVEMENT,
)
from app_utils.forecast_charts import actual_vs_predicted_chart
from app_utils.model_artifacts import (
    load_model_metrics,
    load_model_predictions,
)


render_page_header(
    "Model Performance",
    "Actual demand, model forecasts, baseline comparison and validation",
)

try:
    metrics_payload = load_model_metrics()
    predictions = load_model_predictions()
    artifacts_available = True
except (FileNotFoundError, ValueError) as error:
    artifacts_available = False
    metrics_payload = None
    predictions = pd.DataFrame()
    st.info(
        "Model artifacts have not been generated yet. "
        "Run `python scripts/run_model_pipeline.py` to enable the "
        "Actual vs Predicted chart and live metrics."
    )
    st.caption(str(error))

if artifacts_available:
    model_name = metrics_payload.get("model_name", "Forecast model")
    model_metrics = metrics_payload["model_metrics"]
    mae_improvement = metrics_payload["mae_improvement_pct"]
    rmse_improvement = metrics_payload["rmse_improvement_pct"]

    results = pd.DataFrame(metrics_payload["baseline_results"])
    results = pd.concat(
        [
            results,
            pd.DataFrame(
                [
                    {
                        "Model": model_name,
                        "MAE": model_metrics["MAE"],
                        "RMSE": model_metrics["RMSE"],
                    }
                ]
            ),
        ],
        ignore_index=True,
    )
else:
    model_name = "LightGBM"
    model_metrics = MODEL_RESULTS["LightGBM improved model"]
    mae_improvement = MAE_IMPROVEMENT
    rmse_improvement = RMSE_IMPROVEMENT
    results = (
        pd.DataFrame.from_dict(MODEL_RESULTS, orient="index")
        .rename_axis("Model")
        .reset_index()
    )

columns = st.columns(4)
columns[0].metric(
    "Average forecast error",
    f"{model_metrics['MAE']:.2f} units",
    help=(
        "MAE: on average, the forecast differs from actual demand by "
        "this many product units. Lower is better."
    ),
)
columns[1].metric(
    "Large-error indicator",
    f"{model_metrics['RMSE']:.2f} units",
    help=(
        "RMSE gives extra weight to occasional large forecast errors. "
        "Lower is better."
    ),
)
columns[2].metric(
    "MAE vs best baseline",
    f"{mae_improvement:.2f}% better",
)
columns[3].metric(
    "RMSE vs best baseline",
    f"{rmse_improvement:.2f}% better",
)

if artifacts_available:
    st.subheader("Actual vs Predicted Demand")
    st.caption(
        "Choose one dark store and product to see how closely the model "
        "follows real demand over time."
    )

    filter_left, filter_middle, filter_right = st.columns(3)

    store_options = sorted(predictions["store_id"].dropna().unique())
    selected_store = filter_left.selectbox(
        "Dark store",
        store_options,
    )

    store_predictions = predictions[
        predictions["store_id"] == selected_store
    ]
    product_options = sorted(
        store_predictions["product_id"].dropna().unique()
    )
    selected_product = filter_middle.selectbox(
        "Product",
        product_options,
    )
    aggregation = filter_right.radio(
        "Time aggregation",
        ["Hourly", "Daily"],
        horizontal=True,
    )

    selected_predictions = store_predictions[
        store_predictions["product_id"] == selected_product
    ].copy()

    if selected_predictions.empty:
        st.warning("No predictions are available for this selection.")
    else:
        st.plotly_chart(
            actual_vs_predicted_chart(
                selected_predictions,
                aggregation=aggregation,
            ),
            width="stretch",
        )

        errors = (
            selected_predictions["predicted_demand"]
            - selected_predictions["actual_demand"]
        )
        local_mae = errors.abs().mean()
        local_rmse = np.sqrt(np.mean(np.square(errors)))
        mean_bias = errors.mean()

        local_columns = st.columns(3)
        local_columns[0].metric(
            "Selected-series MAE",
            f"{local_mae:.2f} units",
        )
        local_columns[1].metric(
            "Selected-series RMSE",
            f"{local_rmse:.2f} units",
        )
        local_columns[2].metric(
            "Average forecast bias",
            f"{mean_bias:+.2f} units",
            help=(
                "Positive means the model tends to overforecast; negative "
                "means it tends to underforecast."
            ),
        )

st.write("")
st.subheader("Comparison with simple baselines")
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

if artifacts_available:
    leakage_result = metrics_payload.get("leakage_test", {})
    if leakage_result.get("passed"):
        st.success(
            "Future Permutation Test: PASSED. Historical lag and rolling "
            "features did not change after future sales values were permuted."
        )
    else:
        st.warning("Future Permutation Test did not pass.")
else:
    st.success(
        "Future Permutation Test: PASSED in the documented project run. "
        "Generate artifacts to load the current result dynamically."
    )

with st.expander("How to interpret these metrics", expanded=True):
    st.markdown(
        """
        - **MAE** is the average absolute difference between forecast and
          actual demand, expressed in product units. Lower is better.
        - **RMSE** rises more strongly when the model makes occasional large
          mistakes, which may create higher stock-out or overstock risk.
        - **Improvement vs baseline** shows how much error was reduced compared
          with a simple previous-hour or previous-day forecast.
        - The current validation uses the **last three months as one time-based
          holdout period**. It is not a multi-fold walk-forward evaluation.
        """
    )
