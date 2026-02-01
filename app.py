import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="My Quantified Coffee Life",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. DESIGN & CSS (Thème Café/Journal) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap');
    
    html, body, [class*="css"]  { 
        font-family: 'Lato', sans-serif; 
        background-color: #FAF8F5; /* Papier crème */
        color: #3E2723; /* Marron très foncé */
    }
    
    h1, h2, h3 { color: #4E342E; }
    
    /* Header Personnalisé */
    .header-box {
        background: linear-gradient(135deg, #3E2723 0%, #6D4C41 100%);
        padding: 40px; 
        border-radius: 20px; 
        text-align: center; 
        color: #FFFFFF;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15); 
        margin-bottom: 30px;
    }
    
    /* Cartes KPI */
    div[data-testid="metric-container"] {
        background-color: white;
        border-left: 5px solid #8D6E63;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }

    /* Graphiques */
    .stPlotlyChart { 
        background-color: white; 
        border-radius: 15px; 
        padding: 15px; 
        box-shadow: 0 4px 10px rgba(0,0,0,0.05); 
    }
    
    /* Onglets */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #EFEBE9;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF;
        color: #3E2723;
        font-weight: bold;
        border-top: 2px solid #3E2723;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    file_name = "my_coffee_life.csv"
    
    # Recherche robuste du fichier
    path = None
    if os.path.exists(file_name):
        path = file_name
    elif os.path.exists(os.path.join(os.path.dirname(__file__), file_name)):
        path = os.path.join(os.path.dirname(__file__), file_name)
    
    if path:
        df = pd.read_csv(path)
        
        # Conversion Date
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # Enrichissement Temporel
        df['Hour'] = df['datetime'].dt.hour
        df['DayOfWeek'] = df['datetime'].dt.day_name()
        df['Month'] = df['datetime'].dt.to_period('M').astype(str)
        df['Week'] = df['datetime'].dt.isocalendar().week
        df['Date_Only'] = df['datetime'].dt.date
        
        # Calcul du Boost d'Humeur (Différence Après - Avant)
        df['Mood_Boost'] = df['mood_after'] - df['mood_before']
        
        return df
    else:
        # Fallback si le fichier n'est pas trouvé (pour éviter le crash)
        st.error(f"⚠️ Fichier '{file_name}' introuvable. Veuillez lancer 'generate_data.py' d'abord.")
        return pd.DataFrame()

df = load_data()

# --- 4. SIDEBAR (FILTRES) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2935/2935413.png", width=80)
    st.markdown("## ⚙️ Filtres")
    
    if not df.empty:
        # Filtre Date
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input("📅 Période", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        # Filtre Contexte Social
        all_social = list(df['social_context'].unique())
        sel_social = st.multiselect("👥 Contexte Social", all_social, default=all_social)
        
        # Filtre Lieu
        all_loc = list(df['location'].unique())
        sel_loc = st.multiselect("📍 Lieu", all_loc, default=all_loc)
        
        st.markdown("---")
        st.info("Ce dashboard analyse mes données personnelles générées pour comprendre l'impact de la caféine sur mon sommeil et mon humeur.")

# Application des filtres
if not df.empty:
    mask = (
        (df['datetime'].dt.date >= date_range[0]) & 
        (df['datetime'].dt.date <= date_range[1]) &
        (df['social_context'].isin(sel_social)) &
        (df['location'].isin(sel_loc))
    )
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. EN-TÊTE ---
st.markdown("""
<div class="header-box">
    <h1 style="margin:0;">☕ My Quantified Coffee Life</h1>
    <p style="font-size:18px; margin-top:5px; opacity:0.9;">
        Analyse holistique de ma consommation : Habitudes, Contexte et Impact Biologique.
    </p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("Aucune donnée avec ces filtres.")
    st.stop()

# --- 6. ONGLETS PRINCIPAUX ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Vue d'Ensemble", 
    "🧬 Style de Vie & Contexte", 
    "💤 Impact & Santé", 
    "📝 À propos du Projet"
])

# --- TAB 1: OVERVIEW ---
with tab1:
    # KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cafés", len(df_filtered), help="Nombre total de tasses")
    c2.metric("Budget Total", f"${df_filtered['price'].sum():.0f}", help="Dépense cumulée")
    c3.metric("Sommeil Moyen", f"{df_filtered['sleep_hours_next_night'].mean():.1f}h", help="Moyenne des nuits suivantes")
    c4.metric("Boost Humeur", f"+{df_filtered['Mood_Boost'].mean():.1f} pts", help="Gain moyen d'humeur après café")
    
    st.markdown("---")
    
    col_heat, col_pie = st.columns([2, 1])
    
    with col_heat:
        st.subheader("🕰️ Carte de Chaleur : Mes Habitudes")
        st.caption("Quand est-ce que je bois le plus de café ?")
        
        # Heatmap (Jours vs Heures)
        hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            hm_data, x='Hour', y='DayOfWeek', z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale='Oranges',
            template='simple_white',
            labels={'Hour': 'Heure (0-24)', 'DayOfWeek': 'Jour', 'Count': 'Intensité'}
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_pie:
        st.subheader("☕ Mes Préférences")
        fig_pie = px.donut(
            df_filtered, values='price', names='coffee_type',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Brwnyl,
            template='simple_white'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=False, margin=dict(t=20, b=20, l=20, r=20))
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: LIFESTYLE (NOUVEAU - Exploite les nouvelles colonnes) ---
with tab2:
    st.subheader("🌍 Contexte de consommation")
    
    col_sun, col_act = st.columns(2)
    
    with col_sun:
        st.markdown("**Où, avec qui et quoi ? (Hiérarchie)**")
        # Sunburst Chart : Lieu -> Social -> Type
        fig_sun = px.sunburst(
            df_filtered, 
            path=['location', 'social_context', 'coffee_type'], 
            values='price',
            color='location',
            color_discrete_sequence=px.colors.qualitative.Antique
        )
        fig_sun.update_layout(height=450, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig_sun, use_container_width=True)
        
    with col_act:
        st.markdown("**Que faisais-je en buvant ?**")
        # Bar chart des activités
        act_counts = df_filtered['activity'].value_counts().reset_index()
        act_counts.columns = ['Activité', 'Nombre']
        
        fig_bar = px.bar(
            act_counts, x='Nombre', y='Activité', orientation='h',
            color='Nombre', color_continuous_scale='Brwnyl',
            template='simple_white'
        )
        fig_bar.update_layout(height=450)
        st.plotly_chart(fig_bar, use_container_width=True)

# --- TAB 3: IMPACT (LA PARTIE SCIENTIFIQUE) ---
with tab3:
    st.subheader("🧪 Analyse d'Impact Biologique")
    st.markdown("Cette section explore les corrélations entre mes habitudes (heure, caféine) et ma santé (sommeil, humeur).")
    
    col_sleep, col_mood = st.columns(2)
    
    with col_sleep:
        st.markdown("#### 💤 La Caféine tue-t-elle mon sommeil ?")
        # Scatter Plot : Heure vs Sommeil (avec taille = dose caféine)
        fig_sleep = px.scatter(
            df_filtered, 
            x='Hour', 
            y='sleep_hours_next_night',
            size='caffeine_mg',
            color='location', # Couleur par lieu pour voir si le café du bureau est coupable
            color_discrete_sequence=px.colors.qualitative.Bold,
            template='simple_white',
            labels={'Hour': 'Heure du Café', 'sleep_hours_next_night': 'Heures de Sommeil (Nuit Suivante)'},
            title="Corrélation : Heure vs Sommeil"
        )
        # Zone de danger visuelle (Après 16h)
        fig_sleep.add_vrect(x0=16, x1=24, fillcolor="red", opacity=0.1, annotation_text="Zone à Risque")
        st.plotly_chart(fig_sleep, use_container_width=True)
        
    with col_mood:
        st.markdown("#### 🙂 L'effet sur l'Humeur")
        # Comparaison Humeur Avant vs Après par type de café
        mood_data = df_filtered.groupby('coffee_type')[['mood_before', 'mood_after']].mean().reset_index()
        # Transformation pour le graphique en haltère (dumbell plot) ou lignes
        
        fig_mood = go.Figure()
        fig_mood.add_trace(go.Scatter(
            x=mood_data['mood_before'], y=mood_data['coffee_type'],
            mode='markers', name='Avant', marker=dict(color='gray', size=10)
        ))
        fig_mood.add_trace(go.Scatter(
            x=mood_data['mood_after'], y=mood_data['coffee_type'],
            mode='markers', name='Après', marker=dict(color='orange', size=12)
        ))
        # Lignes connectrices
        for i in range(len(mood_data)):
            fig_mood.add_shape(
                type="line",
                x0=mood_data.iloc[i]['mood_before'], x1=mood_data.iloc[i]['mood_after'],
                y0=mood_data.iloc[i]['coffee_type'], y1=mood_data.iloc[i]['coffee_type'],
                line=dict(color="gray", width=1)
            )
            
        fig_mood.update_layout(
            title="Gain d'Humeur Moyen par Type",
            xaxis_title="Score Humeur (1-10)",
            template="simple_white",
            height=400
        )
        st.plotly_chart(fig_mood, use_container_width=True)

    # Radar Chart Global
    st.markdown("---")
    st.subheader("🕸️ Mon Profil de Consommateur")
    
    # Agrégation par Contexte Social
    radar_df = df_filtered.groupby('social_context').agg({
        'price': 'mean',
        'caffeine_mg': 'mean',
        'mood_after': 'mean',
        'sleep_hours_next_night': 'mean'
    }).reset_index()
    
    # Normalisation (Min-Max) pour le radar
    cols_to_norm = ['price', 'caffeine_mg', 'mood_after', 'sleep_hours_next_night']
    for col in cols_to_norm:
        radar_df[col] = (radar_df[col] - radar_df[col].min()) / (radar_df[col].max() - radar_df[col].min() + 0.01)

    categories = ['Coût', 'Caféine', 'Humeur', 'Sommeil']
    fig_radar = go.Figure()

    for i, row in radar_df.iterrows():
        fig_radar.add_trace(go.Scatterpolar(
            r=[row['price'], row['caffeine_mg'], row['mood_after'], row['sleep_hours_next_night']],
            theta=categories,
            fill='toself',
            name=row['social_context']
        ))

    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True)), 
        title="Impact selon le Contexte Social (Normalisé)",
        height=500
    )
    st.plotly_chart(fig_radar, use_container_width=True)

# --- TAB 4: EXPLIATIONS (CRITÈRE PROJET) ---
with tab4:
    st.markdown("""
    ### 📝 À propos de ce Dashboard ("Quantified Self")
    
    **1. Pourquoi ce sujet ?**
    En tant qu'étudiant, je consomme beaucoup de café. J'ai voulu dépasser la simple question "Combien je dépense ?" pour comprendre **"Quel est l'impact sur ma biologie et ma vie sociale ?"**.
    
    **2. La Donnée (Data Source)**
    Ce dashboard repose sur un jeu de données personnel (`my_coffee_life.csv`) généré pour simuler une année de ma vie.
    Il contient des variables riches :
    * **Contexte :** Lieu, Activité, Météo.
    * **Biométrie (Simulée) :** Niveau de stress, Qualité du sommeil, Humeur.
    
    **3. Choix de Design & Encodage Visuel**
    * **Heatmap (Tab 1) :** Choisie car les habitudes sont cycliques (Semaine vs Weekend). C'est le meilleur moyen de voir les "Hotspots" temporels.
    * **Sunburst (Tab 2) :** Permet de voir la hiérarchie des habitudes (Lieu -> Social -> Type) en un seul coup d'œil.
    * **Scatter Plot (Tab 3) :** Indispensable pour prouver la corrélation négative entre l'heure de consommation (Axe X) et la durée du sommeil (Axe Y). La "Zone Rouge" ajoutée après 16h renforce cette analyse.
    
    **4. Limitations**
    * Les données de sommeil sont auto-déclarées (subjectives) dans ce modèle. L'utilisation d'une montre connectée rendrait l'analyse plus précise.
    """)
    
    st.download_button(
        label="📥 Télécharger les Données Brutes (CSV)",
        data=df_filtered.to_csv(index=False).encode('utf-8'),
        file_name='my_quantified_coffee_life.csv',
        mime='text/csv'
    )

st.markdown("---")
st.caption("Projet Visual Analytics 2024 | Développé avec Streamlit & Plotly")
