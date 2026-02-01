import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="My Coffee Journal",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS "CLEAN & READABLE" ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap');

    /* 1. IMAGE DE FOND AVEC FILTRE BLANC PUISSANT */
    /* Le linear-gradient ajoute un voile blanc à 90% sur l'image */
    .stApp {
        background-image: linear-gradient(rgba(255,255,255,0.90), rgba(255,255,255,0.90)), 
                          url("https://images.unsplash.com/photo-1497935586351-b67a49e012bf?q=80&w=2671&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    /* 2. CONTENEUR PRINCIPAL */
    /* Fond blanc pur pour une lisibilité maximale des graphiques */
    .main .block-container {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.05); /* Ombre légère */
        margin-top: 1rem;
        margin-bottom: 2rem;
        max-width: 95% !important;
    }

    /* 3. TYPOGRAPHIE */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: #2D2420; /* Noir Café */
    }
    p, div, label, span {
        font-family: 'Lato', sans-serif;
        color: #424242; /* Gris foncé lisible */
    }

    /* 4. HEADER */
    .header-journal {
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 2px solid #EEE;
        margin-bottom: 30px;
    }
    .header-journal h1 {
        font-size: 3rem;
        margin-bottom: 10px;
    }

    /* 5. METRICS (KPIs) */
    div[data-testid="metric-container"] {
        background-color: #FAFAFA;
        border: 1px solid #EEE;
        border-left: 4px solid #8D6E63;
        border-radius: 8px;
        padding: 15px;
        box-shadow: none;
    }

    /* 6. GRAPHIQUES */
    .stPlotlyChart {
        border: 1px solid #F0F0F0;
        border-radius: 8px;
        padding: 5px;
    }
    
    /* 7. NAVIGATION ONGLETS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid #DDD;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        border: none;
        color: #757575;
        font-weight: 400;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent !important;
        color: #3E2723 !important;
        font-weight: bold;
        border-bottom: 3px solid #3E2723 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT ROBUSTE DES DONNÉES ---
@st.cache_data
def load_data():
    file_name = "my_coffee_life.csv"
    
    # Recherche du fichier
    path = None
    possible_paths = [file_name, os.path.join(os.path.dirname(__file__), file_name)]
    
    for p in possible_paths:
        if os.path.exists(p):
            path = p
            break
    
    # Données de secours (Anti-Crash)
    if not path:
        st.warning("⚠️ Mode Démo : Fichier CSV introuvable (utilisez generate_data.py).")
        dates = pd.date_range(start="2024-01-01", periods=100)
        df = pd.DataFrame({
            'datetime': dates,
            'location': np.random.choice(['Home', 'Work'], 100),
            'social_context': np.random.choice(['Alone', 'Friends'], 100),
            'activity': np.random.choice(['Working', 'Reading'], 100),
            'weather': np.random.choice(['Sunny', 'Rainy'], 100),
            'coffee_type': np.random.choice(['Espresso', 'Latte'], 100),
            'price': np.random.uniform(2, 5, 100),
            'caffeine_mg': np.random.randint(50, 150, 100),
            'mood_before': np.random.randint(3, 8, 100),
            'mood_after': np.random.randint(5, 10, 100),
            'sleep_hours_next_night': np.random.uniform(5, 9, 100)
        })
    else:
        df = pd.read_csv(path)
        df['datetime'] = pd.to_datetime(df['datetime'])

    # Standardisation des colonnes manquantes (Important !)
    expected_cols = ['weather', 'social_context', 'location', 'activity', 'stress_level', 'pleasure_score']
    for col in expected_cols:
        if col not in df.columns:
            df[col] = "Unknown" if col in ['weather', 'social_context', 'location', 'activity'] else 0

    # Enrichissement
    df['Hour'] = df['datetime'].dt.hour
    df['DayOfWeek'] = df['datetime'].dt.day_name()
    df['Month'] = df['datetime'].dt.to_period('M').astype(str)
    df['Date_Only'] = df['datetime'].dt.date
    df['Mood_Boost'] = df['mood_after'] - df['mood_before']
    
    return df

df = load_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Filtres")
    
    if not df.empty:
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input("📅 Période", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        # Filtre Social
        social_opts = df['social_context'].unique()
        social_filter = st.multiselect("👥 Social", social_opts, default=social_opts)

    st.markdown("---")
    st.caption("Visual Analytics Project 2024")

# Filtrage
if not df.empty:
    mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])
    if social_filter:
        mask = mask & (df['social_context'].isin(social_filter))
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. HEADER ---
st.markdown("""
<div class="header-journal">
    <h1>The Quantified Coffee</h1>
    <p>Une exploration de données personnelles sur mes habitudes de consommation.</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.error("Aucune donnée disponible avec ces filtres.")
    st.stop()

# --- 6. NAVIGATION ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview", 
    "🧬 Style de Vie", 
    "🧪 Impact & Santé", 
    "📝 Méthodologie"
])

# --- TAB 1: OVERVIEW ---
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cafés", len(df_filtered))
    c2.metric("Dépenses", f"${df_filtered['price'].sum():.0f}")
    c3.metric("Caféine Totale", f"{df_filtered['caffeine_mg'].sum()/1000:.1f} g")
    c4.metric("Gain Humeur", f"+{df_filtered['Mood_Boost'].mean():.1f}")
    
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🕰️ Carte de Chaleur (Habitudes)")
        hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            hm_data, x='Hour', y='DayOfWeek', z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale='Oranges',
            template='simple_white'
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_right:
        st.subheader("☕ Types de Café")
        fig_pie = px.pie(
            df_filtered, 
            values='price', 
            names='coffee_type', 
            hole=0.5, 
            color_discrete_sequence=px.colors.sequential.Brwnyl,
            template='simple_white'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: LIFESTYLE ---
with tab2:
    st.subheader("🌍 Analyse du Contexte")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Hiérarchie : Lieu > Activité > Café**")
        if df_filtered['location'].nunique() > 0:
            fig_sun = px.sunburst(
                df_filtered, 
                path=['location', 'activity', 'coffee_type'], 
                values='price',
                color='location',
                color_discrete_sequence=px.colors.qualitative.Antique
            )
            fig_sun.update_layout(height=450)
            st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.info("Pas assez de données pour le graphique solaire.")
        
    with col2:
        st.markdown("**Influence de la Météo**")
        # Vérification et nettoyage pour éviter le crash
        if df_filtered['weather'].nunique() > 1:
            weather_counts = df_filtered.groupby(['weather', 'coffee_type']).size().reset_index(name='Count')
            fig_bar = px.bar(
                weather_counts, x='Count', y='weather', color='coffee_type',
                orientation='h',
                color_discrete_sequence=px.colors.sequential.RdBu,
                template='simple_white'
            )
            fig_bar.update_layout(yaxis_title=None)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Données météo insuffisantes pour l'affichage.")

# --- TAB 3: IMPACT & SANTÉ ---
with tab3:
    st.subheader("🧬 Analyse Biologique")
    
    col_bio1, col_bio2 = st.columns(2)
    
    with col_bio1:
        st.markdown("#### 💤 Heure vs Sommeil")
        fig_sleep = px.scatter(
            df_filtered, x='Hour', y='sleep_hours_next_night',
            size='caffeine_mg', color='location',
            template='simple_white',
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={'sleep_hours_next_night': 'Heures Sommeil'}
        )
        fig_sleep.add_vrect(x0=16, x1=24, fillcolor="red", opacity=0.05, annotation_text="Tardif")
        st.plotly_chart(fig_sleep, use_container_width=True)
        
    with col_bio2:
        st.markdown("#### 🙂 Boost d'Humeur")
        fig_box = px.box(
            df_filtered, x='coffee_type', y='Mood_Boost',
            color='coffee_type',
            template='simple_white',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

    # Radar
    st.markdown("---")
    st.subheader("🕸️ Comparaison des Lieux")
    
    # Agrégation sécurisée
    cols_radar = ['price', 'caffeine_mg', 'stress_level', 'pleasure_score']
    # On s'assure que les colonnes sont numériques
    for c in cols_radar:
        df_filtered[c] = pd.to_numeric(df_filtered[c], errors='coerce').fillna(0)
        
    radar_data = df_filtered.groupby('location')[cols_radar].mean().reset_index()
    
    # Normalisation
    for c in cols_radar:
        max_val = radar_data[c].max()
        if max_val > 0:
            radar_data[c] = radar_data[c] / max_val
            
    fig_radar = go.Figure()
    for i, row in radar_data.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row[c] for c in cols_radar],
            theta=cols_radar, fill='toself', name=row['location']
        ))
    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), height=450)
    st.plotly_chart(fig_radar, use_container_width=True)

# --- TAB 4: MÉTHODOLOGIE ---
with tab4:
    st.markdown("""
    ### 📝 Méthodologie
    
    **1. Données Personnelles**
    Ce projet repose sur un jeu de données généré (`my_coffee_life.csv`) simulant 1 an de consommation.
    Il intègre des facteurs contextuels (Météo, Social) et physiologiques (Stress, Sommeil) pour permettre une analyse de type "Quantified Self".
    
    **2. Design "Clarté avant tout"**
    * Une image de fond évoque le thème du café, mais un **filtre blanc à 90%** assure que les données restent parfaitement lisibles.
    * Les graphiques sont sur fond blanc pur pour maximiser le contraste.
    
    **3. Corrélations Clés**
    * Le *Scatter Plot* (Onglet 3) met en évidence l'impact négatif de la caféine après 16h sur le sommeil.
    * Le *Radar Chart* permet de comparer le rapport "Plaisir / Prix" selon les lieux (Maison vs Café).
    """)
    
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger CSV", data=csv, file_name="my_coffee_data.csv", mime="text/csv")
