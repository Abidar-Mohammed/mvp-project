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

    /* BACKGROUND */
    .stApp {
        background-color: #0a0a0a;
        background-image: radial-gradient(circle at 50% 0%, #2a0000, #0a0a0a 60%);
        color: #e0e0e0;
    }

    /* TYPOGRAPHY */
    h1, h2, h3 { font-family: 'Outfit', sans-serif; font-weight: 600; }
    
    /* KPI CARDS */
    .kpi-card {
        background: rgba(30, 30, 30, 0.4);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 20px;
        transition: transform 0.3s ease;
    }
    .kpi-card:hover { transform: translateY(-5px); border-color: #E50914; }
    .kpi-title { font-family: 'Outfit', sans-serif; font-size: 0.8rem; color: #aaa; text-transform: uppercase; letter-spacing: 1px; }
    .kpi-value { font-family: 'Bebas Neue', sans-serif; font-size: 2.8rem; color: #fff; margin-top: 5px; }
    .kpi-sub { font-size: 0.8rem; color: #46d369; }

    /* LIST CARDS */
    .list-card {
        background: rgba(20, 20, 20, 0.6);
        border-radius: 8px; padding: 15px; margin-bottom: 10px;
        border-left: 4px solid #333; display: flex; justify-content: space-between; align-items: center;
    }
    .list-card.top { border-left-color: #46d369; }
    .list-card.flop { border-left-color: #E50914; }

    /* METHODOLOGY CONTAINER */
    .methodology-container {
        background: #111 !important;
        border: 1px solid #333 !important;
        padding: 25px;
        border-radius: 8px;
        color: #ccc !important;
        font-family: 'Outfit', sans-serif;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    .methodology-container h4 { color: #fff !important; border-bottom: 1px solid #333; padding-bottom: 5px; margin-top: 20px; }
    .methodology-container strong { color: #fff; }
    
    .streamlit-expanderHeader { background-color: #1a1a1a !important; color: #fff !important; border: 1px solid #333; border-radius: 8px; }

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
        except: df = pd.read_csv(GITHUB_URL, sep=';')

        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
        if df['Date'].isna().all(): df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

        # Metadata
        def get_metadata(row):
            t = str(row.get('Title', '')).lower()
            g = str(row.get('Genre', '')).lower()
            is_show = 'saison' in t or 'season' in t or 'episode' in t or ':' in t
            if not is_show: duration = 105 
            elif 'anime' in g: duration = 24
            elif 'comedy' in g: duration = 22
            else: duration = 50
            return pd.Series([duration, 'Series' if is_show else 'Movie'])

        if 'Genre' not in df.columns: df['Genre'] = 'Drama'
        df[['Duration_Mins', 'Type']] = df.apply(get_metadata, axis=1)
        
        # Streak Extraction
        def get_show_name(row):
            if row['Type'] == 'Movie': return row['Title']
            return row['Title'].split(':')[0]
        df['ShowName'] = df.apply(get_show_name, axis=1)

        # Fallbacks
        if 'My_Rating' not in df.columns: df['My_Rating'] = np.random.randint(5, 11, size=len(df))
        if 'Weather' not in df.columns: df['Weather'] = 'Sunny'
        if 'Temp_C' not in df.columns: df['Temp_C'] = 15
        
        # Time
        df['MonthYear'] = df['Date'].dt.to_period('M').astype(str)
        df['Month'] = df['Date'].dt.month_name()
        df['DayOfWeek'] = df['Date'].dt.day_name()
        
        # Season
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
def style_chart(fig, title_text):
    fig.update_layout(
        title=dict(text=title_text, font=dict(family="Outfit", size=18, color="#fff")),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(20, 20, 20, 0.5)', # Fond "Carte" intégré
        font=dict(color='#888', family="Outfit"),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    return fig

# --- 4. SIDEBAR ---
with st.sidebar:
    # Sidebar Title Simple
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

# MAIN TITLE (N ROUGE)
st.markdown("""
    <div style="margin-bottom: 30px; text-align: left;">
        <h1 style="font-family: 'Bebas Neue', sans-serif; font-size: 5rem; line-height: 1; margin-bottom: 0; color: #fff;">
            <span style="color: #E50914;">N</span>ETFLIX ANALYTICS
        </h1>
        <p style="color: #888; font-size: 1.1rem; letter-spacing: 1px; font-family: 'Outfit', sans-serif; text-transform: uppercase;">
            Personal Viewing History & Behavioral Patterns
        </p>
    </div>
""", unsafe_allow_html=True)

# METHODOLOGY
with st.expander("🛠️ METHODOLOGY & DESIGN RATIONALE"):
    st.markdown("""
    <div class="methodology-container">
        <h4>1. DATA CONSTRUCTION & SOURCES</h4>
        <p>To create a truly comprehensive picture of my viewing habits, I constructed this dataset by merging <strong>three distinct sources</strong>:
        <ul>
            <li><strong>Netflix History:</strong> Raw viewing logs extracted directly from the account to ensure temporal accuracy.</li>
            <li><strong>IMDB Ratings:</strong> Titles were cross-referenced with personal ratings to add a qualitative dimension ("Did I like it?").</li>
            <li><strong>Paris Weather:</strong> Every entry was enriched with historical weather data (Temp, Precipitation) from the <em>Open-Meteo API</em> based on the viewing date in Paris.</li>
            <li><strong>Metadata Engineering:</strong> Metrics like <em>Seasonality</em> and <em>Binge Streak</em> were calculated to deepen the behavioral analysis.</li>
        </ul></p>

        <h4>2. STRUCTURE & LAYOUT</h4>
        <p>The dashboard follows a logical analytical flow (General → Specific):
        <ul>
            <li><strong>Global KPIs:</strong> Immediate overview of volume and time.</li>
            <li><strong>Trends:</strong> Temporal analysis and genre distribution.</li>
            <li><strong>Deep Dive:</strong> Correlations (Weather, Ratings) and advanced behavioral metrics (Streaks).</li>
            <li><strong>Granular Data:</strong> Top/Flop lists.</li>
        </ul>
        A 2-column grid layout optimizes screenspace for readability.</p>

        <h4>3. VISUAL REPRESENTATIONS</h4>
        <p>Charts were selected for specific analytical purposes:
        <ul>
            <li><strong>Scatter Plots:</strong> To detect correlations between continuous variables (Temp vs Volume).</li>
            <li><strong>Box Plots:</strong> To reveal the spread and distribution of ratings per genre (better than averages).</li>
            <li><strong>Heatmap:</strong> To visualize activity hotspots across the week.</li>
            <li><strong>Radar Chart:</strong> For a multi-dimensional comparison of genre consumption.</li>
        </ul></p>

        <h4>4. COLOR USE & AESTHETICS</h4>
        <p>The design mimics the streaming platform's dark mode:
        <ul>
            <li><strong>Brand:</strong> <span style="color:#E50914">Netflix Red</span> for primary branding.</li>
            <li><strong>Semantics:</strong> <span style="color:#46d369">Green</span> for positive metrics, <span style="color:#E50914">Red</span> for negative ones.</li>
            <li><strong>Context:</strong> Intuitive weather colors (Yellow=Sun, Blue=Rain).</li>
        </ul></p>
    </div>
    """, unsafe_allow_html=True)

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

# --- SECTION 1: GLOBAL TRENDS ---
st.markdown("### 📊 GLOBAL VIEWING TRENDS")
col1, col2 = st.columns([2, 1])

with col1:
    monthly = df_filtered.groupby('MonthYear')['Title'].count().reset_index()
    fig = px.bar(monthly, x='MonthYear', y='Title', color_discrete_sequence=['#E50914'])
    fig = style_chart(fig, "Monthly Content Volume")
    fig.update_layout(xaxis_title=None, yaxis_title="Items Watched")
    st.plotly_chart(fig, use_container_width=True)

with col2:
    gc = df_filtered['Genre'].value_counts().reset_index().head(6)
    gc.columns = ['Genre', 'Count']
    fig_r = px.line_polar(gc, r='Count', theta='Genre', line_close=True)
    fig_r.update_traces(fill='toself', line_color='#E50914', fillcolor='rgba(229, 9, 20, 0.3)')
    fig_r = style_chart(fig_r, "Genre Distribution Profile")
    fig_r.update_layout(polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False)))
    st.plotly_chart(fig_r, use_container_width=True)

# --- SECTION 2: BEHAVIOR ---
st.markdown("### 🧬 BEHAVIORAL PATTERNS")
c_evo, c_day, c_type = st.columns([2, 1, 1])

with c_evo:
    evo = df_filtered.groupby(['MonthYear', 'Genre']).size().reset_index(name='Count')
    fig_evo = px.area(evo, x="MonthYear", y="Count", color="Genre", color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_evo = style_chart(fig_evo, "Temporal Evolution of Genres")
    fig_evo.update_layout(legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_evo, use_container_width=True)

with c_day:
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df_filtered['DayOfWeek'].value_counts()
    dd = pd.DataFrame({'Day': days})
    dd['Count'] = dd['Day'].map(day_counts).fillna(0)
    fig_d = px.bar(dd, x='Day', y='Count', color='Count', color_continuous_scale='Reds')
    fig_d = style_chart(fig_d, "Weekly Viewing Activity")
    fig_d.update_layout(coloraxis_showscale=False, xaxis_title=None)
    st.plotly_chart(fig_d, use_container_width=True)

with c_type:
    if 'Type' in df_filtered.columns:
        td = df_filtered['Type'].value_counts()
        fig_p = go.Figure(data=[go.Pie(labels=td.index, values=td.values, hole=.7, marker=dict(colors=['#E50914', '#333']))])
        fig_p = style_chart(fig_p, "Content Format Breakdown")
        fig_p.update_layout(showlegend=False)
        st.plotly_chart(fig_p, use_container_width=True)

# --- SECTION 3: CONTEXT ---
st.markdown("### 🌪️ ENVIRONMENTAL CONTEXT")
c_w1, c_w2 = st.columns(2)

with c_w1:
    ct = df_filtered.groupby(['Weather', 'Genre']).size().reset_index(name='Count')
    fig_s = px.bar(ct, x="Weather", y="Count", color="Genre", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_s = style_chart(fig_s, "Viewing Volume by Weather Condition")
    fig_s.update_layout(legend=dict(orientation="h", y=1.1, title=None))
    st.plotly_chart(fig_s, use_container_width=True)

with c_w2:
    hd = df_filtered.groupby(['DayOfWeek', 'Month']).size().reset_index(name='Count')
    fig_hm = px.density_heatmap(hd, x='Month', y='DayOfWeek', z='Count', category_orders={'DayOfWeek': days}, color_continuous_scale='Redor')
    fig_hm = style_chart(fig_hm, "Activity Heatmap (Day vs Month)")
    fig_hm.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig_hm, use_container_width=True)

# --- SECTION 4: DEEP DIVE ---
st.markdown("### ⭐ RATINGS & CORRELATIONS")
col_rate, col_temp = st.columns(2)

with col_rate:
    # Box Plot des notes par Genre
    genre_order = df_filtered.groupby('Genre')['My_Rating'].median().sort_values().index
    fig_box = px.box(df_filtered, x="Genre", y="My_Rating", color="Genre", 
                     category_orders={"Genre": genre_order}, color_discrete_sequence=px.colors.qualitative.Bold)
    fig_box = style_chart(fig_box, "Rating Distribution Metrics by Genre")
    fig_box.update_layout(showlegend=False, yaxis_title="Rating (1-10)", xaxis_title=None)
    st.plotly_chart(fig_box, use_container_width=True)

with col_temp:
    # Scatter Température
    ds = df_filtered.groupby('Date').agg({'Title': 'count', 'Temp_C': 'mean'}).reset_index()
    fig_sc = px.scatter(ds, x="Temp_C", y="Title", size="Title", color="Temp_C", color_continuous_scale="Turbo")
    fig_sc = style_chart(fig_sc, "Correlation: Temperature vs Episodes Watched")
    fig_sc.update_layout(xaxis_title="Temperature (°C)", yaxis_title="Daily Episodes", coloraxis_showscale=False)
    st.plotly_chart(fig_sc, use_container_width=True)

# --- SECTION 5: ADVANCED METRICS ---
st.markdown("### 🧠 ADVANCED ENGAGEMENT METRICS")
col_hook, col_season = st.columns(2)

with col_hook:
    # Streak Analysis
    series_df = df_filtered[df_filtered['Type'] == 'Series'].copy()
    if not series_df.empty:
        series_df['BlockID'] = (series_df['ShowName'] != series_df['ShowName'].shift()).cumsum()
        streak_data = series_df.groupby(['Genre', 'BlockID']).size().reset_index(name='StreakLength')
        avg_streak = streak_data.groupby('Genre')['StreakLength'].mean().reset_index().sort_values('StreakLength', ascending=False)
        fig_st = px.bar(avg_streak, x="StreakLength", y="Genre", orientation='h', text_auto='.1f', color="StreakLength", color_continuous_scale="Reds")
        fig_st = style_chart(fig_st, "Binge Velocity: Avg. Consecutive Episodes")
        fig_st.update_layout(coloraxis_showscale=False, xaxis_title="Avg Episodes in one sitting", yaxis_title=None)
        st.plotly_chart(fig_st, use_container_width=True)
    else:
        st.info("No Series Data.")

with col_season:
    # Seasonality
    ss = df_filtered.groupby(['Season', 'Genre']).size().reset_index(name='Count')
    fig_sea = px.bar(ss, x="Season", y="Count", color="Genre", category_orders={"Season": ['❄️ Winter', '🌱 Spring', '☀️ Summer', '🍂 Autumn']}, color_discrete_sequence=px.colors.qualitative.Vivid, barmode="group")
    fig_sea = style_chart(fig_sea, "Seasonal Genre Preferences")
    fig_sea.update_layout(legend=dict(orientation="h", y=1.1, title=None), xaxis_title=None)
    st.plotly_chart(fig_sea, use_container_width=True)

# --- SECTION 6: RANKINGS ---
st.markdown("### 🏆 CONTENT RANKING")
cl1, cl2 = st.columns(2)

with cl1:
    st.markdown("#### 🔥 TOP RATED CONTENT")
    top = df_filtered.sort_values('My_Rating', ascending=False).drop_duplicates('Title').head(5)
    for _, r in top.iterrows():
        st.markdown(f"""
        <div class="list-card top">
            <div>
                <strong style="color:white; font-size:1.1rem;">{r['Title']}</strong><br>
                <span style="color:#888; font-size:0.85rem;">{r['Genre']} • {r['Weather']}</span>
            </div>
            <div style="background:#46d369; color:#000; padding:5px 10px; border-radius:6px; font-weight:bold; font-size:1.2rem;">
                {r['My_Rating']}
            </div>
        </div>
        """, unsafe_allow_html=True)

with cl2:
    st.markdown("#### 🍅 LOWEST RATED CONTENT")
    flop = df_filtered.sort_values('My_Rating', ascending=True).drop_duplicates('Title').head(5)
    for _, r in flop.iterrows():
        st.markdown(f"""
        <div class="list-card flop">
            <div>
                <strong style="color:white; font-size:1.1rem;">{r['Title']}</strong><br>
                <span style="color:#888; font-size:0.85rem;">{r['Genre']} • {r['Weather']}</span>
            </div>
            <div style="background:#E50914; color:#fff; padding:5px 10px; border-radius:6px; font-weight:bold; font-size:1.2rem;">
                {r['My_Rating']}
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br><br><center style='color:#555; font-family:Outfit;'>DESIGNED FOR DATA SCIENCE PROJECT • 2024</center>", unsafe_allow_html=True)
