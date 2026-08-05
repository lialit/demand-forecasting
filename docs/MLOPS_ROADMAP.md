# MLOps Roadmap

This roadmap shows how the current repository can evolve into a governed production forecasting platform on Google Cloud.

## Stage 0 — Current repository

Implemented today:

- modular Python code;
- LightGBM training;
- demand proxy logic;
- time-based holdout evaluation;
- baseline comparison;
- leakage test;
- reproducible local artifacts;
- Streamlit dashboard;
- business-oriented model interpretation.

Main gap:

The workflow is still executed manually and stores most outputs locally.

## Stage 1 — Reproducible cloud batch pipeline

Goal: run the same workflow reliably in Google Cloud.

Deliverables:

- container image in Artifact Registry;
- input data in BigQuery and Cloud Storage;
- Cloud Run Job for batch execution;
- Cloud Scheduler trigger;
- forecasts written to BigQuery;
- structured Cloud Logging;
- basic alerting.

Exit criteria:

- one command or scheduled trigger produces a complete forecast table;
- failed runs are visible;
- each output is linked to a code version and run identifier.

## Stage 2 — Managed training and model registry

Goal: separate model training from forecast generation and govern model versions.

Deliverables:

- Vertex AI Custom Training;
- Vertex AI Model Registry;
- versioned training datasets;
- stored hyperparameters and feature schema;
- release checks against baselines;
- candidate, staging and production model states.

Exit criteria:

- every production forecast references an approved model version;
- a previous version can be identified and restored;
- evaluation evidence is stored with the model.

## Stage 3 — Vertex AI Pipelines

Goal: orchestrate the ML lifecycle as a repeatable pipeline.

Suggested components:

```text
validate source data
  -> prepare curated dataset
  -> build features
  -> create demand proxy
  -> split by time
  -> train
  -> evaluate
  -> leakage test
  -> release decision
  -> register model
  -> batch forecast
  -> publish outputs
```

Exit criteria:

- pipeline steps are independently observable;
- failed steps can be retried;
- artifacts and metadata are linked through a pipeline run.

## Stage 4 — Monitoring and quality feedback

Goal: detect operational failures and model degradation.

Deliverables:

- pipeline health dashboard;
- source freshness checks;
- schema and data-quality checks;
- prediction distribution monitoring;
- MAE, RMSE and bias after actuals arrive;
- metrics by store and product segment;
- Cloud Monitoring alerts.

Exit criteria:

- the team is alerted before stale or invalid forecasts reach downstream systems;
- degradation can be isolated by segment;
- monitoring history is stored in BigQuery.

## Stage 5 — Controlled retraining

Goal: generate new model candidates automatically without automatically promoting unsafe versions.

Retraining triggers may include:

- scheduled monthly or quarterly review;
- material accuracy degradation;
- persistent forecast bias;
- new stores or products;
- assortment changes;
- seasonal transitions;
- pricing or promotion policy changes;
- significant feature drift.

Recommended process:

```text
trigger
  -> train candidate
  -> evaluate
  -> compare with production model and baselines
  -> business and technical checks
  -> approval
  -> register and promote
```

Exit criteria:

- retraining is reproducible;
- promotion requires explicit gates;
- a new candidate cannot replace production solely because a pipeline completed successfully.

## Stage 6 — Enterprise integration

Goal: embed forecasts into business processes.

Deliverables:

- BigQuery forecast contract;
- ERP and WMS integration;
- Looker semantic model;
- role-based access;
- service-level objectives;
- incident and rollback procedures;
- cost controls and budgets.

Exit criteria:

- business systems consume versioned forecasts;
- ownership and support responsibilities are documented;
- forecast availability and freshness are measurable.

## Service selection principles

### Prefer lightweight serverless components first

Use Cloud Scheduler, Workflows and Cloud Run Jobs for simple scheduled workflows.

### Use Vertex AI Pipelines for the ML lifecycle

This is the recommended managed orchestration path for training, evaluation, registration and forecasting components.

### Use Cloud Composer 3 only when Airflow is justified

Do not add Airflow complexity for a small linear pipeline. Avoid Cloud Composer 1 for new work because of its planned end of life.

### Avoid legacy services

Do not build new components on:

- Legacy AI Platform Training or Prediction;
- Legacy AI Platform Pipelines;
- deprecated Workbench notebook types;
- Vertex AI Feature Store Legacy/V1;
- deprecated optimized online serving.

## Suggested delivery sprints

### Sprint 1 — Cloud foundation

- project structure;
- IAM;
- Artifact Registry;
- BigQuery datasets;
- Cloud Storage buckets.

### Sprint 2 — Batch deployment

- containerize pipeline;
- Cloud Run Job;
- BigQuery forecast output;
- scheduler and logging.

### Sprint 3 — Managed ML

- Vertex AI training;
- Model Registry;
- evaluation gates.

### Sprint 4 — Pipeline orchestration

- Vertex AI Pipelines;
- lineage and metadata;
- environment promotion.

### Sprint 5 — Monitoring

- data quality;
- accuracy tracking;
- alerting;
- retraining candidate triggers.

### Sprint 6 — Enterprise integration

- Looker;
- ERP/WMS interfaces;
- security hardening;
- operational documentation.

## Definition of production readiness

The solution should not be called production-ready until it has:

- automated and repeatable deployment;
- versioned models and data contracts;
- monitoring and alerting;
- rollback procedures;
- access controls;
- tested failure handling;
- documented ownership;
- validated integration with client systems.
