import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The Quantified Coffee",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ULTIMATE CSS (Dark, English, Scrollable) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:wght@700&display=swap');

    /* GLOBAL BACKGROUND */
    .stApp {
        background-image: linear-gradient(rgba(10, 10, 10, 0.85), rgba(10, 10, 10, 0.95)), 
                          url("https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?q=80&w=2670&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
    }

    /* GLASSMORPHISM CONTAINER */
    .main .block-container {
        background: rgba(18, 18, 18, 0.85); /* Darker glass */
        backdrop-filter: blur(15px);
        -webkit-backdrop-filter: blur(15px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
        border-left: 1px solid rgba(255, 255, 255, 0.05);
        padding: 3rem 5rem; /* Wider padding for elegance */
        max-width: 1200px !important;
        margin: 0 auto;
        box-shadow: 0 0 50px rgba(0,0,0,0.8);
    }

    /* TYPOGRAPHY */
    h1, h2, h3 {
        font-family: 'Playfair Display', serif;
        color: #D4AF37 !important; /* Metallic Gold */
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    p, label, span, div, li {
        font-family: 'Montserrat', sans-serif;
        color: #B0BEC5;
    }

    /* SECTION HEADERS (Instead of Tabs) */
    .section-header {
        border-bottom: 1px solid rgba(212, 175, 55, 0.3);
        padding-bottom: 10px;
        margin-top: 60px;
        margin-bottom: 30px;
        font-size: 1.8rem;
        color: #E0E0E0;
        font-family: 'Playfair Display', serif;
    }

    /* MAIN TITLE */
    .main-title {
        text-align: center;
        margin-bottom: 60px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding-bottom: 40px;
    }
    .main-title h1 {
        font-size: 4.5rem;
        background: -webkit-linear-gradient(#FDD835, #D4AF37);
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

    /* METRICS / KPIs */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0px; /* Sharp edges for pro look */
        padding: 20px;
        text-align: center;
    }
    div[data-testid="metric-container"] label {
        font-size: 0.8rem;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: #78909C !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 2.2rem;
        color: #FFF8E1 !important; /* Cream */
        font-family: 'Playfair Display', serif;
    }

    /* CHARTS */
    .stPlotlyChart {
        background-color: transparent !important;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. ROBUST DATA LOADING (English Columns) ---
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
        # Dummy data generator if file missing
        dates = pd.date_range(start="2024-01-01", periods=200)
        df = pd.DataFrame({
            'datetime': dates,
            'location': np.random.choice(['Home', 'Work', 'Coffee Shop'], 200),
            'social_context': np.random.choice(['Alone', 'Friends', 'Colleagues'], 200),
            'activity': np.random.choice(['Working', 'Reading', 'Socializing'], 200),
            'weather': np.random.choice(['Sunny', 'Rainy', 'Cloudy'], 200),
            'coffee_type': np.random.choice(['Espresso', 'Latte', 'Cappuccino'], 200),
            'price': np.random.uniform(0, 6, 200),
            'caffeine_mg': np.random.randint(50, 150, 200),
            'mood_before': np.random.randint(3, 8, 200),
            'mood_after': np.random.randint(5, 10, 200),
            'sleep_hours_next_night': np.random.uniform(5, 9, 200)
        })
    else:
        df = pd.read_csv(path)
        df['datetime'] = pd.to_datetime(df['datetime'])

    # Ensure all columns exist (Safety check)
    cols = ['weather', 'social_context', 'location', 'activity', 'stress_level', 'pleasure_score']
    for c in cols:
        if c not in df.columns: df[c] = "Unknown" if c in ['weather', 'social_context'] else 0

    # Enrich Data (English)
    df['Hour'] = df['datetime'].dt.hour
    df['DayOfWeek'] = df['datetime'].dt.day_name()
    df['Mood_Boost'] = df['mood_after'] - df['mood_before']
    
    return df

df = load_data()

# --- 4. SIDEBAR (Filters) ---
with st.sidebar:
    st.markdown("### ◆ SETTINGS")
    if not df.empty:
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        social_opts = list(df['social_context'].unique())
        social_filter = st.multiselect("Social Context", social_opts, default=social_opts)

    st.markdown("---")
    st.caption("Personal Analytics | 2024")

# Filter Logic
if not df.empty:
    mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])
    if social_filter:
        mask = mask & (df['social_context'].isin(social_filter))
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. MAIN PAGE LAYOUT (SCROLLABLE) ---

# HEADER
st.markdown("""
<div class="main-title">
    <h1>THE QUANTIFIED COFFEE</h1>
    <p>A Personal Data Study on Habits, Health & Expenses</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.error("No data available for the selected range.")
    st.stop()

# --- SECTION 1: GLOBAL OVERVIEW ---
st.markdown('<div class="section-header">01. EXECUTIVE SUMMARY</div>', unsafe_allow_html=True)

# KPIs
c1, c2, c3, c4 = st.columns(4)
c1.metric("TOTAL CUPS", len(df_filtered))
c2.metric("TOTAL SPEND", f"${df_filtered['price'].sum():.0f}")
c3.metric("CAFFEINE INTAKE", f"{df_filtered['caffeine_mg'].sum()/1000:.1f} g")
c4.metric("MOOD BOOST", f"+{df_filtered['Mood_Boost'].mean():.1f}")

st.write("") # Spacer

# Charts Row 1
col_L, col_R = st.columns([2, 1])

# Common layout style for Plotly transparency
layout_style = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#B0BEC5', family="Montserrat"),
    margin=dict(t=40, l=20, r=20, b=20)
)

with col_L:
    st.markdown("##### ◆ TEMPORAL HABITS")
    hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    fig_heat = px.density_heatmap(
        hm_data, x='Hour', y='DayOfWeek', z='Count',
        category_orders={'DayOfWeek': days_order},
        color_continuous_scale='Oranges',
    )
    fig_heat.update_layout(**layout_style)
    fig_heat.update_coloraxes(colorbar_bgcolor="rgba(0,0,0,0)", colorbar_title="")
    st.plotly_chart(fig_heat, use_container_width=True)

with col_R:
    st.markdown("##### ◆ BUDGET SPLIT")
    fig_pie = px.pie(
        df_filtered, 
        values='price', 
        names='coffee_type', 
        hole=0.7,
        color_discrete_sequence=px.colors.sequential.Brwnyl
    )
    fig_pie.update_traces(textposition='outside', textinfo='percent')
    fig_pie.update_layout(showlegend=False, **layout_style)
    st.plotly_chart(fig_pie, use_container_width=True)


# --- SECTION 2: LIFESTYLE & CONTEXT ---
st.markdown('<div class="section-header">02. LIFESTYLE & CONTEXT</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("##### ◆ HIERARCHY: LOCATION > ACTIVITY > TYPE")
    if df_filtered['location'].nunique() > 0:
        fig_sun = px.sunburst(
            df_filtered, 
            path=['location', 'activity', 'coffee_type'], 
            values='price',
            color='location',
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_sun.update_layout(**layout_style, height=450)
        st.plotly_chart(fig_sun, use_container_width=True)

with col2:
    st.markdown("##### ◆ WEATHER INFLUENCE")
    if df_filtered['weather'].nunique() > 1:
        weather_counts = df_filtered.groupby(['weather', 'coffee_type']).size().reset_index(name='Count')
        fig_bar = px.bar(
            weather_counts, x='Count', y='weather', color='coffee_type',
            orientation='h',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_bar.update_layout(**layout_style, yaxis_title=None)
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("Insufficient weather data.")


# --- SECTION 3: BIOLOGICAL IMPACT ---
st.markdown('<div class="section-header">03. BIOLOGICAL IMPACT</div>', unsafe_allow_html=True)

col_bio1, col_bio2 = st.columns([3, 2])

with col_bio1:
    st.markdown("##### ◆ CORRELATION: TIME VS SLEEP")
    fig_sleep = px.scatter(
        df_filtered, x='Hour', y='sleep_hours_next_night',
        size='caffeine_mg', color='location',
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={'sleep_hours_next_night': 'Sleep Duration (Hours)', 'Hour': 'Hour of Intake'}
    )
    # Danger Zone
    fig_sleep.add_vrect(
        x0=16, x1=24, 
        fillcolor="red", opacity=0.1, line_width=0,
        annotation_text="DANGER ZONE (>4PM)", annotation_position="top left", annotation_font_color="salmon"
    )
    fig_sleep.update_layout(**layout_style)
    st.plotly_chart(fig_sleep, use_container_width=True)

with col_bio2:
    st.markdown("##### ◆ MULTIDIMENSIONAL PROFILE")
    # Radar Chart
    cols_radar = ['price', 'caffeine_mg', 'stress_level', 'pleasure_score']
    # Ensure numeric
    for c in cols_radar:
        df_filtered[c] = pd.to_numeric(df_filtered[c], errors='coerce').fillna(0)
    
    radar_data = df_filtered.groupby('location')[cols_radar].mean().reset_index()
    # Normalize
    for c in cols_radar:
        if radar_data[c].max() > 0:
            radar_data[c] = radar_data[c] / radar_data[c].max()
            
    fig_radar = go.Figure()
    for i, row in radar_data.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row[c] for c in cols_radar],
            theta=['COST', 'CAFFEINE', 'STRESS', 'PLEASURE'], 
            fill='toself', 
            name=row['location'],
            line_width=1.5
        ))
    
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, showticklabels=False, linecolor='#555'),
            bgcolor='rgba(255,255,255,0.02)'
        ),
        **layout_style,
        height=400
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #757575; font-size: 0.8rem; margin-top: 50px;">
    VISUAL ANALYTICS PROJECT 2024 | QUANTIFIED SELF | DATA: 1 YEAR LOG
</div>
""", unsafe_allow_html=True)
