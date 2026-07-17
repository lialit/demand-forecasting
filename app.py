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
    "Dashboard": [
        st.Page(
            "views/executive.py",
            title="Executive Overview",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page(
            "views/model_performance.py",
            title="Model Performance",
            icon=":material/model_training:",
        ),
        st.Page(
            "views/business_insights.py",
            title="Business Insights",
            icon=":material/insights:",
        ),
    ],
    "Project": [
        st.Page(
            "views/about.py",
            title="About the Project",
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
