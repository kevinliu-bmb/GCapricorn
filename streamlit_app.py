import altair as alt
import pandas as pd
import streamlit as st

@st.cache
def load_data():
    hpa_df = pd.read_csv("https://www.proteinatlas.org/download/proteinatlas.tsv.zip", compression="zip", sep="\t")
    
    return hpa_df

df = load_data()

st.write("## GCapricorn - A Data Visualization Project")


chart = alt.Chart(df).mark_bar().encode(
    x=alt.X('Chromosome:N'),
    y=alt.Y('count(Gene):Q'),
    color=alt.Color('Chromosome:N') 
)


st.altair_chart(chart, use_container_width=True)