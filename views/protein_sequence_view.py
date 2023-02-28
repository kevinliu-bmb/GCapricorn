from collections import Counter

import altair as alt
import pandas as pd
import requests
import streamlit as st

@st.cache_data
def load_protein_sequence(protein_id: str) -> str:
    """
    Retrieve amino acid sequence in one-letter codes from the UniProt database.
    :param protein_id: UniProt ID.
    :return: The protein sequence as a string of amino acids.
    """
    fasta_string: str = requests.get(f"https://www.uniprot.org/uniprot/{protein_id}.fasta").text
    return "".join([x.strip() for x in fasta_string.split("\n")[1:]])


def generate_protein_sequence_view(uniprot_id: str) -> None:
    """
    Visualize the protein sequence of amino acids.
    :param uniprot_id: The UniProt ID of the protein to visualize.
    :return: None.
    """
    seq = load_protein_sequence(uniprot_id)
    st.write("Amino Acid Sequence")
    st.info(seq)

    amino_acid_counts = Counter(seq)
    amino_acid_counts = pd.DataFrame({"amino_acid": amino_acid_counts.keys(), "count": amino_acid_counts.values()})
    amino_acid_chart = alt.Chart(amino_acid_counts).mark_bar().encode(
        x=alt.X("amino_acid", type="nominal", sort="-y"),
        y=alt.Y("count", type="quantitative")
    ).properties(title="Sequence by amino acid type")
    st.altair_chart(amino_acid_chart, use_container_width=True)