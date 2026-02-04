import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Netflix Unwrapped",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. GESTION DE L'ÉTAT (BOUTON METHODO) ---
if 'show_methodology' not in st.session_state:
    st.session_state.show_methodology = False

def toggle_methodology():
    st.session_state.show_methodology = not st.session_state.show_methodology

# --- 3. CSS NETFLIX DARK MODE ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@300;400;600&display=swap');

    /* FOND & COULEURS GLOBALES */
    .stApp {
        background-color: #141414;
        color: #E5E5E5;
    }

    /* TITRES (Police Netflix-like) */
    h1, h2, h3 {
        font-family: 'Bebas Neue', sans-serif;
        color: #E50914 !important; /* ROUGE NETFLIX */
        letter-spacing: 1.5px;
    }
    
    p, div, label, li, span {
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
        font-size: 0.85rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFF !important;
        font-family: 'Bebas Neue', sans-serif;
        font-size: 3rem;
    }

    /* BOUTON STYLISÉ */
    div.stButton > button {
        background-color: transparent;
        border: 1px solid #E50914;
        color: #E50914;
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.2rem;
        transition: 0.3s;
        border-radius: 2px;
    }
    div.stButton > button:hover {
        background-color: #E50914;
        color: #FFF;
        border-color: #E50914;
    }

    /* GRAPHIQUES PLOTLY TRANSPARENTS */
    .stPlotlyChart {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. CHARGEMENT ET INTELLIGENCE DES DONNÉES ---
@st.cache_data
def load_data():
    # ---------------------------------------------------------
    # 👇 REMPLACE CECI PAR TON LIEN GITHUB RAW SI BESOIN 👇
    GITHUB_URL = "https://github.com/Abidar-Mohammed/mvp-project/main/NetflixHistory.csv"
    LOCAL_FILE = "NetflixHistory.csv"
    # ---------------------------------------------------------
    
    df = None
    
    # 1. Essai depuis GitHub
    try:
        df = pd.read_csv(GITHUB_URL)
    except:
        pass # Si ça rate, on tente le local
        
    # 2. Essai Local
    if df is None:
        if os.path.exists(LOCAL_FILE):
            df = pd.read_csv(LOCAL_FILE)
        else:
            # Création d'un dataframe vide pour éviter le crash
            return pd.DataFrame()

    # Conversion Date
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
    
    # --- FEATURE ENGINEERING (ANALYSE DES TITRES) ---
    def parse_netflix_title(title):
        if not isinstance(title, str): return pd.Series(["Unknown", "Unknown", 0])
        
        # Détection Séries vs Films basés sur les mots-clés
        keywords = ['Saison', 'Season', 'Episode', 'Chapitre', 'Partie']
        is_series = any(k in title for k in keywords) or (title.count(':') >= 2)
        
        if is_series:
            c_type = "TV Show"
            # "Stranger Things: Saison 4: Épisode 1" -> "Stranger Things"
            show_name = title.split(":")[0].strip()
            duration = 50 # Estimation moyenne
        else:
            c_type = "Movie"
            show_name = title
            duration = 105 # Estimation moyenne film
            
        return pd.Series([c_type, show_name, duration])

    df[['Type', 'Show_Name', 'Duration_Mins']] = df['Title'].apply(parse_netflix_title)
    
    # Enrichissement Temporel
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['Year'] = df['Date'].dt.year
    
    return df

df = load_data()

# --- 5. SIDEBAR (FILTRES) ---
with st.sidebar:
    st.markdown("### 🍿 FILTERS")
    
    if not df.empty:
        # Filtre Date
        min_d = df['Date'].min().date()
        max_d = df['Date'].max().date()
        date_range = st.date_input("Period", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        # Filtre Série
        all_shows = sorted(df[df['Type'] == 'TV Show']['Show_Name'].unique())
        selected_shows = st.multiselect("Filter by Series", all_shows)
    
    st.markdown("---")
    st.caption("Visual Analytics Project 2024")

# Application des filtres
if not df.empty:
    mask = (df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])
    if selected_shows:
        mask = mask & (df['Show_Name'].isin(selected_shows))
    df_filtered = df[mask]
else:
    st.error("Data not found. Please check your CSV file or GitHub URL.")
    st.stop()

# --- 6. HEADER PRINCIPAL ---
st.markdown("""
<div style="text-align: center; margin-bottom: 30px;">
    <h1 style="font-size: 5rem; margin-bottom: 0;">NETFLIX UNWRAPPED</h1>
    <p style="text-transform: uppercase; letter-spacing: 3px; font-size: 1.2rem;">My Personal Streaming History Analysis</p>
</div>
""", unsafe_allow_html=True)

# --- 7. BOUTON METHODOLOGIE (CORRIGÉ) ---
col_m1, col_m2, col_m3 = st.columns([1, 2, 1])
btn_text = "✕ CLOSE REPORT" if st.session_state.show_methodology else "ℹ️ VIEW PROJECT METHODOLOGY"

with col_m2:
    st.button(btn_text, on_click=toggle_methodology, use_container_width=True)

if st.session_state.show_methodology:
    # Utilisation de HTML pur sans indentation pour éviter les blocs de code
    st.markdown("""
<div style="background: #181818; padding: 30px; border-radius: 10px; border: 1px solid #333; margin-bottom: 40px;">
<h3 style="color: #E50914; text-align: center; font-family: 'Bebas Neue'; letter-spacing: 1px;">PROJECT METHODOLOGY</h3>
<h4 style="color: #FFF; margin-bottom: 5px;">1. Data Collection & Ethics</h4>
<ul style="color: #B3B3B3; font-family: 'Montserrat'; font-size: 0.9rem; line-height: 1.6;">
<li><strong>Source:</strong> Personal Netflix Viewing Activity (<code>NetflixHistory.csv</code>).</li>
<li><strong>Privacy:</strong> Data was anonymized. Only titles and dates are used. No location or IP data.</li>
</ul>
<br>
<h4 style="color: #FFF; margin-bottom: 5px;">2. Data Engineering</h4>
<ul style="color: #B3B3B3; font-family: 'Montserrat'; font-size: 0.9rem; line-height: 1.6;">
<li><strong>Parsing Logic:</strong> Developed a Python algorithm to distinguish Movies from TV Shows by detecting keywords like "Season" or "Episode" in the raw title strings.</li>
<li><strong>Imputation:</strong> Since Netflix doesn't provide watch duration in the export, I estimated time based on content type (TV Show ≈ 50min, Movie ≈ 105min) to compute "Time Lost".</li>
</ul>
<br>
<h4 style="color: #FFF; margin-bottom: 5px;">3. Visual Encodings</h4>
<ul style="color: #B3B3B3; font-family: 'Montserrat'; font-size: 0.9rem; line-height: 1.6;">
<li><strong>Color Strategy:</strong> Used the official Netflix Brand Palette (Red #E50914 on Black #141414) for thematic immersion.</li>
<li><strong>Heatmap:</strong> Used to reveal "Binge-Watching" patterns (high density on weekends vs weekdays).</li>
</ul>
</div>
""", unsafe_allow_html=True)

# --- 8. KPIs (INDICATEURS CLÉS) ---
total_mins = df_filtered['Duration_Mins'].sum()
total_hours = int(total_mins / 60)
nb_items = len(df_filtered)
# Série la plus regardée
top_show_name = "None"
if not df_filtered[df_filtered['Type']=='TV Show'].empty:
    top_show_name = df_filtered[df_filtered['Type']=='TV Show']['Show_Name'].mode()[0]

st.markdown("##### ❖ OVERVIEW")
k1, k2, k3, k4 = st.columns(4)
k1.metric("ITEMS WATCHED", nb_items)
k2.metric("HOURS STREAMED", f"{total_hours}h")
k3.metric("TOP OBSESSION", top_show_name)
k4.metric("DATA RANGE", f"{len(df_filtered['Date'].unique())} Days")

st.markdown("---")

# Layout Plotly Netflix
netflix_theme = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#B3B3B3', family="Montserrat"),
    margin=dict(t=40, l=10, r=10, b=10),
    colorway=['#E50914', '#B20710', '#FFFFFF', '#555555']
)

# --- 9. ANALYSE TEMPORELLE (HEATMAP) ---
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("##### ❖ WHEN DO I WATCH? (Heatmap)")
    hm_data = df_filtered.groupby(['DayOfWeek', 'Month']).size().reset_index(name='Count')
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    fig_heat = px.density_heatmap(
        hm_data, x='Month', y='DayOfWeek', z='Count',
        category_orders={'DayOfWeek': days_order},
        color_continuous_scale=['#101010', '#800000', '#E50914'],
        title="Streaming Intensity"
    )
    fig_heat.update_layout(**netflix_theme)
    fig_heat.update_coloraxes(colorbar_bgcolor="rgba(0,0,0,0)", colorbar_title="")
    st.plotly_chart(fig_heat, use_container_width=True)

with col2:
    st.markdown("##### ❖ MOVIES VS SERIES")
    type_counts = df_filtered['Type'].value_counts().reset_index()
    type_counts.columns = ['Type', 'Count']
    
    fig_pie = px.pie(
        type_counts, values='Count', names='Type',
        hole=0.6,
        color_discrete_sequence=['#E50914', '#333']
    )
    fig_pie.update_traces(textposition='outside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=False, **netflix_theme)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- 10. BINGE WATCHING & TOP SERIES ---
st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.markdown("##### ❖ TOP 10 SERIES (Volume)")
    # Filtrer uniquement les séries
    tv_data = df_filtered[df_filtered['Type'] == 'TV Show']
    top_series = tv_data['Show_Name'].value_counts().head(10).reset_index()
    top_series.columns = ['Series', 'Episodes']
    
    fig_bar = px.bar(
        top_series, x='Episodes', y='Series',
        orientation='h',
        color='Episodes',
        color_continuous_scale=['#333', '#E50914']
    )
    fig_bar.update_layout(yaxis=dict(autorange="reversed"), **netflix_theme)
    st.plotly_chart(fig_bar, use_container_width=True)

with col4:
    st.markdown("##### ❖ ADDICTION CURVE (Cumulative Hours)")
    # Tri par date pour le cumul
    df_sorted = df_filtered.sort_values('Date')
    df_sorted['Cumul_Hours'] = df_sorted['Duration_Mins'].cumsum() / 60
    
    fig_area = px.area(
        df_sorted, x='Date', y='Cumul_Hours',
        color_discrete_sequence=['#E50914']
    )
    fig_area.update_traces(fillcolor='rgba(229, 9, 20, 0.2)')
    fig_area.update_layout(yaxis_title="Total Hours", **netflix_theme)
    st.plotly_chart(fig_area, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #555; font-size: 0.8rem; margin-top: 30px;">
    NETFLIX PERSONAL ANALYTICS | 2024 PROJECT
</div>
""", unsafe_allow_html=True)

