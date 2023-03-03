import altair as alt
import streamlit as st
import pandas as pd


def generate_cancer_view() -> None:
    st.header("Cancer-related Protein Statistics")
    
    df = st.session_state["data"]
    cancer_selection = st.session_state["cancer_selection"]
    prognosis_selection = st.session_state["prognosis_selection"]

    df2 = df[(df[f"{prognosis_selection} prognostics"].apply(lambda x: cancer_selection in x))]

    df2["Protein class"] = df["Protein class"].apply(lambda x: [item.strip() for item in x.split(",")])
    df2 = df2.explode("Protein class")
    
    protein_selection = st.session_state["protein_selection"]
   
    df3 = df2[df2["Protein class"].isin(protein_selection)]

    if not protein_selection:
        st.warning("No protein classes selected. Displaying only broad-level protein classes.")
        df3 = df2[df2["Protein class"].apply(
            lambda x: any(protein_class in x for protein_class in ["Enzymes", "Transporters", "Transcription factors"])
        )]
    else:
        df3 = df2[df2["Protein class"].apply(
            lambda x: any(protein_class in x for protein_class in protein_selection)
        )]
   
    chromosomes = [str(x) for x in range(1, 23)] + ["X", "Y", "MT", "Unmapped"]

    chart = alt.Chart(df3).mark_bar().encode(
        x=alt.X('Protein class:N', title=None, axis=alt.Axis(tickCount=26, grid=False, labels=False), 
                sort = chromosomes),
        y=alt.Y('count(Gene):Q', axis= alt.Axis(title= "Gene Count", labelAngle = -90)),
        color=alt.Color('Protein class:N'),
        column=alt.Column('Chromosome:O', sort = [str(x) for x in range(1, 23)] + ["X", "Y", "MT", "Unmapped"], spacing=13,
                          header=alt.Header(titleOrient='bottom', labelOrient='bottom')),
        tooltip=["Chromosome", "Protein class", "count(Gene)"]
    ).properties(width=22).configure_legend(orient='bottom')

    st.altair_chart(chart, use_container_width=False)
