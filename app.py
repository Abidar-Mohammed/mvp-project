import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Netflix Analytics | Premium Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PREMIUM "NETFLIX STYLE" ---
st.markdown("""
<style>
    /* FONTS */
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Montserrat:wght@300;400;600&display=swap');

    /* BACKGROUND DARK CINEMA */
    .stApp {
        background-color: #000000;
        color: #FFFFFF;
    }

    /* TITRES */
    h1, h2, h3, .metric-value {
        font-family: 'Bebas Neue', sans-serif !important;
        letter-spacing: 1.5px;
    }
    
    h1 { font-size: 3.5rem; color: #E50914 !important; } /* ROUGE NETFLIX */
    h2 { font-size: 2rem; color: #FFFFFF !important; margin-top: 30px; }
    h3 { font-size: 1.5rem; color: #B3B3B3 !important; }

    /* TEXTE CORPS */
    p, span, div, label, li {
        font-family: 'Montserrat', sans-serif;
        color: #CCCCCC;
    }

    /* KPI CARDS (EFFET GLACÉ) */
    div[data-testid="metric-container"] {
        background: rgba(25, 25, 25, 0.8);
        border: 1px solid #333;
        border-left: 4px solid #E50914;
        border-radius: 6px;
        padding: 15px;
        transition: 0.3s;
    }
    div[data-testid="metric-container"]:hover {
        border-left: 4px solid #FFF;
        transform: translateY(-2px);
    }
    div[data-testid="metric-container"] label {
        color: #888 !important;
        font-size: 0.85rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFF !important;
        font-family: 'Bebas Neue', sans-serif;
        font-size: 3rem;
    }

    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #050505;
        border-right: 1px solid #222;
    }
    
    /* PLOTLY TRANSPARENT */
    .js-plotly-plot .plotly .modebar { display: none !important; }
    
    /* SCROLLBAR ROUGE */
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #000; }
    ::-webkit-scrollbar-thumb { background: #E50914; border-radius: 5px; }
    ::-webkit-scrollbar-thumb:hover { background: #b0060e; }
</style>
""", unsafe_allow_html=True)

# --- 3. CONNEXION GITHUB & CHARGEMENT ---
@st.cache_data
def load_data_from_github():
    # 👇👇👇 REMPLACE CECI PAR TON LIEN RAW GITHUB 👇👇👇
    GITHUB_URL = "https://github.com/Abidar-Mohammed/mvp-project/main/NetflixHistory.csv"
    # 👆👆👆 EXEMPLE: "https://raw.githubusercontent.com/MehdiData/ProjetNetflix/main/NetflixHistory.csv"
    
    try:
        # Lecture directe depuis GitHub
        df = pd.read_csv(GITHUB_URL)
        
        # Traitement des Dates
        df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
        
        # Estimation Durée (Si non présente dans le CSV)
        # On devine que c'est une série si le titre contient "Saison" ou "Episode"
        df['Type'] = df['Title'].apply(lambda x: 'TV Show' if 'Saison' in str(x) or 'Episode' in str(x) else 'Movie')
        df['Duration_Mins'] = df['Type'].apply(lambda x: 45 if x == 'TV Show' else 110)
        
        # Enrichissement Temporel
        df['Month'] = df['Date'].dt.month_name()
        df['DayOfWeek'] = df['Date'].dt.day_name()
        
        return df
        
    except Exception as e:
        st.error(f"❌ ERREUR DE CONNEXION GITHUB : {e}")
        st.info("Vérifie que ton lien commence bien par 'https://raw.githubusercontent.com/...'")
        # Retourne un dataframe vide pour ne pas crasher l'app
        return pd.DataFrame()

df = load_data_from_github()

# STOP SI PAS DE DONNÉES
if df.empty:
    st.stop()

# --- 4. SIDEBAR (FILTRES) ---
with st.sidebar:
    # Logo HTML
    st.markdown("""
    <div style="text-align: center; margin-bottom: 30px;">
        <h1 style="font-size: 5rem; margin:0; line-height: 1; color: #E50914;">N</h1>
        <p style="font-size: 0.7rem; letter-spacing: 4px; color: #FFF; margin-top: -10px;">ANALYTICS</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 FILTRES")
    
    # Filtre Période
    min_date = df['Date'].min().date()
    max_date = df['Date'].max().date()
    date_range = st.slider("Période", min_date, max_date, (min_date, max_date))
    
    # Filtre Genre
    all_genres = sorted(df['Genre'].unique())
    selected_genres = st.multiselect("Genres", all_genres, default=all_genres)
    
    # Application des filtres
    mask = (df['Date'].dt.date >= date_range[0]) & (df['Date'].dt.date <= date_range[1])
    if selected_genres:
        mask = mask & (df['Genre'].isin(selected_genres))
    
    df_filtered = df[mask]
    
    st.markdown("---")
    st.caption(f"Données chargées : {len(df_filtered)} lignes")
    st.caption("Source : GitHub Raw")

# --- 5. DASHBOARD ---

# Header
st.markdown(f"""
<div>
    <h1>MON HISTORIQUE NETFLIX</h1>
    <p style="font-size: 1.2rem; color: #CCC;">Analyse de {len(df_filtered)} visionnages via Data Science</p>
</div>
""", unsafe_allow_html=True)

# KPIS
total_hours = int(df_filtered['Duration_Mins'].sum() / 60)
avg_rating = df_filtered['My_Rating'].mean()
fav_genre = df_filtered['Genre'].mode()[0]
sunny_days = len(df_filtered[df_filtered['Weather'] == 'Sunny'])

col1, col2, col3, col4 = st.columns(4)
col1.metric("HEURES STREAMÉES", f"{total_hours}h")
col2.metric("TITRES VUS", len(df_filtered))
col3.metric("NOTE MOYENNE", f"{avg_rating:.1f}/10")
col4.metric("JOURS DE SOLEIL", f"{sunny_days}", "Paris (Météo Réelle)")

st.markdown("---")

# SECTION METEO & GENRES
c1, c2 = st.columns([2, 1])

with c1:
    st.markdown("### 🌤️ IMPACT MÉTÉO SUR LE VISIONNAGE")
    # Couleurs personnalisées pour la météo
    weather_colors = {
        'Sunny': '#F5D300', # Jaune
        'Cloudy': '#888888', # Gris
        'Rainy': '#2255AA', # Bleu
        'Snowy': '#FFFFFF', # Blanc
        'Foggy': '#555555'  # Gris foncé
    }
    
    weather_counts = df_filtered.groupby('Weather').size().reset_index(name='Count')
    
    fig_w = px.bar(
        weather_counts, x='Weather', y='Count', 
        color='Weather',
        color_discrete_map=weather_colors,
        text_auto=True
    )
    fig_w.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Montserrat", color="#CCC"),
        showlegend=False,
        yaxis=dict(showgrid=True, gridcolor='#333'),
        margin=dict(t=10, l=10, r=10, b=10)
    )
    st.plotly_chart(fig_w, use_container_width=True)

with c2:
    st.markdown("### 🎭 GENRES FAVORIS")
    top_genres = df_filtered['Genre'].value_counts().head(5)
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=top_genres.index, 
        values=top_genres.values, 
        hole=.6,
        marker=dict(colors=['#E50914', '#B20710', '#800509', '#4D0305', '#1A0102']) # Dégradé Rouge
    )])
    fig_pie.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Montserrat", color="#CCC"),
        showlegend=False,
        margin=dict(t=10, l=10, r=10, b=10)
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# SECTION ANALYSE QUALITÉ (RATINGS)
st.markdown("---")
st.markdown("### ⭐ ANALYSE QUALITATIVE")

c3, c4 = st.columns([2, 1])

with c3:
    st.markdown("**DISTRIBUTION DE MES NOTES** (Le Mur de la Vérité)")
    # Catégorisation des notes
    df_filtered['Avis'] = pd.cut(df_filtered['My_Rating'], 
                                 bins=[0, 4, 7, 10], 
                                 labels=['Navet 🍅', 'Moyen 😐', 'Chef d\'œuvre 🔥'])
    
    rating_dist = df_filtered.groupby(['My_Rating', 'Avis']).size().reset_index(name='Count')
    
    fig_hist = px.bar(
        rating_dist, x='My_Rating', y='Count', color='Avis',
        color_discrete_map={'Navet 🍅': '#8B0000', 'Moyen 😐': '#AA8800', 'Chef d\'œuvre 🔥': '#006400'},
    )
    fig_hist.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Montserrat", color="#CCC"),
        xaxis=dict(tickmode='linear', dtick=1, title="Note sur 10"),
        yaxis=dict(showgrid=True, gridcolor='#333'),
        bargap=0.2
    )
    st.plotly_chart(fig_hist, use_container_width=True)

with c4:
    st.markdown("**TEMPÉRATURE MOYENNE**")
    st.markdown("Quand je regarde Netflix...")
    
    fig_temp = px.histogram(df_filtered, x="Temp_C", nbins=10, color_discrete_sequence=['#E50914'])
    fig_temp.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Montserrat", color="#CCC"),
        xaxis_title="Température (°C)",
        yaxis=dict(showgrid=False),
        bargap=0.1
    )
    st.plotly_chart(fig_temp, use_container_width=True)

# SECTION TOP & FLOP (HTML CARDS)
st.markdown("---")
st.markdown("### 🏆 HALL OF FAME vs WALL OF SHAME")

col_top, col_flop = st.columns(2)

with col_top:
    st.markdown("<h4 style='color:#46d369'>🔥 TOP 5 MEILLEURS FILMS/SÉRIES</h4>", unsafe_allow_html=True)
    top_5 = df_filtered.sort_values('My_Rating', ascending=False).drop_duplicates('Title').head(5)
    
    for _, row in top_5.iterrows():
        st.markdown(f"""
        <div style="background: #111; padding: 12px; margin-bottom: 8px; border-left: 4px solid #46d369; border-radius: 4px;">
            <div style="display:flex; justify-content:space-between;">
                <span style="font-weight:bold; color:white;">{row['Title']}</span>
                <span style="background:#46d369; color:#000; padding:2px 6px; border-radius:3px; font-weight:bold;">{row['My_Rating']}</span>
            </div>
            <div style="font-size:0.8rem; color:#888;">{row['Genre']} • {row['Weather']}</div>
        </div>
        """, unsafe_allow_html=True)

with col_flop:
    st.markdown("<h4 style='color:#E50914'>🍅 TOP 5 PIRES NAVETS</h4>", unsafe_allow_html=True)
    flop_5 = df_filtered.sort_values('My_Rating', ascending=True).drop_duplicates('Title').head(5)
    
    for _, row in flop_5.iterrows():
        st.markdown(f"""
        <div style="background: #111; padding: 12px; margin-bottom: 8px; border-left: 4px solid #E50914; border-radius: 4px;">
            <div style="display:flex; justify-content:space-between;">
                <span style="font-weight:bold; color:white;">{row['Title']}</span>
                <span style="background:#E50914; color:#fff; padding:2px 6px; border-radius:3px; font-weight:bold;">{row['My_Rating']}</span>
            </div>
            <div style="font-size:0.8rem; color:#888;">{row['Genre']} • {row['Weather']}</div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; margin-top: 50px; color: #444; font-size: 0.8rem;">
    PROJECT DATA SCIENCE 2024 • POWERED BY PYTHON & STREAMLIT
</div>
""", unsafe_allow_html=True)
