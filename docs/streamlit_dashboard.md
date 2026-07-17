# Streamlit Dashboard V4

V4 is an incremental update of the working V3 architecture.

## Current APIs used

- `st.Page`
- `st.navigation`
- `StreamlitPage.run()`
- `st.metric(..., chart_data=..., chart_type=...)`
- `st.container(border=True, width="stretch", height="stretch")`
- `st.plotly_chart(..., width="stretch")`
- `@st.cache_data`

## New functionality

- Native KPI cards with sparklines
- Period-over-period KPI deltas
- Deterministic business insight cards
- No external AI key or network request is required

## Install

Add or update:

```text
streamlit>=1.59,<2
plotly>=6.0,<7
```

Then run:

```bash
pip install -r requirements.txt --upgrade
python dashboard/build_dashboard_dataset.py
streamlit run app.py
```

## Replacement

Copy the package into the project root with replacement.

The V4 package contains only the application files. It does not replace
your source dataset or ML pipeline.
