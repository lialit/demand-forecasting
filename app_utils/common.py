from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "dashboard" / "demand_dashboard.csv"


@st.cache_data(show_spinner=False)
def load_dashboard_data() -> pd.DataFrame:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Dashboard dataset not found: {DATA_PATH}. "
            "Run `python dashboard/build_dashboard_dataset.py` first."
        )

    df = pd.read_csv(DATA_PATH)

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    date_text = df["date"].astype(str).str.replace(r"\.0$", "", regex=True)
    compact = pd.to_datetime(date_text, format="%Y%m%d", errors="coerce")
    general = pd.to_datetime(date_text, errors="coerce")
    df["date"] = compact.fillna(general)

    numeric_columns = [
        "sales",
        "demand_proxy",
        "stock_on_hand",
        "is_stockout",
        "temperature",
        "price",
        "competitor_price",
        "is_promo",
        "hour",
        "day_of_week",
        "month",
        "week",
        "price_diff",
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

    return df.dropna(subset=["date", "sales"]).copy()


def apply_app_style() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background: #F5F7FA;
        }

        .block-container {
            max-width: 1500px;
            padding-top: 1.4rem;
            padding-bottom: 2.5rem;
        }

        [data-testid="stSidebar"] {
            background: #FFFFFF;
            border-right: 1px solid #E6EBF2;
        }

        [data-testid="stSidebarNav"] {
            padding-top: 0.6rem;
        }

        h1, h2, h3 {
            color: #102348;
        }

        .dashboard-title {
            color: #102348;
            font-size: 2.25rem;
            line-height: 1.15;
            font-weight: 780;
            margin: 0;
        }

        .dashboard-subtitle {
            color: #64748B;
            font-size: 1.02rem;
            margin: 0.3rem 0 1.3rem;
        }

        .kpi-card {
            background: #FFFFFF;
            border: 1px solid #E4EAF2;
            border-radius: 18px;
            padding: 1.05rem 1.15rem;
            min-height: 132px;
            box-shadow: 0 6px 18px rgba(15, 35, 68, 0.05);
        }

        .kpi-icon {
            font-size: 1.2rem;
            margin-right: 0.35rem;
        }

        .kpi-label {
            color: #475569;
            font-size: 0.9rem;
            font-weight: 650;
        }

        .kpi-value {
            color: #102348;
            font-size: 2rem;
            font-weight: 780;
            margin-top: 0.55rem;
            line-height: 1.1;
        }

        .kpi-note {
            color: #64748B;
            font-size: 0.76rem;
            margin-top: 0.55rem;
        }

        .info-card {
            background: #FFFFFF;
            border: 1px solid #E4EAF2;
            border-radius: 16px;
            padding: 0.95rem 1.1rem;
            box-shadow: 0 5px 15px rgba(15, 35, 68, 0.04);
        }

        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E4EAF2;
            padding: 1rem;
            border-radius: 16px;
            box-shadow: 0 5px 15px rgba(15, 35, 68, 0.04);
        }

        div[data-testid="stPlotlyChart"] {
            background: #FFFFFF;
            border: 1px solid #E4EAF2;
            border-radius: 16px;
            padding: 0.25rem;
            box-shadow: 0 5px 15px rgba(15, 35, 68, 0.04);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def compact_number(value: float) -> str:
    if abs(value) >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if abs(value) >= 1_000:
        return f"{value / 1_000:.1f}K"
    return f"{value:,.0f}"


def render_kpi(label: str, value: str, note: str, icon: str) -> None:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">
                <span class="kpi-icon">{icon}</span>{label}
            </div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def chart_layout(fig: go.Figure, height: int = 370) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=18, r=18, t=58, b=18),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        font=dict(family="Arial", color="#334155"),
        title_font=dict(size=17, color="#102348"),
        legend_title_text="",
        hoverlabel=dict(bgcolor="#FFFFFF"),
    )
    fig.update_xaxes(gridcolor="#E8EDF4", zeroline=False)
    fig.update_yaxes(gridcolor="#E8EDF4", zeroline=False)
    return fig


def filter_data(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("## Filters")

    min_date = df["date"].min().date()
    max_date = df["date"].max().date()

    selected_dates = st.sidebar.date_input(
        "Date range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )

    stores = sorted(df["store_id"].astype(str).unique().tolist())
    products = sorted(df["product_id"].astype(str).unique().tolist())

    selected_stores = st.sidebar.multiselect(
        "Store",
        stores,
        default=stores,
    )

    selected_products = st.sidebar.multiselect(
        "Product",
        products,
        default=products,
    )

    promotion = st.sidebar.selectbox(
        "Promotion",
        ["All", "Promo only", "No promo"],
    )

    inventory = st.sidebar.selectbox(
        "Inventory status",
        ["All", "Stock-out only", "In stock only"],
    )

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date = end_date = selected_dates

    result = df[
        df["date"].dt.date.between(start_date, end_date)
    ].copy()

    result = result[
        result["store_id"].astype(str).isin(selected_stores)
    ]
    result = result[
        result["product_id"].astype(str).isin(selected_products)
    ]

    if promotion == "Promo only":
        result = result[result["is_promo"] == 1]
    elif promotion == "No promo":
        result = result[result["is_promo"] == 0]

    if inventory == "Stock-out only":
        result = result[result["is_stockout"] == 1]
    elif inventory == "In stock only":
        result = result[result["is_stockout"] == 0]

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "Python ETL → dashboard dataset → Streamlit"
    )

    return result
