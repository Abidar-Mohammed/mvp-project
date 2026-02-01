import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="The Quantified Coffee",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS DESIGN PROFESSIONNEL ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;600;700&family=Work+Sans:wght@300;400;500;600&display=swap');

    /* === VARIABLES CSS === */
    :root {
        --color-espresso: #1A0E0A;
        --color-mocha: #3E2723;
        --color-latte: #A1887F;
        --color-cream: #F5F1ED;
        --color-accent: #D4A574;
        --color-green: #4A7C59;
        --shadow-soft: 0 4px 24px rgba(0,0,0,0.06);
        --shadow-medium: 0 8px 32px rgba(0,0,0,0.08);
        --shadow-strong: 0 12px 48px rgba(0,0,0,0.12);
        --transition-smooth: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        --transition-bounce: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    /* === ANIMATIONS KEYFRAMES === */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(-40px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }

    @keyframes shimmer {
        0% {
            background-position: -1000px 0;
        }
        100% {
            background-position: 1000px 0;
        }
    }

    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.8;
        }
    }

    @keyframes float {
        0%, 100% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
    }

    /* === BACKGROUND === */
    .stApp {
        background: linear-gradient(135deg, #F5F1ED 0%, #E8DED2 100%);
        position: relative;
        overflow-x: hidden;
    }

    .stApp::before {
        content: '';
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            radial-gradient(circle at 20% 30%, rgba(212, 165, 116, 0.05) 0%, transparent 50%),
            radial-gradient(circle at 80% 70%, rgba(74, 124, 89, 0.05) 0%, transparent 50%),
            url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23D4A574' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        pointer-events: none;
        z-index: 0;
    }

    /* === CONTENEUR PRINCIPAL === */
    .main .block-container {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 3rem 2.5rem;
        border-radius: 24px;
        box-shadow: var(--shadow-strong);
        margin-top: 2rem;
        margin-bottom: 2rem;
        max-width: 96% !important;
        animation: fadeInUp 0.8s ease-out;
        position: relative;
        z-index: 1;
        border: 1px solid rgba(212, 165, 116, 0.15);
    }

    /* === TYPOGRAPHIE === */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Cormorant Garamond', serif;
        color: var(--color-espresso);
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    p, div, label, span, li {
        font-family: 'Work Sans', sans-serif;
        color: var(--color-mocha);
        line-height: 1.7;
    }

    /* === HEADER PRINCIPAL === */
    .header-journal {
        text-align: center;
        padding: 2.5rem 0 2rem;
        margin-bottom: 3rem;
        position: relative;
        animation: fadeInUp 0.6s ease-out;
    }

    .header-journal::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        width: 120px;
        height: 3px;
        background: linear-gradient(90deg, transparent, var(--color-accent), transparent);
    }

    .header-journal h1 {
        font-size: 4rem;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, var(--color-espresso) 0%, var(--color-mocha) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-weight: 700;
        animation: slideInRight 0.8s ease-out;
    }

    .header-journal p {
        font-size: 1.1rem;
        color: var(--color-latte);
        font-weight: 300;
        margin-top: 0.5rem;
        animation: fadeInUp 1s ease-out;
    }

    /* === METRICS CARDS === */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #FFFFFF 0%, var(--color-cream) 100%);
        border: none;
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: var(--shadow-soft);
        transition: var(--transition-smooth);
        position: relative;
        overflow: hidden;
        animation: fadeInUp 0.8s ease-out backwards;
    }

    div[data-testid="metric-container"]:nth-child(1) { animation-delay: 0.1s; }
    div[data-testid="metric-container"]:nth-child(2) { animation-delay: 0.2s; }
    div[data-testid="metric-container"]:nth-child(3) { animation-delay: 0.3s; }
    div[data-testid="metric-container"]:nth-child(4) { animation-delay: 0.4s; }

    div[data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--color-accent), var(--color-green));
        transform: scaleX(0);
        transform-origin: left;
        transition: var(--transition-smooth);
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-medium);
    }

    div[data-testid="metric-container"]:hover::before {
        transform: scaleX(1);
    }

    div[data-testid="metric-container"] label {
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--color-latte);
    }

    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        font-size: 2.2rem;
        font-weight: 600;
        color: var(--color-espresso);
        font-family: 'Cormorant Garamond', serif;
    }

    /* === SIDEBAR === */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--color-mocha) 0%, var(--color-espresso) 100%);
        border-right: 1px solid rgba(212, 165, 116, 0.2);
    }

    section[data-testid="stSidebar"] .block-container {
        background: transparent;
        padding-top: 3rem;
    }

    section[data-testid="stSidebar"] h3 {
        color: var(--color-cream);
        font-size: 1.3rem;
        margin-bottom: 1.5rem;
        padding-bottom: 0.8rem;
        border-bottom: 2px solid var(--color-accent);
    }

    section[data-testid="stSidebar"] label {
        color: var(--color-cream) !important;
        font-weight: 500;
    }

    section[data-testid="stSidebar"] .stMarkdown {
        color: var(--color-cream);
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(212, 165, 116, 0.3);
        margin: 2rem 0;
    }

    /* === TABS === */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--color-cream);
        padding: 0.5rem;
        border-radius: 12px;
        border: none;
        margin-bottom: 2rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 50px;
        background: transparent;
        border: none;
        border-radius: 8px;
        color: var(--color-mocha);
        font-weight: 500;
        font-family: 'Work Sans', sans-serif;
        transition: var(--transition-smooth);
        padding: 0 1.5rem;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 255, 255, 0.5);
        color: var(--color-espresso);
    }

    .stTabs [aria-selected="true"] {
        background: white !important;
        color: var(--color-espresso) !important;
        font-weight: 600;
        box-shadow: var(--shadow-soft);
    }

    /* === GRAPHIQUES === */
    .stPlotlyChart {
        border-radius: 16px;
        padding: 1rem;
        background: white;
        box-shadow: var(--shadow-soft);
        transition: var(--transition-smooth);
        animation: fadeInUp 0.8s ease-out backwards;
    }

    .stPlotlyChart:hover {
        box-shadow: var(--shadow-medium);
        transform: translateY(-2px);
    }

    /* === SUBHEADERS === */
    .stMarkdown h4 {
        color: var(--color-mocha);
        font-size: 1.4rem;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
        padding-left: 1rem;
        border-left: 4px solid var(--color-accent);
    }

    /* === DIVIDERS === */
    hr {
        margin: 2.5rem 0;
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--color-latte), transparent);
    }

    /* === BOUTONS === */
    .stDownloadButton button {
        background: linear-gradient(135deg, var(--color-mocha) 0%, var(--color-espresso) 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-family: 'Work Sans', sans-serif;
        transition: var(--transition-smooth);
        box-shadow: var(--shadow-soft);
    }

    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-medium);
    }

    /* === INFO BOXES === */
    .stAlert {
        border-radius: 12px;
        border-left: 4px solid var(--color-accent);
        background: var(--color-cream);
        animation: slideInRight 0.6s ease-out;
    }

    /* === MULTISELECT & INPUTS === */
    .stMultiSelect > div > div {
        border-radius: 8px;
        border-color: var(--color-latte);
    }

    .stDateInput > div > div {
        border-radius: 8px;
        border-color: var(--color-latte);
    }

    /* === SCROLLBAR === */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: var(--color-cream);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--color-latte);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--color-mocha);
    }

    /* === SECTION TITLES === */
    .section-title {
        font-size: 2rem;
        color: var(--color-espresso);
        margin: 2rem 0 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--color-cream);
        font-weight: 600;
        animation: slideInRight 0.6s ease-out;
    }

    /* === CARD CONTAINERS === */
    .info-card {
        background: linear-gradient(135deg, #FFFFFF 0%, var(--color-cream) 100%);
        border-radius: 16px;
        padding: 2rem;
        box-shadow: var(--shadow-soft);
        margin: 1.5rem 0;
        transition: var(--transition-smooth);
        animation: fadeInUp 0.8s ease-out;
    }

    .info-card:hover {
        box-shadow: var(--shadow-medium);
        transform: translateY(-3px);
    }

    /* === RESPONSIVE === */
    @media (max-width: 768px) {
        .header-journal h1 {
            font-size: 2.5rem;
        }
        
        .main .block-container {
            padding: 2rem 1.5rem;
        }
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
        st.warning("⚠️ Mode Démo : Fichier CSV introuvable. Génération de données de démonstration...")
        dates = pd.date_range(start="2024-01-01", periods=100)
        df = pd.DataFrame({
            'datetime': dates,
            'location': np.random.choice(['Home', 'Work', 'Coffee Shop'], 100),
            'social_context': np.random.choice(['Alone', 'Friends', 'Colleagues'], 100),
            'activity': np.random.choice(['Working', 'Reading', 'Studying', 'Leisure'], 100),
            'weather': np.random.choice(['Sunny', 'Rainy', 'Cloudy'], 100),
            'coffee_type': np.random.choice(['Espresso', 'Latte', 'Cappuccino', 'Americano'], 100),
            'price': np.random.uniform(2, 6, 100),
            'caffeine_mg': np.random.randint(50, 150, 100),
            'mood_before': np.random.randint(3, 8, 100),
            'mood_after': np.random.randint(5, 10, 100),
            'sleep_hours_next_night': np.random.uniform(5, 9, 100),
            'stress_level': np.random.randint(1, 10, 100),
            'pleasure_score': np.random.randint(5, 10, 100)
        })
    else:
        df = pd.read_csv(path)
        df['datetime'] = pd.to_datetime(df['datetime'])

    # Standardisation des colonnes manquantes
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
    st.markdown("### ⚙️ Filtres & Paramètres")
    
    if not df.empty:
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input(
            "📅 Période d'analyse", 
            value=(min_d, max_d), 
            min_value=min_d, 
            max_value=max_d
        )
        
        # Filtre Social
        social_opts = sorted(df['social_context'].unique())
        social_filter = st.multiselect(
            "👥 Contexte Social", 
            social_opts, 
            default=social_opts
        )
        
        # Filtre Type de café
        coffee_opts = sorted(df['coffee_type'].unique())
        coffee_filter = st.multiselect(
            "☕ Type de Café",
            coffee_opts,
            default=coffee_opts
        )

    st.markdown("---")
    st.caption("📊 Visual Analytics Project 2024")
    st.caption("🎨 Crafted with passion for data")

# Filtrage
if not df.empty:
    mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])
    if social_filter:
        mask = mask & (df['social_context'].isin(social_filter))
    if coffee_filter:
        mask = mask & (df['coffee_type'].isin(coffee_filter))
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. HEADER ---
st.markdown("""
<div class="header-journal">
    <h1>☕ The Quantified Coffee</h1>
    <p>Une exploration approfondie de mes habitudes de consommation · Data-Driven Personal Analytics</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.error("❌ Aucune donnée disponible avec ces filtres. Veuillez ajuster vos critères de sélection.")
    st.stop()

# --- 6. NAVIGATION ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Vue d'Ensemble", 
    "🌍 Contexte & Style de Vie", 
    "🧬 Impact Santé & Bien-être", 
    "📖 Méthodologie & Données"
])

# --- TAB 1: OVERVIEW ---
with tab1:
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    
    total_coffees = len(df_filtered)
    total_spent = df_filtered['price'].sum()
    total_caffeine = df_filtered['caffeine_mg'].sum() / 1000
    avg_mood_boost = df_filtered['Mood_Boost'].mean()
    
    c1.metric("☕ Total Cafés", f"{total_coffees}")
    c2.metric("💰 Dépenses", f"{total_spent:.0f} €")
    c3.metric("⚡ Caféine Totale", f"{total_caffeine:.1f} g")
    c4.metric("😊 Boost Humeur Moy.", f"+{avg_mood_boost:.1f}")
    
    st.markdown("---")
    
    # Graphiques principaux
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.markdown('<h3 class="section-title">🕰️ Carte de Chaleur - Mes Habitudes</h3>', unsafe_allow_html=True)
        
        hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            hm_data, 
            x='Hour', 
            y='DayOfWeek', 
            z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale=['#F5F1ED', '#D4A574', '#8D6E63', '#3E2723', '#1A0E0A'],
            template='plotly_white',
            labels={'Hour': 'Heure de la journée', 'DayOfWeek': 'Jour', 'Count': 'Nombre de cafés'}
        )
        fig_heat.update_layout(
            font=dict(family="Work Sans, sans-serif", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_right:
        st.markdown('<h3 class="section-title">📊 Répartition par Type</h3>', unsafe_allow_html=True)
        
        coffee_counts = df_filtered.groupby('coffee_type')['price'].sum().reset_index()
        
        fig_pie = px.pie(
            coffee_counts, 
            values='price', 
            names='coffee_type', 
            hole=0.6, 
            color_discrete_sequence=['#1A0E0A', '#3E2723', '#8D6E63', '#A1887F', '#D4A574', '#4A7C59'],
            template='plotly_white'
        )
        fig_pie.update_traces(
            textposition='outside', 
            textinfo='label+percent',
            textfont_size=13,
            marker=dict(line=dict(color='white', width=2))
        )
        fig_pie.update_layout(
            showlegend=False,
            font=dict(family="Work Sans, sans-serif", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=400
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    # Timeline
    st.markdown("---")
    st.markdown('<h3 class="section-title">📈 Évolution Temporelle</h3>', unsafe_allow_html=True)
    
    timeline_data = df_filtered.groupby('Date_Only').agg({
        'price': 'sum',
        'caffeine_mg': 'sum',
        'Mood_Boost': 'mean'
    }).reset_index()
    
    fig_timeline = go.Figure()
    
    fig_timeline.add_trace(go.Scatter(
        x=timeline_data['Date_Only'],
        y=timeline_data['price'],
        name='Dépenses (€)',
        mode='lines+markers',
        line=dict(color='#3E2723', width=3),
        marker=dict(size=6, color='#D4A574', line=dict(width=2, color='white')),
        fill='tozeroy',
        fillcolor='rgba(212, 165, 116, 0.1)'
    ))
    
    fig_timeline.update_layout(
        template='plotly_white',
        hovermode='x unified',
        font=dict(family="Work Sans, sans-serif", size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=350,
        xaxis_title="Date",
        yaxis_title="Dépenses (€)",
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_timeline, use_container_width=True)

# --- TAB 2: LIFESTYLE ---
with tab2:
    st.markdown('<h3 class="section-title">🌍 Analyse Contextuelle Approfondie</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🗺️ Hiérarchie : Lieu → Activité → Café")
        
        if df_filtered['location'].nunique() > 0:
            fig_sun = px.sunburst(
                df_filtered, 
                path=['location', 'activity', 'coffee_type'], 
                values='price',
                color='location',
                color_discrete_sequence=['#1A0E0A', '#3E2723', '#8D6E63', '#A1887F', '#D4A574', '#4A7C59']
            )
            fig_sun.update_layout(
                height=500,
                font=dict(family="Work Sans, sans-serif", size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            fig_sun.update_traces(marker=dict(line=dict(color='white', width=2)))
            st.plotly_chart(fig_sun, use_container_width=True)
        else:
            st.info("📊 Données insuffisantes pour le graphique sunburst.")
        
    with col2:
        st.markdown("#### 🌦️ Influence Météorologique")
        
        if df_filtered['weather'].nunique() > 1:
            weather_counts = df_filtered.groupby(['weather', 'coffee_type']).size().reset_index(name='Count')
            
            fig_bar = px.bar(
                weather_counts, 
                x='Count', 
                y='weather', 
                color='coffee_type',
                orientation='h',
                color_discrete_sequence=['#1A0E0A', '#3E2723', '#8D6E63', '#D4A574', '#4A7C59'],
                template='plotly_white',
                labels={'Count': 'Nombre de cafés', 'weather': 'Météo', 'coffee_type': 'Type de café'}
            )
            fig_bar.update_layout(
                yaxis_title=None,
                font=dict(family="Work Sans, sans-serif", size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                height=500,
                showlegend=True,
                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("📊 Données météo insuffisantes.")
    
    # Section sociale
    st.markdown("---")
    st.markdown('<h3 class="section-title">👥 Dimension Sociale</h3>', unsafe_allow_html=True)
    
    social_data = df_filtered.groupby('social_context').agg({
        'price': 'sum',
        'coffee_type': 'count',
        'pleasure_score': 'mean',
        'Mood_Boost': 'mean'
    }).reset_index()
    social_data.columns = ['Contexte', 'Dépenses', 'Nombre', 'Plaisir Moyen', 'Boost Humeur']
    
    fig_social = go.Figure()
    
    fig_social.add_trace(go.Bar(
        x=social_data['Contexte'],
        y=social_data['Nombre'],
        name='Nombre de cafés',
        marker_color='#3E2723',
        text=social_data['Nombre'],
        textposition='outside'
    ))
    
    fig_social.update_layout(
        template='plotly_white',
        font=dict(family="Work Sans, sans-serif", size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        xaxis_title="Contexte Social",
        yaxis_title="Nombre de cafés",
        showlegend=False
    )
    
    st.plotly_chart(fig_social, use_container_width=True)

# --- TAB 3: IMPACT & SANTÉ ---
with tab3:
    st.markdown('<h3 class="section-title">🧬 Analyse Biologique & Bien-être</h3>', unsafe_allow_html=True)
    
    col_bio1, col_bio2 = st.columns(2)
    
    with col_bio1:
        st.markdown("#### 💤 Corrélation : Heure de Consommation vs Sommeil")
        
        fig_sleep = px.scatter(
            df_filtered, 
            x='Hour', 
            y='sleep_hours_next_night',
            size='caffeine_mg', 
            color='location',
            template='plotly_white',
            color_discrete_sequence=['#1A0E0A', '#3E2723', '#8D6E63', '#A1887F', '#D4A574', '#4A7C59'],
            labels={
                'sleep_hours_next_night': 'Heures de Sommeil',
                'Hour': 'Heure de Consommation',
                'caffeine_mg': 'Caféine (mg)',
                'location': 'Lieu'
            }
        )
        
        # Zone d'alerte
        fig_sleep.add_vrect(
            x0=16, x1=24, 
            fillcolor="rgba(255, 87, 34, 0.1)", 
            opacity=0.5,
            layer="below", 
            line_width=0,
            annotation_text="⚠️ Zone à Risque",
            annotation_position="top left"
        )
        
        fig_sleep.update_layout(
            font=dict(family="Work Sans, sans-serif", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450
        )
        
        st.plotly_chart(fig_sleep, use_container_width=True)
        
    with col_bio2:
        st.markdown("#### 😊 Distribution du Boost d'Humeur")
        
        fig_box = px.box(
            df_filtered, 
            x='coffee_type', 
            y='Mood_Boost',
            color='coffee_type',
            template='plotly_white',
            color_discrete_sequence=['#1A0E0A', '#3E2723', '#8D6E63', '#A1887F', '#D4A574', '#4A7C59'],
            labels={
                'Mood_Boost': 'Amélioration Humeur',
                'coffee_type': 'Type de Café'
            }
        )
        
        fig_box.update_layout(
            showlegend=False,
            font=dict(family="Work Sans, sans-serif", size=12),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            height=450,
            xaxis_title=None
        )
        
        st.plotly_chart(fig_box, use_container_width=True)

    # Radar Chart
    st.markdown("---")
    st.markdown('<h3 class="section-title">🕸️ Profil Comparatif des Lieux</h3>', unsafe_allow_html=True)
    
    cols_radar = ['price', 'caffeine_mg', 'stress_level', 'pleasure_score']
    
    # Conversion en numérique
    for c in cols_radar:
        df_filtered[c] = pd.to_numeric(df_filtered[c], errors='coerce').fillna(0)
        
    radar_data = df_filtered.groupby('location')[cols_radar].mean().reset_index()
    
    # Normalisation
    for c in cols_radar:
        max_val = radar_data[c].max()
        if max_val > 0:
            radar_data[c] = radar_data[c] / max_val
            
    fig_radar = go.Figure()
    
    colors = ['#1A0E0A', '#3E2723', '#8D6E63', '#D4A574', '#4A7C59']
    
    for i, row in radar_data.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row[c] for c in cols_radar],
            theta=['Prix', 'Caféine', 'Stress', 'Plaisir'],
            fill='toself',
            name=row['location'],
            line_color=colors[i % len(colors)],
            fillcolor=colors[i % len(colors)],
            opacity=0.6
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1],
                showticklabels=True,
                ticks='',
                gridcolor='rgba(161, 136, 127, 0.2)'
            ),
            angularaxis=dict(
                gridcolor='rgba(161, 136, 127, 0.2)'
            ),
            bgcolor='rgba(0,0,0,0)'
        ),
        height=500,
        showlegend=True,
        font=dict(family="Work Sans, sans-serif", size=12),
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    
    st.plotly_chart(fig_radar, use_container_width=True)

# --- TAB 4: MÉTHODOLOGIE ---
with tab4:
    st.markdown('<h3 class="section-title">📖 Méthodologie & Documentation</h3>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h4>🎯 Objectif du Projet</h4>
        <p>
            Ce projet s'inscrit dans la mouvance du <strong>"Quantified Self"</strong>, 
            une approche qui consiste à mesurer et analyser des données personnelles pour 
            mieux comprendre ses habitudes et optimiser son bien-être. L'objectif est d'explorer 
            mes patterns de consommation de café et leurs impacts physiologiques et psychologiques.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h4>📊 Structure des Données</h4>
        <p>
            Le dataset <code>my_coffee_life.csv</code> contient des observations quotidiennes sur une période d'un an.
            Chaque entrée capture :
        </p>
        <ul>
            <li><strong>Contexte Temporel :</strong> Date, heure, jour de la semaine</li>
            <li><strong>Contexte Environnemental :</strong> Lieu, météo, contexte social</li>
            <li><strong>Détails du Café :</strong> Type, prix, teneur en caféine</li>
            <li><strong>Métriques Physiologiques :</strong> Humeur avant/après, qualité du sommeil, niveau de stress</li>
            <li><strong>Indicateurs de Satisfaction :</strong> Score de plaisir, boost d'humeur</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h4>🎨 Choix de Design</h4>
        <p>
            L'interface adopte une <strong>esthétique raffinée et épurée</strong> inspirée des coffee shops artisanaux :
        </p>
        <ul>
            <li><strong>Palette de couleurs :</strong> Tons chauds (espresso, mocha, latte, crème) évoquant l'univers du café</li>
            <li><strong>Typographie :</strong> Combinaison de Cormorant Garamond (serif élégant) et Work Sans (sans-serif moderne)</li>
            <li><strong>Animations :</strong> Transitions fluides et micro-interactions pour une expérience engageante</li>
            <li><strong>Visualisations :</strong> Graphiques Plotly interactifs avec une charte graphique cohérente</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="info-card">
        <h4>🔍 Insights Clés</h4>
        <ul>
            <li><strong>Pattern Temporel :</strong> La carte de chaleur révèle les moments privilégiés de consommation</li>
            <li><strong>Impact sur le Sommeil :</strong> Corrélation négative entre consommation tardive (>16h) et qualité du sommeil</li>
            <li><strong>Contexte Social :</strong> Influence du cadre social sur le type de café choisi et le niveau de satisfaction</li>
            <li><strong>Profil des Lieux :</strong> Le radar chart compare prix, caféine, stress et plaisir selon le lieu</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_dl1, col_dl2, col_dl3 = st.columns([1, 1, 1])
    
    with col_dl2:
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Télécharger les Données (CSV)",
            data=csv,
            file_name=f"coffee_data_{df_filtered['Date_Only'].min()}_{df_filtered['Date_Only'].max()}.csv",
            mime="text/csv"
        )
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0; color: var(--color-latte);">
        <p><strong>Made with ❤️ and ☕</strong></p>
        <p style="font-size: 0.9rem;">Visual Analytics Project · 2024</p>
    </div>
    """, unsafe_allow_html=True)
