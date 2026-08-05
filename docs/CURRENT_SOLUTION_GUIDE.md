# Current Solution Architecture and Code Guide

This document describes the demand forecasting solution **as it is currently implemented** in the repository. It is intended to help developers and stakeholders understand where data preparation, feature engineering, model training, evaluation, validation, inference and dashboard preparation take place.

> Scope note: this repository is currently a production-oriented prototype. It contains modular ML components and an interactive dashboard, but it does not yet include a complete production orchestration, automated retraining, drift monitoring, model registry or deployment pipeline.

## 1. End-to-end flow

```text
Raw CSV
   ↓
src/data_loading.py
   ↓
src/preprocessing.py
   ↓
src/features.py
   ↓
src/decensoring.py
   ↓
src/validation.py
   ↓
src/training.py
   ↓
src/metrics.py
   ↓
src/inference.py
   ↓
dashboard/build_dashboard_dataset.py
   ↓
Streamlit application
```

## 2. Module responsibilities

### `src/data_loading.py`

Responsible for loading the source CSV and validating the basic input schema.

Main functions:

- `load_data(path)`
  - reads the CSV file;
  - parses `timestamp` as datetime;
  - raises `FileNotFoundError` when the file does not exist.
- `validate_schema(df)`
  - checks that all required source columns are present;
  - checks that `timestamp` values were parsed successfully.

Current validation is limited to required columns and timestamps. It does not yet validate numeric ranges, duplicates, negative values, hourly continuity or key uniqueness.

### `src/preprocessing.py`

Responsible for cleaning, chronological ordering, stock-out detection and basic time-based splitting.

Main functions:

- `clean_data(df)`
  - fills missing temperature with the global median;
  - fills missing competitor price with the product's own price;
  - uses neutral defaults for app clicks, holidays, delays and local events.
- `sort_time_series(df)`
  - sorts rows by `store_id`, `product_id` and `timestamp`.
- `add_stockout_flag(df)`
  - creates `is_stockout = 1` when `stock_on_hand <= 0`.
- `time_based_split(df, test_size=0.2)`
  - performs one chronological train/test split.

The missing-value strategy is feature-specific. It is not a universal median-imputation pipeline.

### `src/features.py`

Responsible for feature engineering.

Calendar features:

- `hour`
- `day_of_week`
- `month`
- `is_weekend`

Price features:

- `price_diff = price - competitor_price`
- `price_ratio = price / competitor_price`

Historical sales features, created separately for each `store_id` and `product_id` pair:

- `sales_lag_1h`
- `sales_lag_24h`
- `sales_lag_168h`
- `sales_rolling_mean_24h`
- `sales_rolling_std_24h`

Lag and rolling features use `shift(1)`, so the current target value is not used as its own feature.

Missing historical values are currently filled with zero. This is a simple cold-start fallback and may not be optimal for new stores or products.

### `src/decensoring.py`

Responsible for creating a conservative demand proxy during stock-out periods.

Main function:

- `create_demand_proxy(df)`

Logic:

```text
Normal observation:
    demand_proxy = sales

Stock-out observation:
    demand_proxy = max(sales, recent 24-hour rolling mean)
```

This is a business heuristic intended to reduce underestimation of demand when sales are constrained by unavailable stock. It is not a statistically identified estimate of true hidden demand.

Additional function:

- `summarize_censoring(df)`
  - returns total rows, stock-out rows and stock-out share.

### `src/validation.py`

Responsible for time-based validation helpers, baseline forecasts and a leakage-oriented test.

Main functions:

- `get_three_month_backtest_split(df, months=3)`
  - uses the final three calendar months as the test period;
  - this is one time-based holdout, not a multi-fold walk-forward backtest.
- `create_naive_baselines(test_df)`
  - creates previous-hour and previous-day forecasts.
- `evaluate_baselines(test_df)`
  - calculates MAE and RMSE for the two baselines.
- `future_permutation_test(raw_df, feature_builder)`
  - permutes future sales;
  - rebuilds lag and rolling features;
  - verifies that historical feature values remain unchanged.

The permutation test checks the historical stability of lag and rolling features. It does not prove the absence of every possible form of leakage.

Current baseline limitation:

- baselines are created inside the test set;
- initial missing lags are filled with the median of test-set sales;
- a more rigorous implementation should build baselines on the combined train and test chronology and evaluate only test rows.

### `src/training.py`

Responsible for selecting features, training the LightGBM model, generating predictions and calculating metrics.

#### Feature set

The current model uses the following columns:

```text
store_id
product_id
temperature
local_event_factor
price
is_promo
competitor_price
delivery_delay_hours
holiday_factor
app_clicks
stock_on_hand
hour
day_of_week
month
is_weekend
price_diff
price_ratio
sales_lag_1h
sales_lag_24h
sales_lag_168h
sales_rolling_mean_24h
sales_rolling_std_24h
is_stockout
```

#### Target

The default target is:

```text
demand_proxy
```

#### Model training

The model is currently created in `train_lightgbm_model()`:

```python
lgb.LGBMRegressor(
    objective="regression",
    n_estimators=500,
    learning_rate=0.05,
    num_leaves=31,
    random_state=42,
    n_jobs=-1,
)
```

Training happens here:

```python
model.fit(X_train, y_train)
```

Prediction happens here:

```python
predictions = model.predict(X_test)
```

Evaluation happens here:

```python
metrics = evaluate_predictions(y_test, predictions)
```

The LightGBM parameters are manually defined as a stable project configuration. They are not the output of a documented hyperparameter-optimization process.

#### Returned outputs

`train_and_evaluate()` returns:

1. the trained model;
2. a metrics dictionary;
3. a prediction dataframe with timestamp, store, product, target and prediction.

The model type is currently hardcoded to LightGBM. A future refactor should move model construction to a configurable model factory.

### `src/metrics.py`

Responsible for regression metrics and comparison with baselines.

Main functions:

- `evaluate_predictions(y_true, y_pred)`
  - calculates MAE;
  - calculates RMSE.
- `calculate_improvement(baseline_score, model_score)`
  - calculates percentage improvement over a baseline.

Metrics are currently rounded inside the metric function. A future improvement is to preserve full precision in artifacts and round only in the presentation layer.

### `src/inference.py`

Provides a reusable inference helper.

Main function:

- `predict_demand(model, feature_df, feature_columns)`
  - selects model features;
  - calls `model.predict()`;
  - returns `timestamp`, `store_id`, `product_id` and `predicted_demand`.

This is not yet a complete production inference pipeline. It does not load a persisted model, validate incoming data, build features, save forecasts or support recursive long-horizon forecasting.

### `dashboard/build_dashboard_dataset.py`

Builds the dataset used by the business dashboard.

The current dashboard dataset contains historical and business-analysis fields such as:

- `sales`
- `demand_proxy`
- `stock_on_hand`
- `is_stockout`
- `temperature`
- `price`
- `competitor_price`
- `is_promo`
- calendar fields

Current limitation:

- the dashboard dataset does not include model predictions;
- therefore Actual vs Predicted cannot be produced from the current dashboard file alone.

### `app_utils/config.py`

Contains dashboard paths and manually defined model results.

Current model metrics and improvement percentages are hardcoded. If the model, data, features or validation period changes, the dashboard will continue to display old values until they are manually edited.

A future pipeline should save metrics as an artifact and load them dynamically.

### `views/model_performance.py`

Displays:

- LightGBM MAE and RMSE;
- baseline comparison;
- improvement percentages;
- Future Permutation Test message;
- validation notes.

Current limitations:

- metrics are static;
- there is no Actual vs Predicted chart;
- there are no store/product filters;
- there are no local metrics for a selected slice;
- labels are tied specifically to LightGBM.

## 3. Current forecasting scenario

The use of historical lags inside the test period is closest to a rolling one-step-ahead scenario:

> New actual sales arrive over time, and the next forecast is refreshed using the latest observed history.

It is not yet a strict multi-step forecast for an entire future week or month, because future lag values inside such a horizon would not be available without recursive prediction.

This distinction should be stated when presenting model performance.

## 4. Meaning of the current metrics

### MAE

MAE measures the average absolute difference between predicted and target demand.

Business interpretation:

> An MAE of 2.13 means that the forecast differs from the demand proxy by about 2.13 product units on average for one product-store-hour observation.

### RMSE

RMSE penalizes large forecast errors more strongly than MAE.

Business interpretation:

> A materially larger RMSE than MAE indicates that the model sometimes makes larger errors, for example during peaks, unusual events or difficult stock-out periods.

### Improvement over baseline

Improvement values compare the model with simple previous-hour or previous-day forecasts.

They describe relative predictive improvement, not direct financial savings. Financial impact requires additional business inputs such as margin, spoilage cost, stock-out cost and service-level targets.

## 5. Current strengths

- modular data-processing code;
- chronological splitting instead of random splitting;
- explicit feature list;
- lag and rolling features shifted to avoid direct target leakage;
- baseline comparison;
- conservative stock-out adjustment;
- separate training, metrics and inference modules;
- interactive Streamlit dashboard;
- prediction dataframe already produced by training.

## 6. Current limitations

- one three-month holdout rather than full walk-forward validation;
- baseline initialization uses test-set median values;
- no explicit recursive multi-step forecasting;
- demand proxy is heuristic rather than observed ground truth;
- LightGBM is hardcoded in training;
- model parameters are manually selected;
- metrics are hardcoded in dashboard config;
- predictions are not included in the dashboard dataset;
- no central executable training pipeline;
- no experiment tracking, model registry or automated retraining;
- no drift monitoring;
- no production API or scheduled batch-prediction workflow.

## 7. Recommended next changes

1. Save predictions and metrics as reproducible artifacts.
2. Add Actual vs Predicted to the dashboard.
3. Load dashboard metrics dynamically instead of hardcoding them.
4. Correct baseline generation across train and test chronology.
5. Replace model-specific training with a configurable model factory.
6. Clarify the forecasting horizon and evaluation scenario.
7. Either implement true walk-forward validation or consistently describe the current method as a three-month time-based holdout.
8. Update README wording to match the implemented solution.
9. Add business-oriented interpretations and limitations to the dashboard.
10. Define a future Google Cloud batch-inference and retraining architecture.

## 8. Quick code navigation

| Question | Location |
|---|---|
| Where is the CSV loaded? | `src/data_loading.py::load_data` |
| Where is the schema checked? | `src/data_loading.py::validate_schema` |
| Where are missing values handled? | `src/preprocessing.py::clean_data` |
| Where is stock-out detected? | `src/preprocessing.py::add_stockout_flag` |
| Where are lag features built? | `src/features.py::create_lag_features` |
| Where is the demand proxy created? | `src/decensoring.py::create_demand_proxy` |
| Where is the final three-month split created? | `src/validation.py::get_three_month_backtest_split` |
| Where are baseline forecasts created? | `src/validation.py::create_naive_baselines` |
| Where is leakage-related validation performed? | `src/validation.py::future_permutation_test` |
| Where is LightGBM created? | `src/training.py::train_lightgbm_model` |
| Where is the model trained? | `src/training.py`, `model.fit(...)` |
| Where are forecasts generated during evaluation? | `src/training.py`, `model.predict(...)` |
| Where are MAE and RMSE calculated? | `src/metrics.py::evaluate_predictions` |
| Where is reusable inference implemented? | `src/inference.py::predict_demand` |
| Where is the dashboard CSV built? | `dashboard/build_dashboard_dataset.py` |
| Where are dashboard metrics currently defined? | `app_utils/config.py` |
| Where is the model-performance page rendered? | `views/model_performance.py` |
