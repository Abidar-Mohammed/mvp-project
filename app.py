import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Netflix Analytics | Ultimate",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS PREMIUM (HYBRIDE : COLORÉ + B&W POUR METHODOLOGIE) ---
st.markdown("""
<style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Bebas+Neue&display=swap');

    /* BACKGROUND GLOBAL (Coloré & Sombre) */
    .stApp {
        background-color: #0a0a0a;
        background-image: radial-gradient(circle at 50% 0%, #2a0000, #0a0a0a 60%);
        color: #e0e0e0;
    }

    /* TYPOGRAPHIE */
    h1, h2, h3 { font-family: 'Outfit', sans-serif; font-weight: 600; }
    
    .netflix-font {
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 2px;
        color: #E50914;
        text-shadow: 0 0 20px rgba(229, 9, 20, 0.6);
    }

    /* KPI CARDS (Verre Fumé Coloré) */
    .kpi-card {
        background: rgba(30, 30, 30, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .kpi-card:hover { transform: translateY(-5px); border-color: #E50914; }
    .kpi-title { font-family: 'Outfit', sans-serif; font-size: 0.85rem; color: #aaa; text-transform: uppercase; }
    .kpi-value { font-family: 'Bebas Neue', sans-serif; font-size: 2.8rem; color: #fff; margin-top: 5px; }
    .kpi-sub { font-size: 0.8rem; color: #46d369; }

    /* CHARTS CONTAINER */
    .chart-box {
        background: rgba(20, 20, 20, 0.5);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }

    /* --- ZONE METHODOLOGIE (NOIR & BLANC STRICT) --- */
    .methodology-container {
        background: #111 !important;
        border: 1px solid #333 !important;
        padding: 25px;
        border-radius: 8px;
        color: #ccc !important;
        font-family: 'Outfit', sans-serif;
    }
    .methodology-container h4 { 
        color: #fff !important; 
        border-bottom: 1px solid #333; 
        padding-bottom: 5px; 
        margin-top: 15px; 
        font-family: 'Outfit', sans-serif;
    }
    .streamlit-expanderHeader { 
        background-color: #1a1a1a !important; 
        color: #fff !important; 
        border: 1px solid #333; 
    }

    /* LIST CARDS */
    .list-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px; padding: 12px; margin-bottom: 8px;
        border-left: 3px solid #333; display: flex; justify-content: space-between; align-items: center;
    }
    .list-card.top { border-left-color: #46d369; }
    .list-card.flop { border-left-color: #E50914; }

    /* HIDE DEFAULTS */
    div[data-testid="stMetric"] { display: none; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
@st.cache_data
def load_data():
    GITHUB_URL = "https://raw.githubusercontent.com/Abidar-Mohammed/mvp-project/main/NetflixHistory4.csv"
    try:
        try: df = pd.read_csv(GITHUB_URL)
        except: 
            if os.path.exists("NetflixHistory.csv"): df = pd.read_csv("NetflixHistory.csv")
            else: return pd.DataFrame()

        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
        if df['Date'].isna().all(): df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        def get_metadata(row):
            t = str(row['Title']).lower()
            g = str(row.get('Genre', '')).lower()
            is_show = 'saison' in t or 'season' in t or 'episode' in t or ':' in t
            
            # Duration logic
            if not is_show: duration = 105
            elif 'anime' in g: duration = 24
            elif 'comedy' in g: duration = 22
            else: duration = 50
            
            return pd.Series([duration, 'Series' if is_show else 'Movie'])

        if 'Genre' not in df.columns: df['Genre'] = 'Drama'
        
        # Apply Metadata
        df[['Duration_Mins', 'Type']] = df.apply(get_metadata, axis=1)
        
        # Fallbacks for robustness
        if 'My_Rating' not in df.columns: df['My_Rating'] = np.random.randint(5, 11, size=len(df))
        if 'Weather' not in df.columns: df['Weather'] = 'Sunny'
        
        # Time features
        df['MonthYear'] = df['Date'].dt.to_period('M').astype(str)
        df['DayOfWeek'] = df['Date'].dt.day_name()
        return df

    except Exception as e:
        st.error(f"Data Error: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty: st.stop()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#E50914; font-family: Bebas Neue; font-size: 3rem; text-align:center;'>N <span style='color:white'>DATA</span></h1>", unsafe_allow_html=True)
    st.markdown("---")
    min_d, max_d = df['Date'].min().date(), df['Date'].max().date()
    dr = st.slider("📅 Timeline", min_d, max_d, (min_d, max_d))
    gs = sorted(df['Genre'].astype(str).unique())
    sg = st.multiselect("🎭 Genres", gs, default=gs)
    mask = (df['Date'].dt.date >= dr[0]) & (df['Date'].dt.date <= dr[1])
    if sg: mask = mask & (df['Genre'].isin(sg))
    df_filtered = df[mask]

# --- 5. MAIN DASHBOARD ---

st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 class="netflix-font" style="font-size: 4rem; margin-bottom: 0;">MY VIEWING HISTORY</h1>
        <p style="color: #888; font-size: 1.1rem;">Cinematic data analysis & behavioral patterns.</p>
    </div>
""", unsafe_allow_html=True)

# --- METHODOLOGY (BLACK & WHITE) ---
with st.expander("🛠️ TECHNICAL METHODOLOGY"):
    st.markdown("""
    <div class="methodology-container">
        <h4>1. DATA INGESTION PIPELINE</h4>
        <p>Raw viewing history is extracted from Netflix (CSV). A Python script processes this data to distinguish between movies and episodic content using RegEx patterns.</p>
        <h4>2. ENRICHMENT VIA APIs & LOGIC</h4>
        <ul>
            <li><strong>Weather Data:</strong> Historical conditions retrieved via Open-Meteo API for Paris.</li>
            <li><strong>Duration Estimation:</strong> Logic-based assignment (Anime=24m, Sitcom=22m, Drama=50m, Movie=105m).</li>
            <li><strong>Quality Scoring:</strong> Simulation of user ratings (1-10 scale).</li>
        </ul>
        <h4>3. STACK</h4>
        <p>Built with Streamlit & Plotly for high-performance visualization.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# KPIS
total_h = int(df_filtered['Duration_Mins'].sum() / 60)
nb_t = len(df_filtered)
avg_r = df_filtered['My_Rating'].mean()
fav_g = df_filtered['Genre'].mode()[0]

c1, c2, c3, c4 = st.columns(4)
def kpi(col, t, v, s):
    col.markdown(f"""<div class="kpi-card"><div class="kpi-title">{t}</div><div class="kpi-value">{v}</div><div class="kpi-sub">{s}</div></div>""", unsafe_allow_html=True)

kpi(c1, "Total Hours", f"{total_h}h", "Cumulative Time")
kpi(c2, "Titles Watched", f"{nb_t}", "Movies & Episodes")
kpi(c3, "Avg Rating", f"{avg_r:.1f}/10", "Quality Score")
kpi(c4, "Top Genre", fav_g.upper(), "Most Frequent")

st.markdown("<br>", unsafe_allow_html=True)

# --- ROW 1: RATING PSYCHOLOGY (NEW!) ---
st.markdown("### 🧠 Rating Psychology")
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("**Does Duration Affect My Rating? (Scatter Analysis)**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    # Scatter: Duration vs Rating colored by Type 
    fig_scatter = px.scatter(df_filtered, x="Duration_Mins", y="My_Rating", 
                             color="Genre", size="My_Rating", 
                             hover_data=['Title'],
                             color_discrete_sequence=px.colors.qualitative.Bold)
    fig_scatter.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888', family="Outfit"),
        xaxis_title="Duration (Minutes)", yaxis_title="My Rating (1-10)",
        margin=dict(l=0,r=0,t=10,b=0),
        showlegend=True
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("**Mood Monitor (Avg Rating by Day)**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    # Average rating per day of week
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    mood_data = df_filtered.groupby('DayOfWeek')['My_Rating'].mean().reindex(days).reset_index()
    
    fig_mood = px.bar(mood_data, x="DayOfWeek", y="My_Rating", 
                      color="My_Rating", color_continuous_scale="RdYlGn") # Red (Low) to Green (High)
    fig_mood.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888'),
        coloraxis_showscale=False, xaxis_title=None,
        yaxis=dict(range=[0, 10]),
        margin=dict(l=0,r=0,t=10,b=0)
    )
    st.plotly_chart(fig_mood, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- ROW 2: WEATHER & CONTENT DEEP DIVE ---
st.markdown("### 🧬 Content & Environment")
c_sun, c_box = st.columns([1, 2])

with c_sun:
    st.markdown("**Content DNA (Type > Genre)**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    # SUNBURST CHART 

[Image of Sunburst Chart]

    fig_sun = px.sunburst(df_filtered, path=['Type', 'Genre'], values='Duration_Mins',
                          color='Genre', color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_sun.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ccc'),
        margin=dict(t=0, l=0, r=0, b=0)
    )
    st.plotly_chart(fig_sun, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_box:
    st.markdown("**Does Weather Influence Volume? (Distribution Analysis)**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    # BOX PLOT: Weather vs Daily Count
    daily_vol = df_filtered.groupby(['Date', 'Weather']).size().reset_index(name='DailyCount')
    
    fig_box = px.box(daily_vol, x="Weather", y="DailyCount", color="Weather",
                     color_discrete_map={'Sunny': '#F5D300', 'Cloudy': '#888', 'Rainy': '#2255AA', 'Snowy': '#FFF', 'Foggy': '#555'},
                     points="all") 
    fig_box.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888'),
        showlegend=False,
        yaxis_title="Items Watched per Day",
        margin=dict(l=0,r=0,t=10,b=0)
    )
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- ROW 3: TRENDS ---
st.markdown("### 📈 Evolution Trends")
c_evo = st.container()
with c_evo:
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    evo_data = df_filtered.groupby(['MonthYear', 'Genre']).size().reset_index(name='Count')
    fig_evo = px.area(evo_data, x="MonthYear", y="Count", color="Genre", 
                      color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_evo.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', 
        font=dict(color='#888'), legend=dict(orientation="h", y=1.1),
        margin=dict(l=0,r=0,t=0,b=0)
    )
    st.plotly_chart(fig_evo, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# --- ROW 4: LISTS ---
cl1, cl2 = st.columns(2)
with cl1:
    st.markdown("### 🔥 Hall of Fame")
    top = df_filtered.sort_values('My_Rating', ascending=False).drop_duplicates('Title').head(5)
    for _, r in top.iterrows():
        st.markdown(f"""<div class="list-card top"><div><strong style="color:white;">{r['Title']}</strong><br><span style="color:#888; font-size:0.85rem;">{r['Genre']} • {r['Weather']}</span></div><div style="background:#46d369; color:#000; padding:4px 8px; border-radius:6px; font-weight:bold;">{r['My_Rating']}</div></div>""", unsafe_allow_html=True)

with cl2:
    st.markdown("### 🍅 Wall of Shame")
    flop = df_filtered.sort_values('My_Rating', ascending=True).drop_duplicates('Title').head(5)
    for _, r in flop.iterrows():
        st.markdown(f"""<div class="list-card flop"><div><strong style="color:white;">{r['Title']}</strong><br><span style="color:#888; font-size:0.85rem;">{r['Genre']} • {r['Weather']}</span></div><div style="background:#E50914; color:#fff; padding:4px 8px; border-radius:6px; font-weight:bold;">{r['My_Rating']}</div></div>""", unsafe_allow_html=True)

st.markdown("<br><center style='color:#555'>NETFLIX ANALYTICS • ENGINEERING PROJECT 2024</center>", unsafe_allow_html=True)
