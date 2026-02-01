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

# --- 2. CSS AVANCÉ (Lisibilité Maximale) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap');

    /* 1. IMAGE DE FOND (Fixe et couvrant tout l'écran) */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1497935586351-b67a49e012bf?q=80&w=2671&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    /* 2. LE CONTENEUR PRINCIPAL (La "Feuille de papier" par-dessus l'image) */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.95); /* Blanc quasi opaque pour la lecture */
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.3); /* Ombre portée pour détacher du fond */
        margin-top: 2rem;
        margin-bottom: 2rem;
        max-width: 95% !important;
    }

    /* 3. TYPOGRAPHIE (Noir profond pour contraste) */
    h1, h2, h3, h4, h5 {
        font-family: 'Playfair Display', serif;
        color: #2D2420 !important; /* Marron très foncé presque noir */
        font-weight: 700;
    }
    
    p, div, label, span {
        font-family: 'Lato', sans-serif;
        color: #3E3E3E !important; /* Gris foncé */
    }

    /* 4. HEADER STYLISÉ */
    .header-journal {
        text-align: center;
        padding-bottom: 25px;
        border-bottom: 3px double #D7CCC8;
        margin-bottom: 35px;
    }
    .header-journal h1 {
        font-size: 3.5rem;
        margin-bottom: 5px;
        letter-spacing: 1px;
    }
    .header-journal p {
        font-size: 1.2rem;
        font-style: italic;
        color: #8D6E63 !important;
    }

    /* 5. CARTES KPI (Metrics) */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-left: 5px solid #6D4C41;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    div[data-testid="metric-container"] label {
        color: #757575 !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #3E2723 !important;
        font-weight: bold;
    }

    /* 6. GRAPHIQUES ET SIDEBAR */
    .stPlotlyChart {
        background-color: #FFFFFF;
        border-radius: 10px;
        border: 1px solid #F0F0F0;
        padding: 10px;
    }
    section[data-testid="stSidebar"] {
        background-color: #F9F9F9;
        border-right: 1px solid #E0E0E0;
    }
    
    /* 7. ONGLETS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #DDD;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border: none;
        color: #757575;
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
    
    # Recherche du fichier (Local ou Cloud)
    path = None
    possible_paths = [file_name, os.path.join(os.path.dirname(__file__), file_name)]
    
    for p in possible_paths:
        if os.path.exists(p):
            path = p
            break
    
    # Génération de données de secours si fichier absent (Anti-Crash)
    if not path:
        st.warning("⚠️ Fichier CSV introuvable. Données de démonstration chargées.")
        dates = pd.date_range(start="2024-01-01", periods=100)
        df = pd.DataFrame({
            'datetime': dates,
            'location': np.random.choice(['Home', 'Work'], 100),
            'social_context': np.random.choice(['Alone', 'Friends'], 100),
            'activity': np.random.choice(['Working', 'Reading'], 100),
            'weather': np.random.choice(['Sunny', 'Rainy'], 100), # Colonne importante pour le bug
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

    # Vérification que la colonne 'weather' existe (Correction du Bug)
    if 'weather' not in df.columns:
        df['weather'] = 'Unknown' # Valeur par défaut si absente

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
        
        # Gestion des filtres si les colonnes existent
        if 'social_context' in df.columns:
            social_filter = st.multiselect("👥 Contexte Social", df['social_context'].unique(), default=df['social_context'].unique())
        else:
            social_filter = []
            
    st.markdown("---")
    st.caption("Visual Analytics Project 2024")

# Filtrage
if not df.empty:
    mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])
    if 'social_context' in df.columns and social_filter:
        mask = mask & (df['social_context'].isin(social_filter))
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. HEADER ---
st.markdown("""
<div class="header-journal">
    <h1>The Quantified Coffee</h1>
    <p>Une analyse personnelle de l'impact de la caféine sur mon quotidien.</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.error("Aucune donnée disponible avec ces filtres.")
    st.stop()

# --- 6. NAVIGATION ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Vue d'Ensemble", 
    "🧬 Style de Vie", 
    "🧪 Impact & Santé", 
    "📝 Méthodologie"
])

# --- TAB 1: OVERVIEW ---
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cafés", len(df_filtered))
    c2.metric("Budget Estimé", f"${df_filtered['price'].sum():.0f}")
    c3.metric("Caféine Totale", f"{df_filtered['caffeine_mg'].sum()/1000:.1f} g")
    c4.metric("Gain Humeur Moyen", f"+{df_filtered['Mood_Boost'].mean():.1f} pts")
    
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🕰️ Mes Habitudes Temporelles")
        hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            hm_data, x='Hour', y='DayOfWeek', z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale='Oranges',
            template='simple_white'
        )
        fig_heat.update_layout(xaxis_title="Heure", yaxis_title="Jour")
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_right:
        st.subheader("☕ Préférences")
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

# --- TAB 2: LIFESTYLE (Correction Bug Weather) ---
with tab2:
    st.subheader("🌍 Contexte de consommation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Hiérarchie des Lieux**")
        if all(col in df_filtered.columns for col in ['location', 'activity', 'coffee_type']):
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
            st.info("Données de lieu incomplètes.")
        
    with col2:
        st.markdown("**Influence de la Météo**")
        # --- CORRECTION DU BUG ---
        if 'weather' in df_filtered.columns:
            # On vérifie d'abord s'il y a des données météo
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
            st.warning("La colonne 'weather' n'est pas disponible dans le fichier CSV.")

# --- TAB 3: IMPACT & SANTÉ ---
with tab3:
    st.subheader("🧬 Analyse Quantified Self")
    
    col_bio1, col_bio2 = st.columns(2)
    
    with col_bio1:
        st.markdown("#### 💤 Heure vs Sommeil")
        fig_sleep = px.scatter(
            df_filtered, x='Hour', y='sleep_hours_next_night',
            size='caffeine_mg', color='location',
            template='simple_white',
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={'sleep_hours_next_night': 'Heures de Sommeil'}
        )
        fig_sleep.add_vrect(x0=16, x1=24, fillcolor="red", opacity=0.1, annotation_text="Zone Critique")
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

    # Radar Chart
    st.markdown("---")
    st.subheader("🕸️ Profil Multidimensionnel")
    
    if 'location' in df_filtered.columns:
        # On aggrège seulement sur les colonnes numériques existantes
        cols_to_mean = ['price', 'caffeine_mg']
        if 'stress_level' in df_filtered.columns: cols_to_mean.append('stress_level')
        if 'pleasure_score' in df_filtered.columns: cols_to_mean.append('pleasure_score')
        
        radar_data = df_filtered.groupby('location')[cols_to_mean].mean().reset_index()
        
        # Normalisation
        for c in cols_to_mean:
            radar_data[c] = radar_data[c] / radar_data[c].max()
            
        fig_radar = go.Figure()
        
        for i, row in radar_data.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[row[c] for c in cols_to_mean],
                theta=cols_to_mean, fill='toself', name=row['location']
            ))
        
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), height=450)
        st.plotly_chart(fig_radar, use_container_width=True)

# --- TAB 4: MÉTHODOLOGIE ---
with tab4:
    st.markdown("""
    ### 📝 Méthodologie
    
    **1. Le Jeu de Données (Quantified Self)**
    Ce dashboard utilise un jeu de données personnel généré pour simuler une année de consommation réaliste. 
    L'objectif est de dépasser la simple analyse financière pour comprendre l'impact physiologique.
    
    **2. Choix de Design (Glassmorphism)**
    * **Lisibilité :** Un fond blanc semi-transparent (95% opacité) a été appliqué sur le contenu pour garantir que les textes et graphiques soient parfaitement lisibles, tout en laissant deviner l'ambiance "café" en arrière-plan.
    * **Typographie :** Utilisation de 'Playfair Display' pour les titres afin de donner un aspect éditorial/journal.
    
    **3. Visualisations Clés**
    * **Scatter Plot (Onglet 3) :** Démontre la corrélation négative entre caféine tardive et sommeil.
    * **Heatmap (Onglet 1) :** Visualise les routines hebdomadaires.
    """)
    
    # Bouton de téléchargement
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger les Données (CSV)", data=csv, file_name="my_coffee_data.csv", mime="text/csv")
