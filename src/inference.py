import pandas as pd


def predict_demand(
    model,
    feature_df: pd.DataFrame,
    feature_columns: list[str],
) -> pd.DataFrame:
    """Generate demand forecasts from a trained model."""
    predictions = model.predict(feature_df[feature_columns])

    output = feature_df[["timestamp", "store_id", "product_id"]].copy()
    output["predicted_demand"] = predictions

    return output
