import streamlit as st


def render_page_header(
    title: str,
    subtitle: str,
) -> None:
    st.markdown(
        f'<p class="dashboard-title">{title}</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p class="dashboard-subtitle">{subtitle}</p>',
        unsafe_allow_html=True,
    )


def render_kpi_card(
    label: str,
    value: str,
    note: str,
    icon: str,
) -> None:
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



def render_insight_cards(insights) -> None:
    """Render business insights using native bordered containers."""
    columns = st.columns(2)

    for index, insight in enumerate(insights):
        with columns[index % 2]:
            with st.container(
                border=True,
                width="stretch",
                height="stretch",
                key=f"insight-{index}",
            ):
                st.markdown(f"### {insight.icon} {insight.title}")
                st.write(insight.message)
