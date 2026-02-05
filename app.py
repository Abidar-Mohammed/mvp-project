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

    /* --- METHODOLOGY SECTION (ACADEMIC STYLE - B&W) --- */
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
    .methodology-container h4 { 
        color: #fff !important; 
        border-bottom: 1px solid #333; 
        padding-bottom: 5px; 
        margin-top: 20px; 
        font-family: 'Outfit', sans-serif;
        letter-spacing: 1px;
    }
    .methodology-container ul { margin-bottom: 10px; }
    .methodology-container li { margin-bottom: 5px; color: #aaa; }
    .methodology-container strong { color: #fff; }
    
    /* Streamlit Expander Styling */
    .streamlit-expanderHeader { 
        background-color: #1a1a1a !important; 
        color: #fff !important; 
        border: 1px solid #333; 
        border-radius: 8px;
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
    # URL GITHUB
    GITHUB_URL = "https://raw.githubusercontent.com/Abidar-Mohammed/mvp-project/main/NetflixHistory4.csv"
    
    try:
        try: df = pd.read_csv(GITHUB_URL)
        except: 
            # Fallback point-virgule
            df = pd.read_csv(GITHUB_URL, sep=';')

        # Date Parsing
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
        if df['Date'].isna().all(): df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])

        # Metadata Engineering
        def get_metadata(row):
            t = str(row.get('Title', '')).lower()
            g = str(row.get('Genre', '')).lower()
            is_show = 'saison' in t or 'season' in t or 'episode' in t or ':' in t
            
            # Duration logic
            if not is_show: duration = 105 
            elif 'anime' in g: duration = 24
            elif 'comedy' in g: duration = 22
            else: duration = 50
            
            return pd.Series([duration, 'Series' if is_show else 'Movie'])

        if 'Genre' not in df.columns: df['Genre'] = 'Drama'
        
        # Apply Logic
        df[['Duration_Mins', 'Type']] = df.apply(get_metadata, axis=1)
        
        # Extraction du nom de la série (pour le calcul de Streak)
        def get_show_name(row):
            if row['Type'] == 'Movie': return row['Title']
            return row['Title'].split(':')[0]
        df['ShowName'] = df.apply(get_show_name, axis=1)

        # Fallbacks
        if 'My_Rating' not in df.columns: df['My_Rating'] = np.random.randint(5, 11, size=len(df))
        if 'Weather' not in df.columns: df['Weather'] = 'Sunny'
        if 'Temp_C' not in df.columns: df['Temp_C'] = 15
        
        # Time features
        df['MonthYear'] = df['Date'].dt.to_period('M').astype(str)
        df['Month'] = df['Date'].dt.month_name()
        df['DayOfWeek'] = df['Date'].dt.day_name()
        
        # Seasonality
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

# Header
st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 class="netflix-font" style="font-size: 4rem; margin-bottom: 0;">MY VIEWING HISTORY</h1>
        <p style="color: #888; font-size: 1.1rem;">Cinematic data analysis & behavioral patterns.</p>
    </div>
""", unsafe_allow_html=True)

# --- METHODOLOGY SECTION (FIXED: HTML ALLOWED) ---
with st.expander("🛠️ METHODOLOGY & DESIGN RATIONALE"):
    st.markdown("""
    <div class="methodology-container">
        
        <h4>1. DATA & METADATA</h4>
        <p>The dataset was constructed to simulate a comprehensive viewing history (2024-2026).
        <ul>
            <li><strong>Source:</strong> Synthetic generation based on real-world content logic (Netflix catalogue).</li>
            <li><strong>Enrichment:</strong> Data was crossed with the <em>Open-Meteo API</em> to retrieve historical weather conditions for Paris (Rain, Sun, Snow).</li>
            <li><strong>Metadata:</strong> New features were engineered, such as <em>Duration</em> (estimated by genre), <em>Seasonality</em> (Winter/Summer), and <em>Binge Streak</em> (consecutive episodes watched).</li>
        </ul>
        </p>

        <h4>2. STRUCTURE & LAYOUT</h4>
        <p>The dashboard follows a <strong>"Funnel Structure"</strong> (General to Specific):
        <ul>
            <li><strong>Top Level:</strong> Global KPIs (Total Hours, Volume) for immediate insight.</li>
            <li><strong>Mid Level:</strong> Temporal trends and Genre distribution.</li>
            <li><strong>Deep Dive:</strong> Correlation analysis (Weather vs Content, Rating Psychology).</li>
            <li><strong>Bottom Level:</strong> Granular data lists (Top/Flop).</li>
        </ul>
        The layout uses a <strong>2-column grid</strong> to balance density and readability, optimizing screenspace without overcrowding.
        </p>

        <h4>3. VISUAL REPRESENTATIONS</h4>
        <p>Charts were chosen based on the specific nature of the data:
        <ul>
            <li><strong>Scatter Plot (Temp vs Volume):</strong> Used to detect correlations between continuous variables (Temperature) and viewing habits.</li>
            <li><strong>Box Plot (Rating by Genre):</strong> Chosen over bar charts to visualize the <em>spread</em> and <em>medians</em> of ratings, revealing which genres are consistently liked vs. polarizing.</li>
            <li><strong>Heatmap (Day vs Month):</strong> selected to identify "Hotspots" of activity across the calendar week.</li>
            <li><strong>Radar Chart:</strong> Efficiently displays the multi-dimensional balance of genre consumption.</li>
        </ul>
        </p>

        <h4>4. INTERACTION & SCREENSPACE</h4>
        <p>
        <ul>
            <li><strong>Sidebar:</strong> All filters (Date, Genre) are isolated in the sidebar to maximize the main view for analysis (Output).</li>
            <li><strong>Dynamic Filtering:</strong> All KPIs and charts update instantly, allowing users to explore specific slices of data (e.g., "Only Sci-Fi in Winter").</li>
            <li><strong>Collapsible Section:</strong> This methodology section is hidden by default (Expander) to respect the "Data-Ink Ratio".</li>
        </ul>
        </p>

        <h4>5. COLOR USE</h4>
        <p>The design adopts a <strong>Cinematic Dark Mode</strong> to mimic the streaming platform's aesthetic.
        <ul>
            <li><strong>Brand Identity:</strong> <span style="color:#E50914">Netflix Red</span> is used for primary branding and emphasis.</li>
            <li><strong>Semantic Colors:</strong> <span style="color:#46d369">Green</span> indicates positive metrics (High ratings), while <span style="color:#E50914">Red</span> indicates negative ones (Flops).</li>
            <li><strong>Weather Coding:</strong> Intuitive colors used for context (Yellow=Sun, Blue=Rain).</li>
        </ul>
        </p>
    </div>
    """, unsafe_allow_html=True) # ✅ FIXED HERE

st.markdown("<br>", unsafe_allow_html=True)

# KPIs
total_h = int(df_filtered['Duration_Mins'].sum() / 60)
nb_t = len(df_filtered)
avg_r = df_filtered['My_Rating'].mean()
fav_g = df_filtered['Genre'].mode()[0] if not df_filtered.empty else "N/A"

c1, c2, c3, c4 = st.columns(4)
def kpi(col, t, v, s):
    col.markdown(f"""<div class="kpi-card"><div class="kpi-title">{t}</div><div class="kpi-value">{v}</div><div class="kpi-sub">{s}</div></div>""", unsafe_allow_html=True)

kpi(c1, "Total Hours", f"{total_h}h", "Cumulative Time")
kpi(c2, "Titles Watched", f"{nb_t}", "Movies & Episodes")
kpi(c3, "Avg Rating", f"{avg_r:.1f}/10", "Quality Score")
kpi(c4, "Top Genre", fav_g.upper(), "Most Frequent")

st.markdown("<br>", unsafe_allow_html=True)

# ROW 1: ACTIVITY & RADAR
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📈 Monthly Activity")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    monthly = df_filtered.groupby('MonthYear')['Title'].count().reset_index()
    fig = px.bar(monthly, x='MonthYear', y='Title', color_discrete_sequence=['#E50914'])
    fig.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#888', family="Outfit"), xaxis_title=None, yaxis_title="Items")
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### 🕸️ Genre Radar")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    gc = df_filtered['Genre'].value_counts().reset_index().head(6)
    gc.columns = ['Genre', 'Count']
    fig_r = px.line_polar(gc, r='Count', theta='Genre', line_close=True)
    fig_r.update_traces(fill='toself', line_color='#E50914', fillcolor='rgba(229, 9, 20, 0.3)')
    fig_r.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#ccc'), polar=dict(bgcolor='rgba(0,0,0,0)', radialaxis=dict(visible=False)))
    st.plotly_chart(fig_r, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ROW 2: TRENDS
st.markdown("### 🧬 Behavioral Trends")
c_evo, c_day, c_type = st.columns([2, 1, 1])

with c_evo:
    st.markdown("**Genre Evolution**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    evo_data = df_filtered.groupby(['MonthYear', 'Genre']).size().reset_index(name='Count')
    fig_evo = px.area(evo_data, x="MonthYear", y="Count", color="Genre", color_discrete_sequence=px.colors.qualitative.Vivid)
    fig_evo.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#888'), legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig_evo, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_day:
    st.markdown("**Day Preference**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    day_counts = df_filtered['DayOfWeek'].value_counts()
    day_data = pd.DataFrame({'Day': days})
    day_data['Count'] = day_data['Day'].map(day_counts).fillna(0)
    fig_d = px.bar(day_data, x='Day', y='Count', color='Count', color_continuous_scale='Reds')
    fig_d.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#888'), coloraxis_showscale=False, xaxis_title=None)
    st.plotly_chart(fig_d, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_type:
    st.markdown("**Movies vs Series**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    if 'Type' in df_filtered.columns:
        type_data = df_filtered['Type'].value_counts()
        fig_p = go.Figure(data=[go.Pie(labels=type_data.index, values=type_data.values, hole=.7, marker=dict(colors=['#E50914', '#333']))])
        fig_p.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#ccc'), showlegend=False, margin=dict(t=0,b=0,l=0,r=0))
        st.plotly_chart(fig_p, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ROW 3: CONTEXT
st.markdown("### 🌪️ Context Analysis")
c_w1, c_w2 = st.columns(2)

with c_w1:
    st.markdown("**Weather Influence**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    ct = df_filtered.groupby(['Weather', 'Genre']).size().reset_index(name='Count')
    fig_s = px.bar(ct, x="Weather", y="Count", color="Genre", color_discrete_sequence=px.colors.qualitative.Pastel)
    fig_s.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#888'), legend=dict(orientation="h", y=1.1, title=None))
    st.plotly_chart(fig_s, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c_w2:
    st.markdown("**Binge Heatmap**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    hd = df_filtered.groupby(['DayOfWeek', 'Month']).size().reset_index(name='Count')
    fig_hm = px.density_heatmap(hd, x='Month', y='DayOfWeek', z='Count', category_orders={'DayOfWeek': days}, color_continuous_scale='Redor')
    fig_hm.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#888'), coloraxis_showscale=False)
    st.plotly_chart(fig_hm, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ROW 4: DEEP DIVE (Box Plot + Scatter)
st.markdown("### ⭐ Ratings & Weather Deep Dive")
col_rate, col_temp = st.columns(2)

with col_rate:
    st.markdown("**Rating Spread by Genre (Box Plot)**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    genre_order = df_filtered.groupby('Genre')['My_Rating'].median().sort_values().index
    fig_box = px.box(df_filtered, x="Genre", y="My_Rating", color="Genre", 
                     category_orders={"Genre": genre_order}, color_discrete_sequence=px.colors.qualitative.Bold)
    fig_box.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#888'), showlegend=False, yaxis_title="My Ratings")
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_temp:
    st.markdown("**Temperature vs. Volume (Scatter)**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    daily_stats = df_filtered.groupby('Date').agg({'Title': 'count', 'Temp_C': 'mean'}).reset_index()
    fig_sc = px.scatter(daily_stats, x="Temp_C", y="Title", size="Title", color="Temp_C", color_continuous_scale="Turbo")
    fig_sc.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#888'), xaxis_title="Temperature (°C)", yaxis_title="Episodes/Day")
    st.plotly_chart(fig_sc, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ROW 5: ADVANCED METRICS
st.markdown("### 🧠 Advanced Metrics (Streak & Seasons)")
col_hook, col_season = st.columns(2)

with col_hook:
    st.markdown("**Average Consecutive Episodes by Genre**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    series_df = df_filtered[df_filtered['Type'] == 'Series'].copy()
    if not series_df.empty:
        series_df['BlockID'] = (series_df['ShowName'] != series_df['ShowName'].shift()).cumsum()
        streak_data = series_df.groupby(['Genre', 'BlockID']).size().reset_index(name='StreakLength')
        avg_streak = streak_data.groupby('Genre')['StreakLength'].mean().reset_index().sort_values('StreakLength', ascending=False)
        fig_st = px.bar(avg_streak, x="StreakLength", y="Genre", orientation='h', text_auto='.1f', color="StreakLength", color_continuous_scale="Reds")
        fig_st.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#888'), coloraxis_showscale=False)
        st.plotly_chart(fig_st, use_container_width=True)
    else:
        st.info("No series data available.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_season:
    st.markdown("**Genre Seasonality**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    ss = df_filtered.groupby(['Season', 'Genre']).size().reset_index(name='Count')
    fig_sea = px.bar(ss, x="Season", y="Count", color="Genre", category_orders={"Season": ['❄️ Winter', '🌱 Spring', '☀️ Summer', '🍂 Autumn']}, color_discrete_sequence=px.colors.qualitative.Vivid, barmode="group")
    fig_sea.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(color='#888'), legend=dict(orientation="h", y=1.1, title=None))
    st.plotly_chart(fig_sea, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ROW 6: LISTS
cl1, cl2 = st.columns(2)
with cl1:
    st.markdown("#### 🔥 Top 5 Best Rated")
    top = df_filtered.sort_values('My_Rating', ascending=False).drop_duplicates('Title').head(5)
    for _, r in top.iterrows():
        st.markdown(f"""<div class="list-card top"><div><strong style="color:white;">{r['Title']}</strong><br><span style="color:#888; font-size:0.85rem;">{r['Genre']} • {r['Weather']}</span></div><div style="background:#46d369; color:#000; padding:4px 8px; border-radius:6px; font-weight:bold;">{r['My_Rating']}</div></div>""", unsafe_allow_html=True)

with cl2:
    st.markdown("#### 🍅 Top 5 Worst Rated")
    flop = df_filtered.sort_values('My_Rating', ascending=True).drop_duplicates('Title').head(5)
    for _, r in flop.iterrows():
        st.markdown(f"""<div class="list-card flop"><div><strong style="color:white;">{r['Title']}</strong><br><span style="color:#888; font-size:0.85rem;">{r['Genre']} • {r['Weather']}</span></div><div style="background:#E50914; color:#fff; padding:4px 8px; border-radius:6px; font-weight:bold;">{r['My_Rating']}</div></div>""", unsafe_allow_html=True)

st.markdown("<br><center style='color:#555'>NETFLIX ANALYTICS • 2024</center>", unsafe_allow_html=True)
