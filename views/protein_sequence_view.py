from collections import Counter

import altair as alt
import pandas as pd
import requests
import streamlit as st

amino_acid_info = pd.DataFrame({
    "one_letter_code": ["A", "L", "I", "M", "V", "F", "W",
                        "Y", "N", "C", "Q", "S", "T", "D",
                        "E", "R", "H", "K", "G", "P"],
    "three_letter_code": ["Ala", "Leu", "Ile", "Met", "Val", "Phe", "Trp",
                          "Tyr", "Asn", "Cys", "Gln", "Ser", "Thr", "Asp",
                          "Glu", "Arg", "His", "Lys", "Gly", "Pro"],
    "full_name": ["Alanine", "Leucine", "Isoleucine", "Methionine", "Valine", "Phenylalanine", "Tryptophan",
                  "Tyrosine", "Asparagine", "Cysteine", "Glutamine", "Serine", "Threonine", "Aspartic acid",
                  "Glutamic acid", "Arginine", "Histidine", "Lysine", "Glycine", "Proline"],
    "color": ["#C8C8C8", "#0F820F", "#0F820F", "#E6E600", "#0F820F", "#3232AA", "#B45AB4",
              "#3232AA", "#00DCDC", "#E6E600", "#00DCDC", "#FA9600", "#FA9600", "#E60A0A",
              "#E60A0A", "#145AFF", "#8282D2", "#145AFF", "#EBEBEB", "#DC9682"]
})

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
    amino_acid_counts = pd.DataFrame({"one_letter_code": amino_acid_counts.keys(), "count": amino_acid_counts.values()})
    amino_acid_table = pd.merge(amino_acid_counts, amino_acid_info, on="one_letter_code")
    amino_acid_chart = alt.Chart(amino_acid_table).mark_bar().encode(
        x=alt.X("one_letter_code", type="nominal", sort="-y", title="Amino Acid Type"),
        y=alt.Y("count", type="quantitative", title="Amino Acid Count"),
        color=alt.Color("color", type="nominal", scale=None),
        tooltip=[alt.Tooltip("three_letter_code:N", title="Amino acid"),
                 alt.Tooltip("full_name:N", title="Full name"),
                 alt.Tooltip("count:Q", title="Count")]
    ).properties(title="Sequence by amino acid type")
    st.altair_chart(amino_acid_chart, use_container_width=True)