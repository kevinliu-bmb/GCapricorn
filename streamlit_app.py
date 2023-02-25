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



@st.cache_data
def load_data() -> pd.DataFrame:
    """
    Load the Human Protein Atlas (HPA) DataFrame and prepare the data.
    :return: the tidy DataFrame containing HPA data
    """
    data = pd.read_csv("https://www.proteinatlas.org/download/proteinatlas.tsv.zip", compression="zip", sep="\t")
    data["Favorable prognostics"] = data.apply(lambda row: generate_prognostic_data(row, prognostic_type="favorable"), axis=1)
    data["Unfavorable prognostics"] = data.apply(lambda row: generate_prognostic_data(row, prognostic_type="unfavorable"), axis=1)

    return data


def main():

    st.set_page_config(**site_configuration)

    st.title("GCapricorn")


    data = load_data()
    st.session_state["unfiltered_data"] = data
    st.session_state["data"] = data

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


if __name__ == '__main__':
    main()
