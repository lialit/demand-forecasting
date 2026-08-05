# Шпаргалка по репозиторію Demand Forecasting

Цей файл — коротка пам'ятка у форматі **«де це?» → «ось тут»**.

## Найкоротший маршрут по рішенню

```text
CSV
→ src/data_loading.py
→ src/preprocessing.py
→ src/features.py
→ src/decensoring.py
→ src/validation.py
→ src/training.py
→ artifacts/
→ views/model_performance.py
```

## Де що знаходиться

| Питання | Де дивитися | Що там відбувається |
|---|---|---|
| Де завантажуються дані? | `src/data_loading.py` → `load_data()` | CSV читається в pandas, `timestamp` перетворюється на дату й час. |
| Де перевіряється структура даних? | `src/data_loading.py` → `validate_schema()` | Перевіряються обов'язкові колонки та коректність `timestamp`. |
| Де обробляються пропуски? | `src/preprocessing.py` → `clean_data()` | Для різних ознак використовуються окремі правила заповнення. |
| Де дані сортуються за часом? | `src/preprocessing.py` → `sort_time_series()` | Сортування за магазином, товаром і часом. |
| Де визначається stock-out? | `src/preprocessing.py` → `add_stockout_flag()` | `is_stockout = 1`, якщо `stock_on_hand <= 0`. |
| Де створюються часові ознаки? | `src/features.py` → `create_time_features()` | Година, день тижня, місяць, вихідний. |
| Де створюються цінові ознаки? | `src/features.py` → `create_price_features()` | `price_diff` і `price_ratio`. |
| Де створюються лаги? | `src/features.py` → `create_lag_features()` | Лаги 1, 24 і 168 годин, rolling mean/std за 24 години. |
| Де збираються всі ознаки разом? | `src/features.py` → `build_features()` | Послідовно викликаються всі функції feature engineering. |
| Де створюється demand proxy? | `src/decensoring.py` → `create_demand_proxy()` | Під час stock-out попит коригується за недавнім середнім. |
| Де робиться train/test split? | `src/validation.py` → `get_three_month_backtest_split()` | Останні 3 місяці стають test-періодом. |
| Де створюються baseline-прогнози? | `src/validation.py` → `create_naive_baselines()` | Прогноз за попередньою годиною та попереднім днем. |
| Де оцінюються baselines? | `src/validation.py` → `evaluate_baselines()` | Рахуються MAE та RMSE для простих прогнозів. |
| Де leakage test? | `src/validation.py` → `future_permutation_test()` | Перевіряється, що майбутні значення не змінюють історичні лаги. |
| Де задається список ознак моделі? | `src/training.py` → `FEATURE_COLUMNS` | Повний список колонок, які передаються моделі. |
| Де створюється LightGBM? | `src/training.py` → `train_lightgbm_model()` | Створюється `LGBMRegressor` і задаються параметри. |
| Де навчається модель? | `src/training.py` → `model.fit(X_train, y_train)` | Саме тут відбувається навчання. |
| Де робиться прогноз? | `src/training.py` → `model.predict(X_test)` | Формується прогноз для test-періоду. |
| Де рахується MAE та RMSE? | `src/metrics.py` → `evaluate_predictions()` | Розрахунок основних метрик. |
| Де рахується покращення проти baseline? | `src/metrics.py` → `calculate_improvement()` | Відсоток покращення моделі. |
| Де reusable inference? | `src/inference.py` → `predict_demand()` | Прогноз із уже навченої моделі. |
| Де запускається весь pipeline? | `scripts/run_model_pipeline.py` | Завантаження → features → proxy → split → training → metrics → artifacts. |
| Де зберігаються метрики? | `artifacts/model_metrics.json` | Назва моделі, метрики, baseline comparison, leakage test. |
| Де зберігаються прогнози? | `artifacts/model_predictions.csv` | `actual_demand`, `predicted_demand`, помилка, store/product/time. |
| Де dashboard читає artifacts? | `app_utils/model_artifacts.py` | Завантаження та перевірка JSON/CSV. |
| Де графік Actual vs Predicted? | `app_utils/forecast_charts.py` | Побудова графіка реальних і прогнозних значень. |
| Де сторінка Forecast Accuracy? | `views/model_performance.py` | Метрики, фільтри, графік, bias, business impact. |
| Де Business Overview? | `views/executive.py` | Загальний попит, середній попит, stock-out risk. |
| Де Demand Drivers? | `views/business_insights.py` | Вплив дня тижня, температури, ціни, промо та stock-out. |
| Де пояснення рішення простими словами? | `views/about.py` | Сторінка How It Works. |
| Де фактична архітектура коду? | `docs/CURRENT_SOLUTION_GUIDE.md` | Детальний опис поточної реалізації. |
| Де Google Cloud production architecture? | `docs/PRODUCTION_ARCHITECTURE.md` | BigQuery, Vertex AI, Batch Prediction, Looker, Monitoring. |
| Де план розгортання в Google Cloud? | `docs/GOOGLE_CLOUD_DEPLOYMENT.md` | Практична послідовність deployment. |
| Де MLOps roadmap? | `docs/MLOPS_ROADMAP.md` | Шлях від локального pipeline до production. |
| Де drift і retraining? | `docs/RETRAINING_AND_MONITORING.md` | Що моніторити та коли перенавчати модель. |

## Якщо запитають: «Де змінити модель?»

Зараз модель створюється тут:

```text
src/training.py
→ train_lightgbm_model()
```

Саме там знаходиться:

```python
lgb.LGBMRegressor(...)
```

Щоб замінити LightGBM на іншу модель, потрібно:

1. замінити створення моделі у `train_lightgbm_model()`;
2. зберегти стандартні методи `.fit()` і `.predict()`;
3. перевірити, що нова модель приймає ті самі `FEATURE_COLUMNS`;
4. знову запустити `python scripts/run_model_pipeline.py`;
5. перевірити нові metrics та Actual vs Predicted у dashboard.

## Якщо запитають: «Яка цільова змінна?»

```text
demand_proxy
```

Вона створюється у:

```text
src/decensoring.py
→ create_demand_proxy()
```

Коротка відповідь:

> Ми прогнозуємо не тільки зафіксовані продажі, а консервативну оцінку попиту, скориговану для stock-out періодів.

## Якщо запитають: «Які параметри LightGBM?»

Дивитися тут:

```text
src/training.py
→ train_lightgbm_model()
```

Основні параметри:

```text
objective = regression
n_estimators = 500
learning_rate = 0.05
num_leaves = 31
random_state = 42
n_jobs = -1
```

Коротка відповідь:

> Це стабільна вручну задана конфігурація. Повний hyperparameter tuning у поточний scope не входив.

## Якщо запитають: «Де Actual vs Predicted?»

Дані:

```text
artifacts/model_predictions.csv
```

Побудова графіка:

```text
app_utils/forecast_charts.py
```

Відображення на сторінці:

```text
views/model_performance.py
```

## Якщо запитають: «Що означає MAE 2.13?»

> У середньому прогноз відрізняється від demand proxy приблизно на 2.13 одиниці товару для однієї комбінації магазин–товар–година.

## Якщо запитають: «Що означає RMSE 6.23?»

> Модель іноді робить значно більші помилки, наприклад під час піків попиту або нестандартних ситуацій. RMSE сильніше реагує саме на такі промахи.

## Якщо запитають: «Де бізнесове пояснення?»

У dashboard:

```text
views/model_performance.py
→ Business summary
→ Estimated business impact
→ What these results do and do not prove
```

У README:

```text
Business interpretation
Estimated business impact
```

## Якщо запитають: «Коли робити retraining?»

Повний опис:

```text
docs/RETRAINING_AND_MONITORING.md
```

Коротка відповідь:

> Коли погіршуються MAE/RMSE, з'являється стабільний bias, змінюється розподіл попиту, цін чи промо, додаються нові магазини або товари, або настає планова дата retraining.

## Якщо запитають: «Як інтегрувати в Google Cloud?»

Дивитися:

```text
docs/PRODUCTION_ARCHITECTURE.md
docs/GOOGLE_CLOUD_DEPLOYMENT.md
```

Коротка схема:

```text
Cloud Storage / source systems
→ BigQuery
→ Vertex AI Pipelines
→ Vertex AI Custom Training
→ Model Registry
→ Batch Prediction або Cloud Run Job
→ BigQuery forecast tables
→ Looker / ERP / WMS
```

## Команди, які найчастіше потрібні

```powershell
python scripts\run_model_pipeline.py
python dashboard\build_dashboard_dataset.py
streamlit run app.py
```

## Важливі чесні обмеження

- Дані синтетичні.
- Validation — один three-month holdout, не multi-fold walk-forward.
- Demand proxy — евристика, а не справжній прихований попит.
- Параметри LightGBM вибрані вручну.
- Фінансовий ефект без margin, waste cost і stock-out cost не можна точно порахувати.
- Production Google Cloud architecture поки є рекомендованим target state, а не вже розгорнутою системою.
