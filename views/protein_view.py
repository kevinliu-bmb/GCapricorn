import streamlit as st

from views.protein_details_view import generate_protein_details_view
from views.protein_sequence_view import generate_protein_sequence_view
from views.protein_structure_view import generate_protein_structure_view


def generate_protein_view() -> None:
    """
    Generate the protein details view using the Streamlit API.
    :return: None
    """

    data = st.session_state["data"]

    st.header("Protein Details")

    uniprot_id = st.selectbox("UniProt ID", options=data["Uniprot"].unique())

    info_view, sequence_view = st.columns(2)

    structure_view = st.container()

    with info_view:
        generate_protein_details_view(uniprot_id, data)

    with sequence_view:
        st.subheader("Protein Sequence")
        generate_protein_sequence_view(uniprot_id)

    with structure_view:
        st.subheader("Protein Structure")
        generate_protein_structure_view(uniprot_id)
