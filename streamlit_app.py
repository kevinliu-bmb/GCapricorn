import altair as alt
import pandas as pd
import streamlit as st

@st.cache
def load_data():
    hpa_df = pd.read_csv("https://www.proteinatlas.org/download/proteinatlas.tsv.zip", compression="zip", sep="\t")
    # nonPathology_id_vars = [col for col in hpa_df.columns if col.startswith('Pathology prognostics') == False]
    # hpa_df = hpa_df.melt(id_vars=nonPathology_id_vars, var_name="pathology", value_name="prognostic")
    # nonBloodConc_id_vars = [col for col in hpa_df.columns if col.startswith('Blood concentration') == False]
    # hpa_df = hpa_df.melt(id_vars=nonBloodConc_id_vars, var_name="bloodConcType", value_name="bloodConc")
    # nonExpressionCluster_id_vars = [col for col in hpa_df.columns if col.endswith('expression cluster') == False]
    # hpa_df = hpa_df.melt(id_vars=nonExpressionCluster_id_vars, var_name="expressionClusterType", value_name="expressionCluster")
    
    return hpa_df

df = load_data()

st.write("## GCapricorn - A Data Visualization Project")

chart = alt.Chart(df).mark_bar().encode(
    x='Chromosome:N',
    y='count(Gene):Q',
    color='Chromosome:N'
)
st.altair_chart(chart, use_container_width=True)

# ### P2.1 ###
# year = st.slider(label="Year", min_value=min(df["Year"]), max_value=max(df["Year"]), value=2012)
# subset = df[df["Year"] == year]
# ### P2.1 ###

# ### P2.2 ###
# sex = st.radio(label="Sex", options=df["Sex"].unique()[::-1], index=0)
# subset = subset[subset["Sex"] == sex]
# ### P2.2 ###

# ### P2.3 ###
# countries = [
#     "Austria",
#     "Germany",
#     "Iceland",
#     "Spain",
#     "Sweden",
#     "Thailand",
#     "Turkey"
# ]
# country = st.multiselect(label="Country", options=df["Country"].unique(), default=countries)
# subset = subset[subset["Country"].isin(country)]
# ### P2.3 ###

# ### P2.4 ###
#cancer = st.selectbox(label="Cancer", options=df["pathology"].unique(), index=0)
#subset = subset[subset["Cancer"] == cancer]
# ### P2.4 ###

# ### P2.5 ###
# ages = [
#     "Age <5",
#     "Age 5-14",
#     "Age 15-24",
#     "Age 25-34",
#     "Age 35-44",
#     "Age 45-54",
#     "Age 55-64",
#     "Age >64"
# ]

# chart = alt.Chart(subset).mark_rect().encode(
#     x=alt.X("Age", sort=ages),
#     y=alt.Y("Country:N", title="Countries"),
#     color=alt.Color("Rate", scale=alt.Scale(clamp=True, domain=[0.01, 1000], type="log"), title="Mortality rate per 100k"),
#     tooltip=["Rate:Q"],
# ).properties(
#     title=f"{cancer} mortality rates for {'males' if sex == 'M' else 'females'} in {year}",
#     width=500
# ) & alt.Chart(subset).mark_bar().encode(
#     x=alt.X("sum(Pop):Q", title="Sum of population size"),
#     y=alt.Y("Country:N", sort="-x")
# ).properties(
#     width=500
# )
# ### P2.5 ###

# st.altair_chart(chart, use_container_width=True)

# countries_in_subset = subset["Country"].unique()
# if len(countries_in_subset) != len(countries):
#     if len(countries_in_subset) == 0:
#         st.write("No data avaiable for given subset.")
#     else:
#         missing = set(countries) - set(countries_in_subset)
#         st.write("No data available for " + ", ".join(missing) + ".")