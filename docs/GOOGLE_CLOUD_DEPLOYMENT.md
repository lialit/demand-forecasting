# Google Cloud Deployment Guide

This guide translates the current repository into a practical Google Cloud deployment path.

It is intentionally implementation-oriented, but it does not assume that every client needs every service.

## 1. Recommended minimum viable production stack

For the first production version, use:

- Cloud Storage;
- BigQuery;
- Artifact Registry;
- Cloud Run Jobs;
- Cloud Scheduler;
- Vertex AI Custom Training;
- Vertex AI Model Registry;
- Cloud Logging and Cloud Monitoring;
- Looker or Looker Studio / Data Studio.

Vertex AI Pipelines can be introduced immediately or added after the first stable batch workflow, depending on project scope.

## 2. Environment structure

Recommended projects:

```text
forecasting-dev
forecasting-staging
forecasting-prod
```

Keep service accounts, buckets, datasets and model resources separate by environment.

Recommended regions should be selected according to:

- client data residency requirements;
- BigQuery and Vertex AI regional compatibility;
- Looker deployment region;
- latency to source systems;
- product availability.

## 3. Containerize the pipeline

Create a container image that includes:

- repository source code;
- Python dependencies;
- LightGBM system dependencies;
- one explicit entry point for training;
- one explicit entry point for batch inference.

Suggested entry points:

```text
python -m scripts.run_training_pipeline
python -m scripts.run_batch_forecast
```

Push images to Artifact Registry.

Use immutable image tags linked to a commit SHA rather than relying only on `latest`.

## 4. BigQuery design

Suggested tables:

```text
raw.sales
raw.inventory
raw.promotions
raw.external_factors

curated.hourly_demand_inputs
features.training_features
forecasts.demand_forecasts
monitoring.forecast_accuracy
monitoring.pipeline_runs
```

Partition time-series tables by date and cluster high-volume tables by `store_id` and `product_id` where this improves query patterns.

The production forecast table should preserve history rather than overwriting previous runs.

Example key fields:

```text
prediction_for_timestamp
store_id
product_id
model_version
pipeline_run_id
```

## 5. Data preparation

### Option A: BigQuery SQL and Dataform

Use when most preparation consists of joins, filters, aggregations and assertions.

Recommended uses:

- curated source tables;
- calendar enrichment;
- source freshness assertions;
- duplicate checks;
- referential integrity checks;
- stable feature views.

### Option B: Python job

Use when transformations depend on pandas, model-specific logic or custom time-series operations.

The current lag, rolling and demand-proxy logic fits naturally in Python.

A hybrid implementation is likely best:

```text
BigQuery/Dataform for curated source tables
Python for model-specific features and training
```

## 6. Training deployment

Run training as Vertex AI Custom Training.

Inputs:

- BigQuery training table or exported files;
- pipeline configuration;
- model hyperparameters;
- selected training period.

Outputs:

- trained model artifact;
- feature list;
- metrics JSON;
- prediction sample;
- evaluation plots;
- lineage metadata.

Register a new model version only if mandatory checks pass.

Example release checks:

- schema validation passed;
- leakage test passed;
- no invalid prediction values;
- MAE better than the agreed baseline;
- RMSE within the approved limit;
- forecast bias within tolerance.

## 7. Model Registry

Register each approved model version in Vertex AI Model Registry.

Recommended aliases or labels:

```text
candidate
staging
production
archived
```

Record:

- Git commit SHA;
- container image digest;
- dataset version or query snapshot;
- feature schema version;
- validation period;
- metrics;
- approval decision.

## 8. Batch forecasting deployment

### Preferred initial implementation: Cloud Run Job

A Cloud Run Job can:

1. query current features from BigQuery;
2. load the approved model artifact;
3. generate predictions;
4. write forecasts back to BigQuery;
5. write run metadata and quality checks.

This can be simpler than managed batch prediction for a custom LightGBM workflow.

### Managed alternative: Vertex AI Batch Prediction

Use when model packaging and input/output formats align well with Vertex AI prediction containers and the organization wants prediction jobs managed within Vertex AI.

The project should validate both approaches through a proof of concept before making a final choice.

## 9. Scheduling and orchestration

### Simple workflow

```text
Cloud Scheduler
  -> Workflows
  -> Cloud Run Job or Vertex AI Pipeline
  -> BigQuery
  -> monitoring checks
```

### ML pipeline workflow

```text
Cloud Scheduler
  -> Vertex AI Pipeline
      -> prepare data
      -> train or load approved model
      -> predict
      -> validate output
      -> publish forecasts
```

### Complex enterprise workflow

Use Cloud Composer 3 only when Airflow is justified by complex external dependencies, multiple systems and operational requirements.

Do not use Cloud Composer 1 for a new deployment.

## 10. BI deployment

### Enterprise option: Looker (Google Cloud core)

Use for governed enterprise metrics and client-facing analytics.

Recommended semantic measures:

- actual demand;
- forecast demand;
- absolute forecast error;
- forecast bias;
- stock-out rate;
- hidden demand estimate;
- baseline improvement.

### Lightweight option: Looker Studio / Data Studio

Use for rapid dashboards over prepared BigQuery tables.

Avoid embedding complex metric logic independently in multiple reports. Prefer calculating governed values in BigQuery or Looker modelling layers.

## 11. Logging and monitoring

Every pipeline run should emit structured metadata:

```text
pipeline_run_id
start_time
end_time
status
model_version
input_period
prediction_horizon
row_count
error_message
```

Create alerts for:

- failed scheduled jobs;
- missing forecast partition;
- zero-row output;
- abnormal runtime;
- stale production model;
- accuracy degradation after actuals arrive.

## 12. IAM

Use separate service accounts for:

- data preparation;
- model training;
- batch inference;
- BI access;
- deployment automation.

Grant only the permissions required for each component.

Avoid using user credentials inside containers or scheduled jobs.

Store secrets in Secret Manager.

## 13. CI/CD

Recommended pipeline:

```text
Git push / pull request
  -> unit tests
  -> linting
  -> container build
  -> vulnerability scan
  -> push to Artifact Registry
  -> deploy to dev
  -> integration checks
  -> controlled promotion to staging/prod
```

Use GitHub Actions or Cloud Build according to the client's preferred delivery platform.

## 14. Deployment sequence

### Phase 1

- containerize the existing pipeline;
- create BigQuery schemas;
- run batch inference through Cloud Run Jobs;
- schedule daily forecasts;
- publish forecasts to BigQuery;
- connect BI.

### Phase 2

- move training to Vertex AI Custom Training;
- register model versions;
- add release gates;
- add formal monitoring.

### Phase 3

- orchestrate with Vertex AI Pipelines;
- add automatic retraining candidates;
- add approval workflows;
- implement advanced drift analysis.

## 15. Product lifecycle safeguards

Before implementation:

- check current Google Cloud release notes;
- confirm product launch stages;
- avoid legacy APIs and notebook types;
- prefer current Vertex AI services;
- use Composer 3 if Airflow is required;
- do not adopt Vertex AI Feature Store Legacy/V1;
- confirm current Looker versus Looker Studio / Data Studio naming and licensing with the Google Cloud partner team.
