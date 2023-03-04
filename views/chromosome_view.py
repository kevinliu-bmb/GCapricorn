import pandas as pd
import streamlit as st
import altair as alt


@st.cache_data
def build_chromosome_chart(chromosome_proteins: pd.DataFrame) -> alt.Chart:
    """
    Generates the chromosome Altair chart.
    :param chromosome_proteins: DataFrame containing chromosome/protein information.
    :return: A Chart object ready to be displayed.
    """
    color_scale = st.session_state["color_scale"]
    filtered_color_scale = {k: v for k, v in color_scale.items() if k in chromosome_proteins["Primary Protein Class"].unique()}

    brush = alt.selection(type="interval", encodings=["x"])

    top_line = alt.Chart(chromosome_proteins).mark_line(size=2).encode(
        x=alt.X("Start Position:Q", scale=alt.Scale(domain=brush.ref())),
        tooltip=["Gene", "Start Position", "End Position"],
        color=alt.value("black")
    )

    gene_boxes = alt.Chart(chromosome_proteins).mark_square(size=500).encode(
        x=alt.X("Start Position:Q", scale=alt.Scale(domain=brush.ref()), title="Chromosomal Position"),
        x2=alt.X2("End Position:Q"),
        tooltip=["Gene", "Gene synonym", "Protein class", "Start Position", "End Position"],
        color=alt.Color("Primary Protein Class:N", scale=alt.Scale(domain=list(filtered_color_scale.keys()), range=list(filtered_color_scale.values())))
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
        color=alt.Color("Primary Protein Class:N", scale=alt.Scale(domain=list(filtered_color_scale.keys()), range=list(filtered_color_scale.values()))),
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
        color=alt.Color("Primary Protein Class:N", scale=alt.Scale(domain=list(filtered_color_scale.keys()), range=list(filtered_color_scale.values())))
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
    protein_selection = st.session_state["protein_selection"]
    cancer_selection = st.session_state["cancer_selection"]
    prognosis_selection = st.session_state["prognosis_selection"]

    data = data[(data[f"{prognosis_selection} prognostics"].apply(lambda x: cancer_selection in x))]

    chromosome_select = st.selectbox(label="Select available chromosomes",
                                     options=[str(x) for x in range(1, 23)] + ["X", "Y"], index=0)
    chromosome_data = data[data["Chromosome"] == chromosome_select]

    if not protein_selection:
        st.warning("No protein classes selected. Displaying all proteins in the chromosome.")
        chromosome_proteins = chromosome_data
    else:
        chromosome_proteins = chromosome_data[chromosome_data["Protein class"].apply(
            lambda x: any(protein_class in x for protein_class in protein_selection)
        )]

    chromosome_proteins["Start Position"] = chromosome_proteins["Position"].apply(lambda x: x.split('-')[0].strip())
    chromosome_proteins["End Position"] = chromosome_proteins["Position"].apply(lambda x: x.split('-')[1].strip())

    chromosome_proteins["Primary Protein Class"] = chromosome_proteins["Prioritized Protein Class"].apply(
        lambda x: x[0] if list(filter(lambda y: y in protein_selection, x)) == [] else list(filter(lambda y: y in protein_selection, x))[0]
    )

    chart = build_chromosome_chart(chromosome_proteins)
    st.altair_chart(chart, use_container_width=True)
