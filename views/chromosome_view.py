import random
import numpy as np
import pandas as pd
import streamlit as st
import altair as alt


def generate_simulated_data() -> pd.DataFrame:
    """
    Generate simulated data for testinging the chromosome view.
    :return: A DataFrame with simulated data.
    """
    # Create a dictionary with three keys: 'position', 'value', and 'cancer'
    sim_data = {
        'position': range(1, 1000001),
        'value': [10] * 1000000
    }

    # Create a DataFrame from the dictionary
    df_mock = pd.DataFrame(sim_data)

    # Add a column 'cancer' to the DataFrame with values of "N" initially
    df_mock['cancer'] = 'N'

    # Set maximum of 10000 'Y's
    max_Y = 100000

    # Set consecutive 'Y's in each 1000 rows
    consecutive_Y = 10000

    # Calculate the number of groups of consecutive 'Y's
    num_groups = max_Y // consecutive_Y

    # Calculate the minimum number of rows between each group of consecutive 'Y's
    min_row_diff = (len(df_mock) - consecutive_Y * num_groups) // (num_groups + 1)

    # Calculate the starting index for each group of consecutive 'Y's
    start_indices = [i * (consecutive_Y + min_row_diff) + min_row_diff for i in range(num_groups)]

    # Get random indices to set 'Y' values
    y_indices = np.random.choice(df_mock.index, size=max_Y, replace=False)

    # Split the 'y_indices' into groups of 1000
    y_indices_groups = np.array_split(y_indices, num_groups)

    # Set consecutive 'Y's in each group
    for i, group in enumerate(y_indices_groups):
        start_idx = start_indices[i]
        df_mock.loc[start_idx:start_idx + consecutive_Y - 1, 'cancer'] = 'Y'

    return df_mock


def generate_chromosome_view() -> None:
    """
    Generates the chromosome view.
    :return: None.
    """
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
        #chr_pos = df_chromosome_filt["Position"].str.split("-", expand=True)

        # get the minimal start position and maximal end position
        #min_start = chr_pos[0].astype(int).min()
        #max_end = chr_pos[1].astype(int).max()

        # Create a list of chromosome positions based on the minimal start position and maximal end position.
        #chromosome_positions = [i for i in range(min_start, max_end)]
        
        # chart_top = alt.Chart(df_chromosome_filt).mark_bar().encode(
        #     x=alt.X('Chromosome:N'),
        #     y=alt.Y('count(Gene):Q'),
        #     color=alt.Color('Chromosome:N')
        # )

        df_mock = generate_simulated_data()

        chart = alt.Chart(df_chromosome_filt).mark_bar().encode(
            x=alt.X('Chromosome:N'),
            y=alt.Y('count(Gene):Q'),
            color=alt.Color('Chromosome:N')
        ).properties(
            width=600,
            height=300
        ) & alt.Chart(df_mock).mark_bar().encode(
            x=alt.X('position:Q', title="Chromosome Position", axis=alt.Axis(labels=False)),
            y=alt.Y('value:Q', axis=None),
            color=alt.Color('cancer:N', scale=alt.Scale(domain=['N', 'Y'], range=['#d3d3d3', '#ff0000'])),
        ).properties(
            width=600,
            height=25
        )

        st.altair_chart(chart, use_container_width=True)

