import streamlit as st

from app_utils.theme import apply_app_style


st.set_page_config(
    page_title="Retail Demand Forecasting",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_app_style()

pages = {
    "Business Dashboard": [
        st.Page(
            "views/executive.py",
            title="Business Overview",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page(
            "views/model_performance.py",
            title="Forecast Accuracy",
            icon=":material/model_training:",
        ),
        st.Page(
            "views/business_insights.py",
            title="Demand Drivers",
            icon=":material/insights:",
        ),
    ],
    "Documentation": [
        st.Page(
            "views/about.py",
            title="How It Works",
            icon=":material/info:",
        ),
    ],
}

navigation = st.navigation(
    pages,
    position="sidebar",
    expanded=True,
)

navigation.run()
