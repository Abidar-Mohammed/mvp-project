import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIG PAGE ---
st.set_page_config(
    page_title="Netflix Personal Analytics",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Gestion de l'état du bouton Méthodologie
if 'show_methodology' not in st.session_state:
    st.session_state.show_methodology = False

def toggle_methodology():
    st.session_state.show_methodology = not st.session_state.show_methodology

# --- 2. CSS NETFLIX DARK ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@300;400;600&display=swap');

    /* FOND NOIR */
    .stApp {
        background-color: #141414;
        color: #E5E5E5;
    }

    /* TITRES */
    h1, h2, h3 {
        font-family: 'Bebas Neue', sans-serif;
        color: #E50914 !important; /* Rouge Netflix */
        letter-spacing: 1.5px;
    }
    
    p, div, label, li {
        font-family: 'Montserrat', sans-serif;
        color: #B3B3B3;
    }

    /* KPI CARDS */
    div[data-testid="metric-container"] {
        background-color: #1F1F1F;
        border: 1px solid #333;
        border-left: 4px solid #E50914;
        border-radius: 4px;
        padding: 15px;
    }
    div[data-testid="metric-container"] label {
        color: #757575 !important;
        font-size: 0.8rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFF !important;
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.5rem;
    }

    /* BOUTON */
    div.stButton > button {
        background-color: transparent;
        border: 1px solid #E50914;
        color: #E50914;
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.2rem;
        transition: 0.3s;
    }
    div.stButton > button:hover {
        background-color: #E50914;
        color: #FFF;
    }
    
    /* CHARTS */
    .stPlotlyChart {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT ET TRAITEMENT ---
@st.cache_data
def load_data():
    file_name = "NetflixHistory.csv"
    
    # Recherche robuste du fichier
    path = None
    possible_paths = [
        file_name, 
        os.path.join(os.path.dirname(os.path.abspath(__file__)), file_name)
    ]
    
    for p in possible_paths:
        if os.path.exists(p):
            path = p
            break
            
    if not path:
        st.error(f"⚠️ Fichier '{file_name}' introuvable. Lancez d'abord 'generate_data.py'.")
        return pd.DataFrame()

    df = pd.read_csv(path)
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
    
    # FEATURE ENGINEERING (La "Magie" de l'analyse)
    def parse_content(title):
        # Mots clés indiquant une série
        keywords = ['Saison', 'Season', 'Episode', 'Partie', 'Chapter']
        is_show = any(k in title for k in keywords) or (":" in title and "Episode" in title)
        
        if is_show:
            c_type = "TV Show"
            # Extraction du nom de la série (avant le premier ":")
            name = title.split(":")[0]
            duration = 45 # Estimation 45min/épisode
        else:
            c_type = "Movie"
            name = title
            duration = 105 # Estimation 1h45/film
            
        return pd.Series([c_type, name, duration])

    df[['Type', 'Show_Name', 'Duration_Mins']] = df['Title'].apply(parse_content)
    
    # Enrichissement Temporel
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['WeekEnd'] = df['Date'].dt.weekday >= 5
    
    return df

df = load_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### 🍿 FILTERS")
    if not df.empty:
        min_d = df['Date'].min().date()
        max_d = df['Date'].max().date()
        date_range = st.date_input("Period", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        show_filter = st.multiselect("Select Series", df[df['Type']=='TV Show']['Show_Name'].unique())

    st.markdown("---")
    st.info("Quantified Self Project | Netflix Data")

if df.empty:
    st.stop()

# Filtrage
mask = (df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])
if show_filter:
    mask = mask & (df['Show_Name'].isin(show_filter))
df_filtered = df[mask]

# --- 5. HEADER ---
st.markdown("""
<div style="text-align: center; margin-bottom: 40px;">
    <h1 style="font-size: 4rem; margin: 0;">NETFLIX UNWRAPPED</h1>
    <p style="text-transform: uppercase; letter-spacing: 2px;">My Streaming History Analysis</p>
</div>
""", unsafe_allow_html=True)

# --- 6. METHODOLOGY BUTTON ---
col_info1, col_info2, col_info3 = st.columns([1, 2, 1])
btn_text = "✕ CLOSE REPORT" if st.session_state.show_methodology else "ℹ️ VIEW PROJECT REPORT"

with col_info2:
    st.button(btn_text, on_click=toggle_methodology, use_container_width=True)

if st.session_state.show_methodology:
    st.markdown("""
    <div style="background: #222; padding: 25px; border-radius: 10px; border: 1px solid #444; margin-bottom: 30px;">
        <h3 style="color: #E50914; text-align: center;">PROJECT METHODOLOGY</h3>
        
        <h4 style="color: #FFF;">1. Data Collection</h4>
        <ul style="color: #CCC;">
            <li><strong>Source:</strong> Personal Netflix Data Export (<code>NetflixHistory.csv</code>).</li>
            <li><strong>Constraint:</strong> The raw file only contains <em>Title</em> and <em>Date</em>. No duration, no genre.</li>
        </ul>

        <h4 style="color: #FFF;">2. Data Engineering (Python)</h4>
        <ul style="color: #CCC;">
            <li><strong>Parsing:</strong> I developed a script to parse strings like <em>"Stranger Things: Season 4: Episode 1"</em> to extract the Series Name ("Stranger Things") and the Type ("TV Show").</li>
            <li><strong>Estimation:</strong> Total watch time is estimated based on industry averages (45min/episode, 105min/movie).</li>
        </ul>

        <h4 style="color: #FFF;">3. Visual Design</h4>
        <ul style="color: #CCC;">
            <li><strong>Palette:</strong> Used the Netflix Brand Colors (#E50914 Red, #141414 Black) for immersion.</li>
            <li><strong>Insights:</strong> Focused on <em>Binge-Watching</em> patterns and <em>Time Consumption</em>.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# Layout Plotly
netflix_layout = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#AAA', family="Montserrat"),
    margin=dict(t=30, l=10, r=10, b=10),
    colorway=['#E50914', '#F5F5F1', '#564d4d']
)

# --- 7. KPIS ---
total_hours = int(df_filtered['Duration_Mins'].sum() / 60)
items_count = len(df_filtered)
top_show = df_filtered[df_filtered['Type'] == 'TV Show']['Show_Name'].mode()[0] if not df_filtered[df_filtered['Type'] == 'TV Show'].empty else "N/A"
binge_days = df_filtered[df_filtered['Date'].duplicated(keep=False)]['Date'].nunique()

st.markdown("##### ❖ OVERVIEW")
c1, c2, c3, c4 = st.columns(4)
c1.metric("TOTAL WATCHED", f"{items_count}", "Items")
c2.metric("TIME LOST", f"{total_hours}h", "Estimated")
c3.metric("OBSESSION", top_show, "Most Watched")
c4.metric("BINGE DAYS", binge_days, "Multiple Eps/Day")

# --- 8. CHARTS ---
st.markdown("---")

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("##### ❖ WATCHING HABITS (Heatmap)")
    hm_data = df_filtered.groupby(['DayOfWeek', 'Month']).size().reset_index(name='Count')
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    fig_heat = px.density_heatmap(
        hm_data, x='Month', y='DayOfWeek', z='Count',
        category_orders={'DayOfWeek': days_order},
        color_continuous_scale=['#141414', '#B20710', '#E50914'],
        title=""
    )
    fig_heat.update_layout(**netflix_layout)
    st.plotly_chart(fig_heat, use_container_width=True)

with col2:
    st.markdown("##### ❖ CONTENT TYPE")
    type_counts = df_filtered['Type'].value_counts().reset_index()
    type_counts.columns = ['Type', 'Count']
    
    fig_pie = px.pie(
        type_counts, values='Count', names='Type',
        hole=0.6,
        color_discrete_sequence=['#E50914', '#333333']
    )
    fig_pie.update_traces(textposition='outside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=False, **netflix_layout)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- BINGE ANALYSIS ---
st.markdown("---")
st.markdown("##### ❖ BINGE-WATCHING ANALYSIS")

col_b1, col_b2 = st.columns(2)

with col_b1:
    st.markdown("**Cumulative Time Spent (The 'Slope' of Addiction)**")
    df_sorted = df_filtered.sort_values('Date')
    df_sorted['Cumul_Hours'] = df_sorted['Duration_Mins'].cumsum() / 60
    
    fig_area = px.area(
        df_sorted, x='Date', y='Cumul_Hours',
        color_discrete_sequence=['#E50914']
    )
    fig_area.update_traces(fillcolor='rgba(229, 9, 20, 0.2)')
    fig_area.update_layout(yaxis_title="Hours", **netflix_layout)
    st.plotly_chart(fig_area, use_container_width=True)

with col_b2:
    st.markdown("**Top 10 Series (Volume)**")
    top_shows = df_filtered[df_filtered['Type'] == 'TV Show']['Show_Name'].value_counts().head(10).reset_index()
    top_shows.columns = ['Series', 'Episodes']
    
    fig_bar = px.bar(
        top_shows, x='Episodes', y='Series',
        orientation='h',
        color='Episodes',
        color_continuous_scale=['#333', '#E50914']
    )
    fig_bar.update_layout(**netflix_layout, yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_bar, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #555; font-size: 0.8rem; margin-top: 50px;">
    NETFLIX PERSONAL ANALYTICS | PROJECT 2024
</div>
""", unsafe_allow_html=True)
