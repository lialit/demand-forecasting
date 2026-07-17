# Modern Streamlit Dashboard

## Where to copy the files

Copy the contents of this package into the root of the existing
`DemandForecasting` repository.

The resulting structure should be:

```text
DemandForecasting/
├── app.py
├── pages/
│   ├── 1_Model_Performance.py
│   └── 2_Business_Insights.py
├── app_utils/
│   ├── __init__.py
│   └── common.py
├── .streamlit/
│   └── config.toml
├── dashboard/
│   ├── build_dashboard_dataset.py
│   └── demand_dashboard.csv
└── requirements.txt
```

## Add dependencies

Add these lines to `requirements.txt`:

```text
streamlit>=1.37,<2
plotly>=5.22,<7
```

## Generate the dashboard dataset

```bash
python dashboard/build_dashboard_dataset.py
```

## Run the application

From the repository root:

```bash
streamlit run app.py
```

The browser should open automatically. Otherwise, open:

```text
http://localhost:8501
```

## Navigation

Streamlit automatically displays the pages in the left sidebar:

- Executive Dashboard
- Model Performance
- Business Insights
