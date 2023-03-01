import altair as alt
import streamlit as st


def generate_cancer_view() -> None:
    st.header("HPA Cancer Statistics")
    
    df = st.session_state["data"]
    cancer_selection = st.session_state["cancer_selection"]

    df["Unfavorable prognostics"] = df["Unfavorable prognostics"].apply(lambda x: [item.strip() for item in x.split(",")])
    #df2 = df.explode("Unfavorable prognostics")
    df2 = df[df["Unfavorable prognostics"].apply(lambda x: cancer_selection in x)]

    df2["Protein class"] = df["Protein class"].apply(lambda x: [item.strip() for item in x.split(",")])
    df2 = df2.explode("Protein class")
    
    protein_selection = st.session_state["protein_selection"]
    df3 = df2[df2["Protein class"].isin(protein_selection)]

    chart = alt.Chart(df3).mark_bar().encode(
        x=alt.X('Protein class:N', title=None, axis=alt.Axis(tickCount=26, grid=False, labels=False)),
        y=alt.Y('count(Gene):Q', title= "Gene Count"),
        color=alt.Color('Protein class:N'), 
        column=alt.Column('Chromosome:O', sort = [str(x) for x in range(1, 23)] + ["MT", "X", "Y", "Unmapped"], spacing=0,
                          header=alt.Header(titleOrient='bottom', labelOrient='bottom'))).properties(width=20).configure_range(category={'scheme': 'dark2'})
        
    st.altair_chart(chart, use_container_width=False)
