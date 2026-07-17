from dataclasses import dataclass
from datetime import date

import pandas as pd
import streamlit as st


@dataclass(frozen=True)
class DashboardFilters:
    start_date: date
    end_date: date
    stores: tuple[str, ...]
    products: tuple[str, ...]
    promotion: str
    inventory: str


def render_sidebar_filters(
    df: pd.DataFrame,
) -> DashboardFilters:
    """Render shared dashboard filters in the sidebar."""
    st.sidebar.markdown("### Filters")

    minimum_date = df["date"].min().date()
    maximum_date = df["date"].max().date()

    selected_dates = st.sidebar.date_input(
        "Date range",
        value=(minimum_date, maximum_date),
        min_value=minimum_date,
        max_value=maximum_date,
    )

    if (
        isinstance(selected_dates, tuple)
        and len(selected_dates) == 2
    ):
        start_date, end_date = selected_dates
    else:
        start_date = end_date = selected_dates

    stores = sorted(
        df["store_id"].astype("string").dropna().unique().tolist()
    )
    products = sorted(
        df["product_id"].astype("string").dropna().unique().tolist()
    )

    selected_stores = st.sidebar.multiselect(
        "Store",
        options=stores,
        default=stores,
    )
    selected_products = st.sidebar.multiselect(
        "Product",
        options=products,
        default=products,
    )

    promotion = st.sidebar.selectbox(
        "Promotion",
        options=("All", "Promo only", "No promo"),
    )
    inventory = st.sidebar.selectbox(
        "Inventory status",
        options=("All", "Stock-out only", "In stock only"),
    )

    st.sidebar.divider()
    st.sidebar.caption(
        "Python ETL → dashboard dataset → Streamlit"
    )

    return DashboardFilters(
        start_date=start_date,
        end_date=end_date,
        stores=tuple(selected_stores),
        products=tuple(selected_products),
        promotion=promotion,
        inventory=inventory,
    )


def apply_filters(
    df: pd.DataFrame,
    filters: DashboardFilters,
) -> pd.DataFrame:
    """Apply the selected filters to dashboard data."""
    mask = df["date"].dt.date.between(
        filters.start_date,
        filters.end_date,
    )

    mask &= (
        df["store_id"]
        .astype("string")
        .isin(filters.stores)
    )
    mask &= (
        df["product_id"]
        .astype("string")
        .isin(filters.products)
    )

    if filters.promotion == "Promo only":
        mask &= df["is_promo"].eq(1)
    elif filters.promotion == "No promo":
        mask &= df["is_promo"].eq(0)

    if filters.inventory == "Stock-out only":
        mask &= df["is_stockout"].eq(1)
    elif filters.inventory == "In stock only":
        mask &= df["is_stockout"].eq(0)

    return df.loc[mask].copy()
