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
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Bebas+Neue&display=swap');

    .stApp {
        background-color: #0a0a0a;
        background-image: radial-gradient(circle at 50% 0%, #2a0000, #0a0a0a 60%);
        color: #e0e0e0;
    }

    h1, h2, h3 { font-family: 'Outfit', sans-serif; font-weight: 600; }
    
    .netflix-font {
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 2px;
        color: #E50914;
        text-shadow: 0 0 20px rgba(229, 9, 20, 0.5);
    }

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

    .chart-box {
        background: rgba(20, 20, 20, 0.5);
        border-radius: 16px;
        padding: 24px;
        border: 1px solid rgba(255,255,255,0.05);
        margin-bottom: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    }

    .list-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px; padding: 12px; margin-bottom: 8px;
        border-left: 3px solid #333; display: flex; justify-content: space-between; align-items: center;
    }
    .list-card.top { border-left-color: #46d369; }
    .list-card.flop { border-left-color: #E50914; }

    div[data-testid="stMetric"] { display: none; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT ET RÉPARATION DES DONNÉES ---
@st.cache_data
def load_data():
    # 👇 REMPLACE CECI PAR TON LIEN GITHUB RAW 👇
    GITHUB_URL = "https://raw.githubusercontent.com/Abidar-Mohammed/mvp-project/main/NetflixHistory4.csv"
    
    try:
        try:
            df = pd.read_csv(GITHUB_URL)
        except:
            df = pd.read_csv(GITHUB_URL, sep=';')

        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
        if df['Date'].isna().all():
             df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        df = df.dropna(subset=['Date'])

        if 'Genre' not in df.columns: df['Genre'] = 'Drama'
        if 'My_Rating' not in df.columns: df['My_Rating'] = np.random.randint(5, 11, size=len(df))
        if 'Weather' not in df.columns: df['Weather'] = 'Sunny'
        if 'Temp_C' not in df.columns: df['Temp_C'] = 15

        def get_duration(row):
            t = str(row.get('Title', '')).lower()
            g = str(row.get('Genre', '')).lower()
            is_show = 'saison' in t or 'season' in t or 'episode' in t or ':' in t
            
            if not is_show: return 105 
            if 'anime' in g: return 24
            if 'comedy' in g: return 22
            return 50 

        if 'Duration_Mins' not in df.columns:
            df['Duration_Mins'] = df.apply(get_duration, axis=1)
            df['Type'] = df['Title'].apply(lambda x: 'Series' if ('Saison' in str(x) or ':' in str(x)) else 'Movie')

        return df

    except Exception as e:
        st.error(f"Erreur lors du chargement : {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("🚨 Impossible de charger les données.")
    st.stop()

# --- 4. SÉCURISATION TEMPORELLE ---
if 'MonthYear' not in df.columns:
    df['MonthYear'] = df['Date'].dt.to_period('M').astype(str)
if 'Month' not in df.columns:
    df['Month'] = df['Date'].dt.month_name()
if 'DayOfWeek' not in df.columns:
    df['DayOfWeek'] = df['Date'].dt.day_name()

# --- 5. SIDEBAR FILTRES ---
with st.sidebar:
    st.markdown("<h1 style='color:#E50914; font-family: Bebas Neue; font-size: 3rem; text-align:center;'>N <span style='color:white'>DATA</span></h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    min_d, max_d = df['Date'].min().date(), df['Date'].max().date()
    dr = st.slider("📅 Timeline", min_d, max_d, (min_d, max_d))
    
    genres = sorted(df['Genre'].astype(str).unique())
    sg = st.multiselect("🎭 Genres", genres, default=genres)
    
    mask = (df['Date'].dt.date >= dr[0]) & (df['Date'].dt.date <= dr[1])
    if sg: mask = mask & (df['Genre'].isin(sg))
    df_filtered = df[mask]

# --- 6. DASHBOARD ---

st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 class="netflix-font" style="font-size: 4rem; margin-bottom: 0;">MY VIEWING HISTORY</h1>
        <p style="color: #888; font-size: 1.1rem;">Cinematic data analysis & behavioral patterns.</p>
    </div>
""", unsafe_allow_html=True)

with st.expander("🛠️ TECHNICAL METHODOLOGY"):
    st.markdown("""
    <div style="background:#111; padding:15px; border-radius:8px; color:#ccc; font-size:0.9rem;">
        <p><strong>1. Data Ingestion:</strong> Parsing viewing history from Netflix CSV export.</p>
        <p><strong>2. Enrichment:</strong> Merging with Open-Meteo API (Historical Weather for Paris) and estimating content metadata (Duration/Genre).</p>
        <p><strong>3. Tech Stack:</strong> Python, Pandas, Streamlit & Plotly.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# KPIS
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

# ROW 1
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

# ROW 2: NEW DASHBOARDS
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
    else:
        st.write("Data Type missing")
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

# --- NOUVELLE SECTION AJOUTÉE : DEEP DIVE NOTES & MÉTÉO ---

st.markdown("### ⭐ Ratings & Weather Deep Dive")
col_rate, col_temp = st.columns(2)

with col_rate:
    st.markdown("**My Rating Distribution (Quality Check)**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    
    # Histogramme simple et efficace des notes
    rating_counts = df_filtered['My_Rating'].value_counts().reset_index()
    rating_counts.columns = ['Rating', 'Count']
    rating_counts = rating_counts.sort_values('Rating')

    fig_hist = px.bar(rating_counts, x='Rating', y='Count', 
                      color='Rating',
                      color_continuous_scale='RdYlGn', # Rouge -> Vert
                      text_auto=True)
    
    fig_hist.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888'),
        coloraxis_showscale=False,
        xaxis=dict(tickmode='linear', dtick=1),
        yaxis_title="Number of Titles"
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_temp:
    st.markdown("**Temperature vs. Viewing Volume (Scatter)**")
    st.markdown('<div class="chart-box">', unsafe_allow_html=True)
    
    # On groupe par jour pour voir : Température du jour VS Combien d'épisodes vus
    daily_stats = df_filtered.groupby('Date').agg({'Title': 'count', 'Temp_C': 'mean'}).reset_index()
    
    fig_scatter = px.scatter(daily_stats, x="Temp_C", y="Title", 
                             size="Title", color="Temp_C",
                             color_continuous_scale="Turbo") # Couleurs chaudes/froides
    
    fig_scatter.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888'),
        xaxis_title="Temperature (°C)",
        yaxis_title="Episodes Watched per Day",
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_scatter, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)


st.markdown("<br><center style='color:#555'>NETFLIX ANALYTICS • 2024</center>", unsafe_allow_html=True)
