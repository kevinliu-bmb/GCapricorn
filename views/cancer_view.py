import altair as alt
import streamlit as st


def generate_cancer_view() -> None:
    st.header("HPA Cancer Statistics")

    df = st.session_state["data"]

    mock_cancers = ["Breast Cancer", "Prostate Cancer", "Lung Cancer", "Colorectal Cancer", "Pancreatic Cancer"]
    cancer = st.selectbox(label="Cancer Type", options=mock_cancers, index=0)
    
    mock_protein_classes = ["Transcription Factors", "Receptors", "Enzymes", "Transporters", "Structural Proteins"]
    protein_class = st.multiselect(label="Protein Class", options=mock_protein_classes, default=None)

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Chromosome:N'),
        y=alt.Y('count(Gene):Q'),
        color=alt.Color('Chromosome:N')
    )

    st.altair_chart(chart, use_container_width=True)
