import streamlit as st


def apply_app_style() -> None:
    """Apply the shared application style."""
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
