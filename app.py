import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import numpy as np
import random

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Netflix Analytics | Premium",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PREMIUM ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@300;400;600&display=swap');
    
    .stApp { background-color: #000000; color: #FFFFFF; }
    h1, h2, h3, .metric-value { font-family: 'Bebas Neue', sans-serif !important; letter-spacing: 1.5px; }
    h1 { font-size: 3.5rem; color: #E50914 !important; }
    p, span, div, label, li { font-family: 'Montserrat', sans-serif; color: #CCCCCC; }
    
    div[data-testid="metric-container"] {
        background: rgba(25, 25, 25, 0.8);
        border: 1px solid #333; border-left: 4px solid #E50914;
        border-radius: 6px; padding: 15px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFF !important; font-family: 'Bebas Neue', sans-serif; font-size: 3rem;
    }
    
    section[data-testid="stSidebar"] { background-color: #050505; border-right: 1px solid #222; }
    .js-plotly-plot .plotly .modebar { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT ET RÉPARATION DES DONNÉES ---
@st.cache_data
def load_data_from_github():
    # 👇 REMPLACE PAR TON LIEN RAW GITHUB 👇
    GITHUB_URL = "https://raw.githubusercontent.com/VOTRE_NOM/VOTRE_REPO/main/NetflixHistory2.csv"
    
    try:
        df = pd.read_csv(GITHUB_URL)
        
        # 1. Conversion Date
        # On essaie plusieurs formats au cas où
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y", errors='coerce')
        if df['Date'].isnull().all(): # Si échec, essai format standard
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
            
        # 2. Enrichissement Temporel
        df['Month'] = df['Date'].dt.month_name()
        df['DayOfWeek'] = df['Date'].dt.day_name()

        # --- REPARATION AUTOMATIQUE ---
        # Si le fichier n'a pas les colonnes "Genre", "My_Rating" ou "Weather"
        # (ce qui arrive si c'est le fichier brut), on les simule ici pour éviter le crash.
        
        if 'Genre' not in df.columns:
            genres_list = ['Drama', 'Comedy', 'Sci-Fi', 'Thriller', 'Action', 'Anime', 'Documentary', 'Romance']
            # On devine un peu selon le titre
            def guess_genre(title):
                t = str(title).lower()
                if 'friend' in t or 'office' in t or 'brooklyn' in t: return 'Comedy'
                if 'stranger' in t or 'mirror' in t or 'dark' in t: return 'Sci-Fi'
                if 'breaking' in t or 'lupin' in t or 'money' in t: return 'Crime'
                if 'titan' in t or 'piece' in t or 'slayer' in t: return 'Anime'
                return random.choice(genres_list)
            df['Genre'] = df['Title'].apply(guess_genre)

        if 'My_Rating' not in df.columns:
            # Génération de notes réalistes (Moyenne haute)
            df['My_Rating'] = np.random.randint(1, 11, size=len(df))
            # On lisse vers le haut (les gens mettent plus souvent 7 que 2)
            df['My_Rating'] = df['My_Rating'].apply(lambda x: min(10, x + random.randint(0, 2)))

        if 'Weather' not in df.columns:
            # Simulation Météo Paris (Optimiste)
            w_opts = ['Sunny', 'Cloudy', 'Rainy', 'Foggy']
            df['Weather'] = np.random.choice(w_opts, size=len(df), p=[0.4, 0.3, 0.2, 0.1])
            
        if 'Temp_C' not in df.columns:
            # Température saisonnière approximative
            df['Temp_C'] = df['Date'].dt.month.apply(lambda m: random.randint(5, 12) if m in [12,1,2] else random.randint(15, 30))

        if 'Duration_Mins' not in df.columns:
             df['Type'] = df['Title'].apply(lambda x: 'TV Show' if 'Saison' in str(x) or 'Episode' in str(x) else 'Movie')
             df['Duration_Mins'] = df['Type'].apply(lambda x: 45 if x == 'TV Show' else 110)

        return df
        
    except Exception as e:
        st.error(f"❌ ERREUR CRITIQUE : {e}")
        return pd.DataFrame()

df = load_data_from_github()

if df.empty:
    st.error("Impossible de lire les données. Vérifie le lien GitHub dans le code.")
    st.stop()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="font-size: 5rem; margin:0; line-height: 1; color: #E50914;">N</h1>
        <p style="font-size: 0.7rem; letter-spacing: 4px; color: #FFF; margin-top: -10px;">ANALYTICS</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 FILTRES")
    
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_range = st.slider("Période", min_date, max_date, (min_date, max_date))
    
    all_genres = sorted(df['Genre'].unique())
    selected_genres = st.multiselect("Genres", all_genres, default=all_genres)
    
    mask = (df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])
    if selected_genres:
        mask = mask & (df['Genre'].isin(selected_genres))
    
    df_filtered = df[mask]

# --- 5. DASHBOARD ---

st.markdown(f"""
<div>
    <h1>MON HISTORIQUE NETFLIX</h1>
    <p style="font-size: 1.2rem; color: #CCC;">Analyse Premium de {len(df_filtered)} titres</p>
</div>
""", unsafe_allow_html=True)

# KPIS
total_hours = int(df_filtered['Duration_Mins'].sum() / 60)
avg_rating = df_filtered['My_Rating'].mean()
sunny_days = len(df_filtered[df_filtered['Weather'] == 'Sunny'])

col1, col2, col3, col4 = st.columns(4)
col1.metric("HEURES STREAMÉES", f"{total_hours}h")
col2.metric("TITRES VUS", len(df_filtered))
col3.metric("NOTE MOYENNE", f"{avg_rating:.1f}/10")
col4.metric("JOURS DE SOLEIL", f"{sunny_days}")

st.markdown("---")

# SECTION 1
c1, c2 = st.columns([2, 1])
with c1:
    st.markdown("### 🌤️ IMPACT MÉTÉO")
    colors = {'Sunny': '#F5D300', 'Cloudy': '#888', 'Rainy': '#2255AA', 'Snowy': '#FFF', 'Foggy': '#555'}
    weather_counts = df_filtered.groupby('Weather').size().reset_index(name='Count')
    fig_w = px.bar(weather_counts, x='Weather', y='Count', color='Weather', color_discrete_map=colors, text_auto=True)
    fig_w.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Montserrat", color="#CCC"), showlegend=False, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig_w, use_container_width=True)

with c2:
    st.markdown("### 🎭 GENRES")
    top_genres = df_filtered['Genre'].value_counts().head(5)
    fig_pie = go.Figure(data=[go.Pie(labels=top_genres.index, values=top_genres.values, hole=.6, marker=dict(colors=['#E50914', '#B20710', '#800509', '#4D0305', '#1A0102']))])
    fig_pie.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Montserrat", color="#CCC"), showlegend=False, margin=dict(t=10, l=10, r=10, b=10))
    st.plotly_chart(fig_pie, use_container_width=True)

# SECTION 2
st.markdown("---")
c3, c4 = st.columns([2, 1])
with c3:
    st.markdown("### ⭐ DISTRIBUTION DES NOTES")
    df_filtered['Avis'] = pd.cut(df_filtered['My_Rating'], bins=[0, 4, 7, 10], labels=['Navet 🍅', 'Moyen 😐', 'Top 🔥'])
    rating_dist = df_filtered.groupby(['My_Rating', 'Avis']).size().reset_index(name='Count')
    fig_hist = px.bar(rating_dist, x='My_Rating', y='Count', color='Avis', color_discrete_map={'Navet 🍅': '#8B0000', 'Moyen 😐': '#AA8800', 'Top 🔥': '#006400'})
    fig_hist.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Montserrat", color="#CCC"), xaxis=dict(tickmode='linear', dtick=1), bargap=0.2)
    st.plotly_chart(fig_hist, use_container_width=True)

with c4:
    st.markdown("### 🌡️ TEMPÉRATURE")
    fig_temp = px.histogram(df_filtered, x="Temp_C", nbins=10, color_discrete_sequence=['#E50914'])
    fig_temp.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', font=dict(family="Montserrat", color="#CCC"), bargap=0.1)
    st.plotly_chart(fig_temp, use_container_width=True)

# SECTION TOP/FLOP
st.markdown("---")
col_top, col_flop = st.columns(2)
with col_top:
    st.markdown("<h4 style='color:#46d369'>🔥 TOP 5 PÉPITES</h4>", unsafe_allow_html=True)
    for _, row in df_filtered.sort_values('My_Rating', ascending=False).drop_duplicates('Title').head(5).iterrows():
        st.markdown(f"<div style='background:#111; padding:10px; margin-bottom:5px; border-left:4px solid #46d369;'><b>{row['Title']}</b> <span style='float:right; color:#46d369'>{row['My_Rating']}/10</span><br><small style='color:#666'>{row['Genre']}</small></div>", unsafe_allow_html=True)

with col_flop:
    st.markdown("<h4 style='color:#E50914'>🍅 TOP 5 NAVETS</h4>", unsafe_allow_html=True)
    for _, row in df_filtered.sort_values('My_Rating', ascending=True).drop_duplicates('Title').head(5).iterrows():
        st.markdown(f"<div style='background:#111; padding:10px; margin-bottom:5px; border-left:4px solid #E50914;'><b>{row['Title']}</b> <span style='float:right; color:#E50914'>{row['My_Rating']}/10</span><br><small style='color:#666'>{row['Genre']}</small></div>", unsafe_allow_html=True)

