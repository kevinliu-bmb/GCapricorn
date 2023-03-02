import operator
from functools import reduce
from typing import Optional

import altair as alt
import pandas as pd
import streamlit as st

tpm_column_names = {
    "cell": "RNA single cell type specific nTPM",
    "tissue": "RNA tissue specific nTPM"
}


@st.cache_data
def load_protein_tpm(protein_info: pd.Series, by: str = "cell") -> Optional[pd.DataFrame]:
    """
    Obtain TPM data from a row of the Human Protein Atlas DataFrame.
    :param protein_info: The row of the HPA DataFrame as a pandas Series object.
    :param by: What type of TPM to retrieve. One of {"cell", "tissue"}.
    :return: A DataFrame with the TPM information per cell or tissue, or None of no information is available.
    """
    if pd.isna(protein_info[tpm_column_names[by]]):
        return None
    else:
        values = protein_info[tpm_column_names[by]]
        values_dict = {x.split(":")[0].strip().title(): float(x.split(":")[1].strip()) for x in values.split(";")}
        return pd.DataFrame({by: values_dict.keys(), "TPM": values_dict.values()})


def generate_protein_details_view(uniprot_id: str, data: pd.DataFrame) -> None:
    """
    Display protein data such as chromosome, gene, disease relatedness and others.
    :param uniprot_id: UniProt ID of the protein in question.
    :param data: DataFrame from the Human Protein Atlas containing information about the protein.
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
    protein_classes = [f"<li>{protein_class.strip()}</li>" for protein_class in protein_info['Protein class'].split(",")]
    info_row_1[1].markdown(f"Protein classes <br> <div class='gc-info-box'><ul>{''.join(protein_classes)}</ul></div>",
                           unsafe_allow_html=True)

    info_row_2 = st.columns(2)
    row_index = 0
    if not pd.isna(protein_info["Gene synonym"]):
        info_row_2[row_index].markdown(
            rf"Gene synonyms <br> <div class='gc-info-box'>{protein_info['Gene synonym']}</div>",
            unsafe_allow_html=True)
        row_index += 1
    if not pd.isna(protein_info["Biological process"]):
        biological_processes = [f"<li>{process.strip()}</li>" for process in
                                protein_info["Biological process"].split(",")]
        info_row_2[row_index].markdown(
            rf"Biological process <br> <div class='gc-info-box'><ul>{''.join(biological_processes)}</ul></div>",
            unsafe_allow_html=True)


    info_row_3 = st.columns(2)
    row_index = 0
    if not pd.isna(protein_info["Molecular function"]):
        info_row_3[row_index].markdown(
            rf"Molecular function <br> <div class='gc-info-box'>{protein_info['Molecular function']}</div>",
            unsafe_allow_html=True)
        row_index += 1
    if not pd.isna(protein_info["Disease involvement"]):
        diseases = [f"<li>{process.strip()}</li>" for process in
                                protein_info["Disease involvement"].split(",")]
        info_row_3[row_index].markdown(
            rf"Disease involvement <br> <div class='gc-info-box'><ul>{''.join(diseases)}</ul></div>",
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

    try:
        chart = reduce(operator.or_, bar_charts)
        st.altair_chart(chart, use_container_width=True)
    except TypeError:
        pass
