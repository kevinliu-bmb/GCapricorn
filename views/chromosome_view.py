
import streamlit as st
import altair as alt


def generate_chromosome_view() -> None:
    """
    Generates the chromosome view.
    :return: None.
    """
    st.header("Chromosome View")

    # Load the gene data
    df = st.session_state["data"]

    # implememnt a dropdown menu to select the chromosome
    chromosome_select = st.selectbox(label="Chromosome", options=df["Chromosome"].unique(), index=0)

    # Filter the data to only include the selected chromosome.
    df_chromosome_filt = df[df["Chromosome"] == chromosome_select]

   # separate unique protein classes into a list when they are separated by a comma
    protein_classes = [x.split(", ") for x in df_chromosome_filt["Protein class"]]

    # flatten the list
    protein_classes = [item for sublist in protein_classes for item in sublist]

    # remove duplicates
    protein_classes = list(set(protein_classes))

    # Create protein types selection widget.
    selected_protein_classes = st.multiselect(label="Selected Protein Classes", options=protein_classes, default=protein_classes)

    # Filter the data to only include the selected protein classes.
    mask_protein_types = df_chromosome_filt["Protein class"].str.split(", ", expand=True).isin(selected_protein_classes).any(axis=1)
    df_protein_types = df_chromosome_filt[mask_protein_types]

    # if selected_protein_classes is empty, then do not filter the data and display all protein classes and throw a warning.
    if not selected_protein_classes:
        st.warning("No protein classes selected. Please select at least one protein class.")
    else:
        # create a new column in the data frame that includes the start and end position of the gene.
        df_protein_types["start_position"] = df_protein_types["Position"].str.split("-", expand=True)[0]
        df_protein_types["end_position"] = df_protein_types["Position"].str.split("-", expand=True)[1]

        # add a brush selection tool
        brush = alt.selection(type="interval", encodings=["x"])

        # create the bottom chart that will be used to visualize the selected chromosome and represent the genes as rectangles.
        chart_chromosome = alt.Chart(df_protein_types).mark_line().encode(
            x="start_position:Q",
            tooltip=["Gene", "start_position", "end_position"]
        )

        # create the bottom chart that will be used to visualize the select genes as rectangles and color them based on the protein class.
        chart_genes = alt.Chart(df_protein_types).mark_rect(size=10).encode(
            x="start_position:Q",
            x2="end_position:Q",
            tooltip=["Gene", "start_position", "end_position"],
            color="Protein class:N"
        )

        chart_bottom = (chart_chromosome + chart_genes).properties(
            width=600,
            height=50,
            title=f"Brush over to zoom into Chromosome {chromosome_select}"
        ).add_selection(brush)    
        
        chart_chromosome_top = alt.Chart(df_protein_types).mark_line().encode(
            x="start_position:Q",
            tooltip=["Gene", "start_position", "end_position"]
        ).properties(
            width=600,
            height=150
        ).transform_filter(brush)
        
        # create the top chart that will only display the selected genes as circles based on the brush selection.
        chart_selected_genes = alt.Chart(df_protein_types).mark_circle(size=50).encode(
            x="start_position:Q",
            color="Protein class:N",
            tooltip=["Gene", "start_position", "end_position", "Protein class"]
        ).properties(
            width=600,
            height=50,
            title=f"Selected Chromosomal Region"
        ).transform_filter(brush).interactive()
        
        chart_top = (chart_chromosome_top + chart_selected_genes)

        # combine the top and bottom charts to create the chromosome view.
        chart = chart_top & chart_bottom

        # remove the axis title
        chart = chart.configure_axis(
            titleFontSize=0
        )
        
        # display the chart
        st.altair_chart(chart, use_container_width=True)

