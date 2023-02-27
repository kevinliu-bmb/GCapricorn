
import streamlit as st
import altair as alt


def generate_chromosome_view() -> None:
    """
    Generates the chromosome view.
    :return: None.
    """
    st.header("Chromosome View")

    df = st.session_state["data"]

    chromosome_select = st.selectbox(label="Chromosome", options=df["Chromosome"].unique(), index=0)
    df_chromosome_filt = df[df["Chromosome"] == chromosome_select]

    protein_classes = [x.split(", ") for x in df_chromosome_filt["Protein class"]]
    protein_classes = [item for sublist in protein_classes for item in sublist]
    protein_classes = list(set(protein_classes))

    selected_protein_classes = st.multiselect(label="Selected Protein Classes", options=protein_classes, default=None)
    mask_protein_types = df_chromosome_filt["Protein class"].str.split(", ", expand=True).isin(selected_protein_classes).any(axis=1)
    df_filt = df_chromosome_filt[mask_protein_types]

    if not selected_protein_classes:
        st.warning("No protein classes selected. Please select at least one protein class.")
    else:
        df_filt["start_position"] = df_filt["Position"].str.split("-", expand=True)[0]
        df_filt["end_position"] = df_filt["Position"].str.split("-", expand=True)[1]

        brush = alt.selection(type="interval", encodings=["x"])

        chart_chromosome = alt.Chart(df_filt).mark_line().encode(
            x="start_position:Q",
            tooltip=["Gene", "start_position", "end_position"]
        )

        chart_genes = alt.Chart(df_filt).mark_rect(size=10).encode(
            x="start_position:Q",
            x2="end_position:Q",
            tooltip=["Gene", "start_position", "end_position"],
            color=alt.Color("Protein class:N", legend=None) # TODO: color by selected protein classes.
        )

        chart_bottom = (chart_chromosome + chart_genes).properties(
            width=600,
            height=50,
            title=f"Brush over to only display the selected region on Chromosome {chromosome_select}"
        ).add_selection(brush)
        
        chart_chromosome_top = alt.Chart(df_filt).mark_line().encode(
            x="start_position:Q",
            tooltip=["Gene", "start_position", "end_position"]
        ).properties(
            width=600,
            height=150
        ).transform_filter(brush)
        
        chart_selected_genes = alt.Chart(df_filt).mark_circle(size=50).encode(
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
            titleFontSize=0
        )
        
        st.altair_chart(chart, use_container_width=True)

