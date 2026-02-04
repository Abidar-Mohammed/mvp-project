import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
import random
from datetime import timedelta, datetime

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Netflix Unwrapped | Personal Analytics",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. GENERATEUR DE DONNÉES RÉALISTES (Si le fichier n'existe pas) ---
def generate_fake_netflix_data():
    """
    Crée un fichier CSV qui imite parfaitement l'export Netflix officiel.
    Simule des comportements humains (Binge watching, pauses, weekends).
    """
    shows = [
        ("Stranger Things", 4, 8), ("The Crown", 6, 10), ("Black Mirror", 6, 5),
        ("Narcos", 3, 10), ("Squid Game", 1, 9), ("Breaking Bad", 5, 13),
        ("The Office (U.S.)", 9, 22), ("Friends", 10, 24), ("Better Call Saul", 6, 10)
    ]
    movies = [
        "The Irishman", "Marriage Story", "Extraction", "Bird Box", "Don't Look Up",
        "Glass Onion", "Red Notice", "Inception", "Interstellar", "Spider-Man"
    ]
    
    data = []
    start_date = datetime(2023, 1, 1)
    end_date = datetime.today()
    current_date = start_date

    while current_date < end_date:
        # Logique humaine : Plus de chance de regarder le weekend
        is_weekend = current_date.weekday() >= 5
        daily_chance = 0.7 if is_weekend else 0.3
        
        if random.random() < daily_chance:
            # On regarde quelque chose aujourd'hui
            if random.random() < 0.2: 
                # 20% de chance que ce soit un film
                movie = random.choice(movies)
                data.append([movie, current_date.strftime("%d/%m/%Y")])
            else:
                # 80% de chance que ce soit une série (Binge Watching !)
                show_name, seasons, eps_per_season = random.choice(shows)
                season = random.randint(1, seasons)
                # On regarde entre 1 et 5 épisodes d'un coup
                episodes_to_watch = random.randint(1, 5) if is_weekend else random.randint(1, 2)
                
                for i in range(episodes_to_watch):
                    ep_num = random.randint(1, eps_per_season)
                    title = f"{show_name}: Saison {season}: Épisode {ep_num}"
                    data.append([title, current_date.strftime("%d/%m/%Y")])
        
        # Avancer d'un jour
        current_date += timedelta(days=1)

    # Création du DataFrame et sauvegarde
    df = pd.DataFrame(data, columns=['Title', 'Date'])
    df.to_csv("NetflixHistory.csv", index=False)
    return df

# --- 3. CHARGEMENT ET TRAITEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    file_name = "NetflixHistory.csv"
    
    # Si le fichier n'existe pas, on le génère
    if not os.path.exists(file_name):
        df = generate_fake_netflix_data()
    else:
        df = pd.read_csv(file_name)

    # Convertir la date (Format Netflix: DD/MM/YYYY)
    df['Date'] = pd.to_datetime(df['Date'], format="%d/%m/%Y")
    
    # --- FEATURE ENGINEERING (La partie "Intelligence") ---
    def parse_content(title):
        # Mots clés indiquant une série
        keywords = ['Saison', 'Season', 'Episode', 'Partie', 'Part', 'Chapter']
        is_show = any(k in title for k in keywords) or (":" in title)
        
        if is_show:
            type_content = "TV Show"
            # On essaie d'extraire le nom de la série (avant le premier ":")
            show_name = title.split(":")[0]
            duration = 45 # Moyenne estimée pour une série
        else:
            type_content = "Movie"
            show_name = title
            duration = 100 # Moyenne estimée pour un film
            
        return pd.Series([type_content, show_name, duration])

    df[['Type', 'Show_Name', 'Duration_Mins']] = df['Title'].apply(parse_content)
    
    # Enrichissement temporel
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['Year'] = df['Date'].dt.year
    
    return df

df = load_data()

# --- 4. CSS "NETFLIX DARK MODE" ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');

    /* FOND NOIR NETFLIX */
    .stApp {
        background-color: #141414;
        color: #FFFFFF;
    }
    
    /* TITRES */
    h1, h2, h3 {
        font-family: 'Bebas Neue', sans-serif;
        color: #E50914 !important; /* ROUGE NETFLIX */
        letter-spacing: 2px;
    }
    
    p, label, li {
        font-family: 'Roboto', sans-serif;
        color: #B3B3B3;
    }

    /* CARTES KPI */
    div[data-testid="metric-container"] {
        background-color: #1F1F1F;
        border-radius: 4px;
        padding: 15px;
        border-left: 5px solid #E50914;
    }
    div[data-testid="metric-container"] label {
        color: #808080 !important;
        font-size: 0.9rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 2.5rem;
        font-family: 'Bebas Neue', sans-serif;
    }

    /* BOUTON METHODOLOGIE */
    div.stButton > button {
        background-color: transparent;
        border: 1px solid #E50914;
        color: #E50914;
        border-radius: 2px;
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.2rem;
    }
    div.stButton > button:hover {
        background-color: #E50914;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

# --- 5. HEADER ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("NETFLIX UNWRAPPED")
    st.markdown("*Analyse de mes habitudes de visionnage & Binge-Watching*")

# --- 6. METHODOLOGY BUTTON ---
if 'show_meta' not in st.session_state:
    st.session_state.show_meta = False

def toggle_meta():
    st.session_state.show_meta = not st.session_state.show_meta

with col_h2:
    st.write("") # Spacer
    btn_text = "✕ CLOSE INFO" if st.session_state.show_meta else "ℹ️ ABOUT DATA"
    st.button(btn_text, on_click=toggle_meta, use_container_width=True)

if st.session_state.show_meta:
    st.markdown("""
    <div style="background-color: #1F1F1F; padding: 20px; border-radius: 5px; border: 1px solid #333; margin-bottom: 20px;">
        <h4 style="color: white;">ℹ️ Methodology</h4>
        <ul style="color: #999;">
            <li><strong>Data Source:</strong> Netflix "Viewing Activity" Export (Simulated for Demo).</li>
            <li><strong>Feature Engineering:</strong> The raw data only contains 'Title' and 'Date'. I used Python to parse the titles and distinguish between Movies and TV Shows based on keywords (Season, Episode).</li>
            <li><strong>Estimation:</strong> Duration is estimated (45min for Series, 100min for Movies) to calculate total time lost.</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

# --- 7. KPIs ---
total_items = len(df)
total_mins = df['Duration_Mins'].sum()
total_hours = int(total_mins / 60)
top_show = df[df['Type'] == 'TV Show']['Show_Name'].mode()[0]
active_days = df['Date'].nunique()

c1, c2, c3, c4 = st.columns(4)
c1.metric("TOTAL WATCHED", f"{total_items}", "Items")
c2.metric("TIME LOST", f"{total_hours}h", "Approx.")
c3.metric("OBSESSION", top_show, "Top Series")
c4.metric("ACTIVE DAYS", active_days, "Days/Year")

st.markdown("---")

# --- 8. VISUALISATIONS ---

# Layout Plotly Noir/Rouge
netflix_layout = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#B3B3B3', family="Roboto"),
    margin=dict(t=30, l=10, r=10, b=10),
    colorway=['#E50914', '#F5F5F1', '#564d4d'] # Palette Netflix
)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📅 Activity Calendar (Heatmap)")
    # Préparation données Heatmap
    heatmap_data = df.groupby(['DayOfWeek', 'Month']).size().reset_index(name='Count')
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    fig_heat = px.density_heatmap(
        heatmap_data, x='Month', y='DayOfWeek', z='Count',
        category_orders={'DayOfWeek': days_order},
        color_continuous_scale=['#000000', '#B20710', '#E50914'], # Noir vers Rouge
        title="Quand est-ce que je regarde Netflix ?"
    )
    fig_heat.update_layout(**netflix_layout)
    st.plotly_chart(fig_heat, use_container_width=True)

with col2:
    st.subheader("🎥 Movies vs TV Shows")
    type_counts = df['Type'].value_counts().reset_index()
    type_counts.columns = ['Type', 'Count']
    
    fig_pie = px.pie(
        type_counts, values='Count', names='Type',
        hole=0.6,
        color_discrete_sequence=['#E50914', '#555555']
    )
    fig_pie.update_traces(textposition='outside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=False, **netflix_layout)
    st.plotly_chart(fig_pie, use_container_width=True)

# --- TOP 10 SERIES ---
st.subheader("🏆 Top 10 Most Watched Series")
top_shows = df[df['Type'] == 'TV Show']['Show_Name'].value_counts().head(10).reset_index()
top_shows.columns = ['Series', 'Episodes']

fig_bar = px.bar(
    top_shows, x='Episodes', y='Series',
    orientation='h',
    color='Episodes',
    color_continuous_scale=['#333333', '#E50914']
)
fig_bar.update_layout(**netflix_layout, yaxis=dict(autorange="reversed"))
st.plotly_chart(fig_bar, use_container_width=True)

# --- BINGE WATCHING ANALYSIS ---
st.markdown("---")
col_b1, col_b2 = st.columns(2)

with col_b1:
    st.subheader("📈 Consumption Velocity")
    # Cumul des heures au fil du temps
    df = df.sort_values('Date')
    df['Cumul_Hours'] = df['Duration_Mins'].cumsum() / 60
    
    fig_line = px.area(
        df, x='Date', y='Cumul_Hours',
        title="Total Hours Accumulated Over Time"
    )
    fig_line.update_traces(line_color='#E50914', fillcolor='rgba(229, 9, 20, 0.2)')
    fig_line.update_layout(**netflix_layout)
    st.plotly_chart(fig_line, use_container_width=True)

with col_b2:
    st.subheader("🧠 Binge-Watching Intensity")
    # Nombre d'épisodes par jour
    daily_activity = df.groupby('Date').size().reset_index(name='Items')
    
    fig_hist = px.histogram(
        daily_activity, x='Items',
        nbins=20,
        title="Distribution: How many items per session?",
        color_discrete_sequence=['#E50914']
    )
    fig_hist.update_layout(bargap=0.1, **netflix_layout)
    st.plotly_chart(fig_hist, use_container_width=True)

st.markdown("""
<div style="text-align: center; color: #666; font-size: 0.8rem; margin-top: 50px;">
    NETFLIX UNWRAPPED | VISUAL ANALYTICS PROJECT 2024
</div>
""", unsafe_allow_html=True)
