import gzip
import json
import os
from typing import Optional

import py3Dmol
import requests
import streamlit as st
import streamlit.components.v1 as components


@st.cache_data
def load_protein_sequence(protein_id: str) -> str:
    """
    Retrieve amino acid sequence in one-letter codes from the UniProt database.
    :param protein_id: UniProt ID.
    :return: The protein sequence as a string of amino acids.
    """
    fasta_string: str = requests.get(f"https://www.uniprot.org/uniprot/{protein_id}.fasta").text
    return ''.join(fasta_string.split('\n')[1:])

@st.cache_data
def load_protein_structures(sequence: str) -> Optional[dict[str, dict[str, str]]]:
    """
    Retrieve protein structures from a protein sequence. Uses the PDB API in order to obtain PDB entries that match
    the provided sequence.
    :param sequence: The protein sequence as a string of 1-letter amino acids.
    :return: A dictionary containing the PDB ID as a key and PDB structure and score as values. The score is a numeric
    value from 0 to 1 representing the sequence match.
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

    try:
        pdb_response = json.loads(requests.get(
            f"https://search.rcsb.org/rcsbsearch/v2/query?json={json.dumps(query, separators=(',', ':'))}").text
        )
    except json.JSONDecodeError:
        return None

    structures = {}
    for pdb_result in pdb_response["result_set"]:
        pdb_id = pdb_result["identifier"]
        score = pdb_result["score"]
        structure = requests.get(f"https://files.rcsb.org/download/{pdb_id}.pdb.gz").content
        structures[pdb_id] = {"score": score, "structure": gzip.decompress(structure).decode()}
    return structures

def render_py3DMol(molecule: str, string_format: str = "pdb") -> None:
    """
    Render the molecule using the Py3DMol API.
    :param molecule: path to the molecule file, or string literal containing molecule information.
    :param string_format: format of the protein. Default format is PDB.
    :return: None.
    """
    visualization_type = st.selectbox("Structure View", options=["cartoon", "stick", "sphere"],
                                      format_func=lambda x: f"{x.title()} model")

    viewer = py3Dmol.view(width=600, height=400)
    if os.path.exists(molecule):
        with open(molecule, "r") as file:
            viewer.addModel(file.read(), string_format)
    else:
        viewer.addModel(molecule, string_format)
    viewer.setStyle({visualization_type: {"color": "spectrum"}})
    viewer.zoomTo()
    components.html(viewer._make_html(), width=600, height=400)

def generate_protein_view() -> None:
    """
    Generate the protein details view using the Streamlit API.
    :return: None
    """

    data = st.session_state["data"]
    st.header("Protein Details")

    uniprot_id = st.selectbox("UniProt ID", options=data["Uniprot"].unique())
    seq = load_protein_sequence(uniprot_id)
    st.text_area("Amino Acid Sequence", seq)

    structures = load_protein_structures(seq)
    if structures is not None:
        structure_selector = st.radio(f"Structure matches for UniProt ID {uniprot_id}", options=structures.keys(), horizontal=True,
                                      format_func=lambda x: f"{x} - Sequence Match Score: {structures[x]['score']:.2f}")
        render_py3DMol(structures[structure_selector]["structure"])
    else:
        st.write(f"No structure found for UniProt ID {uniprot_id}")

