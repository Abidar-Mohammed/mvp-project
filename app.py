import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="My Coffee Journal | Dark Mode",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS "DARK PREMIUM" ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700&family=Roboto:wght@300;400;700&display=swap');

    /* ANIMATION D'ENTRÉE */
    @keyframes fadeInUp {
        from { opacity: 0; transform: translate3d(0, 30px, 0); }
        to { opacity: 1; transform: translate3d(0, 0, 0); }
    }

    .main .block-container {
        animation: fadeInUp 0.8s ease-out;
    }

    /* FOND GLOBALE (DARK) */
    .stApp {
        background-image: linear-gradient(rgba(0,0,0,0.85), rgba(0,0,0,0.95)), 
                          url("https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?q=80&w=2574&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    /* CONTENEUR PRINCIPAL (Dark Glassmorphism) */
    .main .block-container {
        background-color: rgba(30, 27, 24, 0.85); /* Marron très très foncé transparent */
        padding: 2.5rem;
        border-radius: 15px;
        border: 1px solid #3E2723;
        box-shadow: 0 0 30px rgba(0,0,0,0.7);
        max-width: 95% !important;
    }

    /* TYPOGRAPHIE */
    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif;
        color: #EFEBE9 !important; /* Blanc cassé */
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }
    
    p, span, div, label, li {
        font-family: 'Roboto', sans-serif;
        color: #BCAAA4 !important; /* Gris beige */
    }

    /* HEADER */
    .header-title {
        text-align: center;
        border-bottom: 1px solid #4E342E;
        padding-bottom: 20px;
        margin-bottom: 30px;
    }
    .header-title h1 {
        font-size: 3.5rem;
        color: #D7CCC8 !important; /* Titre clair */
        letter-spacing: 2px;
    }
    .header-title p {
        font-size: 1.2rem;
        font-style: italic;
        color: #A1887F !important;
    }

    /* METRICS (KPIs) en Dark Mode */
    div[data-testid="metric-container"] {
        background-color: #2D2420; /* Fond carte */
        border: 1px solid #4E342E;
        border-left: 4px solid #FFB74D; /* Bordure Orange/Or */
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3);
    }
    div[data-testid="metric-container"] label {
        color: #A1887F !important; /* Label discret */
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFF8E1 !important; /* Valeur brillante */
        font-weight: bold;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #181513;
        border-right: 1px solid #333;
    }
    
    /* ONGLETS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid #444;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        color: #888;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3E2723 !important;
        color: #FFF !important;
        border-radius: 5px 5px 0 0;
    }

    /* GRAPHIQUES PLOTLY */
    .stPlotlyChart {
        background-color: #25201D;
        border-radius: 10px;
        padding: 10px;
        border: 1px solid #3E2723;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DONNÉES ROBUSTES ---
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
            'social_context': np.random.choice(['Alone', 'Friends'], 150),
            'activity': np.random.choice(['Working', 'Reading'], 150),
            'weather': np.random.choice(['Sunny', 'Rainy'], 150),
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

    # Standardisation colonnes
    required = ['weather', 'social_context', 'location', 'activity', 'stress_level', 'pleasure_score']
    for col in required:
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
    st.markdown("### ⚙️ Control Panel")
    if not df.empty:
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input("📅 Période", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        social_opts = list(df['social_context'].unique())
        social_filter = st.multiselect("👥 Social", social_opts, default=social_opts)

    st.markdown("---")
    st.info("Dark Mode Enabled 🌙")

# Filtres
if not df.empty:
    mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])
    if social_filter:
        mask = mask & (df['social_context'].isin(social_filter))
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. HEADER ---
st.markdown("""
<div class="header-title">
    <h1>THE QUANTIFIED COFFEE</h1>
    <p>Une plongée nocturne dans mes données personnelles.</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.error("Aucune donnée disponible.")
    st.stop()

# --- 6. CONTENU ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview", "🧬 Style de Vie", "🧪 Impact & Santé", "📝 Méthodologie"
])

# --- TAB 1: OVERVIEW ---
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cafés", len(df_filtered))
    c2.metric("Budget", f"${df_filtered['price'].sum():.0f}")
    c3.metric("Caféine", f"{df_filtered['caffeine_mg'].sum()/1000:.1f} g")
    c4.metric("Gain Humeur", f"+{df_filtered['Mood_Boost'].mean():.1f}")
    
    st.markdown("---")
    
    col_L, col_R = st.columns([2, 1])
    
    with col_L:
        st.subheader("🕰️ Intensité Hebdomadaire")
        hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            hm_data, x='Hour', y='DayOfWeek', z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale='Oranges', # Reste Orange pour le contraste
            template='plotly_dark' # Thème Dark activé
        )
        fig_heat.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_R:
        st.subheader("☕ Répartition Types")
        fig_pie = px.pie(
            df_filtered, 
            values='price', 
            names='coffee_type', 
            hole=0.6,
            color_discrete_sequence=px.colors.sequential.Brwnyl,
            template='plotly_dark'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: LIFESTYLE ---
with tab2:
    st.subheader("🌍 Contexte & Environnement")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Lieu > Activité > Type**")
        if df_filtered['location'].nunique() > 0:
            fig_sun = px.sunburst(
                df_filtered, 
                path=['location', 'activity', 'coffee_type'], 
                values='price',
                color='location',
                color_discrete_sequence=px.colors.qualitative.Pastel,
                template='plotly_dark'
            )
            fig_sun.update_layout(height=450, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_sun, use_container_width=True)
            
    with col2:
        st.markdown("**Influence de la Météo**")
        if df_filtered['weather'].nunique() > 1:
            weather_counts = df_filtered.groupby(['weather', 'coffee_type']).size().reset_index(name='Count')
            fig_bar = px.bar(
                weather_counts, x='Count', y='weather', color='coffee_type',
                orientation='h',
                color_discrete_sequence=px.colors.sequential.RdBu,
                template='plotly_dark'
            )
            fig_bar.update_layout(yaxis_title=None, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Données météo non disponibles.")

# --- TAB 3: SANTÉ ---
with tab3:
    st.subheader("🧬 Biologie & Impact")
    
    col_bio1, col_bio2 = st.columns(2)
    
    with col_bio1:
        st.markdown("#### 💤 Heure vs Sommeil")
        fig_sleep = px.scatter(
            df_filtered, x='Hour', y='sleep_hours_next_night',
            size='caffeine_mg', color='location',
            template='plotly_dark',
            color_discrete_sequence=px.colors.qualitative.Bold,
            labels={'sleep_hours_next_night': 'Heures de Sommeil'}
        )
        # Zone Rouge
        fig_sleep.add_vrect(
            x0=16, x1=24, 
            fillcolor="red", opacity=0.15, 
            annotation_text="Zone Critique", annotation_font_color="white"
        )
        fig_sleep.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_sleep, use_container_width=True)
        
    with col_bio2:
        st.markdown("#### 🙂 Boost d'Humeur")
        fig_box = px.box(
            df_filtered, x='coffee_type', y='Mood_Boost',
            color='coffee_type',
            template='plotly_dark',
            color_discrete_sequence=px.colors.qualitative.Prism
        )
        fig_box.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")
    st.subheader("🕸️ Comparaison Multidimensionnelle")
    
    cols_radar = ['price', 'caffeine_mg', 'stress_level', 'pleasure_score']
    for c in cols_radar:
        df_filtered[c] = pd.to_numeric(df_filtered[c], errors='coerce').fillna(0)
    
    radar_data = df_filtered.groupby('location')[cols_radar].mean().reset_index()
    for c in cols_radar:
        radar_data[c] = radar_data[c] / radar_data[c].max()
            
    fig_radar = go.Figure()
    for i, row in radar_data.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row[c] for c in cols_radar],
            theta=cols_radar, fill='toself', name=row['location']
        ))
    
    fig_radar.update_layout(
        template='plotly_dark',
        polar=dict(
            radialaxis=dict(visible=True, showticklabels=False),
            bgcolor='rgba(0,0,0,0)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        height=450
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# --- TAB 4: MÉTHODOLOGIE ---
with tab4:
    st.markdown("""
    ### 📝 Méthodologie & Design
    
    **1. Données Personnelles**
    Analyse basée sur un an de données simulées (`my_coffee_life.csv`). Les variables incluent le contexte social, la météo et des mesures physiologiques (sommeil, stress).
    
    **2. Design "Dark Premium"**
    * **Choix du Dark Mode :** Le fond sombre (`#1E1B18`) réduit la fatigue oculaire et fait ressortir les couleurs des données (Data-Ink Ratio).
    * **Contrastes :** Utilisation de l'or et de l'orange pour les données importantes, contrastant avec le fond anthracite.
    * **Animations :** Transition douce (FadeIn) à l'ouverture pour une expérience utilisateur fluide.
    """)
    
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Télécharger CSV", data=csv, file_name="my_dark_coffee_data.csv", mime="text/csv")
