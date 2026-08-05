import lightgbm as lgb
import pandas as pd

from src.metrics import evaluate_predictions


FEATURE_COLUMNS = [
    "store_id",
    "product_id",
    "temperature",
    "local_event_factor",
    "price",
    "is_promo",
    "competitor_price",
    "delivery_delay_hours",
    "holiday_factor",
    "app_clicks",
    "stock_on_hand",
    "hour",
    "day_of_week",
    "month",
    "is_weekend",
    "price_diff",
    "price_ratio",
    "sales_lag_1h",
    "sales_lag_24h",
    "sales_lag_168h",
    "sales_rolling_mean_24h",
    "sales_rolling_std_24h",
    "is_stockout",
]


def get_feature_target_data(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_col: str = "demand_proxy",
):
    """Prepare train and test matrices."""
    X_train = train_df[FEATURE_COLUMNS]
    y_train = train_df[target_col]

    X_test = test_df[FEATURE_COLUMNS]
    y_test = test_df[target_col]

    return X_train, y_train, X_test, y_test


def train_lightgbm_model(
    X_train: pd.DataFrame,
    y_train: pd.Series,
) -> lgb.LGBMRegressor:
    """Train the current LightGBM regression model."""
    model = lgb.LGBMRegressor(
        objective="regression",
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    return model


def train_and_evaluate(
    train_df: pd.DataFrame,
    test_df: pd.DataFrame,
    target_col: str = "demand_proxy",
):
    """Train the model, evaluate it and return row-level forecasts."""
    X_train, y_train, X_test, y_test = get_feature_target_data(
        train_df,
        test_df,
        target_col=target_col,
    )

    model = train_lightgbm_model(X_train, y_train)
    predictions = model.predict(X_test)

    metrics = evaluate_predictions(y_test, predictions)

    prediction_df = test_df[
        ["timestamp", "store_id", "product_id"]
    ].copy()
    prediction_df["actual_demand"] = y_test.to_numpy()
    prediction_df["predicted_demand"] = predictions
    prediction_df["forecast_error"] = (
        prediction_df["predicted_demand"]
        - prediction_df["actual_demand"]
    )

    return model, metrics, prediction_df
