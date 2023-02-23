import json
import os

import requests
import py3Dmol
import streamlit as st
import streamlit.components.v1 as components

@st.cache
def load_protein_sequence(protein_id: str) -> str:
    """
    Retrieve amino acid sequence in one-letter codes from the UniProt database.
    :param protein_id: UniProt ID.
    :return: The protein sequence as a string of amino acids.
    """
    fasta_string: str = requests.get(f"https://www.uniprot.org/uniprot/{protein_id}.fasta").text
    return ''.join(fasta_string.split('\n')[1:])

#@st.cache
def load_protein_structure(sequence: str) -> str:
    # TODO: this is still under construction
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

    pdb_id = requests.get(f"https://search.rcsb.org/rcsbsearch/v2/", params=query).text
    st.write(pdb_id, type(pdb_id), f"https://search.rcsb.org/rcsbsearch/v2/query?json={json.dumps(query, separators=(',', ':'))}")
    #result = requests.get(f"https://files.rcsb.org/download/{pdb_id}.pdb.gz").text
    #return gzip.decompress(result.encode()).decode()
    return pdb_id

def render_py3DMol(molecule: str, string_format: str = "pdb") -> None:
    """
    Render the molecule using the Py3DMol API.
    :param molecule: path to the molecule file, or string literal containing molecule information.
    :param string_format: format of the protein. Default format is PDB.
    :return: None.
    """
    visualization_type = st.selectbox("Type", options=["cartoon", "stick", "sphere"],
                                      format_func=lambda x: f"{x.title()} model")

    viewer = py3Dmol.view(width=400, height=400)
    if os.path.exists(molecule):
        with open(molecule, "r") as file:
            viewer.addModel(file.read(), string_format)
    else:
        viewer.addModel(molecule, string_format)
    viewer.setStyle({visualization_type: {"color": "spectrum"}})
    viewer.zoomTo()
    components.html(viewer._make_html(), height=400, width=400)

def generate_protein_view() -> None:
    """
    Generate the protein details view using the Streamlit API.
    :return: None
    """

    st.title("View3")

    molecule_id = "O43657"  # Hardcoded for now
    seq = load_protein_sequence(molecule_id)
    st.write(seq)

    load_protein_structure(seq)

    # Also hardcoded for now. If you want to try your own, download from PDB database.
    molecule_path = "/home/diego/Universidad/Harvard/Capstone/PDBBind/PDBBind_processed/1azx/1azx_protein_processed.pdb"
    render_py3DMol(molecule_path)

