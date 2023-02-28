import streamlit as st

from views.protein_info_view import generate_protein_info_view
from views.protein_structure_view import generate_protein_structure_view


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
