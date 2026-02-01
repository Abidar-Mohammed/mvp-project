import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="My Coffee Journal | Ultimate",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar fermée par défaut pour l'immersion
)

# --- 2. CSS ULTIMATE (DARK & GOLD THEME) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;700&family=Playfair+Display:wght@700&display=swap');

    /* FOND GLOBAL */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.8), rgba(0,0,0,0.9)), 
                          url("https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?q=80&w=2670&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
    }

    /* CONTENEUR PRINCIPAL (Carte Vitrée) */
    .main .block-container {
        background: rgba(20, 20, 20, 0.75);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 3rem;
        margin-top: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.5);
        max-width: 95% !important;
    }

    /* TYPOGRAPHIE */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: #D4AF37 !important; /* Or Métallique */
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    p, label, span, div {
        font-family: 'Montserrat', sans-serif;
        color: #E0E0E0;
    }

    /* HEADER */
    .header-title {
        text-align: center;
        margin-bottom: 40px;
    }
    .header-title h1 {
        font-size: 4rem;
        margin-bottom: 0;
        background: -webkit-linear-gradient(#FDD835, #D4AF37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .header-title p {
        font-size: 1.2rem;
        letter-spacing: 3px;
        text-transform: uppercase;
        color: #BDBDBD !important;
    }

    /* CARTES KPI (METRICS) */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        transition: transform 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: #D4AF37;
        background: rgba(255, 255, 255, 0.08);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.9rem;
        color: #B0BEC5 !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 2rem;
        color: #FFECB3 !important; /* Crème */
    }

    /* ONGLETS MODERNES */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #9E9E9E;
        border: none;
        font-size: 1.1rem;
    }
    .stTabs [aria-selected="true"] {
        color: #D4AF37 !important;
        font-weight: bold;
        border-bottom: 2px solid #D4AF37 !important;
    }

    /* GRAPHIQUES PLOTLY */
    .stPlotlyChart {
        background-color: transparent !important;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT ROBUSTE ---
@st.cache_data
def load_data():
    file_name = "my_coffee_life.csv"
    path = None
    possible_paths = [file_name, os.path.join(os.path.dirname(__file__), file_name)]
    
    for p in possible_paths:
        if os.path.exists(p):
            path = p
            break
            
    if not path:
        # Données de secours silencieuses
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
    else:
        df = pd.read_csv(path)
        df['datetime'] = pd.to_datetime(df['datetime'])

    # Sécurisation des colonnes
    required_cols = ['weather', 'social_context', 'location', 'activity', 'stress_level', 'pleasure_score']
    for col in required_cols:
        if col not in df.columns:
            df[col] = "Unknown" if col in ['weather', 'social_context', 'location', 'activity'] else 0

    df['Hour'] = df['datetime'].dt.hour
    df['DayOfWeek'] = df['datetime'].dt.day_name()
    df['Mood_Boost'] = df['mood_after'] - df['mood_before']
    
    return df

df = load_data()

# --- 4. SIDEBAR (FILTRES) ---
with st.sidebar:
    st.markdown("### ⚙️ Paramètres")
    if not df.empty:
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input("📅 Période", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        social_opts = list(df['social_context'].unique())
        social_filter = st.multiselect("👥 Social", social_opts, default=social_opts)

    st.markdown("---")
    st.info("Données personnelles | Quantified Self Project")

# Filtres
if not df.empty:
    mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])
    if social_filter:
        mask = mask & (df['social_context'].isin(social_filter))
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. HEADER PRINCIPAL ---
st.markdown("""
<div class="header-title">
    <h1>THE QUANTIFIED COFFEE</h1>
    <p>Analytics Personnels & Impact Biologique</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.error("Aucune donnée disponible.")
    st.stop()

# --- 6. CONTENU (3 ONGLETS SEULEMENT) ---
# Suppression de l'onglet Méthodologie comme demandé
tab1, tab2, tab3 = st.tabs([
    "📊 Vue d'Ensemble", "🧬 Style de Vie", "🧪 Impact & Santé"
])

# CONFIGURATION PLOTLY COMMUNE (POUR UN LOOK TRANSPARENT)
common_layout = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#E0E0E0'),
    margin=dict(t=30, l=10, r=10, b=10),
)

# --- TAB 1: OVERVIEW ---
with tab1:
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cafés", len(df_filtered))
    c2.metric("Budget", f"${df_filtered['price'].sum():.0f}")
    c3.metric("Caféine", f"{df_filtered['caffeine_mg'].sum()/1000:.1f} g")
    c4.metric("Gain Humeur", f"+{df_filtered['Mood_Boost'].mean():.1f}")
    
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
            title="Quand est-ce que je bois du café ?"
        )
        fig_heat.update_layout(**common_layout)
        fig_heat.update_coloraxes(colorbar_bgcolor="rgba(0,0,0,0)", colorbar_title="")
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_R:
        st.subheader("☕ Répartition")
        fig_pie = px.pie(
            df_filtered, 
            values='price', 
            names='coffee_type', 
            hole=0.7, # Donut très fin (élégant)
            color_discrete_sequence=px.colors.sequential.Brwnyl,
            title="Budget par Type"
        )
        fig_pie.update_traces(textposition='outside', textinfo='percent')
        fig_pie.update_layout(showlegend=False, **common_layout)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: LIFESTYLE ---
with tab2:
    st.subheader("🌍 Contexte & Environnement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Hiérarchie : Lieu > Activité > Café**")
        if df_filtered['location'].nunique() > 0:
            fig_sun = px.sunburst(
                df_filtered, 
                path=['location', 'activity', 'coffee_type'], 
                values='price',
                color='location',
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_sun.update_layout(**common_layout)
            st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.info("Données insuffisantes.")
            
    with col2:
        st.markdown("**Influence de la Météo**")
        if df_filtered['weather'].nunique() > 1:
            weather_counts = df_filtered.groupby(['weather', 'coffee_type']).size().reset_index(name='Count')
            fig_bar = px.bar(
                weather_counts, x='Count', y='weather', color='coffee_type',
                orientation='h',
                color_discrete_sequence=px.colors.sequential.RdBu,
                title="Météo vs Choix"
            )
            fig_bar.update_layout(**common_layout)
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Données météo non variées.")

# --- TAB 3: IMPACT & SANTÉ ---
with tab3:
    st.subheader("🧬 Biologie & Impact")
    
    col_bio1, col_bio2 = st.columns(2)
    
    with col_bio1:
        st.markdown("#### 💤 Heure vs Sommeil")
        fig_sleep = px.scatter(
            df_filtered, x='Hour', y='sleep_hours_next_night',
            size='caffeine_mg', color='location',
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={'sleep_hours_next_night': 'Heures de Sommeil'}
        )
        # Zone Critique (Design subtil)
        fig_sleep.add_vrect(
            x0=16, x1=24, 
            fillcolor="red", opacity=0.1, 
            line_width=0,
            annotation_text="DANGER (16h+)", annotation_font_color="salmon"
        )
        fig_sleep.update_layout(**common_layout)
        st.plotly_chart(fig_sleep, use_container_width=True)
        
    with col_bio2:
        st.markdown("#### 🙂 Profil Multidimensionnel")
        # Radar Chart
        cols_radar = ['price', 'caffeine_mg', 'stress_level', 'pleasure_score']
        # Sécurité numérique
        for c in cols_radar:
            df_filtered[c] = pd.to_numeric(df_filtered[c], errors='coerce').fillna(0)
        
        radar_data = df_filtered.groupby('location')[cols_radar].mean().reset_index()
        # Normalisation
        for c in cols_radar:
            if radar_data[c].max() > 0:
                radar_data[c] = radar_data[c] / radar_data[c].max()
                
        fig_radar = go.Figure()
        for i, row in radar_data.iterrows():
            fig_radar.add_trace(go.Scatterpolar(
                r=[row[c] for c in cols_radar],
                theta=['Coût', 'Caféine', 'Stress', 'Plaisir'], 
                fill='toself', 
                name=row['location'],
                line_width=1
            ))
        
        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, showticklabels=False, linecolor='#555'),
                bgcolor='rgba(255,255,255,0.05)'
            ),
            **common_layout
        )
        st.plotly_chart(fig_radar, use_container_width=True)
