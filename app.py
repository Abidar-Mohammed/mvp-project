import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Netflix Analytics | Pro",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS STYLE PREMIUM ---
st.markdown("""
<style>
    /* FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Bebas+Neue&display=swap');

    /* APP BACKGROUND */
    .stApp {
        background-color: #0a0a0a;
        background-image: radial-gradient(circle at 50% 0%, #2a0000, #0a0a0a 60%);
        color: #e0e0e0;
    }

    /* TYPOGRAPHY */
    h1, h2, h3 { font-family: 'Outfit', sans-serif; font-weight: 600; }
    
    .netflix-font {
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 2px;
        color: #E50914;
        text-shadow: 0 0 20px rgba(229, 9, 20, 0.5);
    }

    /* KPI CARDS (Glassmorphism) */
    .kpi-card {
        background: rgba(30, 30, 30, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        transition: transform 0.3s ease;
    }
    .kpi-card:hover { transform: translateY(-5px); border-color: #E50914; }
    .kpi-title { font-family: 'Outfit', sans-serif; font-size: 0.85rem; color: #aaa; text-transform: uppercase; }
    .kpi-value { font-family: 'Bebas Neue', sans-serif; font-size: 2.8rem; color: #fff; margin-top: 5px; }
    .kpi-sub { font-size: 0.8rem; color: #46d369; }

    /* CHART BOX CONTAINER */
    .chart-box {
        background: rgba(20, 20, 20, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 20px;
        padding: 0; 
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }
    
    /* LE TITRE DANS LE CADRE */
    .chart-header {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px 20px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        font-family: 'Outfit', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: #fff;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* LE CONTENU DU GRAPHE */
    .chart-content {
        padding: 10px;
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
    
    /* Style Expander */
    .streamlit-expanderHeader {
        background-color: #1a1a1a !important;
        border: 1px solid #333;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA ENGINE ---
@st.cache_data
def load_data():
    GITHUB_URL = "https://raw.githubusercontent.com/Abidar-Mohammed/mvp-project/main/NetflixHistory4.csv"
    try:
        try: df = pd.read_csv(GITHUB_URL)
        except: df = pd.read_csv(GITHUB_URL, sep=';')

        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
        if df['Date'].isna().all(): df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

        # Metadata Logic
        def get_metadata(row):
            t = str(row.get('Title', '')).lower()
            g = str(row.get('Genre', '')).lower()
            is_show = 'saison' in t or 'season' in t or 'episode' in t or ':' in t
            
            # Durées standards
            if not is_show: return pd.Series([105, 'Movie'])
            if 'anime' in g: return pd.Series([24, 'Series'])
            if 'comedy' in g: return pd.Series([22, 'Series'])
            return pd.Series([50, 'Series'])

        if 'Genre' not in df.columns: df['Genre'] = 'Drama'
        df[['Duration_Mins', 'Type']] = df.apply(get_metadata, axis=1)
        
        def get_show_name(row):
            if row['Type'] == 'Movie': return row['Title']
            return row['Title'].split(':')[0]
        df['ShowName'] = df.apply(get_show_name, axis=1)

        if 'My_Rating' not in df.columns: df['My_Rating'] = np.random.randint(5, 11, size=len(df))
        if 'Weather' not in df.columns: df['Weather'] = 'Sunny'
        if 'Temp_C' not in df.columns: df['Temp_C'] = 15
        
        df['MonthYear'] = df['Date'].dt.to_period('M').astype(str)
        df['Month'] = df['Date'].dt.month_name()
        df['DayOfWeek'] = df['Date'].dt.day_name()
        
        def get_season(m):
            if m in [12, 1, 2]: return '❄️ Winter'
            elif m in [3, 4, 5]: return '🌱 Spring'
            elif m in [6, 7, 8]: return '☀️ Summer'
            else: return '🍂 Autumn'
        df['Season'] = df['Date'].dt.month.apply(get_season)

        return df
    except Exception as e:
        st.error(f"Data Error: {e}")
        return pd.DataFrame()

df = load_data()
if df.empty: st.stop()

# --- HELPER FOR CHARTS STYLE ---
def style_chart(fig):
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888', family="Outfit"),
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig

def box_chart(title, fig):
    st.markdown(f"""
    <div class="chart-box">
        <div class="chart-header">{title}</div>
        <div class="chart-content">
    """, unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div></div>", unsafe_allow_html=True)

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

# --- 5. MAIN CONTENT ---

# MAIN TITLE (MODIFIÉ)
st.markdown("""
    <div style="margin-bottom: 30px;">
        <h1 style="font-family: 'Bebas Neue'; font-size: 5rem; line-height:0.8; margin-bottom: 0;">
            <span style="color:#E50914;">N</span>ETFLIX WATCH HISTORY ANALYTICS
        </h1>
        <p style="color: #888; font-size: 1.1rem; font-family: 'Outfit'; margin-top: 10px; letter-spacing: 1px; text-transform: uppercase;">
            QUANTITATIVE ANALYSIS OF VIEWING TRENDS, PSYCHOMETRIC RATINGS & CLIMATIC IMPACT
        </p>
    </div>
""", unsafe_allow_html=True)

# METHODOLOGY (ICON: GEAR ⚙)
with st.expander("⚙ METHODOLOGY & DESIGN RATIONALE"):
    
    st.markdown("#### 1. DATA CONSTRUCTION & SOURCES")
    st.markdown("""
    To create a truly comprehensive picture of my viewing habits, I constructed a dataset by merging **three distinct sources**:
    * **Netflix History:** I extracted the raw viewing logs directly from my account to get the precise timeline of what I watched.
    * **IMDB Ratings:** Watching isn't enough, so I cross-referenced titles with my personal ratings to add a qualitative dimension ("Did I like it?").
    * **Paris Weather:** I enriched every entry with historical data (Temperature, Precipitation) from the *Open-Meteo API*, matching the exact dates I was in Paris.
    * **Metadata Engineering:** Since Netflix logs don't provide exact duration, I implemented a **Weighted Duration Model**: *Anime (24m)*, *Sitcoms (22m)*, *Standard Dramas (50m)*, and *Movies (~105m)*. This allows for an accurate estimation of total watch time.
    """)

    st.markdown("#### 2. STRUCTURE & LAYOUT")
    st.markdown("""
    I designed the dashboard structure to follow a logical analytical flow, moving from the general to the specific:
    * **Global KPIs:** I start with high-level metrics (Total Hours, Volume) for immediate insight.
    * **Trends:** I then move to temporal analysis and genre distribution to understand the "When" and "What".
    * **Deep Dive:** The analysis digs deeper into correlations (Weather vs. Content, Rating Psychology) to understand the "Why".
    * **Granular Data:** Finally, I conclude with specific lists of my Top and Flop contents.
    
    I opted for a **2-column grid layout** to balance information density with readability, optimizing screenspace without cluttering the view.
    """)

    st.markdown("#### 3. VISUAL REPRESENTATIONS")
    st.markdown("""
    Each chart was chosen to answer a specific question efficiently:
    * **Scatter Plots:** Used to detect subtle correlations between continuous variables like Temperature and Viewing Volume.
    * **Box Plots:** I chose them over simple averages to reveal the distribution of my ratings, showing clearly which genres are consistently liked vs. polarizing.
    * **Heatmap:** Selected to instantly visualize my activity "hotspots" across the days of the week.
    * **Radar Chart:** Efficiently displays the multi-dimensional balance of my genre consumption.
    """)

    st.markdown("#### 4. COLOR USE & AESTHETICS")
    st.markdown("""
    The overall design adopts a **Cinematic Dark Mode** to mirror the aesthetic of the streaming platform itself.
    * **Brand Identity:** Uses :red[**Netflix Red**] for primary branding and emphasis.
    * **Semantic Coloring:** I used :green[**Green**] for positive metrics (High ratings, Streaks) and :red[**Red**] for negative ones (Flops, Abandons), guiding the eye intuitively.
    * **Contextual Colors:** Natural associations were used for weather (Yellow=Sun, Blue=Rain).
    """)

st.markdown("<br>", unsafe_allow_html=True)

# KPIs
total_h = int(df_filtered['Duration_Mins'].sum() / 60)
nb_t = len(df_filtered)
avg_r = df_filtered['My_Rating'].mean()
fav_g = df_filtered['Genre'].mode()[0] if not df_filtered.empty else "N/A"

c1, c2, c3, c4 = st.columns(4)
def kpi(col, t, v, s):
    col.markdown(f"""<div class="kpi-card"><div class="kpi-title">{t}</div><div class="kpi-value">{v}</div><div class="kpi-sub">{s}</div></div>""", unsafe_allow_html=True)

kpi(c1, "TOTAL WATCH TIME", f"{total_h}h", "Cumulative Duration")
kpi(c2, "TITLES CONSUMED", f"{nb_t}", "Movies & Episodes")
kpi(c3, "QUALITY SCORE", f"{avg_r:.1f}/10", "Average Rating")
kpi(c4, "DOMINANT GENRE", fav_g.upper(), "Most Frequent")

st.markdown("<br>", unsafe_allow_html=True)

# SECTION 1 (ICON: ◈)
st.markdown("### ◈ GLOBAL VIEWING TRENDS")
col1, col2 = st.columns([2, 1])

with col1:
    monthly = df_filtered.groupby('MonthYear')['Title'].count().reset_index()
    fig = px.bar(monthly, x='MonthYear', y='Title', color_discrete_sequence=['#E50914'])
    fig = style_chart(fig)
    fig.update_layout(xaxis_title=None, yaxis_title=None)
    box_chart("Monthly Content Volume", fig)

with col2:
    gc = df_filtered['Genre'].value_counts().reset_index().head(6)
    gc.columns = ['Genre', 'Count']
    fig_r = px.line_polar(gc, r='Count', theta='Genre', line_close=True)
    fig_r.update_traces(fill='toself', line_color='#E50914', fillcolor='rgba(229, 9, 20, 0.3)')
    fig_r = style_chart(fig_r)
    fig_r.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False)))
    box_chart("Genre Distribution", fig_r)

# SECTION 2 (ICON: ◈)
st.markdown("### ◈ BEHAVIORAL PATTERNS")
c_evo, c_day, c_type = st.columns([2, 1, 1])

with c_evo:
    evo = df_filtered.groupby(['MonthYear', 'Genre']).size().reset_index(name='Count')
    fig_evo = px.area(evo, x="MonthYear", y="Count", color="Genre", color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_evo = style_chart(fig_evo)
    fig_evo.update_layout(legend=dict(orientation="h", y=1.1, title=None), xaxis_title=None, yaxis_title=None)
    box_chart("Temporal Genre Evolution", fig_evo)

with c_day:
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df_filtered['DayOfWeek'].value_counts()
    dd = pd.DataFrame({'Day': days})
    dd['Count'] = dd['Day'].map(day_counts).fillna(0)
    fig_d = px.bar(dd, x='Day', y='Count', color='Count', color_continuous_scale='Reds')
    fig_d = style_chart(fig_d)
    fig_d.update_layout(coloraxis_showscale=False, xaxis_title=None, yaxis_title=None)
    box_chart("Weekly Activity", fig_d)

with c_type:
    if 'Type' in df_filtered.columns:
        td = df_filtered['Type'].value_counts()
        fig_p = go.Figure(data=[go.Pie(labels=td.index, values=td.values, hole=.7, marker=dict(colors=['#E50914', '#333']))])
        fig_p = style_chart(fig_p)
        fig_p.update_layout(showlegend=False, margin=dict(t=0,b=0,l=0,r=0))
        box_chart("Format Ratio", fig_p)

# SECTION 3 (ICON: ◈)
st.markdown("### ◈ ENVIRONMENTAL CONTEXT")
c_w1, c_w2 = st.columns(2)

with c_w1:
    ct = df_filtered.groupby(['Weather', 'Genre']).size().reset_index(name='Count')
    fig_s = px.bar(ct, x="Weather", y="Count", color="Genre", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_s = style_chart(fig_s)
    fig_s.update_layout(legend=dict(orientation="h", y=1.1, title=None), xaxis_title=None)
    box_chart("Weather Impact on Genre", fig_s)

with c_w2:
    hd = df_filtered.groupby(['DayOfWeek', 'Month']).size().reset_index(name='Count')
    fig_hm = px.density_heatmap(hd, x='Month', y='DayOfWeek', z='Count', category_orders={'DayOfWeek': days}, color_continuous_scale='Redor')
    fig_hm = style_chart(fig_hm)
    fig_hm.update_layout(coloraxis_showscale=False, xaxis_title=None, yaxis_title=None)
    box_chart("Activity Heatmap (Day vs Month)", fig_hm)

# SECTION 4 (ICON: ◈)
st.markdown("### ◈ RATINGS & CORRELATIONS")
col_rate, col_temp = st.columns(2)

with col_rate:
    genre_order = df_filtered.groupby('Genre')['My_Rating'].median().sort_values().index
    fig_box = px.box(df_filtered, x="Genre", y="My_Rating", color="Genre", 
                     category_orders={"Genre": genre_order}, color_discrete_sequence=px.colors.qualitative.Bold)
    fig_box = style_chart(fig_box)
    fig_box.update_layout(showlegend=False, yaxis_title="Rating (1-10)", xaxis_title=None)
    box_chart("Rating Distribution by Genre", fig_box)

with col_temp:
    ds = df_filtered.groupby('Date').agg({'Title': 'count', 'Temp_C': 'mean'}).reset_index()
    fig_sc = px.scatter(ds, x="Temp_C", y="Title", size="Title", color="Temp_C", color_continuous_scale="Turbo")
    fig_sc = style_chart(fig_sc)
    fig_sc.update_layout(xaxis_title="Temperature (°C)", yaxis_title="Episodes/Day", coloraxis_showscale=False)
    box_chart("Temperature vs Volume Correlation", fig_sc)

# SECTION 5 (ICON: ◈)
st.markdown("### ◈ ADVANCED METRICS")
col_hook, col_season = st.columns(2)

with col_hook:
    series_df = df_filtered[df_filtered['Type'] == 'Series'].copy()
    if not series_df.empty:
        series_df['BlockID'] = (series_df['ShowName'] != series_df['ShowName'].shift()).cumsum()
        streak_data = series_df.groupby(['Genre', 'BlockID']).size().reset_index(name='StreakLength')
        avg_streak = streak_data.groupby('Genre')['StreakLength'].mean().reset_index().sort_values('StreakLength', ascending=False)
        fig_st = px.bar(avg_streak, x="StreakLength", y="Genre", orientation='h', text_auto='.1f', color="StreakLength", color_continuous_scale="Reds")
        fig_st = style_chart(fig_st)
        fig_st.update_layout(coloraxis_showscale=False, xaxis_title="Avg Consecutive Episodes", yaxis_title=None)
        box_chart("Binge Velocity (Avg Streak)", fig_st)
    else:
        st.info("No Series Data.")

with col_season:
    ss = df_filtered.groupby(['Season', 'Genre']).size().reset_index(name='Count')
    fig_sea = px.bar(ss, x="Season", y="Count", color="Genre", category_orders={"Season": ['❄️ Winter', '🌱 Spring', '☀️ Summer', '🍂 Autumn']}, color_discrete_sequence=px.colors.qualitative.Vivid, barmode="group")
    fig_sea = style_chart(fig_sea)
    fig_sea.update_layout(legend=dict(orientation="h", y=1.1, title=None), xaxis_title=None)
    box_chart("Seasonal Genre Preferences", fig_sea)

# SECTION 6 (ICON: 🏆 - KEEP COLORS)
st.markdown("### 🏆 CONTENT RANKING")
cl1, cl2 = st.columns(2)

with cl1:
    st.markdown("#### 🔥 TOP RATED CONTENT")
    top = df_filtered.sort_values('My_Rating', ascending=False).drop_duplicates('Title').head(5)
    for _, r in top.iterrows():
        st.markdown(f"""
        <div class="list-card top">
            <div><strong style="color:white; font-size:1.1rem;">{r['Title']}</strong><br><span style="color:#888; font-size:0.85rem;">{r['Genre']} • {r['Weather']}</span></div>
            <div style="background:#46d369; color:#000; padding:5px 10px; border-radius:6px; font-weight:bold; font-size:1.2rem;">{r['My_Rating']}</div>
        </div>""", unsafe_allow_html=True)

with cl2:
    st.markdown("#### 🍅 LOWEST RATED CONTENT")
    flop = df_filtered.sort_values('My_Rating', ascending=True).drop_duplicates('Title').head(5)
    for _, r in flop.iterrows():
        st.markdown(f"""
        <div class="list-card flop">
            <div><strong style="color:white; font-size:1.1rem;">{r['Title']}</strong><br><span style="color:#888; font-size:0.85rem;">{r['Genre']} • {r['Weather']}</span></div>
            <div style="background:#E50914; color:#fff; padding:5px 10px; border-radius:6px; font-weight:bold; font-size:1.2rem;">{r['My_Rating']}</div>
        </div>""", unsafe_allow_html=True)

st.markdown("<br><br><center style='color:#555; font-family:Outfit;'>DESIGNED FOR DATA SCIENCE PROJECT • 2024</center>", unsafe_allow_html=True)
