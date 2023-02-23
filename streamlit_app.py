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

@st.cache
def load_data() -> pd.DataFrame:
    """
    Load the Human Protein Atlas (HPA) DataFrame and prepare the data.
    :return: the tidy DataFrame containing HPA data
    """
    hpa_df = pd.read_csv("https://www.proteinatlas.org/download/proteinatlas.tsv.zip", compression="zip", sep="\t")
    return hpa_df

def main():

    st.set_page_config(**site_configuration)

    st.write("## GCapricorn - A Data Visualization Project")


    df = load_data()
    st.session_state["data"] = df

    # 2 + 1 layout
    left_panel, view3 = st.columns(2)
    view1 = left_panel.container()
    view2 = left_panel.container()

    with view1:
        generate_cancer_view()

    with view2:
        generate_chromosome_view()

    with view3:
        generate_protein_view()

if __name__ == '__main__':
    main()