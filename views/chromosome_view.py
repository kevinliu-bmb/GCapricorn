import pandas as pd
import streamlit as st
import altair as alt

# TODO: Add all available protein protein_classes, sorted by priority.
# The class with the highest priority will be the one chosen for the protein as its class.
protein_class_priority = [
    "Enzymes",
    "Transporters"
]

@st.cache_data
def build_chromosome_chart(chromosome_proteins: pd.DataFrame) -> alt.Chart:
    """
    Generates the chromosome Altair chart.
    :param chromosome_proteins: DataFrame containing chromosome/protein information.
    :return: None.
    """

    brush = alt.selection(type="interval", encodings=["x"]) # BUG: when hovering over brushed region, displays "True" in the tooltip.

    top_line = alt.Chart(chromosome_proteins).mark_line().encode(
        x=alt.X("Start Position:Q", scale=alt.Scale(domain=brush.ref())),
        tooltip=["Gene", "Start Position", "End Position"]
    )

    gene_details = alt.Chart(chromosome_proteins).mark_circle(size=50).encode(
        x=alt.X("Start Position:Q", scale=alt.Scale(domain=brush.ref()), title="Chromosomal Position"),
        color=alt.Color("Primary Protein Class:N"),
        tooltip=["Gene", "Gene synonym", "Protein class", "Ensembl", "Uniprot", "Biological process", "Start Position", "End Position"]
    )

    detailed_view = (top_line + gene_details).properties(
        width=600,
        height=150
    )

    bottom_line = alt.Chart(chromosome_proteins).mark_line().encode(
        x=alt.X("Start Position:Q"),
        tooltip=["Gene", "Start Position", "End Position"]
    )

    gene_overview = alt.Chart(chromosome_proteins).mark_rect(size=10).encode(
        x=alt.X("Start Position:Q", title="Drag to select chromosomal region, scroll to zoom in/out"),
        x2=alt.X2("End Position:Q"),
        tooltip=["Gene", "Start Position", "End Position"],
        color=alt.Color("Primary Protein Class:N") # TODO: color by selected protein protein_classes; BUG: not displaying the simplified selected protein protein_classes.
    )

    general_view = (bottom_line + gene_overview).properties(
        width=600,
        height=50,
    ).add_selection(brush)

    return detailed_view & general_view


def get_primary_protein_class(protein_classes: str) -> str:
    """
    Retrieve the primary protein class from a comma-separated string of protein classes.
    :param protein_classes: Protein classes in a comma-separated format.
    :return: The primary protein class as a string.
    """
    class_list = [x.strip() for x in protein_classes.split(",")]
    prioritized_protein_classes = [x for x in protein_class_priority if x in class_list]
    if prioritized_protein_classes:
        return prioritized_protein_classes[0]
    return class_list[0]


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
        st.warning("No protein protein_classes selected. Displaying all proteins in the chromosome.")
        chromosome_proteins = chromosome_data
    else:
        chromosome_proteins = chromosome_data[chromosome_data["Protein class"].apply(
            lambda x: any(protein_class in x for protein_class in protein_selection)
        )]

    chromosome_proteins["Start Position"] = chromosome_proteins["Position"].str.split("-", expand=True)[0]
    chromosome_proteins["End Position"] = chromosome_proteins["Position"].str.split("-", expand=True)[1]

    chromosome_proteins["Primary Protein Class"] = chromosome_proteins["Protein class"].apply(get_primary_protein_class)

    chart = build_chromosome_chart(chromosome_proteins)
    st.altair_chart(chart, use_container_width=True)
