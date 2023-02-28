
import streamlit as st
import altair as alt


def generate_chromosome_view() -> None:
    """
    Generates the chromosome view.
    :return: None.
    """
    st.header("Chromosome View")

    data = st.session_state["data"]

    protein_selection = st.session_state["protein_selection"]

    chromosome_select = st.selectbox(label="Chromosome", options=data["Chromosome"].unique(), index=0)
    chromosome_data = data[data["Chromosome"] == chromosome_select]

    # TODO: filter to only include proteins and chromosomes associated with the selected cancer type.

    if not protein_selection:
        st.warning("No protein classes selected. Displaying all proteins in the chromosome.")
        chromosome_proteins = chromosome_data
    else:
        chromosome_proteins = chromosome_data[chromosome_data["Protein class"].apply(
            lambda x: any(protein_class in x for protein_class in protein_selection)
        )]

    chromosome_proteins["start_position"] = chromosome_proteins["Position"].str.split("-", expand=True)[0]
    chromosome_proteins["end_position"] = chromosome_proteins["Position"].str.split("-", expand=True)[1]

    brush = alt.selection(type="interval", encodings=["x"]) # BUG: when hovering over brushed region, displays "True" in the tooltip.

    chart_chromosome = alt.Chart(chromosome_proteins).mark_line().encode(
        x="start_position:Q",
        tooltip=["Gene", "start_position", "end_position"]
    )

    chart_genes = alt.Chart(chromosome_proteins).mark_rect(size=10).encode(
        x="start_position:Q",
        x2="end_position:Q",
        tooltip=["Gene", "start_position", "end_position"],
        color=alt.Color("Protein class:N") # TODO: color by selected protein classes; BUG: not displaying the simplified selected protein classes.
    )

    chart_bottom = (chart_chromosome + chart_genes).properties(
        width=600,
        height=50,
        title=f"Brush over to only display the selected region on Chromosome {chromosome_select}"
    ).add_selection(brush)

    chart_chromosome_top = alt.Chart(chromosome_proteins).mark_line().encode(
        x="start_position:Q",
        tooltip=["Gene", "start_position", "end_position"]
    ).properties(
        width=600,
        height=150
    ).transform_filter(brush)

    chart_selected_genes = alt.Chart(chromosome_proteins).mark_circle(size=50).encode(
        x="start_position:Q",
        color="Protein class:N",
        tooltip=["Gene", "start_position", "end_position", "Protein class"]
    ).properties(
        width=600,
        height=50,
        title=f"Scroll to zoom into the chromosomal region"
    ).transform_filter(brush).interactive() # TODO: fix the horizontal pan to minimum value of 0 and update based on the brush selection.

    chart_top = (chart_chromosome_top + chart_selected_genes)

    chart = (chart_top & chart_bottom).configure_axis(
        titleFontSize=0 # BUG: not hiding the axis title.
    )

    st.altair_chart(chart, use_container_width=True)

