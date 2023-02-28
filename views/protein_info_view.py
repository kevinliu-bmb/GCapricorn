import operator
from collections import Counter
from functools import reduce
from typing import Optional

import altair as alt
import pandas as pd
import requests
import streamlit as st


tpm_column_names = {
    "cell": "RNA single cell type specific nTPM",
    "tissue": "RNA tissue specific nTPM"
}

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
def load_protein_tpm(protein_info: pd.Series, by: str = "cell") -> Optional[pd.DataFrame]:
    if pd.isna(protein_info[tpm_column_names[by]]):
        return None
    else:
        values = protein_info[tpm_column_names[by]]
        values_dict = {x.split(":")[0].strip().title(): float(x.split(":")[1].strip()) for x in values.split(";")}
        return pd.DataFrame({by: values_dict.keys(), "TPM": values_dict.values()})


def generate_protein_info_view(uniprot_id: str, data: pd.DataFrame) -> None:
    """
    The left part of the protein details, containing protein data and a sequence visualization.
    :param uniprot_id: The UniProt ID of the protein to visualize.
    :param data: The DataFrame object containing protein information.
    :return: None.
    """

    protein_info = data[data["Uniprot"] == uniprot_id]
    assert len(protein_info) == 1
    protein_info = protein_info.iloc[0]

    gene_col, chromosome_col, ensembl_col = st.columns([2, 1, 3])
    gene_col.metric("Gene", protein_info["Gene"])
    chromosome_col.metric("Chromosome", protein_info["Chromosome"])
    ensembl_col.metric("Ensembl ID", protein_info["Ensembl"])

    info_row_1 = st.columns(2)
    info_row_1[0].markdown(rf"Gene description <br> <div class='gc-info-box'>{protein_info['Gene description']}</div>",
                     unsafe_allow_html=True)
    info_row_1[1].markdown(rf"Protein classes <br> <div class='gc-info-box'>{protein_info['Protein class']}</div>",
                     unsafe_allow_html=True)

    info_row_2 = st.columns(2)
    row_index = 0
    if not pd.isna(protein_info["Molecular function"]):
        info_row_2[row_index].markdown(rf"Molecular function <br> <div class='gc-info-box'>{protein_info['Molecular function']}</div>",
                                       unsafe_allow_html=True)
        row_index += 1
    if not pd.isna(protein_info["Disease involvement"]):
        info_row_2[row_index].markdown(rf"Protein classes <br> <div class='gc-info-box'>{protein_info['Disease involvement']}</div>",
                               unsafe_allow_html=True)

    cell_tpm = load_protein_tpm(protein_info, by="cell")
    tissue_tpm = load_protein_tpm(protein_info, by="tissue")

    bar_charts = []
    if cell_tpm is not None:
        cell_chart = alt.Chart(cell_tpm).mark_bar(color="steelblue").encode(
            x=alt.X('cell:N', sort="-y", title="Cell Type"),
            y=alt.Y('TPM:Q'),
        ).properties(title="RNA expression (TPM) by cell type", width=(350 if tissue_tpm is not None else 700))
        bar_charts.append(cell_chart)

    if tissue_tpm is not None:
        tissue_chart = alt.Chart(tissue_tpm).mark_bar(color="orange").encode(
            x=alt.X('tissue:N', sort="-y", title="Tissue Type"),
            y=alt.Y('TPM:Q'),
        ).properties(title="RNA expression (TPM) by tissue type", width=(350 if cell_tpm is not None else 700))
        bar_charts.append(tissue_chart)

    chart = reduce(operator.or_, bar_charts)
    st.altair_chart(chart, use_container_width=True)

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