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

    brush = alt.selection(type="interval", encodings=["x"]) # BUG: when hovering over brushed region, displays "true" in the tooltip.

    top_line = alt.Chart(chromosome_proteins).mark_line(size=2).encode(
        x=alt.X("Start Position:Q", scale=alt.Scale(domain=brush.ref())),
        tooltip=["Gene", "Start Position", "End Position"],
        color=alt.value("black")
    )

    gene_boxes = alt.Chart(chromosome_proteins).mark_square(size=500).encode(
        x=alt.X("Start Position:Q", scale=alt.Scale(domain=brush.ref()), title="Chromosomal Position"),
        x2=alt.X2("End Position:Q"),
        tooltip=["Gene", "Gene synonym", "Protein class", "Ensembl", "Uniprot", "Biological process", "Start Position", "End Position"],
        color=alt.Color("Primary Protein Class:N")
    )
    
    gene_box_names = alt.Chart(chromosome_proteins).mark_text(
        align="center", 
        baseline="middle", 
        fontWeight="bold",
        font="monospace",
        dy=-20,
        dx=-30
    ).encode(
        x=alt.X("Start Position:Q", scale=alt.Scale(domain=brush.ref()), title="Chromosomal Position"),
        x2=alt.X2("End Position:Q"),
        text="Gene",
        color=alt.Color("Primary Protein Class:N"),
        angle=alt.value(45)
    )

    gene_details = gene_boxes + gene_box_names

    detailed_view = (top_line + gene_details).properties(
        width=500,
        height=150
    )

    bottom_line = alt.Chart(chromosome_proteins).mark_line(size=2).encode(
        x=alt.X("Start Position:Q"),
        tooltip=["Gene", "Start Position", "End Position"],
        color=alt.value("black")
    )

    gene_overview = alt.Chart(chromosome_proteins).mark_circle(size=50).encode(
        x=alt.X("Start Position:Q", title="Drag to select chromosomal region, scroll to zoom in/out"),
        x2=alt.X2("End Position:Q"),
        tooltip=["Gene", "Start Position", "End Position"],
        color=alt.Color("Primary Protein Class:N")
    )

    general_view = (bottom_line + gene_overview).properties(
        width=500,
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
    data = data[(data["Unfavorable prognostics"].apply(lambda x: cancer_selection in x)) |
                (data["Favorable prognostics"].apply(lambda x: cancer_selection in x))]

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

    chromosome_proteins["Start Position"] = chromosome_proteins["Position"].str.split("-", expand=True)[0] # BUG: raises key error with certain cancer type and protein class selection combinations.
    chromosome_proteins["End Position"] = chromosome_proteins["Position"].str.split("-", expand=True)[1]

    chromosome_proteins["Primary Protein Class"] = chromosome_proteins["Prioritized Protein Class"].apply(
        lambda x: x[0] if list(filter(lambda y: y in protein_selection, x)) == [] else list(filter(lambda y: y in protein_selection, x))[0]
    )

    chart = build_chromosome_chart(chromosome_proteins)
    st.altair_chart(chart, use_container_width=True)
