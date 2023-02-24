import streamlit as st


def generate_chromosome_view() -> None:
    st.header("Chromosome View")

    chromosome_ids = [i for i in range(1, 23)].append("X").append("Y")
    chromosome_names = [f"Chr {i}" for i in chromosome_ids]
    chromosome = st.selectbox(label="Chromosome", options=chromosome_names, index=0)