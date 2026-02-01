import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The Quantified Coffee | Ultimate",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS "MIDNIGHT GOLD" (LUXURY DARK MODE) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:wght@700&display=swap');

    /* BACKGROUND */
    .stApp {
        background-image: linear-gradient(rgba(5, 5, 5, 0.90), rgba(5, 5, 5, 0.95)), 
                          url("https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?q=80&w=2574&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
    }

    /* CONTAINERS (Glassmorphism Dark) */
    .main .block-container {
        background: rgba(20, 20, 20, 0.7);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(212, 175, 55, 0.1); /* Gold border subtile */
        border-radius: 15px;
        padding: 3rem 4rem;
        max-width: 95% !important;
        box-shadow: 0 0 40px rgba(0,0,0,0.8);
    }

    /* TYPOGRAPHY */
    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif;
        color: #D4AF37 !important; /* Gold */
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    p, label, span, div, li {
        font-family: 'Montserrat', sans-serif;
        color: #BDBDBD;
    }

    /* SECTION HEADERS */
    .section-separator {
        border-bottom: 1px solid rgba(212, 175, 55, 0.3);
        margin-top: 60px;
        margin-bottom: 30px;
        padding-bottom: 10px;
        font-size: 1.5rem;
        color: #F9F9F9;
        font-family: 'Playfair Display', serif;
    }

    /* METRICS */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 15px;
        border-left: 3px solid #D4AF37;
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        background: rgba(255, 255, 255, 0.05);
        transform: translateY(-2px);
    }
    div[data-testid="metric-container"] label {
        color: #78909C !important;
        font-size: 0.8rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFF8E1 !important;
        font-family: 'Playfair Display', serif;
    }

    /* CHARTS */
    .stPlotlyChart {
        background-color: transparent !important;
    }
    
    /* SCROLLBAR */
    ::-webkit-scrollbar {
        width: 10px;
        background: #121212;
    }
    ::-webkit-scrollbar-thumb {
        background: #333;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING ---
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
        # Dummy data generator
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

    # Enrich Data
    df['Hour'] = df['datetime'].dt.hour
    df['DayOfWeek'] = df['datetime'].dt.day_name()
    df['Month'] = df['datetime'].dt.to_period('M').astype(str)
    df['Date_Only'] = df['datetime'].dt.date
    df['Mood_Boost'] = df['mood_after'] - df['mood_before']
    df['Cumul_Spend'] = df['price'].cumsum() # For Financial Chart
    
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
    st.caption("Personal Analytics | 2024")

if not df.empty:
    mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])
    if social_filter:
        mask = mask & (df['social_context'].isin(social_filter))
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. DASHBOARD HEADER ---
st.markdown("""
<div style="text-align: center; margin-bottom: 50px;">
    <h1 style="font-size: 4rem; margin-bottom: 10px; background: -webkit-linear-gradient(#FDD835, #D4AF37); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">THE QUANTIFIED COFFEE</h1>
    <p style="text-transform: uppercase; letter-spacing: 3px; font-size: 1rem;">Habits, Health & Financial Impact Analysis</p>
</div>
""", unsafe_allow_html=True)

# LAYOUT CONFIG FOR PLOTLY
layout_dark = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#cfd8dc', family="Montserrat"),
    margin=dict(t=30, l=10, r=10, b=10)
)

# --- 01. EXECUTIVE SUMMARY ---
st.markdown('<div class="section-separator">01. EXECUTIVE SUMMARY</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("TOTAL CUPS", len(df_filtered), "Volume")
c2.metric("TOTAL SPEND", f"${df_filtered['price'].sum():.0f}", "USD")
c3.metric("CAFFEINE", f"{df_filtered['caffeine_mg'].sum()/1000:.1f} g", "Intake")
c4.metric("AVG SLEEP", f"{df_filtered['sleep_hours_next_night'].mean():.1f} h", "Next Night")

col1, col2 = st.columns([2, 1])
with col1:
    st.markdown("##### ◆ WEEKLY RHYTHM")
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
    st.markdown("##### ◆ ACTIVITY BREAKDOWN")
    fig_tree = px.treemap(
        df_filtered, 
        path=['activity', 'coffee_type'], 
        values='price',
        color='activity',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_tree.update_layout(**layout_dark)
    st.plotly_chart(fig_tree, use_container_width=True)

# --- 02. FINANCIAL ANALYSIS (NEW) ---
st.markdown('<div class="section-separator">02. FINANCIAL INSIGHTS</div>', unsafe_allow_html=True)

col_f1, col_f2 = st.columns(2)

with col_f1:
    st.markdown("##### ◆ SPENDING TREND (CUMULATIVE)")
    fig_line = px.area(
        df_filtered, x='datetime', y='Cumul_Spend',
        color_discrete_sequence=['#D4AF37']
    )
    fig_line.update_layout(**layout_dark, showlegend=False)
    st.plotly_chart(fig_line, use_container_width=True)

with col_f2:
    st.markdown("##### ◆ PRICE DISTRIBUTION BY TYPE")
    fig_box = px.box(
        df_filtered, x='coffee_type', y='price',
        color='coffee_type',
        color_discrete_sequence=px.colors.qualitative.Antique
    )
    fig_box.update_layout(**layout_dark, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)

# --- 03. SOCIAL & CONTEXT (NEW VISUALS) ---
st.markdown('<div class="section-separator">03. SOCIAL & CONTEXT</div>', unsafe_allow_html=True)

st.markdown("##### ◆ THE COFFEE FLOW: SOCIAL > LOCATION > TYPE")
# Parallel Categories Diagram (Sankey-like)
fig_parcat = px.parallel_categories(
    df_filtered, 
    dimensions=['social_context', 'location', 'coffee_type'],
    color="price", 
    color_continuous_scale=px.colors.sequential.Inferno
)
fig_parcat.update_layout(**layout_dark, height=400)
st.plotly_chart(fig_parcat, use_container_width=True)

# --- 04. BIOLOGICAL IMPACT ---
st.markdown('<div class="section-separator">04. BIOLOGICAL IMPACT</div>', unsafe_allow_html=True)

col_b1, col_b2 = st.columns(2)

with col_b1:
    st.markdown("##### ◆ CAFFEINE VS SLEEP CORRELATION")
    fig_scatter = px.scatter(
        df_filtered, x='Hour', y='sleep_hours_next_night',
        size='caffeine_mg', color='location',
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={'sleep_hours_next_night': 'Sleep Hours'}
    )
    fig_scatter.add_vrect(x0=16, x1=24, fillcolor="red", opacity=0.1, line_width=0, annotation_text="LATE CAFFEINE", annotation_position="top left", annotation_font_color="salmon")
    fig_scatter.update_layout(**layout_dark)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_b2:
    st.markdown("##### ◆ MOOD SHIFT (BEFORE -> AFTER)")
    # Aggregated mood change
    mood_agg = df_filtered.groupby('activity')[['mood_before', 'mood_after']].mean().reset_index()
    
    fig_slope = go.Figure()
    for i, row in mood_agg.iterrows():
        fig_slope.add_trace(go.Scatter(
            x=['Before', 'After'], y=[row['mood_before'], row['mood_after']],
            mode='lines+markers', name=row['activity'],
            line=dict(width=3)
        ))
    fig_slope.update_layout(title="Average Mood Impact by Activity", **layout_dark)
    st.plotly_chart(fig_slope, use_container_width=True)

# --- 05. MULTIDIMENSIONAL PROFILE ---
st.markdown('<div class="section-separator">05. LOCATION PROFILING</div>', unsafe_allow_html=True)

cols_radar = ['price', 'caffeine_mg', 'mood_after', 'sleep_hours_next_night']
# Normalize
radar_df = df_filtered.groupby('location')[cols_radar].mean().reset_index()
for c in cols_radar:
    radar_df[c] = radar_df[c] / radar_df[c].max()

fig_radar = go.Figure()
for i, row in radar_df.iterrows():
    fig_radar.add_trace(go.Scatterpolar(
        r=[row[c] for c in cols_radar],
        theta=['COST', 'CAFFEINE', 'MOOD', 'SLEEP'],
        fill='toself', name=row['location']
    ))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, showticklabels=False, linecolor='#444'),
        bgcolor='rgba(255,255,255,0.02)'
    ),
    **layout_dark,
    height=500
)
st.plotly_chart(fig_radar, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 0.8rem; color: #757575;">
    VISUAL ANALYTICS PROJECT 2024 | QUANTIFIED SELF | DATA SOURCE: MY_COFFEE_LIFE.CSV
</div>
""", unsafe_allow_html=True)
