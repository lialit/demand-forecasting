from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DATA_PATH = (
    PROJECT_ROOT / "dashboard" / "demand_dashboard.csv"
)

MODEL_RESULTS = {
    "Naive Forecast (previous hour)": {
        "MAE": 8.72,
        "RMSE": 17.07,
    },
    "Seasonal Naive Forecast (previous day)": {
        "MAE": 7.66,
        "RMSE": 15.07,
    },
    "LightGBM improved model": {
        "MAE": 2.13,
        "RMSE": 6.23,
    },
}

MAE_IMPROVEMENT = 72.15
RMSE_IMPROVEMENT = 58.63
