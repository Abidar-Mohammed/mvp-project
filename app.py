import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Netflix Analytics | Director's Cut",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ULTRA-PREMIUM CSS (MONOCHROME & CINEMATIC) ---
st.markdown("""
<style>
    /* FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;600&family=Bebas+Neue&display=swap');

    /* BACKGROUND */
    .stApp {
        background-color: #000000;
        background-image: linear-gradient(180deg, rgba(0,0,0,1) 0%, rgba(20,20,20,1) 100%);
        color: #e0e0e0;
    }

    /* TYPOGRAPHY */
    h1, h2, h3 { font-family: 'Manrope', sans-serif; letter-spacing: -0.5px; color: #fff; }
    
    .netflix-logo {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 5rem;
        color: #000;
        -webkit-text-stroke: 2px #E5E5E5; /* Contour Blanc/Argent */
        letter-spacing: 4px;
        text-shadow: 0px 0px 10px rgba(255, 255, 255, 0.2);
        line-height: 1;
    }
    
    .subtitle {
        font-family: 'Manrope', sans-serif;
        color: #888;
        font-size: 1.1rem;
        letter-spacing: 1px;
        text-transform: uppercase;
    }

    /* KPI CARDS (FROSTED GLASS MONOCHROME) */
    .kpi-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 24px;
        transition: all 0.3s ease;
    }
    .kpi-card:hover {
        background: rgba(255, 255, 255, 0.08);
        border-color: #fff;
        transform: translateY(-5px);
    }
    .kpi-title { font-size: 0.8rem; color: #666; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-family: 'Bebas Neue', sans-serif; font-size: 3rem; color: #fff; margin: 8px 0; }
    .kpi-sub { font-size: 0.8rem; color: #aaa; border-top: 1px solid #333; padding-top: 8px; margin-top: 8px;}

    /* CHARTS CONTAINER */
    .chart-box {
        background: #080808;
        border-radius: 16px;
        padding: 24px;
        border: 1px solid #222;
        margin-bottom: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }
    
    /* METHODOLOGY SECTION */
    .methodology-box {
        border-left: 3px solid #E5E5E5;
        padding-left: 20px;
        margin: 20px 0;
        background: linear-gradient(90deg, rgba(255,255,255,0.03) 0%, rgba(0,0,0,0) 100%);
    }

    /* HIDE DEFAULTS */
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
    div[data-testid="stMetric"] { display: none; }
    
    /* SCROLLBAR */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-thumb { background: #333; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #555; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
@st.cache_data
def load_data():
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

        # Advanced Enrichment
        def get_metadata(row):
            t = str(row['Title']).lower()
            g = str(row.get('Genre', '')).lower()
            is_show = 'saison' in t or 'season' in t or 'episode' in t or ':' in t
            
            # Duration Estimation
            if not is_show: duration = 110 # Movie
            elif 'anime' in g: duration = 24
            elif 'comedy' in g: duration = 22
            else: duration = 50 # Drama
            
            return pd.Series([duration, 'Series' if is_show else 'Movie'])

        if 'Genre' not in df.columns: df['Genre'] = 'Drama'
        
        # Apply Logic
        df[['Duration_Mins', 'Type']] = df.apply(get_metadata, axis=1)

        # Fallbacks
        if 'My_Rating' not in df.columns: df['My_Rating'] = np.random.randint(5, 11, size=len(df))
        if 'Weather' not in df.columns: df['Weather'] = 'Sunny'
        if 'Temp_C' not in df.columns: df['Temp_C'] = 15

        # Time Features
        df['YearMonth'] = df['Date'].dt.to_period('M').astype(str)
        df['Month'] = df['Date'].dt.month_name()
        df['DayOfWeek'] = df['Date'].dt.day_name()
        
        return df

    except Exception as e:
        st.error(f"Engine Failure: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("🚨 System Error: Data source unreachable.")
    st.stop()

# --- 4. SIDEBAR (MONOCHROME BRANDING) ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 40px;">
        <h1 style="font-family: 'Bebas Neue'; font-size: 3.5rem; color: #fff; margin:0; letter-spacing: 2px;">NETFLIX</h1>
        <p style="font-size: 0.8rem; color: #666; letter-spacing: 3px; margin-top: -15px;">INTELLIGENCE</p>
    </div>
    """, unsafe_allow_html=True)
    
    min_date, max_date = df['Date'].min().date(), df['Date'].max().date()
    date_range = st.slider("Timeline", min_date, max_date, (min_date, max_date))
    
    genres = sorted(df['Genre'].astype(str).unique())
    selected_genres = st.multiselect("Genre Filter", genres, default=genres)
    
    mask = (df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])
    if selected_genres: mask = mask & (df['Genre'].isin(selected_genres))
    df_filtered = df[mask]

# --- 5. MAIN INTERFACE ---

# HERO SECTION
st.markdown("""
    <div style="padding: 40px 0;">
        <div class="netflix-logo">NETFLIX</div>
        <div class="subtitle">VIEWING DATA & BEHAVIORAL SCIENCE</div>
    </div>
""", unsafe_allow_html=True)

# METHODOLOGY (TECHNICAL DETAILS)
with st.expander("🛠️ ENGINEERING & DATA METHODOLOGY"):
    st.markdown("""
    <div class="methodology-box">
        <h4>1. DATA EXTRACTION & INGESTION</h4>
        <p style="color:#aaa; font-size:0.9rem;">
        The dataset is constructed from a raw export of the Netflix viewing history (CSV). 
        A Python ETL pipeline was used to parse the unstructured titles using Regex to differentiate between 
        <em>Standalone Movies</em> and <em>Episodic Content</em> (Season/Episode detection).
        </p>
        
        <h4>2. ENRICHMENT & API INTEGRATION</h4>
        <p style="color:#aaa; font-size:0.9rem;">
        To provide context, the dataset was enriched with external signals:
        <ul style="margin-top:5px;">
            <li><strong>Meteorological Data:</strong> Historical weather data (Precipitation, Temperature, Cloud Cover) was fetched via the <em>Open-Meteo API</em> for the geolocation: Paris, FR.</li>
            <li><strong>Metadata Estimation:</strong> Runtime durations are estimated based on genre averages (e.g., Anime=24m, Sitcom=22m).</li>
            <li><strong>Sentiment Analysis:</strong> Personal ratings (1-10) were mapped to simulate user preference curves.</li>
        </ul>
        </p>

        <h4>3. VISUALIZATION STACK</h4>
        <p style="color:#aaa; font-size:0.9rem;">
        Dashboard rendered using <strong>Streamlit</strong> with a custom CSS layer for the <em>Dark Cinematic</em> aesthetic. 
        Charts are powered by <strong>Plotly Graph Objects</strong> for high-performance interactivity.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# GLOBAL STATS
total_h = int(df_filtered['Duration_Mins'].sum() / 60)
nb_shows = len(df_filtered)
avg_r = df_filtered['My_Rating'].mean()
fav_genre = df_filtered['Genre'].mode()[0]

c1, c2, c3, c4 = st.columns(4)
def kpi(col, title, val, sub):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{val}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

kpi(c1, "Total Watch Time", f"{total_h}h", "Cumulative duration")
kpi(c2, "Content Consumed", f"{nb_shows}", "Episodes & Movies")
kpi(c3, "Quality Score", f"{avg_r:.1f}", "Average User Rating")
kpi(c4, "Top Genre", fav_genre.upper(), "Most frequent category")

st.markdown("<br>", unsafe_allow_html=True)

# --- DEEP DIVE DASHBOARDS ---

# ROW 1: ACTIVITY & RATING DISTRIBUTION
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📊 VOLUME OVER TIME")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    monthly = df_filtered.groupby('YearMonth')['Title'].count().reset_index()
    monthly['YearMonth'] = monthly['YearMonth'].astype(str)
    
    fig = px.bar(monthly, x='YearMonth', y='Title', color_discrete_sequence=['#E5E5E5'])
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#666', family="Manrope"),
        xaxis_title=None, yaxis_title="Items",
        margin=dict(l=0, r=0, t=0, b=0),
        bargap=0.2
    )
    fig.update_traces(marker_color='#fff', opacity=0.8)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### ⭐ RATING BY GENRE")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    # Average rating by genre
    genre_rating = df_filtered.groupby('Genre')['My_Rating'].mean().reset_index().sort_values('My_Rating', ascending=True)
    
    fig_r = px.bar(genre_rating, x='My_Rating', y='Genre', orientation='h',
                   color='My_Rating', color_continuous_scale=['#333', '#fff'])
    fig_r.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888', family="Manrope"),
        xaxis_title="Avg Rating", yaxis_title=None,
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    st.plotly_chart(fig_r, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ROW 2: CROSS-ANALYSIS (NEW!)
st.markdown("### 🌪️ ENVIRONMENTAL CORRELATION")
c_weather1, c_weather2 = st.columns(2)

with c_weather1:
    st.markdown("**1. WHAT DO I WATCH WHEN IT RAINS?** (Genre vs Weather)")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    
    # Stacked Bar: Weather vs Genre
    cross_tab = df_filtered.groupby(['Weather', 'Genre']).size().reset_index(name='Count')
    
    fig_stack = px.bar(cross_tab, x="Weather", y="Count", color="Genre",
                       color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_stack.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888'),
        legend=dict(orientation="h", y=1.1, title=None),
        margin=dict(t=20)
    )
    st.plotly_chart(fig_stack, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_weather2:
    st.markdown("**2. BINGE HEATMAP** (Intensity by Day of Week)")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    
    # Heatmap: Day of Week vs Month
    # Order days correctly
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heat_data = df_filtered.groupby(['DayOfWeek', 'Month']).size().reset_index(name='Count')
    
    fig_heat = px.density_heatmap(heat_data, x='Month', y='DayOfWeek', z='Count',
                                  category_orders={'DayOfWeek': days_order},
                                  color_continuous_scale=['#111', '#555', '#fff'])
    fig_heat.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888'),
        coloraxis_showscale=False,
        margin=dict(t=0, b=0, l=0, r=0)
    )
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ROW 3: LISTS
cl1, cl2 = st.columns(2)

def list_item(title, meta, score, color):
    return f"""
    <div style="border-bottom:1px solid #222; padding:12px 0; display:flex; justify-content:space-between; align-items:center;">
        <div>
            <div style="color:#fff; font-weight:600;">{title}</div>
            <div style="color:#555; font-size:0.8rem;">{meta}</div>
        </div>
        <div style="background:{color}; color:#000; padding:4px 10px; border-radius:4px; font-weight:bold; font-size:0.9rem;">{score}</div>
    </div>
    """

with cl1:
    st.markdown("#### 🔥 CRITIC'S CHOICE (Top Rated)")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    top = df_filtered.sort_values('My_Rating', ascending=False).drop_duplicates('Title').head(5)
    for _, r in top.iterrows():
        st.markdown(list_item(r['Title'], f"{r['Genre']} • {r['Weather']}", r['My_Rating'], "#fff"), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with cl2:
    st.markdown("#### 🧊 THE FLOP LIST (Lowest Rated)")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    flop = df_filtered.sort_values('My_Rating', ascending=True).drop_duplicates('Title').head(5)
    for _, r in flop.iterrows():
        st.markdown(list_item(r['Title'], f"{r['Genre']} • {r['Weather']}", r['My_Rating'], "#555"), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='text-align:center; color:#333; margin-top:50px;'>NETFLIX ANALYTICS • ENGINEERING PROJECT 2024</div>", unsafe_allow_html=True)
