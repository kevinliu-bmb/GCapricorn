
import streamlit as st
import pandas as pd
import altair as alt


def generate_chromosome_view() -> None:
    """
    Generates the chromosome view.
    :return: None.
    """
    st.header("Chromosome View")

    # Load the gene data
    df = st.session_state["data"]

    # Mock data for testing.
    mock_selected_cancer_type = ["Liver cancer"]
    mock_selected_protein_types = ["Enzymes", "Transporters"] 
    mock_protein_classes = ["Enzymes", "Transporters"]

    # Generate a list of chromosome IDs and names.
    chromosome_ids = df["Chromosome"].unique()
    chromosome_names = [f"Chr {i}" for i in chromosome_ids]

    # Create chromosome selection widget.
    chromosome_select = st.selectbox(label="Chromosome", options=chromosome_names, index=0)
    chromosome_select = chromosome_select.split(" ")[-1]
    
    # Create protein types selection widget.
    selected_protein_classes = st.multiselect(label="Selected Protein Classes", options=mock_protein_classes, default=mock_selected_protein_types)

    # Filter the data to only include the selected protein classes.
    mask_protein_types = df['Protein class'].str.split(', ', expand=True).isin(selected_protein_classes).any(axis=1)
    df_protein_types = df[mask_protein_types]

    # Filter the data to only include the selected chromosome.
    df_chromosome_filt = df_protein_types[df_protein_types["Chromosome"] == chromosome_select]

    chr_pos = df_chromosome_filt['Position'].str.split('-', expand=True)
    chr_pos['name'] = df_chromosome_filt['Gene']
    chr_pos.columns = ['start_position', 'end_position', 'name']

    # add a brush selection tool
    brush = alt.selection(type='interval', encodings=['x'])

    chromosome = alt.Chart(chr_pos).mark_line().encode(
        x='start_position:Q'
    ).properties(
        title=f"Displaying results for Chromosome {chromosome_select}"
    )

    genes = chromosome.mark_rect(size=10).encode(
        x='start_position:Q',
        x2='end_position:Q',
        tooltip=['name', 'start_position', 'end_position']
    )

    chart = (chromosome + genes).properties(
        width=600,
        height=130
    ).add_selection(
        brush
    )

    st.altair_chart(chart, use_container_width=True)

