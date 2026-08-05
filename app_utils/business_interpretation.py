from __future__ import annotations


def interpret_bias(mean_bias: float) -> tuple[str, str]:
    """Return a short business interpretation of forecast bias."""
    if abs(mean_bias) < 0.25:
        return (
            "Balanced forecast",
            "The selected forecast has little systematic over- or under-forecasting.",
        )

    if mean_bias > 0:
        return (
            "Overforecasting tendency",
            (
                "The model predicts more demand than is observed on average. "
                "This may increase inventory and waste risk if the pattern is persistent."
            ),
        )

    return (
        "Underforecasting tendency",
        (
            "The model predicts less demand than is observed on average. "
            "This may increase stock-out and lost-sales risk if the pattern is persistent."
        ),
    )


def interpret_error_level(mae: float, rmse: float) -> str:
    """Explain the relationship between average and large forecast errors."""
    if mae <= 0:
        return "The current selection does not contain a meaningful error estimate."

    error_ratio = rmse / mae

    if error_ratio < 1.35:
        return (
            "Forecast errors are relatively consistent. Large misses are not much "
            "larger than the typical error for this selection."
        )

    if error_ratio < 2.0:
        return (
            "The forecast is usually close, but some periods contain noticeably "
            "larger errors. Demand peaks and unusual operating conditions should be reviewed."
        )

    return (
        "Large forecast misses occur more often than the average error alone suggests. "
        "Review demand spikes, promotions, events and stock-out periods before using the "
        "forecast for automated replenishment."
    )


def build_business_summary(
    *,
    mae: float,
    rmse: float,
    mae_improvement: float,
    rmse_improvement: float,
) -> list[str]:
    """Build concise business-facing conclusions from model metrics."""
    return [
        (
            f"The model misses actual demand by about {mae:.2f} product units "
            "on average for each evaluated store-product-time observation."
        ),
        (
            f"Compared with the best simple baseline, average error was reduced by "
            f"{mae_improvement:.2f}% and large-error sensitivity improved by "
            f"{rmse_improvement:.2f}%."
        ),
        interpret_error_level(mae, rmse),
        (
            "These metrics describe forecasting accuracy, not direct financial value. "
            "To estimate savings, the client must add product margin, waste cost, "
            "stock-out cost and replenishment constraints."
        ),
    ]


def retraining_guidance() -> list[str]:
    """Return practical conditions that should trigger model review or retraining."""
    return [
        "MAE or RMSE increases materially against the approved production baseline.",
        "Forecast bias becomes persistently positive or negative for important products.",
        "The distribution of prices, promotions, traffic, stock levels or demand changes.",
        "New stores, products or operating regions are introduced.",
        "Seasonality or customer behavior changes after holidays, campaigns or market events.",
        "A scheduled retraining date is reached, even when no alert has fired.",
    ]
