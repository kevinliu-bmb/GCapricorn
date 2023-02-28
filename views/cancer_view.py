import altair as alt
import streamlit as st


def generate_cancer_view() -> None:
    st.header("HPA Cancer Statistics")

    df = st.session_state["data"]
    df = df.rename(columns={'Unfavorable prognostics': 'cancer'})
    df = df.rename(columns={'Protein class': 'p_class'})

    df.cancer = df.cancer.str.split(',')
    df2 = df.explode('cancer')

    df2.p_class = df.p_class.str.split(',')
    df2 = df2.explode('p_class')
    
    cancersls = df2["cancer"].unique().tolist()
    cancer_dropdown = alt.binding_select(options=cancersls)
    cancer_select = alt.selection_single(fields = ['cancer'], on = 'click', bind=cancer_dropdown, name='Cancer Type')

    protclasses = df2["p_class"].unique().tolist()
    proteinselect = st.multiselect('Protein Classes', options=protclasses)

    chart = alt.Chart(df2).mark_bar().encode(
        x=alt.X('Chromosome:O', sort = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "MT", "X", "Y", "Unmapped"]),
        y=alt.Y('count(Gene):Q'),
        color=alt.Color('p_class:N'),
        column = alt.Column('p_class')).add_selection(cancer_select).transform_filter(cancer_select)

    st.altair_chart(chart, use_container_width=True)
