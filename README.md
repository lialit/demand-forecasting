## Project Status

✅ Completed

# Demand Forecasting for Retail

## Business Problem

Retail companies must accurately forecast product demand to maintain optimal inventory levels.

Overestimating demand increases storage costs and product waste.

Underestimating demand leads to stock shortages, lost sales, and dissatisfied customers.

This project develops a machine learning solution to forecast hourly product demand for each product at every dark store location. The resulting forecasts can support inventory planning, purchasing decisions, and supply chain optimization.

---

## Dataset

The dataset contains historical hourly sales records together with operational and external factors, including:

- Product ID
- Store ID
- Timestamp
- Temperature
- Promotions
- Competitor prices
- Stock availability
- Local events
- Delivery delays
- Customer app activity

Target variable:

- Sales

---

## Project Objectives

- Explore historical sales patterns
- Perform feature engineering
- Build forecasting models
- Compare model performance with baseline methods
- Generate business recommendations based on forecasting results

---

## Technologies

- Python
- Pandas
- NumPy
- Scikit-learn
- LightGBM
- Matplotlib
- Jupyter Notebook

---

## Exploratory Data Analysis

*(In progress)*

---

## Feature Engineering

*(In progress)*

---

## Model Development

*(In progress)*

---

## Results

The improved LightGBM model significantly outperformed both baseline forecasting approaches.

| Model | MAE | RMSE |
|------|----:|----:|
| Naive Forecast (previous hour) | 8.72 | 17.07 |
| Seasonal Naive Forecast (previous day) | 7.66 | 15.07 |
| **LightGBM** | **2.13** | **6.23** |

### Improvement over the best baseline

- MAE improved by **72.15%**
- RMSE improved by **58.63%**

These improvements indicate that the model captures temporal demand patterns much more effectively than simple baseline approaches.
**

## Business Recommendations

Based on the forecasting results, retailers can:

- Reduce stock shortages by improving replenishment planning.
- Decrease overstock and product waste.
- Improve purchasing decisions using more accurate demand forecasts.
- Optimize inventory levels across multiple dark stores.
- Support supply chain planning with hourly demand predictions.

## Results

The LightGBM model significantly outperformed both baseline forecasting approaches.

| Model | MAE | RMSE |
|------|----:|----:|
| Naive Forecast | 8.72 | 17.07 |
| Seasonal Naive | 7.66 | 15.07 |
| LightGBM | **2.13** | **6.23** |

Compared to the strongest baseline model:

- **72.15% lower MAE**
- **58.63% lower RMSE**

These results demonstrate that feature engineering and gradient boosting substantially improve demand forecasting accuracy.
---

## Future Work

- Hyperparameter optimization
- Additional external features
- Power BI dashboard
- Automated forecasting pipeline
