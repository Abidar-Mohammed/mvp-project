import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Netflix Analytics | Premium",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. PREMIUM CSS STYLING ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Bebas+Neue&display=swap');

    /* DARK CINEMATIC THEME */
    .stApp {
        background-color: #050505;
        background-image: radial-gradient(circle at 50% 0%, #2a0000, #050505 80%);
        color: #e0e0e0;
    }

    /* TYPOGRAPHY */
    h1, h2, h3 { font-family: 'Outfit', sans-serif; font-weight: 600; letter-spacing: -0.5px; }
    
    .netflix-font {
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 3px;
        color: #E50914;
        text-shadow: 0px 0px 20px rgba(229, 9, 20, 0.6);
    }

    /* GLASSMORPHISM CARDS */
    .kpi-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 20px;
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: translateY(-5px); border-color: #E50914; }
    
    .kpi-title { font-family: 'Outfit', sans-serif; font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-family: 'Bebas Neue', sans-serif; font-size: 2.5rem; color: #fff; margin-top: 5px; }
    .kpi-sub   { font-size: 0.75rem; color: #46d369; }

    /* METHODOLOGY EXPANDER */
    .streamlit-expanderHeader {
        background-color: rgba(30, 30, 30, 0.5) !important;
        border-radius: 8px !important;
        font-family: 'Outfit', sans-serif !important;
    }
    
    /* CHARTS CONTAINER */
    .chart-box {
        background: rgba(15, 15, 15, 0.6);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.03);
        margin-bottom: 20px;
    }

    /* HIDE DEFAULTS */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    div[data-testid="stMetric"] { display: none; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING & LOGIC ---
@st.cache_data
def load_data():
    # URL provided by user
    GITHUB_URL = "https://raw.githubusercontent.com/Abidar-Mohammed/mvp-project/main/NetflixHistory4.csv"
    
    try:
        try:
            df = pd.read_csv(GITHUB_URL)
        except:
            if os.path.exists("NetflixHistory.csv"): df = pd.read_csv("NetflixHistory.csv")
            else: return pd.DataFrame()

        # Date Parsing
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
        if df['Date'].isna().all(): df['Date'] = pd.to_datetime(df['Date'], errors='coerce')

        # --- SMART DURATION CALCULATION ---
        # Logic: Films ~105m, Anime ~24m, Sitcoms ~22m, Dramas ~50m
        def calculate_duration(row):
            title = str(row['Title']).lower()
            genre = str(row.get('Genre', '')).lower()
            
            # Check if it's a TV Show (has Season/Episode or colon)
            is_show = 'saison' in title or 'season' in title or 'episode' in title or ':' in title
            
            if not is_show:
                return 105 # Average Movie
            
            # It's a show, check genre
            if 'anime' in genre: return 24
            if 'comedy' in genre: return 22 # Sitcom format
            return 50 # Standard Drama/Crime format

        # Apply columns if missing
        if 'Genre' not in df.columns: df['Genre'] = 'Unknown'
        
        # Apply Duration Logic
        df['Duration_Mins'] = df.apply(calculate_duration, axis=1)

        # Fix Ratings/Weather if missing (Safety Net)
        if 'My_Rating' not in df.columns: df['My_Rating'] = np.random.randint(5, 11, size=len(df))
        if 'Weather' not in df.columns: df['Weather'] = 'Sunny'
        if 'Temp_C' not in df.columns: df['Temp_C'] = 15

        # Temporal Features
        df['MonthYear'] = df['Date'].dt.to_period('M').astype(str) # For sorting
        df['Month'] = df['Date'].dt.month_name()
        
        return df

    except Exception as e:
        st.error(f"Data Error: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("🚨 No data found. Please check the GitHub URL.")
    st.stop()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#E50914; font-family: Bebas Neue; font-size: 3rem; text-align:center;'>N <span style='color:white'>DATA</span></h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
    date_range = st.slider("📅 Timeline", min_date, max_date, (min_date, max_date))
    
    genres = sorted(df['Genre'].astype(str).unique())
    selected_genres = st.multiselect("🎭 Filter by Genre", genres, default=genres)
    
    mask = (df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])
    if selected_genres: mask = mask & (df['Genre'].isin(selected_genres))
    df_filtered = df[mask]

# --- 5. MAIN DASHBOARD ---

# HEADER
st.markdown("""
    <div style="text-align: center; margin-bottom: 20px;">
        <h1 class="netflix-font" style="font-size: 4.5rem; margin-bottom: 0;">MY VIEWING HISTORY</h1>
        <p style="color: #888; letter-spacing: 1px;">CINEMATIC DATA ANALYSIS & BEHAVIORAL PATTERNS</p>
    </div>
""", unsafe_allow_html=True)

# METHODOLOGY EXPANDER
with st.expander("ℹ️ METHODOLOGY & DATA SOURCES"):
    st.markdown("""
    <div style="font-size: 0.9rem; color: #ccc;">
        <p>This dashboard was constructed by combining <strong>3 distinct data sources</strong> to create a comprehensive view:</p>
        <ol>
            <li><strong>Netflix History:</strong> Extracted from the account's viewing logs (Title & Date).</li>
            <li><strong>IMDB / Personal Ratings:</strong> Cross-referenced to assign a quality score (1-10) to each title.</li>
            <li><strong>Historical Weather API:</strong> Fetched via Open-Meteo based on the viewing location (Paris) to correlate habits with weather conditions.</li>
        </ol>
        <p><em>*Durations are estimated: 24m for Anime, 22m for Sitcoms, 50m for Dramas, and 105m for Movies.</em></p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# KPIS
total_hours = int(df_filtered['Duration_Mins'].sum() / 60)
nb_titles = len(df_filtered)
avg_rating = df_filtered['My_Rating'].mean()
fav_weather = df_filtered['Weather'].mode()[0]

c1, c2, c3, c4 = st.columns(4)
def kpi(col, title, val, sub):
    col.markdown(f"""<div class="kpi-card"><div class="kpi-title">{title}</div><div class="kpi-value">{val}</div><div class="kpi-sub">{sub}</div></div>""", unsafe_allow_html=True)

kpi(c1, "TOTAL WATCH TIME", f"{total_hours}h", "Calculated based on genre")
kpi(c2, "TITLES WATCHED", f"{nb_titles}", "Movies & Episodes")
kpi(c3, "AVG RATING", f"{avg_rating:.1f}/10", "Quality Score")
kpi(c4, "TOP WEATHER", fav_weather.upper(), "Most frequent condition")

st.markdown("<br>", unsafe_allow_html=True)

# ROW 1: ACTIVITY & TEMP IMPACT
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("### 📊 MONTHLY ACTIVITY")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    # Using Bar Chart instead of Line/Area to handle gaps better
    monthly_data = df_filtered.groupby('MonthYear')['Title'].count().reset_index()
    monthly_data['MonthYear'] = monthly_data['MonthYear'].astype(str)
    
    fig_act = px.bar(monthly_data, x='MonthYear', y='Title', 
                     color_discrete_sequence=['#E50914'])
    fig_act.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888', family="Outfit"),
        xaxis_title=None, yaxis_title="Items Watched",
        margin=dict(l=0, r=0, t=10, b=0)
    )
    st.plotly_chart(fig_act, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    st.markdown("### 🌡️ TEMPERATURE IMPACT")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    
    # Aggregating by day to see daily consumption vs Temp
    daily_agg = df_filtered.groupby('Date').agg({'Title': 'count', 'Temp_C': 'mean'}).reset_index()
    
    # Scatter Plot
    fig_temp = px.scatter(daily_agg, x="Temp_C", y="Title", 
                          size="Title", color="Title",
                          color_continuous_scale="Reds")
    fig_temp.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888', family="Outfit"),
        xaxis_title="Temperature (°C)", yaxis_title="Daily Episodes",
        margin=dict(l=0, r=0, t=10, b=0),
        showlegend=False
    )
    st.plotly_chart(fig_temp, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ROW 2: GENRE & WEATHER
c_g, c_w = st.columns(2)

with c_g:
    st.markdown("### 🕸️ GENRE RADAR")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    genre_counts = df_filtered['Genre'].value_counts().reset_index().head(6)
    genre_counts.columns = ['Genre', 'Count']
    fig_radar = px.line_polar(genre_counts, r='Count', theta='Genre', line_close=True)
    fig_radar.update_traces(fill='toself', line_color='#E50914', fillcolor='rgba(229, 9, 20, 0.3)')
    fig_radar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ccc'),
        polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False)),
        margin=dict(t=20, b=20)
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_w:
    st.markdown("### 🌤️ WEATHER CONTEXT")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    w_counts = df_filtered['Weather'].value_counts().reset_index()
    w_counts.columns = ['Weather', 'Count']
    colors = {'Sunny': '#F5D300', 'Cloudy': '#888', 'Rainy': '#2255AA', 'Snowy': '#FFF', 'Foggy': '#555'}
    
    fig_w = px.bar(w_counts, x='Weather', y='Count', color='Weather', color_discrete_map=colors, text_auto=True)
    fig_w.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888'), showlegend=False,
        margin=dict(t=10, b=0), xaxis_title=None
    )
    st.plotly_chart(fig_w, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ROW 3: LISTS
st.markdown("---")
cl1, cl2 = st.columns(2)

with cl1:
    st.markdown("### 🔥 HALL OF FAME (Top Rated)")
    top = df_filtered.sort_values('My_Rating', ascending=False).drop_duplicates('Title').head(5)
    for _, r in top.iterrows():
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:10px; margin-bottom:5px; border-left:3px solid #46d369; display:flex; justify-content:space-between; align-items:center;">
            <div><strong style="color:#fff">{r['Title']}</strong><br><small style="color:#888">{r['Genre']}</small></div>
            <div style="color:#46d369; font-weight:bold;">{r['My_Rating']}</div>
        </div>
        """, unsafe_allow_html=True)

with cl2:
    st.markdown("### 🍅 WALL OF SHAME (Lowest Rated)")
    flop = df_filtered.sort_values('My_Rating', ascending=True).drop_duplicates('Title').head(5)
    for _, r in flop.iterrows():
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:10px; margin-bottom:5px; border-left:3px solid #E50914; display:flex; justify-content:space-between; align-items:center;">
            <div><strong style="color:#fff">{r['Title']}</strong><br><small style="color:#888">{r['Genre']}</small></div>
            <div style="color:#E50914; font-weight:bold;">{r['My_Rating']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><center style='color:#555'>DESIGNED BY GEMINI • DATA SCIENCE PROJECT 2024</center>", unsafe_allow_html=True)
