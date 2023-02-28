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


@st.cache_data
def generate_amino_acid_counts_chart(seq: str) -> alt.Chart:
    """
    Given a protein sequence, build a bar chart displaying amino acid frequency data.
    :param seq: The sequence of amino acids as one-letter codes.
    :return: an Altair bar chart displaying amino acid frequencies.
    """
    amino_acid_counts = Counter(seq)
    amino_acid_counts = pd.DataFrame({"one_letter_code": amino_acid_counts.keys(), "count": amino_acid_counts.values()})
    amino_acid_table = pd.merge(amino_acid_counts, amino_acid_info, on="one_letter_code")
    amino_acid_chart = alt.Chart(amino_acid_table).mark_bar().encode(
        x=alt.X("three_letter_code", type="nominal", sort="-y", title="Amino Acid Type"),
        y=alt.Y("count", type="quantitative", title="Amino Acid Count"),
        color=alt.Color("color", type="nominal", scale=None),
        tooltip=[alt.Tooltip("three_letter_code:N", title="Amino acid"),
                 alt.Tooltip("full_name:N", title="Full name"),
                 alt.Tooltip("count:Q", title="Count")]
    ).properties(title="Sequence by amino acid type")
    return amino_acid_chart


@st.cache_data
def generate_sequence_visualization(seq: str) -> alt.Chart:
    """
    Given a protein sequence, generate a protein sequence visualization.
    :param seq: The sequence to visualize.
    :return: An Altair Chart showing an interactive view of the sequence, allowing users to zoom and pan.
    """
    sequence_table = pd.DataFrame({'amino_acid': list(seq),
                                   'position': [x for x in range(len(seq))]})
    sequence_table["amino_acid_name"] = sequence_table["amino_acid"].apply(
        lambda x: amino_acid_info[amino_acid_info["one_letter_code"] == x]["full_name"].iloc[0]
    )
    sequence_table["amino_acid_three_letter"] = sequence_table["amino_acid"].apply(
        lambda x: amino_acid_info[amino_acid_info["one_letter_code"] == x]["three_letter_code"].iloc[0]
    )
    sequence_table["color"] = sequence_table["amino_acid"].apply(
        lambda x: amino_acid_info[amino_acid_info["one_letter_code"] == x]["color"].iloc[0]
    )
    sequence_table["position"] += 1
    sequence_table["empty_string"] = ""

    interval = alt.selection(type="interval", name="interval_select", encodings=["x"], init={"x": [1, 51]}, zoom=True)

    sequence_visualization = alt.Chart(sequence_table).transform_calculate(
        show_text="isDefined(interval_select.position) \
        ? ((interval_select.position[1] - interval_select.position[0] <= 9) \
            ? datum.amino_acid_name \
            : ((interval_select.position[1] - interval_select.position[0] <= 25) ? datum.amino_acid_three_letter : \
                ((interval_select.position[1] - interval_select.position[0] <= 90) ? datum.amino_acid : datum.empty_string)\
            ) \
        ) \
        : datum.empty_string"
    ).mark_text(
        fontWeight='bold',
        color="black",
        font="monospace"
    ).encode(
        x=alt.X("position", type="quantitative", title="Residue number",
                bin=alt.Bin(step=1), scale=alt.Scale(domain=interval.ref())),
        text="show_text:N",
        tooltip=[alt.Tooltip("amino_acid_name", title="Amino acid"), alt.Tooltip("position", title="Position")],
    ).properties(
        width=800,
        height=50
    )

    sequence_colors = alt.Chart(sequence_table).mark_rect().encode(
        x=alt.X("position", type="quantitative", title="Residue number",
                bin=alt.Bin(step=1), scale=alt.Scale(domain=interval.ref())),
        color=alt.Color("color", type="nominal", scale=None),
        tooltip=[alt.Tooltip("amino_acid_name", title="Amino acid"), alt.Tooltip("position", title="Position")]
    )

    position_selector = alt.Chart(sequence_table).mark_line().encode(
        x=alt.X("position", type="quantitative", title="Drag to select", scale=alt.Scale(domain=(1, len(seq) + 1)))
    ).properties(
        width=800,
        height=50
    ).add_selection(interval)

    return ((sequence_colors + sequence_visualization) & position_selector).configure_axisX(format="d")


def generate_protein_sequence_view(uniprot_id: str) -> None:
    """
    Visualize the protein sequence of amino acids.
    :param uniprot_id: The UniProt ID of the protein to visualize.
    :return: None.
    """
    seq = load_protein_sequence(uniprot_id)

    sequence_visualization = generate_sequence_visualization(seq)
    st.altair_chart(sequence_visualization, use_container_width=True)

    amino_acid_chart = generate_amino_acid_counts_chart(seq)
    st.altair_chart(amino_acid_chart, use_container_width=True)
