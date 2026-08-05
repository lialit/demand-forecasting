# Release Candidate Checklist

This checklist is used before presenting or releasing the demand forecasting project.

## Repository integrity

- [x] `README.md` describes the current implementation rather than planned functionality.
- [x] `LICENSE` contains the complete MIT License text.
- [x] Generated model artifacts are excluded from Git and recreated by the documented pipeline.
- [x] Obsolete experiment stubs with invalid imports have been removed.
- [x] The current architecture and Google Cloud target architecture are documented separately.

## Reproducibility

1. Place the source file at:

   ```text
   data/demand_train_val_1.5years.csv
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Generate model artifacts:

   ```bash
   python scripts/run_model_pipeline.py
   ```

4. Generate the historical dashboard dataset when required:

   ```bash
   python dashboard/build_dashboard_dataset.py
   ```

5. Start the application:

   ```bash
   streamlit run app.py
   ```

## Expected generated outputs

The model pipeline creates local, untracked files:

```text
artifacts/model_metrics.json
artifacts/model_predictions.csv
```

The files are deliberately excluded from Git because they are generated outputs and may change after retraining.

## Functional smoke test

- [ ] Business Overview opens without an exception.
- [ ] Forecast Accuracy loads current artifacts.
- [ ] Actual vs Predicted chart renders.
- [ ] Store and product selectors work.
- [ ] Hourly and daily aggregation work.
- [ ] Demand Drivers filters and charts work.
- [ ] How It Works page opens.
- [ ] Missing artifacts produce a helpful message rather than an application crash.

## Model and data checks

- [ ] Required source columns are present.
- [ ] Timestamp parsing succeeds.
- [ ] Train data ends before the holdout period.
- [ ] MAE and RMSE are written to `model_metrics.json`.
- [ ] Baseline results are present.
- [ ] Future Permutation Test result is present.
- [ ] Prediction rows contain `actual_demand` and `predicted_demand`.

## Documentation checks

- [x] Current code map: `CURRENT_SOLUTION_GUIDE.md`.
- [x] Target production design: `PRODUCTION_ARCHITECTURE.md`.
- [x] Google Cloud deployment: `GOOGLE_CLOUD_DEPLOYMENT.md`.
- [x] MLOps evolution: `MLOPS_ROADMAP.md`.
- [x] Monitoring and retraining: `RETRAINING_AND_MONITORING.md`.

## Known limitations to disclose

- Synthetic source data.
- One three-month holdout rather than multi-fold walk-forward validation.
- Heuristic demand proxy during stock-outs.
- Manually selected LightGBM parameters.
- Limited cold-start handling.
- No deployed production pipeline or client-system integration yet.

## Release decision

The repository is suitable for client review and portfolio demonstration after the unchecked local smoke-test items above have been completed on the release commit.
