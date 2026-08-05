# Retraining and Monitoring Strategy

This document defines a practical monitoring and retraining approach for the demand forecasting solution.

The thresholds below are examples. Final values must be calibrated with historical data, business costs and client service-level objectives.

## 1. Monitoring objectives

Monitoring should answer four questions:

1. Did the pipeline run successfully?
2. Are the input data complete and plausible?
3. Has the operating environment changed?
4. Is the forecast still useful for business decisions?

## 2. Pipeline monitoring

Track every scheduled run.

Required fields:

```text
pipeline_run_id
scheduled_time
start_time
end_time
status
model_version
input_data_end
forecast_horizon
input_row_count
output_row_count
error_message
```

Alert conditions:

- pipeline failed;
- forecast table was not produced;
- output row count is zero;
- forecast partition is late;
- execution time is materially above normal;
- production model cannot be loaded;
- downstream write failed.

Recommended Google Cloud services:

- Cloud Logging;
- Cloud Monitoring;
- alerting policies;
- BigQuery monitoring tables.

## 3. Data quality monitoring

### Schema checks

- required columns exist;
- timestamp is valid;
- numeric fields have valid types;
- key columns are non-null;
- expected categorical values are present.

### Uniqueness and continuity

- one row per timestamp-store-product key;
- duplicate count;
- missing hourly intervals;
- missing stores or products;
- source freshness.

### Range checks

- non-negative sales;
- non-negative stock;
- valid prices;
- reasonable temperature range;
- valid promotion flags;
- plausible delivery delay values.

### Missing-value checks

Track missing rates for every source feature and compare them with historical norms.

A sudden increase in missing values should block or quarantine the run when the affected feature is critical.

## 4. Data drift monitoring

Data drift means that current input distributions differ from the distributions used to train the model.

Monitor at least:

- sales and demand proxy;
- stock-on-hand;
- stock-out rate;
- price;
- competitor price;
- promotion frequency;
- app clicks;
- temperature;
- holiday and local-event factors;
- store and product mix.

Useful statistics:

- mean and median;
- standard deviation;
- quantiles;
- missing rate;
- category frequency;
- population stability index or another agreed drift statistic.

Monitor both globally and by important segments.

A stable global distribution can hide serious changes in one store, product group or demand tier.

## 5. Prediction drift monitoring

Prediction drift means that the forecast distribution changes materially, even before actual values become available.

Track:

- average predicted demand;
- prediction quantiles;
- share of zero predictions;
- share of unusually high predictions;
- forecast volatility;
- forecasts by store and product segment;
- difference from naive baseline predictions.

Prediction drift is an investigation signal, not automatic proof that the model is wrong.

## 6. Model performance monitoring

When actual demand becomes available, join forecasts with actual observations using:

```text
prediction_for_timestamp
store_id
product_id
```

Calculate:

- MAE;
- RMSE;
- mean forecast bias;
- underforecast rate;
- overforecast rate;
- model improvement versus baselines;
- metrics by store;
- metrics by product;
- metrics by demand volume;
- metrics during promotions and stock-outs.

### Business-cost metrics

When business cost data becomes available, add:

- estimated lost-sales cost;
- estimated overstock carrying cost;
- waste cost;
- service-level impact;
- weighted asymmetric error.

Underforecast and overforecast normally have different business costs. MAE alone cannot represent this asymmetry.

## 7. Example alert thresholds

The following are starting points only:

- MAE increased by more than 15–20% relative to the approved reference period;
- RMSE increased materially while MAE remained stable, indicating larger peak errors;
- absolute mean bias exceeded an agreed number of units or percentage of average demand;
- model no longer outperformed the best naive baseline;
- critical source missing rate exceeded the agreed limit;
- stock-out rate shifted materially;
- new stores or products exceeded the cold-start capacity of the current model.

Use persistence rules to avoid alerts caused by one noisy hour or day.

Example:

```text
trigger only if the threshold is exceeded for 3 consecutive evaluation windows
```

## 8. Retraining policy

Use both scheduled review and event-driven review.

### Scheduled review

Recommended starting point:

- monthly performance review;
- quarterly full retraining review;
- additional review before major seasonal periods.

The correct cadence depends on demand volatility, assortment changes and data volume.

### Event-driven triggers

Create a new model candidate when one or more conditions occur:

- persistent accuracy degradation;
- persistent forecast bias;
- meaningful input drift;
- new stores;
- large numbers of new products;
- assortment restructuring;
- pricing or promotion policy change;
- supply-chain process change;
- seasonal transition;
- feature pipeline change.

## 9. Candidate evaluation

A retraining trigger should create a candidate, not automatically replace production.

Candidate checks:

1. schema and data-quality validation;
2. time-based backtest;
3. comparison with the production model;
4. comparison with naive baselines;
5. leakage checks;
6. segment-level performance;
7. bias analysis;
8. business-cost analysis when available;
9. reproducibility and artifact checks.

## 10. Promotion policy

Promote a candidate only when:

- mandatory technical checks pass;
- it meets or exceeds agreed global thresholds;
- it does not create unacceptable regressions in critical segments;
- its bias is within tolerance;
- business owners approve material trade-offs;
- model metadata and lineage are complete.

Recommended Model Registry states:

```text
candidate
validated
staging
production
archived
```

## 11. Rollback

Every production deployment should preserve:

- previous production model version;
- previous container image;
- feature schema version;
- configuration;
- forecast publication procedure.

Rollback conditions:

- invalid forecasts;
- downstream integration failures;
- severe performance regression;
- unexpected business impact;
- data-pipeline mismatch.

## 12. Google Cloud implementation

Suggested implementation:

```text
BigQuery monitoring tables
        |
        v
scheduled SQL / Dataform / Python evaluation
        |
        v
Cloud Monitoring custom metrics and alerts
        |
        +--> operational alert
        |
        +--> retraining candidate trigger
                    |
                    v
             Vertex AI Pipeline
                    |
                    v
             Model Registry
                    |
                    v
             approval and promotion
```

Vertex AI managed monitoring capabilities may be evaluated where they fit the selected serving pattern. For batch forecasting, BigQuery-based monitoring plus Cloud Monitoring can provide a transparent and flexible first implementation.

## 13. Product lifecycle safeguards

Avoid building new monitoring or retraining dependencies on deprecated Google Cloud components.

In particular:

- use current Vertex AI services rather than Legacy AI Platform;
- avoid Vertex AI Feature Store Legacy/V1;
- use current Vertex AI Workbench instances if managed notebook environments are required;
- use Cloud Composer 3 only if Airflow is justified;
- review Vertex AI and Looker release notes before implementation.
