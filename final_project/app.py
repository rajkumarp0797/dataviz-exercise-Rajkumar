import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ------------------------------------------------------------------------------
# 1. Page Setup & Configuration
# ------------------------------------------------------------------------------
st.set_page_config(
    page_title="Global Air Quality Analytics",
    page_icon="🌍",
    layout="wide"
)

# ------------------------------------------------------------------------------
# 2. Data Loading & Caching
# ------------------------------------------------------------------------------
@st.cache_data
def load_data():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(BASE_DIR, 'data', 'global air pollution dataset.csv')
    
    df = pd.read_csv(csv_path)
    df = df.dropna(subset=['Country'])
    
    pollutant_cols = ['CO AQI Value', 'Ozone AQI Value', 'NO2 AQI Value', 'PM2.5 AQI Value']
    df['Primary_Pollutant'] = df[pollutant_cols].idxmax(axis=1).str.replace(' AQI Value', '')
    df['PM2.5_Ratio'] = np.where(df['AQI Value'] > 0, df['PM2.5 AQI Value'] / df['AQI Value'], 0)
    return df

df = load_data()

# ------------------------------------------------------------------------------
# 3. Sidebar Filtering Controls
# ------------------------------------------------------------------------------
st.sidebar.header("🌍 Global Filters")

all_countries = sorted(df['Country'].unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Select Countries",
    options=all_countries,
    default=['United States of America', 'India', 'Brazil', 'Germany', 'Italy', 'China', 'Poland']
)

all_categories = df['AQI Category'].unique().tolist()
selected_categories = st.sidebar.multiselect(
    "Select AQI Severity Tiers",
    options=all_categories,
    default=all_categories
)

# Apply Filter Logic
filtered_df = df[
    (df['Country'].isin(selected_countries)) &
    (df['AQI Category'].isin(selected_categories))
]

# ------------------------------------------------------------------------------
# 4. Main Dashboard UI
# ------------------------------------------------------------------------------
st.title("🌍 Global Air Quality & Pollutant Explorer")
st.markdown("Interactive analysis of multi-pollutant drivers across global cities.")

# Summary Metrics Row
col1, col2, col3, col4 = st.columns(4)
col1.metric("Cities Included", f"{len(filtered_df):,}")
col2.metric("Mean AQI Score", f"{filtered_df['AQI Value'].mean():.1f}" if not filtered_df.empty else "N/A")
col3.metric("Mean PM2.5 AQI", f"{filtered_df['PM2.5 AQI Value'].mean():.1f}" if not filtered_df.empty else "N/A")
col4.metric("Mean Ozone AQI", f"{filtered_df['Ozone AQI Value'].mean():.1f}" if not filtered_df.empty else "N/A")

st.divider()

# Tab Navigation
tab1, tab2, tab3 = st.tabs([
    "📊 Primary Drivers & Pollutants", 
    "🗺️ Cross-National Comparisons", 
    "🔥 Pollutant Correlations"
])

with tab1:
    st.subheader("Primary Pollutant Breakdown")
    if not filtered_df.empty:
        q1_data = filtered_df['Primary_Pollutant'].value_counts().reset_index()
        q1_data.columns = ['Pollutant', 'City_Count']
        
        fig1 = px.bar(
            q1_data,
            x='Pollutant',
            y='City_Count',
            color='Pollutant',
            text='City_Count',
            title="<b>Primary Driver:</b> Dominant Pollutants Across Selected Subset",
            labels={'City_Count': 'Number of Cities', 'Pollutant': 'Pollutant Driver'},
            color_discrete_map={'PM2.5': '#2b5c8f', 'Ozone': '#e07a5f', 'NO2': '#f4a261', 'CO': '#81b29a'},
            template='plotly_white'
        )
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.warning("No data matching current sidebar filters.")

with tab2:
    st.subheader("PM2.5 Distribution Across Selected Nations")
    if not filtered_df.empty:
        fig2 = px.box(
            filtered_df,
            x='Country',
            y='PM2.5 AQI Value',
            color='Country',
            title="<b>National Range:</b> PM2.5 Concentrations by Country",
            labels={'PM2.5 AQI Value': 'PM2.5 AQI Score', 'Country': 'Country'},
            template='plotly_white'
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.warning("No data matching current sidebar filters.")

with tab3:
    st.subheader("NO2 vs. Ozone Interactions")
    if not filtered_df.empty:
        fig3 = px.scatter(
            filtered_df,
            x='NO2 AQI Value',
            y='Ozone AQI Value',
            color='AQI Category',
            hover_data=['Country', 'City'],
            title="<b>Scatter Matrix:</b> NO2 vs Ozone Scores",
            labels={'NO2 AQI Value': 'NO2 AQI Score', 'Ozone AQI Value': 'Ozone AQI Score'},
            template='plotly_white',
            opacity=0.7
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.warning("No data matching current sidebar filters.")