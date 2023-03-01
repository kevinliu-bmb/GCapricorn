import pandas as pd
import streamlit as st
import altair as alt


@st.cache_data
def build_chromosome_chart(chromosome_proteins: pd.DataFrame) -> alt.Chart:
    """
    Generates the chromosome Altair chart.
    :param chromosome_proteins: DataFrame containing chromosome/protein information.
    :return: None.
    """

    brush = alt.selection(type="interval", encodings=["x"]) # BUG: when hovering over brushed region, displays "True" in the tooltip.

    top_line = alt.Chart(chromosome_proteins).mark_line().encode(
        x=alt.X("start_position", type="quantitative", scale=alt.Scale(domain=brush.ref())),
        tooltip=["Gene", "start_position", "end_position"]
    )

    gene_details = alt.Chart(chromosome_proteins).mark_circle(size=50).encode(
        x=alt.X("start_position", type="quantitative", scale=alt.Scale(domain=brush.ref()), title="Chromosomal Position"),
        color="Protein class:N",
        tooltip=["Gene", "start_position", "end_position", "Protein class"]
    )

    detailed_view = (top_line + gene_details).properties(
        width=600,
        height=150
    )

    bottom_line = alt.Chart(chromosome_proteins).mark_line().encode(
        x="start_position:Q",
        tooltip=["Gene", "start_position", "end_position"]
    )

    gene_overview = alt.Chart(chromosome_proteins).mark_rect(size=10).encode(
        x=alt.X("start_position", type="quantitative", title="Drag to zoom"),
        x2="end_position:Q",
        tooltip=["Gene", "start_position", "end_position"],
        color=alt.Color("Protein class:N") # TODO: color by selected protein classes; BUG: not displaying the simplified selected protein classes.
    )

    general_view = (bottom_line + gene_overview).properties(
        width=600,
        height=50,
    ).add_selection(brush)

    return detailed_view & general_view


def generate_chromosome_view() -> None:
    """
    Generates the chromosome view.
    :return: None.
    """

    st.header("Chromosome View")

    data = st.session_state["data"]

    cancer_selection = st.session_state["cancer_selection"]
    # TODO: filter to only include proteins and chromosomes associated with the selected cancer type.

    protein_selection = st.session_state["protein_selection"]

    chromosome_select = st.selectbox(label="Chromosome", options=data["Chromosome"].unique(), index=0)
    chromosome_data = data[data["Chromosome"] == chromosome_select]

    if not protein_selection:
        st.warning("No protein classes selected. Displaying all proteins in the chromosome.")
        chromosome_proteins = chromosome_data
    else:
        chromosome_proteins = chromosome_data[chromosome_data["Protein class"].apply(
            lambda x: any(protein_class in x for protein_class in protein_selection)
        )]

    chromosome_proteins["start_position"] = chromosome_proteins["Position"].str.split("-", expand=True)[0]
    chromosome_proteins["end_position"] = chromosome_proteins["Position"].str.split("-", expand=True)[1]

    chromosome_proteins["Protein class"] = chromosome_proteins["Protein class"].str.split(", ")
    chromosome_proteins = chromosome_proteins["Protein class"].explode()

    chart = build_chromosome_chart(chromosome_proteins)
    st.altair_chart(chart, use_container_width=True)
