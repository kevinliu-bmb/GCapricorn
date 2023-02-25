import streamlit as st
import altair as alt


def generate_chromosome_view() -> None:
    st.header("Chromosome View")

    df = st.session_state["data"]

    # Mock data for testing.
    mock_selected_cancer_type = ["Liver cancer"]
    mock_selected_protein_types = ["Enzymes", "Transporters"] 
    mock_protein_classes = ["Transcription Factors", "Receptors", "Enzymes", "Transporters", "Structural Proteins"]

    # Generate a list of chromosome IDs and names.
    chromosome_ids = df["Chromosome"].unique()
    chromosome_names = [f"Chr {i}" for i in chromosome_ids]

    # Create chromosome selection widget.
    chromosome_select = st.selectbox(label="Chromosome", options=chromosome_names, index=0)
    chromosome_select = chromosome_select.split(" ")[-1]
    
    # Create protein types selection widget.
    selected_protein_classes = st.multiselect(label="Selected Protein Classes", options=mock_protein_classes, default=mock_selected_protein_types)

    # Filter the data to only include the selected protein classes.
    ## Split the protein_types column by commas and create a boolean mask using isin()
    mask_protein_types = df['Protein class'].str.split(', ', expand=True).isin(selected_protein_classes).any(axis=1)

    # Filter the DataFrame using the boolean mask
    df_protein_types = df[mask_protein_types]

    # Filter the data to only include the selected chromosome.
    df_chromosome_filt = df_protein_types[df_protein_types["Chromosome"] == chromosome_select]

    # Place holder for the chromosome visualization.
    if df_chromosome_filt.empty:
        st.write("No data to display.")
    else:
        # Convert the Position column to a list of start and end positions.
        chr_pos = df_chromosome_filt["Position"].str.split("-", expand=True)

        # get the minimal start position and maximal end position
        min_start = chr_pos[0].astype(int).min()
        max_end = chr_pos[1].astype(int).max()

        chart = alt.Chart(df_chromosome_filt).mark_bar().encode(
            x=alt.X('Chromosome:N'),
            y=alt.Y('count(Gene):Q'),
            color=alt.Color('Chromosome:N')
        ) & alt.Chart(df_chromosome_filt).mark_bar().encode(
            x=alt.X('Chromosome:N'),
            y=alt.Y('count(Gene):Q'),
            color=alt.Color('Chromosome:N')
        )       

        st.altair_chart(chart, use_container_width=True)

