import numpy as np
import pandas as pd
import streamlit as st

from app_utils.business_interpretation import (
    build_business_summary,
    interpret_bias,
    interpret_error_level,
    retraining_guidance,
)
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
    "How closely the forecast follows demand and what the result means for business",
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

st.subheader("Business summary")
for conclusion in build_business_summary(
    mae=model_metrics["MAE"],
    rmse=model_metrics["RMSE"],
    mae_improvement=mae_improvement,
    rmse_improvement=rmse_improvement,
):
    st.markdown(f"- {conclusion}")

columns = st.columns(4)
columns[0].metric(
    "Typical forecast miss",
    f"{model_metrics['MAE']:.2f} units",
    help=(
        "The average absolute difference between forecast and actual demand. "
        "Lower is better."
    ),
)
columns[1].metric(
    "Large-error indicator",
    f"{model_metrics['RMSE']:.2f} units",
    help=(
        "This metric reacts strongly to occasional large misses. Lower is better."
    ),
)
columns[2].metric(
    "Average-error reduction",
    f"{mae_improvement:.2f}%",
    help="Improvement over the best simple previous-hour or previous-day baseline.",
)
columns[3].metric(
    "Large-error reduction",
    f"{rmse_improvement:.2f}%",
    help="Reduction in RMSE relative to the best simple baseline.",
)

if artifacts_available:
    st.subheader("Actual demand vs forecast")
    st.caption(
        "Choose one dark store and product. The closer the two lines are, "
        "the more accurately the model follows real demand."
    )

    filter_left, filter_middle, filter_right = st.columns(3)

    store_options = sorted(predictions["store_id"].dropna().unique())
    selected_store = filter_left.selectbox("Dark store", store_options)

    store_predictions = predictions[
        predictions["store_id"] == selected_store
    ]
    product_options = sorted(
        store_predictions["product_id"].dropna().unique()
    )
    selected_product = filter_middle.selectbox("Product", product_options)
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
            "Typical miss for selection",
            f"{local_mae:.2f} units",
        )
        local_columns[1].metric(
            "Large-error indicator",
            f"{local_rmse:.2f} units",
        )
        local_columns[2].metric(
            "Forecast bias",
            f"{mean_bias:+.2f} units",
            help=(
                "Positive means overforecasting; negative means underforecasting."
            ),
        )

        bias_title, bias_text = interpret_bias(mean_bias)
        st.markdown(f"**{bias_title}.** {bias_text}")
        st.caption(interpret_error_level(local_mae, local_rmse))

st.write("")
st.subheader("Comparison with simple planning rules")
st.caption(
    "The baselines represent forecasts that simply reuse demand from the "
    "previous hour or previous day. Lower bars are better."
)
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
            "Leakage check passed for lag and rolling features: changing future "
            "sales did not alter historical feature values."
        )
    else:
        st.warning("The current leakage check did not pass.")
else:
    st.success(
        "The documented project run passed the lag-feature leakage check. "
        "Generate artifacts to load the current result dynamically."
    )

with st.expander("What these results do and do not prove", expanded=True):
    st.markdown(
        """
        - **MAE** describes the typical error in product units.
        - **RMSE** highlights occasional large errors that may create greater
          stock-out or overstock risk.
        - **Forecast bias** shows whether the model persistently over- or
          under-predicts demand.
        - The current validation uses the **last three months as one time-based
          holdout period**. It is not a multi-fold walk-forward evaluation.
        - Accuracy metrics alone do not calculate financial savings. A monetary
          business case requires product margin, waste cost, stock-out cost and
          replenishment constraints.
        - The dataset is synthetic, so the result demonstrates the method rather
          than guaranteed production performance on a client's real operations.
        """
    )

with st.expander("When should the model be reviewed or retrained?"):
    for condition in retraining_guidance():
        st.markdown(f"- {condition}")
    st.caption(
        "Exact thresholds should be agreed with the client and tested against "
        "historical business impact."
    )
