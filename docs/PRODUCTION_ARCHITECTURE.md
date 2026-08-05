# Production Architecture

This document describes how the current demand forecasting prototype can evolve into a production solution on Google Cloud.

The repository currently contains a modular local Python pipeline, reproducible model artifacts and a Streamlit dashboard. The architecture below is a recommended target state, not a claim that every component is already implemented.

## 1. Business objective

Forecast demand at the Product–Dark Store–Hour level and make the result available to inventory planning, replenishment, operations and analytics systems.

The production solution should support:

- scheduled demand forecasts;
- traceable model versions;
- reliable storage of inputs, outputs and metrics;
- monitoring of data quality and forecast quality;
- controlled retraining;
- integration with ERP, WMS, BI and planning tools.

## 2. Recommended Google Cloud architecture

```text
Source systems
ERP / POS / WMS / promotions / weather / holidays
        |
        v
Cloud Storage and/or ingestion connectors
        |
        v
BigQuery raw and curated datasets
        |
        v
Data quality and feature preparation
Dataform / BigQuery SQL / Python jobs
        |
        v
Vertex AI Pipelines
        |
        +--> Vertex AI Custom Training
        |        |
        |        v
        |   Vertex AI Model Registry
        |
        +--> Evaluation and release checks
        |
        v
Vertex AI Batch Prediction or Cloud Run Job
        |
        v
BigQuery forecast tables
        |
        +--> Looker (Google Cloud core)
        +--> Looker Studio / Data Studio
        +--> ERP / WMS / replenishment systems
        +--> APIs and operational applications
```

## 3. Why batch forecasting is the default

Demand planning normally does not require a permanently deployed low-latency endpoint. A scheduled batch process is usually simpler and more cost-efficient.

Recommended default:

- generate forecasts hourly or daily;
- forecast the agreed planning horizon;
- write predictions into BigQuery;
- let downstream systems read the latest approved forecast version.

An online endpoint should be added only when a client system needs predictions synchronously for an individual request.

## 4. Data layer

### Cloud Storage

Use Cloud Storage for:

- raw files received from external systems;
- exported training datasets;
- model artifacts and pipeline outputs;
- temporary batch prediction inputs and outputs;
- backups and long-term retention where appropriate.

### BigQuery

Use BigQuery as the analytical system of record for:

- historical sales;
- inventory snapshots;
- promotions and prices;
- competitor prices;
- weather and holiday enrichment;
- training datasets;
- forecast outputs;
- evaluation metrics;
- monitoring history.

Suggested datasets:

```text
raw
curated
features
forecasts
monitoring
```

Each forecast record should include at least:

```text
forecast_timestamp
prediction_for_timestamp
store_id
product_id
predicted_demand
model_version
pipeline_run_id
created_at
```

## 5. Feature preparation

For the current project, feature engineering is implemented in Python. In production, the split between SQL and Python should be chosen deliberately.

Good candidates for BigQuery SQL or Dataform:

- schema normalization;
- joins between sales, inventory and promotion tables;
- calendar dimensions;
- daily data quality assertions;
- reusable curated tables.

Good candidates for Python pipeline components:

- model-specific lag and rolling features;
- demand proxy logic;
- training matrices;
- model evaluation;
- serialization of custom LightGBM models.

Do not introduce a feature store only because it is fashionable. For scheduled batch forecasting, versioned BigQuery feature tables may be sufficient. If a feature store is later required, use the current Vertex AI Feature Store offering and avoid Vertex AI Feature Store Legacy/V1 and deprecated optimized online serving components.

## 6. Training and model management

### Vertex AI Custom Training

Package the current modular Python pipeline into a reproducible training job.

The job should:

1. read a versioned training dataset;
2. run preprocessing and feature engineering;
3. perform time-based evaluation;
4. calculate model and baseline metrics;
5. run leakage checks;
6. save the model and metadata;
7. register an approved model version.

### Vertex AI Model Registry

Use Model Registry to store and govern model versions.

Recommended metadata:

- model name and version;
- training dataset period;
- feature schema version;
- hyperparameters;
- MAE, RMSE and bias;
- baseline improvements;
- approval status;
- code commit SHA;
- pipeline run identifier.

## 7. Orchestration

### Recommended default: Vertex AI Pipelines

Use Vertex AI Pipelines for the ML workflow:

```text
prepare data
  -> build features
  -> train
  -> evaluate
  -> validate
  -> register model
  -> generate batch forecasts
  -> publish outputs
```

### Lightweight scheduling

For simple schedules, use Cloud Scheduler to trigger one of:

- Workflows;
- a Cloud Run Job;
- a Vertex AI Pipeline run.

### Complex Airflow orchestration

Use Managed Service for Apache Airflow only when there are complex cross-system dependencies that justify Airflow. For new implementations, prefer Cloud Composer 3. Do not design a new solution around Cloud Composer 1, which is approaching end of life.

## 8. Prediction and serving

### Batch option

Preferred for this project:

- Vertex AI Batch Prediction when the registered model and serving container fit the workflow;
- Cloud Run Jobs when custom Python inference and direct BigQuery writes provide a simpler implementation.

The choice should be validated in a small proof of concept because custom LightGBM packaging, input format, cost and operational simplicity may differ by client environment.

### Online option

Use a Vertex AI endpoint or Cloud Run service only when a client application needs low-latency predictions on demand.

## 9. BI and downstream use

### Looker (Google Cloud core)

Recommended for enterprise BI when the client needs:

- governed metric definitions;
- LookML modelling;
- robust access control;
- embedded analytics;
- scheduled delivery and alerts;
- stronger Google Cloud administration integration.

### Looker Studio / Data Studio

Suitable for:

- rapid reporting;
- lightweight self-service dashboards;
- prototypes;
- simple reports over prepared BigQuery tables.

Google documentation currently presents the self-service product under Data Studio naming in some updated pages. To reduce documentation risk, implementation documents should refer to the product as `Looker Studio / Data Studio` until the client's licensed product and current Google naming are confirmed.

## 10. Monitoring

Monitor four layers:

### Pipeline health

- scheduled run success;
- duration;
- failed steps;
- missing outputs;
- stale forecasts.

Use Cloud Logging, Cloud Monitoring and alerting policies.

### Data quality

- missing required columns;
- invalid timestamps;
- duplicate store-product-hour keys;
- missing hours;
- abnormal price or inventory values;
- unexpected category values.

### Data and prediction drift

- average demand;
- price distribution;
- promotion frequency;
- stock-out frequency;
- temperature;
- app clicks;
- predicted demand distribution.

### Model quality

When actual demand becomes available, calculate:

- MAE;
- RMSE;
- forecast bias;
- metrics by store, product and demand segment;
- comparison with baseline forecasts.

## 11. Security and governance

Recommended controls:

- separate development, staging and production projects;
- least-privilege service accounts;
- Secret Manager for credentials;
- BigQuery row-level or column-level security where required;
- CMEK only when client policy requires customer-managed keys;
- private networking and VPC Service Controls for regulated workloads;
- audit logging;
- explicit retention policies;
- model and dataset lineage.

## 12. Scalability

The architecture scales by separating storage, transformation, training and serving.

- BigQuery handles large historical tables.
- Vertex AI training jobs scale compute independently.
- batch prediction avoids permanent endpoint cost.
- Looker reads governed warehouse data.
- downstream applications consume versioned forecast tables.

## 13. Current implementation versus target state

| Area | Current repository | Recommended production state |
|---|---|---|
| Data source | Local CSV | Cloud Storage and BigQuery |
| Pipeline | Local Python script | Vertex AI Pipeline |
| Training | Local LightGBM | Vertex AI Custom Training |
| Model storage | Local pickle artifact | Vertex AI Model Registry |
| Prediction | Local script | Scheduled batch prediction |
| Forecast output | CSV artifact | Versioned BigQuery table |
| Dashboard | Streamlit | Streamlit and/or Looker |
| Monitoring | Documented proposal | Cloud Monitoring plus quality tables |
| Retraining | Manual | Scheduled and condition-based |

## 14. Product lifecycle notes

The architecture intentionally avoids deprecated or legacy components:

- Legacy AI Platform Training and Prediction;
- Legacy AI Platform Pipelines;
- Vertex AI Workbench managed and user-managed notebook types that reached their migration deadlines;
- Vertex AI Feature Store Legacy/V1;
- deprecated Feature Store optimized online serving;
- Cloud Composer 1 for new deployments.

The exact Google Cloud product matrix should be reviewed before every client implementation because service names, launch stages and recommended patterns can change.
