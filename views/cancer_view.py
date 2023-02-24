import altair as alt
import streamlit as st


def generate_cancer_view() -> None:
    st.write("View1")

    df = st.session_state["data"]

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Chromosome:N'),
        y=alt.Y('count(Gene):Q'),
        color=alt.Color('Chromosome:N')
    )

    st.altair_chart(chart, use_container_width=True)
