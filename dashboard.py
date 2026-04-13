## Streamlit Dashboard
# Tokyo Olympics 2021 - Medal Efficiency Project
# - Run with: streamlit run dashboard.py
# - Install dependencies first:

import subprocess

# Install dependencies
subprocess.run(["pip", "install", "streamlit"])

# Libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page Config - This should be the first Streamlit command
st.set_page_config(
    page_title = "Tokyo Olympics 2021 Medal Efficiency",
    page_icon="🥇",
    layout="wide"
)

# Load the Data
# TODO: Load data from Phase 3 output
# Use @st.cache_data so it doesn't reload on every interaction
@st.cache_data
def load_data():
  df_url = "https://raw.githubusercontent.com/Hrish52/Tokyo-Olympics-2021-Analytics/refs/heads/main/olympics_final_analysis.csv"
  df = pd.read_csv(df_url, index_col=0)
  return df

df = load_data()

# Sidebar Filters
## This will let users slice the data interactively ##
st.sidebar.title("🎯 Filters")

## Country Size Filters
selected_sizes = st.sidebar.multiselect(
    "Country Size",
    options=df['country_size_category'].unique(),
    default=df['country_size_category'].unique()
)

## Minimum medals filter
min_medals = st.sidebar.slider(
    "Minimum Total Medals",
    min_value=int(df['total'].min()),
    max_value=int(df['total'].max()),
    value=int(df['total'].min())
)

## GDP Category filter
selected_gdp = st.sidebar.multiselect(
    "GDP Category",
    options=df['gdp_category'].unique(),
    default=df['gdp_category'].unique()
)

# d) Apply filters to create a filtered dataframe
df = df[
    (df['country_size_category'].isin(selected_sizes)) &
    (df['total'] >= min_medals) &
    (df['gdp_category'].isin(selected_gdp))
]

# Header & Key Story Metrics (Storytelling Section)
# This section tells the "headline" story before users explore #

st.title("🏅 Tokyo 2021: Who Really Won the Olympics?")
st.markdown("""
Beyond raw medal counts lies a deeper story — which nations truly
punched above their weight? This dashboard explores medal **efficiency**
by comparing results against each country's athletes, population, and GDP.
""")

# Create 4 key metric cards using st.columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Countries", len(df))

with col2:
    # Most efficient country by medals per athlete
    # Using .name because 'country' is the index
    top_eff = df.loc[df['medals_per_athlete'].idxmax()]
    st.metric("Most Efficient (per athlete)", top_eff.name)

with col3:
    # Most efficient by population
    top_pop = df.loc[df['medals_per_million_pop'].idxmax()]
    st.metric("Most Efficient (per capita)", top_pop.name)

with col4:
    # Most efficient by GDP
    top_gdp = df.loc[df['medals_per_billion_gdp'].idxmax()]
    st.metric("Most Efficient (per $B GDP)", top_gdp.name)

# Key Insight — Raw Medals vs Efficiency
# This chart is the "aha moment" — showing that the traditional
# medal table tells a very different story than efficiency metrics

st.header("📊 The Traditional View vs Reality")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Traditional Medal Count (Top 10)")
    # Bar chart of top 10 countries by Total medals
    top10_total = df.nlargest(10, 'total')
    # Use df.index to refer to the country names if they are in the index
    fig_total = px.bar(top10_total, x=top10_total.index, y='total',
                       color='gold', title="Top 10 by Total Medal Count",
                       color_continuous_scale="Viridis")
    st.plotly_chart(fig_total, use_container_width=True)

with col_right:
    st.subheader("Efficiency View (Top 10)")
    # Bar chart of top 10 countries by Medals_Per_Athlete
    top10_eff = df.nlargest(10, 'medals_per_athlete')
    fig_eff = px.bar(top10_eff, x=top10_eff.index, y='medals_per_athlete',
                     title="Top 10 by Medals per Athlete",
                     color_discrete_sequence=['#FFA15A'])
    st.plotly_chart(fig_eff, use_container_width=True)

# Scatter Plot — Athletes vs Medals
st.header("🔍 Deep Dive: Athletes vs Medals")

fig = px.scatter(
    df,
    x='athlete_count',
    y='total',
    size='population',
    color='country_size_category',
    hover_name=df.index,
    hover_data=['gold', 'silver', 'bronze', 'medals_per_athlete'],
    title="Team Size vs Medal Haul",
    labels={'athlete_count': 'Number of Athletes', 'total': 'Total Medals'}
)
st.plotly_chart(fig, width='stretch')

st.markdown("""
> **Insight:** Countries above the trend line are over-performing
> relative to their team size. Countries below are under-performing.
""")

# Efficiency Comparison — User Selects the Metric
# Let users choose which efficiency metric to explore

st.header("ፈ Efficiency Rankings")

# Add a selectbox to choose the metric
metric = st.selectbox("Choose efficiency metric:", [
    'medals_per_athlete',
    'medals_per_million_pop',
    'medals_per_billion_gdp',
    'weighted_score_per_athlete',
    'gold_percentage'
])

# Create a horizontal bar chart of top 15 for selected metric
top15 = df.nlargest(15, metric)
fig = px.bar(top15, x=metric, y=top15.index, orientation='h',
             color=metric, color_continuous_scale='YlOrRd',
             title=f"Top 15 Countries by {metric}",
             labels={'index': 'Country'})

fig.update_layout(yaxis={'categoryorder': 'total ascending'})
st.plotly_chart(fig, width='stretch')

# GDP vs Population Efficiency Matrix
st.header("ጠ Who Punches Above Their Weight?")

fig = px.scatter(
    df,
    x='medals_per_million_pop',
    y='medals_per_billion_gdp',
    size='total',
    color='country_size_category',
    hover_name=df.index,
    hover_data=['total', 'gold', 'population', 'gdp'],
    title="Population Efficiency vs GDP Efficiency"
)
st.plotly_chart(fig, width='stretch')

st.markdown("""
> **Top-right quadrant** = countries that are efficient on BOTH measures.
> These are the true over-performers of the Olympics.
""")

# Country Deep Dive
# Let users select a specific country to see all its details

st.header("ጒ Country Deep Dive")

# Add a selectbox for country selection from the index
selected_country = st.selectbox(
    "Select a country to inspect:",
    options=df.index.sort_values().unique()
)

# Extract data for the selected country
country_data = df.loc[selected_country]

# Display key metrics in columns
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Medals", int(country_data['total']))
    st.metric("Gold Medals", int(country_data['gold']))

with col2:
    st.metric("Athletes Sent", int(country_data['athlete_count']))
    st.metric("Medals per Athlete", f"{country_data['medals_per_athlete']:.3f}")

with col3:
    st.metric("Per Million Pop", f"{country_data['medals_per_million_pop']:.2f}")
    st.metric("Per $B GDP", f"{country_data['medals_per_billion_gdp']:.2f}")

# Show relative performance insights
st.subheader(f"Rankings for {selected_country}")
st.markdown(f"""
Based on the current filtered dataset of {len(df)} countries:
- **Medals per Athlete:** Top {((df['medals_per_athlete'] > country_data['medals_per_athlete']).sum() + 1)}
- **Per Capita Efficiency:** Top {((df['medals_per_million_pop'] > country_data['medals_per_million_pop']).sum() + 1)}
- **GDP Efficiency:** Top {((df['medals_per_billion_gdp'] > country_data['medals_per_billion_gdp']).sum() + 1)}
""")

# Medal Breakdown Treemap
st.header("ማ Medal Distribution")

# Reset index temporarily for treemap path if needed or use index
temp_df = df.reset_index()
fig = px.treemap(
    temp_df,
    path=['country_size_category', 'country'],
    values='total',
    color='medals_per_athlete',
    color_continuous_scale='RdYlGn',
    hover_data=['gold', 'silver', 'bronze'],
    title="Medal Distribution (Size = Total Medals, Color = Efficiency)"
)

fig.update_layout(margin=dict(t=50, l=25, r=25, b=25))
st.plotly_chart(fig, width='stretch')

# Full Data Table
# Let users explore the raw data

st.header("📋 Full Data")

# Display an interactive table of the current filtered data
st.dataframe(
    df.sort_values('total', ascending=False),
    use_container_width=True,
    hide_index=False
)

st.info(f"Displaying {len(df)} countries based on your current filters.")

# FOOTER

st.markdown("---")
st.markdown("""
**Data Sources:** Tokyo 2021 Olympics dataset, World Bank (GDP & Population 2021),
IMF/UN (Cuba, Venezuela, Taiwan)
**Built with:** Python, Pandas, Plotly, Streamlit
""")