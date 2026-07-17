# Streamlit Dashboard V3

This version uses the preferred modern multipage architecture:

- `st.Page`
- `st.navigation`
- `navigation.run()`
- `width="stretch"`
- `@st.cache_data`

## Copy the files

Copy the package contents to the root of `DemandForecasting`.

Expected structure:

```text
DemandForecasting/
├── app.py
├── views/
│   ├── executive.py
│   ├── model_performance.py
│   ├── business_insights.py
│   └── about.py
├── app_utils/
│   ├── charts.py
│   ├── components.py
│   ├── config.py
│   ├── filters.py
│   ├── loader.py
│   ├── metrics.py
│   └── theme.py
├── dashboard/
│   └── demand_dashboard.csv
└── requirements.txt
```

The old `pages/` directory is no longer required for this version and should
be removed to avoid confusion.

## Requirements

Add:

```text
streamlit>=1.54,<2
plotly>=6.0,<7
```

Then run:

```bash
pip install -r requirements.txt --upgrade
python dashboard/build_dashboard_dataset.py
streamlit run app.py
```
