import streamlit as st
import altair as alt


def generate_chromosome_view() -> None:
    st.header("Chromosome View")

    # Generate a list of chromosome IDs and names.
    chromosome_ids = [i for i in range(1, 23)]
    chromosome_ids.append("X")
    chromosome_ids.append("Y")
    chromosome_names = [f"Chr {i}" for i in chromosome_ids]

    # Create chromosome selection widget.
    chromosome_select = st.selectbox(label="Chromosome", options=chromosome_names, index=0)

    df = st.session_state["data"]

    # Filter the data to only include the selected chromosome.
    chromosome_df = df[df["Chromosome"] == chromosome_select[-1:]]

    # Place holder for the chromosome visualization.
    chart = alt.Chart(chromosome_df).mark_bar().encode(
        x=alt.X('Chromosome:N'),
        y=alt.Y('count(Gene):Q'),
        color=alt.Color('Chromosome:N')
    )

    st.altair_chart(chart, use_container_width=True)

