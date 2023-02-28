import gzip
import json
import os
import re
from typing import Optional, Union

import altair as alt
import pandas as pd
import py3Dmol
import requests
import streamlit as st
import streamlit.components.v1 as components

tpm_column_names = {
    "cell": "RNA single cell type specific nTPM",
    "tissue": "RNA tissue specific nTPM"
}

@st.cache_data
def load_protein_tpm(protein_info: pd.Series, by: str = "cell") -> Optional[pd.DataFrame]:
    if pd.isna(protein_info[tpm_column_names[by]]):
        return None
    else:
        values = protein_info[tpm_column_names[by]]
        values_dict = {x.split(":")[0].strip().title(): float(x.split(":")[1].strip()) for x in values.split(";")}
        return pd.DataFrame({by: values_dict.keys(), "TPM": values_dict.values()})


@st.cache_data
def load_protein_sequence(protein_id: str) -> str:
    """
    Retrieve amino acid sequence in one-letter codes from the UniProt database.
    :param protein_id: UniProt ID.
    :return: The protein sequence as a string of amino acids.
    """
    fasta_string: str = requests.get(f"https://www.uniprot.org/uniprot/{protein_id}.fasta").text
    return "".join([x.strip() for x in fasta_string.split("\n")[1:]])


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

    if cell_tpm is not None:
        cell_chart = alt.Chart(cell_tpm).mark_bar(color="steelblue").encode(
            x=alt.X('cell:N', sort="-y", title="Cell Type"),
            y=alt.Y('TPM:Q'),
        ).properties(title="RNA expression (TPM) by cell type")
        st.altair_chart(cell_chart, use_container_width=True)

    if tissue_tpm is not None:
        tissue_chart = alt.Chart(tissue_tpm).mark_bar(color="orange").encode(
            x=alt.X('tissue:N', sort="-y", title="Tissue Type"),
            y=alt.Y('TPM:Q'),
        ).properties(title="RNA expression (TPM) by tissue type")
        st.altair_chart(tissue_chart, use_container_width=True)

    seq = load_protein_sequence(uniprot_id)
    seq = re.sub(r"(\w{10})", r"\1 ", seq)
    st.write("Amino Acid Sequence")
    st.info(seq)


@st.cache_data
def load_protein_structures(sequence: str) -> Optional[dict[str, dict[str, Union[str, int]]]]:
    """
    Retrieve protein structures from a protein sequence. Uses the PDB API in order to obtain PDB entries that match
    the provided sequence.
    :param sequence: The protein sequence as a string of 1-letter amino acids.
    :return: A dictionary containing the PDB ID as a key another dictionary with PDB structure and score as values.
    The score is a numeric value from 0 to 1 representing the sequence match.
    """
    query = {
        "query": {
            "type": "terminal",
            "service": "sequence",
            "parameters": {
                "sequence_type": "protein",
                "value": sequence
            }
        },
        "request_options": {
            "scoring_strategy": "sequence"
        },
        "return_type": "entry"
    }

    structures = {}

    try:
        pdb_response = json.loads(requests.get(
            f"https://search.rcsb.org/rcsbsearch/v2/query?json={json.dumps(query, separators=(',', ':'))}").text
        )
    except json.JSONDecodeError:
        return structures

    for pdb_result in pdb_response["result_set"]:
        pdb_id = pdb_result["identifier"]
        score = pdb_result["score"]
        structure = requests.get(f"https://files.rcsb.org/download/{pdb_id}.pdb.gz").content
        try:
            structures[pdb_id] = {"score": score, "structure": gzip.decompress(structure).decode()}
        except gzip.BadGzipFile:
            continue
    return structures


def render_py3DMol(molecule: str, string_format: str = "pdb") -> py3Dmol.view:
    """
    Render the molecule using the Py3DMol API.
    :param molecule: path to the molecule file, or string literal containing molecule information.
    :param string_format: format of the protein. Default format is "pdb". One of "pdb", "sdf", "mol2", "xyz", and "cube".
    :return: The view object.
    """
    visualization_type = st.selectbox("Structure View", options=["cartoon", "stick", "sphere"],
                                      format_func=lambda x: f"{x.title()} model")

    viewer_dimensions = {"height": 500}

    viewer = py3Dmol.view(**viewer_dimensions)

    if os.path.exists(molecule):
        with open(molecule, "r") as file:
            viewer.addModel(file.read(), string_format)
    else:
        viewer.addModel(molecule, string_format)

    if visualization_type == "cartoon":
        colorscheme = st.radio("Color", options=[0, 1, 2], horizontal=True,
                               format_func=lambda x: ["Amino acids", "Secondary structure", "Monomers"][x])
        viewer.setStyle({"cartoon": {"colorscheme": ["amino", "ssPyMol", "chainHetatm"][colorscheme]}})
    else:
        viewer.setStyle({visualization_type: {}})

    viewer.setHoverable({}, True,
        f"""
        // On hover function
        function(atom, viewer, event, container) {{
            if (!atom.label) {{
                atom.label = viewer.addLabel(
                    atom.resn.charAt(0) + atom.resn.slice(1).toLowerCase() + 
                    atom.resi {'+ ":" + atom.atom' if visualization_type != 'cartoon' else ''},
                {{position: atom, backgroundColor: 'black', fontColor:'white'}});
            }}}}
        """,
        """
        // On remove hover function
        function(atom, viewer) { 
            if(atom.label) {
                viewer.removeLabel(atom.label);
                delete atom.label;
            }
        }
        """
    )

    viewer.setClickable({}, True,
        """
        function(atom, viewer, event, container) {
            viewer.zoomTo({serial: atom.serial});
            viewer.removeAllLabels();
            var label = viewer.addLabel("Selected " + atom.resn.charAt(0) + atom.resn.slice(1).toLowerCase() +
             atom.resi + " Chain: " + atom.chain, 
                {
                    useScreen:true,
                    inFront: true,
                    position: {x: 0, y: 0, z: 0},
                    fontColor: "steelblue",
                    backgroundColor: "white",
                    borderThickness: 3,
                    borderColor: "steelblue",
                }
            );
        }
        """
    )
    viewer.zoomTo()
    components.html(viewer._make_html(), **viewer_dimensions)
    return viewer


def reset_view(viewer: py3Dmol.view) -> None:
    """
    Reset a py3Dmol visualization to its default state.
    :param viewer: The view object to reset.
    :return: None.
    """
    viewer.removeAllLabels()
    viewer.zoomTo()


def generate_protein_structure_view(uniprot_id: str) -> None:
    """
    The right part of the protein details, containing structural information and a 3D molecule visualization.
    :param uniprot_id: The UniProt ID of the protein to visualize.
    :return: None.
    """
    seq = load_protein_sequence(uniprot_id)
    structures = load_protein_structures(seq)

    matched_structures = {k: v for k, v in structures.items() if v["score"] > 0.0}

    if len(matched_structures) > 0:
        structure_selector = st.radio(f"Found {len(matched_structures)} sequence matches for UniProt ID {uniprot_id}",
                                      options=matched_structures.keys(), horizontal=True,
                                      format_func=lambda
                                          x: f"{x} - Score: {matched_structures[x]['score'] * 100:.2f}%")
        viewer = render_py3DMol(structures[structure_selector]["structure"])
        st.columns(3)[1].button("Reset view", on_click=lambda: reset_view(viewer))
    else:
        st.write(f"No structure found for UniProt ID {uniprot_id}")


def generate_protein_view() -> None:
    """
    Generate the protein details view using the Streamlit API.
    :return: None
    """

    data = st.session_state["data"]

    st.header("Protein Details")

    uniprot_id = st.selectbox("UniProt ID", options=data["Uniprot"].unique())

    info_view, structure_view = st.columns(2)

    with info_view:
        generate_protein_info_view(uniprot_id, data)

    with structure_view:
        generate_protein_structure_view(uniprot_id)
