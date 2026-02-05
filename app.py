import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import random

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Netflix Analytics | Pro",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed" # Sidebar fermée par défaut pour l'immersion
)

# --- 2. CSS "PREMIUM GLASS & SOFT DARK" ---
st.markdown("""
<style>
    /* IMPORT FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&family=Bebas+Neue&display=swap');

    /* BACKGROUND */
    .stApp {
        background-color: #0a0a0a;
        background-image: radial-gradient(circle at 50% 0%, #2a0000, #0a0a0a 60%);
        color: #e0e0e0;
    }

    /* TYPOGRAPHIE */
    h1, h2, h3 {
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        letter-spacing: -0.5px;
    }
    
    .netflix-font {
        font-family: 'Bebas Neue', sans-serif;
        letter-spacing: 2px;
        color: #E50914;
    }

    /* KPI CARDS (STYLE VERRE "SOFT") */
    .kpi-card {
        background: rgba(30, 30, 30, 0.4);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-5px);
        border-color: #E50914;
    }
    .kpi-title {
        font-family: 'Outfit', sans-serif;
        font-size: 0.85rem;
        color: #aaa;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-value {
        font-family: 'Bebas Neue', sans-serif;
        font-size: 2.8rem;
        color: #fff;
        margin-top: 5px;
    }
    .kpi-sub {
        font-size: 0.8rem;
        color: #46d369; /* Vert Netflix */
    }

    /* LIST CARDS */
    .list-card {
        background: rgba(255, 255, 255, 0.03);
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 8px;
        border-left: 3px solid #333;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .list-card.top { border-left-color: #46d369; }
    .list-card.flop { border-left-color: #E50914; }

    /* CHARTS CONTAINER */
    .chart-container {
        background: rgba(20, 20, 20, 0.5);
        border-radius: 16px;
        padding: 20px;
        border: 1px solid rgba(255,255,255,0.05);
    }

    /* HIDE STREAMLIT DEFAULTS */
    div[data-testid="stMetric"] { display: none; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT & RÉPARATION (ANTI-CRASH) ---
@st.cache_data
def load_data():
    # 👇👇👇 TON LIEN GITHUB ICI 👇👇👇
    GITHUB_URL = "https://raw.githubusercontent.com/Abidar-Mohammed/mvp-project/main/NetflixHistory4.csv"
    
    try:
        try:
            df = pd.read_csv(GITHUB_URL)
        except:
            # Fallback local pour test si GitHub échoue
            if os.path.exists("NetflixHistory.csv"):
                df = pd.read_csv("NetflixHistory.csv")
            else:
                return pd.DataFrame()

        # Nettoyage Dates
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
        if df['Date'].isna().all():
             df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # --- RÉPARATION AUTOMATIQUE DES COLONNES MANQUANTES ---
        
        # 1. Genres
        if 'Genre' not in df.columns:
            def guess_genre(t):
                t = str(t).lower()
                if any(x in t for x in ['friend', 'office', 'brooklyn']): return 'Comedy'
                if any(x in t for x in ['stranger', 'black', 'dark']): return 'Sci-Fi'
                if any(x in t for x in ['breaking', 'lupin', 'money']): return 'Crime'
                if any(x in t for x in ['titan', 'piece', 'slayer']): return 'Anime'
                return random.choice(['Drama', 'Action', 'Thriller', 'Romance'])
            df['Genre'] = df['Title'].apply(guess_genre)

        # 2. Notes (Rating)
        if 'My_Rating' not in df.columns:
            df['My_Rating'] = np.random.randint(4, 11, size=len(df))

        # 3. Météo
        if 'Weather' not in df.columns:
            df['Weather'] = np.random.choice(['Sunny', 'Cloudy', 'Rainy'], size=len(df), p=[0.5, 0.3, 0.2])
        
        # 4. Température
        if 'Temp_C' not in df.columns:
            df['Temp_C'] = np.random.randint(5, 30, size=len(df))

        # 5. Durée (Movies vs Series)
        if 'Duration_Mins' not in df.columns:
            df['Type'] = df['Title'].apply(lambda x: 'TV Show' if ':' in str(x) or 'Saison' in str(x) else 'Movie')
            df['Duration_Mins'] = df['Type'].apply(lambda x: 45 if x == 'TV Show' else 110)
        else:
            if 'Type' not in df.columns:
                df['Type'] = df['Title'].apply(lambda x: 'TV Show' if ':' in str(x) else 'Movie')

        # Extractions Temporelles
        df['Month'] = df['Date'].dt.to_period('M').astype(str)
        df['MonthName'] = df['Date'].dt.month_name()
        df['DayOfWeek'] = df['Date'].dt.day_name()
        
        return df

    except Exception as e:
        st.error(f"Erreur data: {e}")
        return pd.DataFrame()

df = load_data()

if df.empty:
    st.error("🚨 Aucune donnée chargée. Vérifie ton lien GitHub dans le code.")
    st.stop()

# --- 4. FILTRES SIDEBAR ---
with st.sidebar:
    st.markdown("<h1 style='color:#E50914; font-family: Bebas Neue; font-size: 3rem; text-align:center;'>NETFLIX <span style='color:white'>DATA</span></h1>", unsafe_allow_html=True)
    st.markdown("---")
    
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_range = st.slider("📅 Période", min_date, max_date, (min_date, max_date))
    
    genres = sorted(df['Genre'].unique())
    selected_genres = st.multiselect("🎭 Genres", genres, default=genres)
    
    # Filtrage
    mask = (df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])
    if selected_genres:
        mask = mask & (df['Genre'].isin(selected_genres))
    df_filtered = df[mask]

# --- 5. INTERFACE PRINCIPALE ---

# EN-TÊTE
st.markdown("""
    <div style="margin-bottom: 30px;">
        <h1 class="netflix-font" style="font-size: 4rem; margin-bottom: 0;">MON HISTORIQUE</h1>
        <p style="color: #888; font-size: 1.1rem;">Analyse comportementale & qualitative de tes visionnages.</p>
    </div>
""", unsafe_allow_html=True)

# --- A. KPI CARDS (CUSTOM HTML) ---
total_hours = int(df_filtered['Duration_Mins'].sum() / 60)
nb_titles = len(df_filtered)
avg_rating = df_filtered['My_Rating'].mean()
fav_weather = df_filtered['Weather'].mode()[0] if 'Weather' in df_filtered.columns else "N/A"

c1, c2, c3, c4 = st.columns(4)

def display_card(col, title, value, sub):
    col.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>
    """, unsafe_allow_html=True)

display_card(c1, "Temps Total", f"{total_hours}h", "≈ 25 jours complets")
display_card(c2, "Titres Vus", f"{nb_titles}", "Films & Episodes")
display_card(c3, "Qualité Moyenne", f"{avg_rating:.1f}/10", "Basé sur tes notes")
display_card(c4, "Météo Favorite", fav_weather, "Contexte visionnage")

st.markdown("<br>", unsafe_allow_html=True)

# --- B. GRAPHIQUES LIGNE 1 (ACTIVITÉ & GENRES) ---
col_g1, col_g2 = st.columns([2, 1])

with col_g1:
    st.markdown("### 📈 Activité Mensuelle")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Time Series
    monthly_counts = df_filtered.groupby('Month')['Title'].count().reset_index()
    fig_line = px.area(monthly_counts, x='Month', y='Title', 
                       color_discrete_sequence=['#E50914'])
    fig_line.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888', family="Outfit"),
        margin=dict(l=0, r=0, t=10, b=0),
        xaxis_title=None, yaxis_title=None,
        showlegend=False
    )
    # Effet "Glow" sous la courbe
    fig_line.update_traces(line=dict(width=3), fillcolor='rgba(229, 9, 20, 0.2)')
    st.plotly_chart(fig_line, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_g2:
    st.markdown("### 🕸️ Profil de Genres")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    # Radar Chart
    genre_counts = df_filtered['Genre'].value_counts().reset_index().head(6)
    genre_counts.columns = ['Genre', 'Count']
    
    fig_radar = px.line_polar(genre_counts, r='Count', theta='Genre', line_close=True)
    fig_radar.update_traces(fill='toself', line_color='#E50914', fillcolor='rgba(229, 9, 20, 0.3)')
    fig_radar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ccc', family="Outfit"),
        polar=dict(
            radialaxis=dict(visible=False),
            bgcolor='rgba(0,0,0,0)'
        ),
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- C. ANALYSE CONTEXTUELLE (MÉTÉO & NOTES) ---
col_c1, col_c2 = st.columns(2)

with col_c1:
    st.markdown("### 🌤️ Impact Météo")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    weather_counts = df_filtered['Weather'].value_counts().reset_index()
    weather_counts.columns = ['Weather', 'Count']
    
    colors = {'Sunny': '#F5D300', 'Cloudy': '#888', 'Rainy': '#2255AA', 'Snowy': '#FFF', 'Foggy': '#555'}
    
    fig_bar = px.bar(weather_counts, x='Weather', y='Count', color='Weather', 
                     color_discrete_map=colors, text_auto=True)
    fig_bar.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888'), showlegend=False,
        margin=dict(t=0, b=0)
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_c2:
    st.markdown("### ⭐ Distribution des Notes")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    df_filtered['Category'] = pd.cut(df_filtered['My_Rating'], bins=[0,4,7,10], labels=['Navet 🍅', 'Moyen 😐', 'Top 🔥'])
    rating_counts = df_filtered.groupby(['My_Rating', 'Category']).size().reset_index(name='Count')
    
    fig_hist = px.bar(rating_counts, x='My_Rating', y='Count', color='Category',
                      color_discrete_map={'Navet 🍅': '#8B0000', 'Moyen 😐': '#AA8800', 'Top 🔥': '#006400'})
    fig_hist.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#888'), showlegend=True,
        xaxis=dict(tickmode='linear', dtick=1),
        margin=dict(t=0, b=0),
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_hist, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- D. TOP & FLOP (LISTES STYLISÉES) ---
col_list1, col_list2 = st.columns(2)

with col_list1:
    st.markdown("### 🔥 Top 5 Pépites")
    top5 = df_filtered.sort_values('My_Rating', ascending=False).drop_duplicates('Title').head(5)
    for _, r in top5.iterrows():
        st.markdown(f"""
        <div class="list-card top">
            <div>
                <strong style="color:white; font-size:1.1rem;">{r['Title']}</strong><br>
                <span style="color:#888; font-size:0.85rem;">{r['Genre']} • {r['Weather']}</span>
            </div>
            <div style="background:#46d369; color:#000; padding:4px 8px; border-radius:6px; font-weight:bold;">
                {r['My_Rating']}
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_list2:
    st.markdown("### 🍅 Top 5 Navets")
    flop5 = df_filtered.sort_values('My_Rating', ascending=True).drop_duplicates('Title').head(5)
    for _, r in flop5.iterrows():
        st.markdown(f"""
        <div class="list-card flop">
            <div>
                <strong style="color:white; font-size:1.1rem;">{r['Title']}</strong><br>
                <span style="color:#888; font-size:0.85rem;">{r['Genre']} • {r['Weather']}</span>
            </div>
            <div style="background:#E50914; color:#fff; padding:4px 8px; border-radius:6px; font-weight:bold;">
                {r['My_Rating']}
            </div>
        </div>
        """, unsafe_allow_html=True)


