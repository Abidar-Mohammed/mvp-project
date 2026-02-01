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

# --- 2. CSS "ULTIMATE" (ANIMATIONS & STYLE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap');

    /* ANIMATION D'ENTRÉE (Fade In + Slide Up) */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translate3d(0, 40px, 0); }
        to { opacity: 1; transform: translate3d(0, 0, 0); }
    }

    /* APPLICATION DE L'ANIMATION AU CONTENU PRINCIPAL */
    .main .block-container {
        animation-duration: 0.8s;
        animation-fill-mode: both;
        animation-name: fadeInUp;
        
        /* Glassmorphism parfait */
        background-color: rgba(255, 255, 255, 0.92); /* Blanc à 92% */
        backdrop-filter: blur(10px); /* Flou d'arrière-plan */
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin-top: 2rem;
        margin-bottom: 3rem;
        max-width: 95% !important;
    }

    /* IMAGE DE FOND (Fixe) */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?q=80&w=2670&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    /* TYPOGRAPHIE */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: #2D2420;
        font-weight: 700;
    }
    p, span, div {
        font-family: 'Lato', sans-serif;
        color: #4A4A4A;
    }

    /* HEADER */
    .header-title {
        text-align: center;
        border-bottom: 1px solid #E0E0E0;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }
    .header-title h1 {
        font-size: 3.5rem;
        margin-bottom: 5px;
        text-shadow: 0px 2px 2px rgba(0,0,0,0.1);
    }
    .header-title p {
        font-size: 1.2rem;
        font-style: italic;
        color: #8D6E63;
    }

    /* METRICS STYLISÉES */
    div[data-testid="metric-container"] {
        background: white;
        border-radius: 12px;
        padding: 15px;
        border: 1px solid #F0F0F0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        transition: transform 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        border-color: #D7CCC8;
    }

    /* ONGLETS MODERNES */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        border-bottom: 1px solid #EEE;
        padding-bottom: 5px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: transparent;
        border: none;
        font-size: 16px;
        color: #9E9E9E;
        transition: color 0.3s;
    }
    .stTabs [aria-selected="true"] {
        color: #3E2723 !important;
        font-weight: bold;
        border-bottom: 3px solid #3E2723 !important;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #FDFBF7; /* Crème très léger */
        border-right: 1px solid #EFEBE9;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT DES DONNÉES (AVEC GÉNÉRATEUR AUTOMATIQUE) ---
@st.cache_data
def load_data():
    file_name = "my_coffee_life.csv"
    
    # 1. Chercher le fichier
    path = None
    possible_paths = [file_name, os.path.join(os.path.dirname(__file__), file_name)]
    
    for p in possible_paths:
        if os.path.exists(p):
            path = p
            break
            
    # 2. Si pas de fichier, on en génère un "Live" (plus besoin de generate_data.py séparé)
    if not path:
        # Génération silencieuse de données de secours
        dates = pd.date_range(start="2024-01-01", periods=150)
        df = pd.DataFrame({
            'datetime': dates,
            'location': np.random.choice(['Home', 'Work', 'Coffee Shop'], 150),
            'social_context': np.random.choice(['Alone', 'Friends', 'Colleagues'], 150),
            'activity': np.random.choice(['Working', 'Reading', 'Socializing'], 150),
            'weather': np.random.choice(['Sunny', 'Rainy', 'Cloudy'], 150),
            'coffee_type': np.random.choice(['Espresso', 'Latte', 'Cappuccino'], 150),
            'price': np.random.uniform(0, 6, 150),
            'caffeine_mg': np.random.randint(50, 150, 150),
            'mood_before': np.random.randint(3, 8, 150),
            'mood_after': np.random.randint(5, 10, 150),
            'sleep_hours_next_night': np.random.uniform(5, 9, 150)
        })
        st.toast("⚠️ Données de démonstration générées (CSV absent)", icon="ℹ️")
    else:
        df = pd.read_csv(path)
        df['datetime'] = pd.to_datetime(df['datetime'])

    # 3. Nettoyage et Enrichissement
    # Sécurité : créer les colonnes manquantes si besoin
    required_cols = ['weather', 'social_context', 'location', 'activity', 'stress_level', 'pleasure_score']
    for col in required_cols:
        if col not in df.columns:
            df[col] = "Unknown" if col in ['weather', 'social_context', 'location', 'activity'] else 0

    df['Hour'] = df['datetime'].dt.hour
    df['DayOfWeek'] = df['datetime'].dt.day_name()
    df['Month'] = df['datetime'].dt.to_period('M').astype(str)
    df['Mood_Boost'] = df['mood_after'] - df['mood_before']
    
    return df

df = load_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### ⚙️ Dashboard Controls")
    
    if not df.empty:
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input("📅 Période", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        social_opts = list(df['social_context'].unique())
        social_filter = st.multiselect("👥 Social", social_opts, default=social_opts)

    st.markdown("---")
    st.image("https://images.unsplash.com/photo-1511920170033-f8396924c348?q=80&w=300&auto=format&fit=crop", caption="My Daily Fuel", use_container_width=True)

# Filtres
if not df.empty:
    mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])
    if social_filter:
        mask = mask & (df['social_context'].isin(social_filter))
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. CONTENU PRINCIPAL ---

# Header avec animation CSS implicite
st.markdown("""
<div class="header-title">
    <h1>The Quantified Coffee</h1>
    <p>Habitudes, Santé & Finances : Une année de données personnelles.</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.error("Aucune donnée disponible. Essayez d'élargir les filtres.")
    st.stop()

# Onglets
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview", "🧬 Style de Vie", "🧪 Impact & Santé", "📝 Méthodologie"
])

# --- TAB 1: OVERVIEW ---
with tab1:
    # Métriques avec colonnes
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cafés", len(df_filtered), delta="Cumul")
    c2.metric("Dépenses", f"${df_filtered['price'].sum():.0f}", delta="Estimé")
    c3.metric("Caféine", f"{df_filtered['caffeine_mg'].sum()/1000:.1f} g", delta="Total")
    c4.metric("Gain Humeur", f"+{df_filtered['Mood_Boost'].mean():.1f}", delta="Moyen")
    
    st.markdown("---")
    
    col_L, col_R = st.columns([2, 1])
    
    with col_L:
        st.subheader("🕰️ Carte de Chaleur (Habitudes)")
        hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            hm_data, x='Hour', y='DayOfWeek', z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale='Oranges',
            template='simple_white',
            title="Intensité Hebdomadaire"
        )
        fig_heat.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_R:
        st.subheader("☕ Répartition")
        fig_pie = px.pie(
            df_filtered, 
            values='price', 
            names='coffee_type', 
            hole=0.5, # Effet Donut
            color_discrete_sequence=px.colors.sequential.Brwnyl,
            template='simple_white',
            title="Parts de Budget"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: LIFESTYLE ---
with tab2:
    st.subheader("🌍 Analyse du Contexte")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Où, Quoi et Comment ?**")
        # Sunburst (Toujours impressionnant)
        if df_filtered['location'].nunique() > 0:
            fig_sun = px.sunburst(
                df_filtered, 
                path=['location', 'activity', 'coffee_type'], 
                values='price',
                color='location',
                color_discrete_sequence=px.colors.qualitative.Antique
            )
            fig_sun.update_layout(height=450, margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.info("Données insuffisantes pour le graphique hiérarchique.")
            
    with col2:
        st.markdown("**Influence de la Météo**")
        if df_filtered['weather'].nunique() > 1:
            weather_counts = df_filtered.groupby(['weather', 'coffee_type']).size().reset_index(name='Count')
            fig_bar = px.bar(
                weather_counts, x='Count', y='weather', color='coffee_type',
                orientation='h',
                color_discrete_sequence=px.colors.sequential.RdBu,
                template='simple_white'
            )
            fig_bar.update_layout(yaxis_title=None, plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Pas de données météo variées.")

# --- TAB 3: SANTÉ & IMPACT ---
with tab3:
    st.subheader("🧬 Corrélations Biologiques")
    st.caption("Preuve par les données de l'impact de mes choix.")
    
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
        # Zone Rouge (Transition visuelle)
        fig_sleep.add_vrect(
            x0=16, x1=24, 
            fillcolor="red", opacity=0.08, 
            annotation_text="Zone Critique (>16h)", annotation_position="top left"
        )
        fig_sleep.update_layout(plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_sleep, use_container_width=True)
        
    with col_bio2:
        st.markdown("#### 🙂 Quel café me rend heureux ?")
        fig_box = px.box(
            df_filtered, x='coffee_type', y='Mood_Boost',
            color='coffee_type',
            template='simple_white',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_box.update_layout(showlegend=False, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_box, use_container_width=True)

    # Radar Chart
    st.markdown("---")
    st.subheader("🕸️ Profil Multidimensionnel")
    
    # Préparation des données Radar
    cols_radar = ['price', 'caffeine_mg', 'stress_level', 'pleasure_score']
    # Sécurité: conversion en numérique
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
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)), 
        height=450,
        template="plotly_white"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# --- TAB 4: METHODOLOGIE ---
with tab4:
    st.markdown("""
    ### 📝 Méthodologie du Projet
    
    **1. Données Personnelles (Quantified Self)**
    Ce dashboard repose sur le fichier `my_coffee_life.csv` (généré pour simuler 1 an de vie réelle).
    J'ai voulu répondre à la question : *"Est-ce que le café améliore ma productivité ou détruit mon sommeil ?"*.
    
    **2. Design "Glassmorphism"**
    * J'ai utilisé une image de fond fixe pour l'ambiance, mais recouverte d'un calque blanc à **92% d'opacité** et d'un flou (`backdrop-filter`).
    * Résultat : Le texte est parfaitement lisible, mais l'interface a de la profondeur.
    
    **3. Animations (CSS)**
    * Une animation `fadeInUp` a été ajoutée en CSS pur pour que le dashboard apparaisse doucement à l'ouverture, donnant une sensation "Premium".
    """)
    
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger les Données (CSV)", data=csv, file_name="my_quantified_data.csv", mime="text/csv")
