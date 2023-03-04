import altair as alt
import pandas as pd
import streamlit as st

from views.cancer_view import generate_cancer_view
from views.chromosome_view import generate_chromosome_view
from views.protein_view import generate_protein_view


site_configuration = {
    "page_title": "GCapricorn",
    "page_icon": "res/favicon.ico",
    "layout": "wide"
}

# Prioritized list of protein classes.
# Proteins that belong to multiple classes will have
# their "primary protein class" be the one that appears closest to the top of the list.
protein_class_priority = [
    "Enzymes",
    "Transporters",
    "Transcription factors",
    "Plasma proteins",
    "Ribosomal proteins",
    "Metabolic proteins",
    "G-protein coupled receptors",
    "Voltage-gated ion channels",
    "Immunoglobulin genes",
    "T-cell receptor genes",
    "Nuclear receptors",
    "Disease related genes",
    "Human disease related genes",
    "Cancer-related genes",
    "Potential drug targets",
    "FDA approved drug targets",
    "RAS pathway related proteins",
    "CD markers",
    "Candidate cardiovascular disease genes",
    "Blood group antigen proteins",
    "RNA polymerase related proteins",
    "Citric acid cycle related proteins",
    "Predicted intracellular proteins",
    "Predicted membrane proteins",
    "Predicted secreted proteins"
]

color_scale = {k: v for k, v in zip(protein_class_priority, 
                      ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728',
                        '#9467bd', '#8c564b', '#e377c2', '#7f7f7f',
                        '#bcbd22', '#17becf', '#2c3e50', '#8e44ad',
                        '#2ecc71', '#e74c3c', '#2980b9', '#f1c40f',
                        '#c0392b', '#9b59b6', '#1abc9c', '#7f8c8d',
                        '#34495e', '#95a5a6', '#f39c12', '#d35400',
                        '#c0392b'])}

with open("stylesheet.css") as stylesheet:
    site_style = f"<style>{stylesheet.read()}</style>"


def generate_prognostic_data(row: pd.Series, prognostic_type: str) -> str:
    """
    Generate a prognostics value for a given protein.
    :param row: A Human Protein Atlas entry. Must contain prognostics information in different cancer columns.
    :param prognostic_type: one of "favorable" or "unfavorable".
    :return: A comma-separated string containing all the cancer types for
    which the protein has a prognostic_type prognostic.
    """
    prognostic_fields = row[pd.Series(row.index).apply(lambda x: "Pathology prognostics" in x).values]
    prognostics_row = row[prognostic_fields.index]
    prognostics = prognostics_row[prognostics_row.apply(lambda x: prognostic_type in str(x).lower().split())].index
    return ",".join(map(lambda x: x.split("-")[1].strip(), prognostics))


def prioritize_protein_class(protein_classes: str, priority_list: list[str] = None) -> list[str]:
    """
    Get a list of prioritized protein classes from a comma-separated string of protein classes.
    :param protein_classes: Protein classes in a comma-separated format.
    :param priority_list: list of prioritized protein classes.
    :return: The primary protein class as a string.
    """

    if priority_list is None:
        priority_list = protein_class_priority

    class_list = [x.strip() for x in protein_classes.split(",")]
    prioritized_protein_classes = [x for x in priority_list if x in class_list]
    if prioritized_protein_classes:
        return prioritized_protein_classes
    return class_list


@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load the Human Protein Atlas (HPA) DataFrame and prepare the data.
    :return: the tidy DataFrame containing HPA data
    """
    data = pd.read_csv("https://www.proteinatlas.org/download/proteinatlas.tsv.zip", compression="zip", sep="\t")
    data["Favorable prognostics"] = data.apply(lambda row: generate_prognostic_data(row, prognostic_type="favorable"), axis=1)
    data["Unfavorable prognostics"] = data.apply(lambda row: generate_prognostic_data(row, prognostic_type="unfavorable"), axis=1)
    data.dropna(subset=["Uniprot"], inplace=True)
    data["Prioritized Protein Class"] = data["Protein class"].apply(prioritize_protein_class)
    data.drop(data[(data["Chromosome"] == "MT") | (data["Chromosome"] == "Unmapped")].index, inplace=True)
    
    return data


def main():

    st.set_page_config(**site_configuration)
    st.markdown(site_style, unsafe_allow_html=True)

    alt.themes.enable("urbaninstitute")

    st.title("GCapricorn")

    data = load_data()
    st.session_state["unfiltered_data"] = data
    st.session_state["data"] = data

    st.session_state["color_scale"] = color_scale

    protein_classes = [x.split(", ") for x in data["Protein class"]]
    protein_classes = [item for sublist in protein_classes for item in sublist]
    protein_classes = list(set(protein_classes))

    left, middle, right = st.columns(3)
    protein_selection = middle.multiselect(label="Select Protein Classes", options=protein_classes,
                                          default=["Enzymes", "Transporters", "Transcription factors"])
    st.session_state["protein_selection"] = protein_selection
    cancer_types = map(lambda x: x.split("-")[1].strip(),
                       filter(lambda x: "Pathology prognostics" in x, data.columns))
    cancer_selection = left.selectbox(label="Select Cancer Type", options=cancer_types, index=0)
    st.session_state["cancer_selection"] = cancer_selection

    prognosis_selection = right.selectbox(label = "Select Prognosis", options = ["Favorable", "Unfavorable"])
    st.session_state["prognosis_selection"] = prognosis_selection

    # Horizontal 2 + 1 layout
    top_panel = st.container()
    view1, view2 = top_panel.columns(2)
    view3 = st.container()

    with view1:
        generate_cancer_view()

    with view2:
        generate_chromosome_view()
    
    with view3:
        generate_protein_view()


if __name__ == "__main__":
    main()
