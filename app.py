import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The Quantified Coffee",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS "DARK LUXURY" (AVEC IMAGE SUBTILE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:wght@700&display=swap');

    /* FOND GLOBAL AVEC IMAGE ET FILTRE SOMBRE */
    .stApp {
        /* L'astuce est ici : on superpose un dégradé noir presque opaque sur l'image */
        background-image: linear-gradient(rgba(0, 0, 0, 0.85), rgba(20, 10, 5, 0.9)), 
                          url("https://images.unsplash.com/photo-1509042239860-f550ce710b93?q=80&w=2574&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
        background-position: center;
    }

    /* CONTENEUR PRINCIPAL (Carte Vitrée Sombre) */
    .main .block-container {
        background: rgba(18, 18, 18, 0.75); /* Noir transparent */
        backdrop-filter: blur(10px); /* Effet de flou derrière */
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 3rem 4rem;
        max-width: 95% !important;
        margin-top: 2rem;
        box-shadow: 0 20px 50px rgba(0,0,0,0.8);
    }

    /* TYPOGRAPHIE */
    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif;
        color: #D4AF37 !important; /* Or Métallique */
        text-transform: uppercase;
        letter-spacing: 1.5px;
        text-shadow: 0 2px 4px rgba(0,0,0,0.8);
    }
    
    p, label, span, div, li {
        font-family: 'Montserrat', sans-serif;
        color: #BDBDBD; /* Gris argenté pour le texte */
    }

    /* TITRE PRINCIPAL */
    .main-title {
        text-align: center;
        margin-bottom: 60px;
        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
        padding-bottom: 40px;
    }
    .main-title h1 {
        font-size: 4.5rem;
        background: -webkit-linear-gradient(#FDD835, #D4AF37); /* Dégradé Or */
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .main-title p {
        font-size: 1.1rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #757575 !important;
        margin-top: 10px;
    }

    /* SEPARATEURS DE SECTION */
    .section-header {
        border-left: 5px solid #D4AF37;
        padding-left: 20px;
        margin-top: 70px;
        margin-bottom: 30px;
        font-size: 2rem;
        color: #F5F5F5;
        font-family: 'Playfair Display', serif;
        background: linear-gradient(90deg, rgba(212, 175, 55, 0.1), transparent);
        padding-top: 10px;
        padding-bottom: 10px;
    }

    /* METRICS (KPIs) */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        transition: transform 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: #D4AF37;
        background: rgba(212, 175, 55, 0.05);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.8rem;
        letter-spacing: 2px;
        color: #90A4AE !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 2.5rem;
        color: #FFF8E1 !important; /* Crème */
        font-family: 'Playfair Display', serif;
    }

    /* GRAPHIQUES */
    .stPlotlyChart {
        background-color: transparent !important;
    }
    
    /* SCROLLBAR MODERNE */
    ::-webkit-scrollbar {
        width: 12px;
        background: #000;
    }
    ::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 6px;
        border: 2px solid #000;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT DONNÉES ---
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
        # Fallback dummy data
        dates = pd.date_range(start="2024-01-01", periods=100)
        df = pd.DataFrame({
            'datetime': dates,
            'location': np.random.choice(['Home', 'Work', 'Coffee Shop'], 100),
            'social_context': np.random.choice(['Alone', 'Friends'], 100),
            'activity': np.random.choice(['Working', 'Reading'], 100),
            'coffee_type': np.random.choice(['Espresso', 'Latte'], 100),
            'price': np.random.uniform(0, 6, 100),
            'caffeine_mg': np.random.randint(50, 150, 100),
            'mood_before': np.random.randint(3, 8, 100),
            'mood_after': np.random.randint(5, 10, 100),
            'sleep_hours_next_night': np.random.uniform(5, 9, 100)
        })
    else:
        df = pd.read_csv(path)
        df['datetime'] = pd.to_datetime(df['datetime'])

    df['Hour'] = df['datetime'].dt.hour
    df['DayOfWeek'] = df['datetime'].dt.day_name()
    df['Month'] = df['datetime'].dt.to_period('M').astype(str)
    df['Date_Only'] = df['datetime'].dt.date
    df['Mood_Boost'] = df['mood_after'] - df['mood_before']
    df['Cumul_Spend'] = df['price'].cumsum()
    
    return df

df = load_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### ◆ SETTINGS")
    if not df.empty:
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        social_opts = list(df['social_context'].unique())
        social_filter = st.multiselect("Social Context", social_opts, default=social_opts)
    
    st.markdown("---")
    st.caption("Visual Analytics Project | 2024")

if not df.empty:
    mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])
    if social_filter:
        mask = mask & (df['social_context'].isin(social_filter))
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. MAIN PAGE (SCROLLING LAYOUT) ---

# HEADER
st.markdown("""
<div class="main-title">
    <h1>THE QUANTIFIED COFFEE</h1>
    <p>A Data-Driven Exploration of Habits & Health</p>
</div>
""", unsafe_allow_html=True)

# LAYOUT PLOTLY DARK TRANSPARENT
layout_dark = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#B0BEC5', family="Montserrat"),
    margin=dict(t=30, l=10, r=10, b=10)
)

# --- SECTION 01: EXECUTIVE SUMMARY ---
st.markdown('<div class="section-header">01. EXECUTIVE SUMMARY</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("TOTAL CUPS", len(df_filtered), "Volume")
c2.metric("TOTAL SPEND", f"${df_filtered['price'].sum():.0f}", "USD")
c3.metric("CAFFEINE", f"{df_filtered['caffeine_mg'].sum()/1000:.1f} g", "Intake")
c4.metric("AVG SLEEP", f"{df_filtered['sleep_hours_next_night'].mean():.1f} h", "Next Night")

st.write("") # Spacer

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("##### ◆ WEEKLY INTENSITY")
    hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    fig_heat = px.density_heatmap(
        hm_data, x='Hour', y='DayOfWeek', z='Count',
        category_orders={'DayOfWeek': days_order},
        color_continuous_scale='Oranges',
    )
    fig_heat.update_layout(**layout_dark)
    fig_heat.update_coloraxes(colorbar_bgcolor="rgba(0,0,0,0)", colorbar_title="")
    st.plotly_chart(fig_heat, use_container_width=True)

with col2:
    st.markdown("##### ◆ PREFERENCES")
    fig_pie = px.pie(
        df_filtered, 
        values='price', 
        names='coffee_type', 
        hole=0.7,
        color_discrete_sequence=px.colors.sequential.Brwnyl
    )
    fig_pie.update_traces(textposition='outside', textinfo='percent')
    fig_pie.update_layout(showlegend=False, **layout_dark)
    st.plotly_chart(fig_pie, use_container_width=True)


# --- SECTION 02: FINANCIAL INSIGHTS ---
st.markdown('<div class="section-header">02. FINANCIAL INSIGHTS</div>', unsafe_allow_html=True)

col_f1, col_f2 = st.columns(2)

with col_f1:
    st.markdown("##### ◆ SPENDING VELOCITY")
    fig_area = px.area(
        df_filtered, x='datetime', y='Cumul_Spend',
        color_discrete_sequence=['#D4AF37'] # Gold color
    )
    fig_area.update_layout(**layout_dark, showlegend=False)
    st.plotly_chart(fig_area, use_container_width=True)

with col_f2:
    st.markdown("##### ◆ COST DISTRIBUTION")
    fig_box = px.box(
        df_filtered, x='coffee_type', y='price',
        color='coffee_type',
        color_discrete_sequence=px.colors.qualitative.Antique
    )
    fig_box.update_layout(**layout_dark, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)


# --- SECTION 03: CONTEXT & FLOW ---
st.markdown('<div class="section-header">03. CONTEXT & FLOW</div>', unsafe_allow_html=True)

st.markdown("##### ◆ THE COFFEE JOURNEY: SOCIAL > LOCATION > TYPE")
fig_parcat = px.parallel_categories(
    df_filtered, 
    dimensions=['social_context', 'location', 'coffee_type'],
    color="price", 
    color_continuous_scale=px.colors.sequential.Inferno
)
fig_parcat.update_layout(**layout_dark, height=450)
st.plotly_chart(fig_parcat, use_container_width=True)


# --- SECTION 04: BIOLOGICAL IMPACT ---
st.markdown('<div class="section-header">04. BIOLOGICAL IMPACT</div>', unsafe_allow_html=True)

col_b1, col_b2 = st.columns([3, 2])

with col_b1:
    st.markdown("##### ◆ CAFFEINE VS SLEEP CORRELATION")
    fig_scatter = px.scatter(
        df_filtered, x='Hour', y='sleep_hours_next_night',
        size='caffeine_mg', color='location',
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={'sleep_hours_next_night': 'Sleep (Hours)', 'Hour': 'Hour of Day'}
    )
    # Danger zone visual
    fig_scatter.add_vrect(
        x0=16, x1=24, 
        fillcolor="red", opacity=0.1, line_width=0,
        annotation_text="DANGER (>4PM)", annotation_position="top left", annotation_font_color="#EF5350"
    )
    fig_scatter.update_layout(**layout_dark)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_b2:
    st.markdown("##### ◆ MULTI-DIMENSIONAL PROFILE")
    
    # Radar Chart
    cols_radar = ['price', 'caffeine_mg', 'mood_after', 'sleep_hours_next_night']
    # Normalize for radar
    radar_df = df_filtered.groupby('location')[cols_radar].mean().reset_index()
    for c in cols_radar:
        radar_df[c] = radar_df[c] / radar_df[c].max()

    fig_radar = go.Figure()
    for i, row in radar_df.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row[c] for c in cols_radar],
            theta=['COST', 'CAFFEINE', 'MOOD', 'SLEEP'],
            fill='toself', 
            name=row['location'],
            line_width=1.5
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, showticklabels=False, linecolor='#444'),
            bgcolor='rgba(255,255,255,0.02)'
        ),
        **layout_dark,
        height=400,
        showlegend=True,
        legend=dict(x=0, y=1)
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #757575; margin-top: 50px; font-size: 0.8rem;">
    VISUAL ANALYTICS PROJECT 2024 | QUANTIFIED SELF DATA | DESIGNED WITH STREAMLIT & PLOTLY
</div>
""", unsafe_allow_html=True)
