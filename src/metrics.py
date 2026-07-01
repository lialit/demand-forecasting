import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def evaluate_predictions(y_true, y_pred) -> dict:
    """Calculate MAE and RMSE."""
    mae = mean_absolute_error(y_true, y_pred)
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))

    return {
        "MAE": round(mae, 2),
        "RMSE": round(rmse, 2),
    }


def calculate_improvement(baseline_score: float, model_score: float) -> float:
    """Calculate percentage improvement over baseline."""
    return round((baseline_score - model_score) / baseline_score * 100, 2)