import gzip
import json
import os
from typing import Optional, Union

import py3Dmol
import requests
import streamlit as st
import streamlit.components.v1 as components

from views.protein_sequence_view import load_protein_sequence


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


def render_py3DMol(molecule: str, visualization_type: str, colorscheme: int, string_format: str = "pdb") -> py3Dmol.view:
    """
    Render the molecule using the Py3DMol API.
    :param molecule: path to the molecule file, or string literal containing molecule information.
    :param visualization_type: the type of visualization to render. One of {"cartoon", "stick", "sphere"}.
    :param colorscheme: the color scheme to show in the visualization.
    An integer to index the ["amino", "ssPyMol", "chainHetatm"] list.
    :param string_format: format of the protein. Default format is "pdb". One of "pdb", "sdf", "mol2", "xyz", and "cube".
    :return: The view object.
    """

    viewer_dimensions = {"height": 500}

    viewer = py3Dmol.view(**viewer_dimensions)

    if os.path.exists(molecule):
        with open(molecule, "r") as file:
            viewer.addModel(file.read(), string_format)
    else:
        viewer.addModel(molecule, string_format)

    if visualization_type == "cartoon":
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
    Visualize the 3D structure of the protein.
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
        visualization_type = st.selectbox("Structure View", options=["cartoon", "stick", "sphere"],
                                          format_func=lambda x: f"{x.title()} model")
        colorscheme = st.radio("Color", options=[0, 1, 2],
                               format_func=lambda x: ["Amino acids", "Secondary structure", "Monomers"][x])
        viewer = render_py3DMol(structures[structure_selector]["structure"], visualization_type, colorscheme)
        st.columns(3)[1].button("Reset view", on_click=lambda: reset_view(viewer))
    else:
        st.write(f"No structure found for UniProt ID {uniprot_id}")