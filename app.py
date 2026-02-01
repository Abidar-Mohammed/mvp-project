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

# --- 2. DESIGN PREMIUM (CSS AVEC IMAGE DE FOND) ---
st.markdown("""
<style>
    /* Import des polices Google */
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Lato:wght@300;400;700&display=swap');

    /* IMAGE DE FOND GLOBALE */
    .stApp {
        background-image: url("https://images.unsplash.com/photo-1447933601403-0c6688de566e?q=80&w=2561&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
    }

    /* FILTRE BLANC SEMI-TRANSPARENT SUR LE CONTENU */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.92);
        padding: 3rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        margin-top: 2rem;
        margin-bottom: 2rem;
        max-width: 95% !important;
    }

    /* TYPOGRAPHIE */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: #3E2723;
    }
    p, div, label {
        font-family: 'Lato', sans-serif;
        color: #4E342E;
    }

    /* HEADER STYLE JOURNAL */
    .header-journal {
        text-align: center;
        padding-bottom: 20px;
        border-bottom: 2px solid #D7CCC8;
        margin-bottom: 30px;
    }
    .header-journal h1 {
        font-size: 3.5rem;
        margin-bottom: 0;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    .header-journal p {
        font-size: 1.2rem;
        font-style: italic;
        color: #8D6E63;
    }

    /* CARTES KPI STYLISÉES */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #FFF8E1 0%, #FFFFFF 100%);
        border: 1px solid #EFEBE9;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        transition: transform 0.2s;
    }
    div[data-testid="metric-container"]:hover {
        transform: scale(1.02);
        border-color: #A1887F;
    }

    /* GRAPHIQUES PLOTLY */
    .stPlotlyChart {
        background-color: transparent;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #F5F5F5;
        border-right: 1px solid #ddd;
    }
    
    /* ONGLETS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background-color: #FFFFFF;
        border-radius: 10px 10px 0 0;
        border: 1px solid #ddd;
        border-bottom: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3E2723 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    file_name = "my_coffee_life.csv"
    
    # Recherche robuste du fichier
    path = None
    possible_paths = [file_name, os.path.join(os.path.dirname(__file__), file_name)]
    
    for p in possible_paths:
        if os.path.exists(p):
            path = p
            break
    
    if path:
        df = pd.read_csv(path)
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Enrichissement
        df['Hour'] = df['datetime'].dt.hour
        df['DayOfWeek'] = df['datetime'].dt.day_name()
        df['Month'] = df['datetime'].dt.to_period('M').astype(str)
        df['Date_Only'] = df['datetime'].dt.date
        df['Mood_Boost'] = df['mood_after'] - df['mood_before']
        
        return df
    else:
        st.error(f"⚠️ Fichier '{file_name}' introuvable. Veuillez lancer 'generate_data.py'.")
        return pd.DataFrame()

df = load_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h2 style='text-align: center;'>☕ My Settings</h2>", unsafe_allow_html=True)
    st.markdown("---")
    
    if not df.empty:
        # Filtres
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input("📅 Période", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        social_filter = st.multiselect("👥 Social Context", df['social_context'].unique(), default=df['social_context'].unique())
        
        st.markdown("---")
        st.caption("Dashboard personnel - Visual Analytics Project 2024")

if not df.empty:
    mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1]) & (df['social_context'].isin(social_filter))
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. HEADER ---
st.markdown("""
<div class="header-journal">
    <h1>The Quantified Coffee</h1>
    <p>Une exploration personnelle de mes habitudes, de ma santé et de mon budget.</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("Aucune donnée disponible avec ces filtres.")
    st.stop()

# --- 6. NAVIGATION ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview & Budget", 
    "🧬 Style de Vie", 
    "🧪 Impact & Santé", 
    "📝 Méthodologie"
])

# --- TAB 1: OVERVIEW ---
with tab1:
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cafés", len(df_filtered))
    c2.metric("Budget Estimé", f"${df_filtered['price'].sum():.0f}")
    c3.metric("Caféine Totale", f"{df_filtered['caffeine_mg'].sum()/1000:.1f} g")
    c4.metric("Gain Humeur", f"+{df_filtered['Mood_Boost'].mean():.1f} pts")
    
    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🕰️ Mes Habitudes Temporelles")
        # Heatmap
        hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            hm_data, x='Hour', y='DayOfWeek', z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale='Oranges',
            template='simple_white',
            title="Intensité de consommation (Jour vs Heure)"
        )
        fig_heat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_right:
        st.subheader("☕ Répartition")
        # CORRECTION DU BUG : Utilisation de px.pie au lieu de px.donut
        fig_pie = px.pie(
            df_filtered, 
            values='price', 
            names='coffee_type', 
            hole=0.5, # C'est ça qui crée l'effet Donut
            color_discrete_sequence=px.colors.sequential.Brwnyl,
            template='simple_white',
            title="Dépenses par Type"
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: LIFESTYLE ---
with tab2:
    st.subheader("🌍 Analyse du Contexte")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Hiérarchie des Lieux & Activités**")
        fig_sun = px.sunburst(
            df_filtered, 
            path=['location', 'activity', 'coffee_type'], 
            values='price',
            color='location',
            color_discrete_sequence=px.colors.qualitative.Antique
        )
        fig_sun.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_sun, use_container_width=True)
        
    with col2:
        st.markdown("**Météo & Préférences**")
        # Bar chart : Quel café je bois selon la météo ?
        weather_counts = df_filtered.groupby(['weather', 'coffee_type']).size().reset_index(name='Count')
        fig_bar = px.bar(
            weather_counts, x='Count', y='weather', color='coffee_type',
            orientation='h',
            title="Influence de la Météo",
            color_discrete_sequence=px.colors.sequential.RdBu,
            template='simple_white'
        )
        fig_bar.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

# --- TAB 3: IMPACT & SANTÉ ---
with tab3:
    st.subheader("🧬 Analyse Quantified Self")
    st.markdown("Exploration des corrélations entre la caféine, le sommeil et l'humeur.")
    
    col_bio1, col_bio2 = st.columns(2)
    
    with col_bio1:
        st.markdown("#### 💤 Impact sur le Sommeil")
        # Scatter Plot avec Zone de Danger
        fig_sleep = px.scatter(
            df_filtered, x='Hour', y='sleep_hours_next_night',
            size='caffeine_mg', color='location',
            title="Heure du Café vs Durée du Sommeil",
            template='simple_white',
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        # Ajout Zone Rouge (Après 16h)
        fig_sleep.add_vrect(
            x0=16, x1=24, 
            fillcolor="red", opacity=0.1, 
            annotation_text="Zone Critique", annotation_position="top left"
        )
        fig_sleep.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_sleep, use_container_width=True)
        
    with col_bio2:
        st.markdown("#### 🙂 Impact sur l'Humeur")
        # Box Plot pour voir la distribution du gain d'humeur
        fig_box = px.box(
            df_filtered, x='coffee_type', y='Mood_Boost',
            color='coffee_type',
            title="Quel café me rend le plus heureux ?",
            template='simple_white',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_box.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_box, use_container_width=True)

    # Radar Chart
    st.markdown("---")
    st.subheader("🕸️ Profil Multidimensionnel")
    
    radar_data = df_filtered.groupby('location').agg({
        'price': 'mean',
        'caffeine_mg': 'mean',
        'stress_level': 'mean',
        'pleasure_score': 'mean'
    }).reset_index()
    
    # Normalisation
    for c in ['price', 'caffeine_mg', 'stress_level', 'pleasure_score']:
        radar_data[c] = radar_data[c] / radar_data[c].max()
        
    fig_radar = go.Figure()
    categories = ['Prix', 'Caféine', 'Stress', 'Plaisir']
    
    for i, row in radar_data.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row['price'], row['caffeine_mg'], row['stress_level'], row['pleasure_score']],
            theta=categories, fill='toself', name=row['location']
        ))
    
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)),
        paper_bgcolor='rgba(0,0,0,0)',
        title="Comparaison des Lieux (Normalisé)"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# --- TAB 4: MÉTHODOLOGIE ---
with tab4:
    st.markdown("""
    ### 📝 Méthodologie & Choix de Design
    
    **1. Le Jeu de Données (Quantified Self)**
    Ce dashboard utilise un jeu de données personnel (`my_coffee_life.csv`) généré pour simuler une année de consommation réaliste. Il inclut des métriques contextuelles (Météo, Social) et physiologiques (Sommeil, Stress).
    
    **2. Choix Esthétiques**
    * **Thème :** "Journal de bord" avec une image de fond texturée et des polices Serif (Playfair Display) pour un aspect humain et personnel.
    * **Couleurs :** Une palette sémantique (Marron, Crème, Orange) rappelant l'univers du café.
    
    **3. Visualisations Clés**
    * **Sunburst (Onglet 2) :** Choisi pour montrer la hiérarchie complexe entre le *Lieu*, le *Contexte Social* et le *Type de boisson*.
    * **Scatter Plot (Onglet 3) :** Essentiel pour démontrer la corrélation négative entre la consommation tardive et le sommeil. La zone rouge guide l'œil vers l'insight principal.
    * **Radar Chart (Onglet 3) :** Permet de comparer qualitativement les différents lieux de consommation (ex: Le travail est stressant mais gratuit, le café est cher mais plaisant).
    """)
    
    with open(file_name, "rb") as file:
        st.download_button(
            label="📥 Télécharger les Données (CSV)",
            data=file,
            file_name="my_coffee_data.csv",
            mime="text/csv"
        )
