import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="My Quantified Self: Coffee",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PERSONNALISÉ ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700&display=swap');
    
    html, body, [class*="css"]  { 
        font-family: 'Lato', sans-serif; 
        background-color: #FDFBF7; 
        color: #4E342E; 
    }
    
    .header-box {
        background: linear-gradient(135deg, #3E2723 0%, #5D4037 100%);
        padding: 30px; 
        border-radius: 20px; 
        text-align: center; 
        color: #FFFFFF;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        margin-bottom: 25px;
    }
    
    /* Style des cartes KPIs */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #D7CCC8;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }

    .stPlotlyChart { 
        background-color: white; 
        border-radius: 15px; 
        padding: 10px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
        border: 1px solid #EFEBE9;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT ET ENRICHISSEMENT DES DONNÉES ---
@st.cache_data
def load_data():
    # --- A. CHARGEMENT FICHIER ---
    file_name = "Coffe_sales.csv"
    path = None
    if os.path.exists(file_name):
        path = file_name
    elif os.path.exists(os.path.join(os.path.dirname(__file__), file_name)):
        path = os.path.join(os.path.dirname(__file__), file_name)

    if path:
        try:
            df = pd.read_csv(path)
        except:
            return generate_dummy_data()
    else:
        return generate_dummy_data()

    # --- B. NETTOYAGE ---
    df.columns = df.columns.str.strip()
    col_map = {
        'coffee_name': 'Type', 'coffee_type': 'Type', 
        'money': 'Price', 'price': 'Price',
        'Date': 'Date_Str', 'date': 'Date_Str', 'Time': 'Time_Str'
    }
    df = df.rename(columns=col_map)
    
    # Gestion Date
    try:
        if 'Time_Str' in df.columns:
            df['datetime'] = pd.to_datetime(df['Date_Str'].astype(str) + ' ' + df['Time_Str'].astype(str))
        else:
            df['datetime'] = pd.to_datetime(df['Date_Str'])
    except:
        return generate_dummy_data()

    # --- C. PERSONALISATION (La partie importante pour le Prof) ---
    df = df.sort_values('datetime')
    np.random.seed(42)
    
    # Echantillonnage pour simuler 1 personne
    if len(df) > 800:
        df_personal = df.sample(frac=0.15).copy()
    else:
        df_personal = df.copy()
        
    df_personal = df_personal.sort_values('datetime')
    n = len(df_personal)
    
    # Ajout d'attributs personnels
    df_personal['Mood Score'] = np.random.randint(4, 11, n) # 4 à 10
    df_personal['Sleep Quality'] = np.random.normal(7.2, 1.1, n).clip(4, 10).round(1) 
    df_personal['Location'] = np.random.choice(['Home', 'Office', 'University', 'Cafe'], n, p=[0.3, 0.4, 0.2, 0.1])
    
    # Estimation Caféine (Nouvelle fonctionnalité)
    caffeine_map = {
        'Latte': 75, 'Americano': 95, 'Espresso': 63, 'Cappuccino': 80, 
        'Cocoa': 5, 'Hot Chocolate': 5, 'Tea': 40
    }
    # Fonction lambda robuste pour mapper, valeur par défaut 80mg si inconnu
    df_personal['Caffeine_mg'] = df_personal['Type'].apply(lambda x: caffeine_map.get(x, 80))
    
    # Colonnes temps
    df_personal['Hour'] = df_personal['datetime'].dt.hour
    df_personal['DayOfWeek'] = df_personal['datetime'].dt.day_name()
    df_personal['Month'] = df_personal['datetime'].dt.to_period('M').astype(str)
    df_personal['Week'] = df_personal['datetime'].dt.isocalendar().week
    
    return df_personal

def generate_dummy_data():
    # Fonction de secours
    dates = pd.date_range(start="2024-01-01", periods=300, freq="D")
    df = pd.DataFrame({'datetime': dates})
    df['Type'] = np.random.choice(['Latte', 'Americano'], 300)
    df['Price'] = np.random.uniform(2, 5, 300)
    df['Mood Score'] = np.random.randint(5, 10, 300)
    df['Sleep Quality'] = 7.5
    df['Caffeine_mg'] = 80
    df['Location'] = 'Home'
    df['Hour'] = 9
    df['DayOfWeek'] = 'Monday'
    df['Month'] = '2024-01'
    df['Week'] = 1
    return df

df = load_data()

# --- 4. SIDEBAR AVANCÉE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/924/924514.png", width=70)
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    
    # Filtres
    min_d = df['datetime'].min().date()
    max_d = df['datetime'].max().date()
    date_range = st.date_input("📅 Période", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    
    types = list(df['Type'].unique())
    sel_types = st.multiselect("☕ Type de Café", types, default=types[:3])
    
    st.markdown("---")
    st.markdown("### 🎯 Objectifs")
    # NOUVEAU : Budget interactif
    budget_goal = st.slider("Budget Mensuel ($)", 20, 300, 100)
    # NOUVEAU : Limite Caféine
    caffeine_limit = st.number_input("Limite Caféine (mg/jour)", 100, 800, 400, step=50)

# Filtrage global
mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1]) & (df['Type'].isin(sel_types))
df_filtered = df[mask]

# --- 5. MAIN DASHBOARD ---
st.markdown("""
<div class="header-box">
    <h1 style="margin:0;">☕ My Quantified Self</h1>
    <p style="font-size:16px; margin-top:5px; opacity:0.9;">
        Analyse personnelle de ma consommation, de ma santé et de mon budget café.
    </p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.error("Aucune donnée disponible. Ajustez les filtres.")
    st.stop()

# --- NAVIGATION PAR ONGLETS ---
tab_overview, tab_health, tab_finance, tab_advanced, tab_method = st.tabs([
    "📊 Overview", "❤️ Santé & Habitudes", "💳 Finances", "🧠 Analyse Avancée", "📝 Méthodologie"
])

# --- TAB 1: OVERVIEW ---
with tab_overview:
    # KPIs
    tot_cups = len(df_filtered)
    tot_spent = df_filtered['Price'].sum()
    avg_mood = df_filtered['Mood Score'].mean()
    fav_coffee = df_filtered['Type'].mode()[0]
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tasses", f"{tot_cups}")
    c2.metric("Dépense Totale", f"${tot_spent:,.0f}")
    c3.metric("Humeur Moyenne", f"{avg_mood:.1f}/10")
    c4.metric("Café Favori", f"{fav_coffee}")
    
    st.markdown("---")
    
    # Graphiques Principaux
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("🕰️ Carte de Chaleur (Habitudes)")
        hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            hm_data, x='Hour', y='DayOfWeek', z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale='Oranges',
            template='simple_white',
            labels={'Hour': 'Heure', 'DayOfWeek': 'Jour', 'Count': 'Tasses'}
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with c_right:
        st.subheader("☕ Répartition")
        fig_pie = px.pie(
            df_filtered, values='Price', names='Type', 
            hole=0.4, 
            color_discrete_sequence=px.colors.sequential.RdBu,
            template='simple_white'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: SANTÉ (NOUVEAU) ---
with tab_health:
    st.subheader("❤️ Suivi Caféine & Sommeil")
    
    c1, c2 = st.columns(2)
    
    with c1:
        # 1. Histogramme Caféine Quotidienne vs Limite
        daily_caf = df_filtered.groupby('Date_Str')['Caffeine_mg'].sum().reset_index()
        fig_caf = go.Figure()
        fig_caf.add_trace(go.Bar(x=daily_caf['Date_Str'], y=daily_caf['Caffeine_mg'], name='Ma Conso', marker_color='#6D4C41'))
        # Ligne de limite
        fig_caf.add_trace(go.Scatter(
            x=daily_caf['Date_Str'], y=[caffeine_limit]*len(daily_caf), 
            mode='lines', name='Limite Santé', line=dict(color='red', dash='dash')
        ))
        fig_caf.update_layout(title="Caféine Quotidienne vs Limite", template="simple_white", yaxis_title="mg")
        st.plotly_chart(fig_caf, use_container_width=True)
        
    with c2:
        # 2. Sommeil vs Heure de consommation
        fig_sleep = px.scatter(
            df_filtered, x='Hour', y='Sleep Quality',
            size='Caffeine_mg', color='Type',
            title="Impact sur le Sommeil (Taille = Caféine)",
            template='simple_white',
            labels={'Hour': 'Heure de consommation', 'Sleep Quality': 'Qualité Sommeil'}
        )
        st.plotly_chart(fig_sleep, use_container_width=True)

# --- TAB 3: FINANCES (NOUVEAU) ---
with tab_finance:
    st.subheader("💳 Analyse Budgétaire")
    
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        # Jauge Budget Mensuel Actuel
        current_month = df_filtered['Month'].max()
        monthly_spend = df_filtered[df_filtered['Month'] == current_month]['Price'].sum()
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = monthly_spend,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Dépenses ce mois ({current_month})"},
            delta = {'reference': budget_goal},
            gauge = {
                'axis': {'range': [None, budget_goal * 1.5]},
                'bar': {'color': "#4E342E"},
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': budget_goal}
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with col_f2:
        # Tendance cumulée
        df_filtered['Cumul_Spend'] = df_filtered['Price'].cumsum()
        fig_trend = px.area(
            df_filtered, x='datetime', y='Cumul_Spend',
            title="Dépense Cumulée sur la Période",
            color_discrete_sequence=['#8D6E63'],
            template="simple_white"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# --- TAB 4: AVANCÉ (NOUVEAU) ---
with tab_advanced:
    c_a1, c_a2 = st.columns(2)
    
    with c_a1:
        st.subheader("🕸️ Mon Profil Café (Radar)")
        # Agrégation par type
        radar_data = df_filtered.groupby('Type').agg({
            'Price': 'mean',
            'Mood Score': 'mean',
            'Sleep Quality': 'mean',
            'Caffeine_mg': 'mean'
        }).reset_index()
        
        # Normalisation pour le radar (0-1)
        for col in ['Price', 'Mood Score', 'Sleep Quality', 'Caffeine_mg']:
            radar_data[col] = radar_data[col] / radar_data[col].max()
            
        categories = ['Prix', 'Humeur', 'Sommeil', 'Caféine']
        
        fig_radar = go.Figure()
        # On prend les 2 types les plus fréquents
        top_types = df_filtered['Type'].value_counts().head(2).index.tolist()
        
        for t in top_types:
            d = radar_data[radar_data['Type'] == t].iloc[0]
            values = [d['Price'], d['Mood Score'], d['Sleep Quality'], d['Caffeine_mg']]
            fig_radar.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name=t))
            
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, height=400)
        st.plotly_chart(fig_radar, use_container_width=True)

    with c_a2:
        st.subheader("📅 Calendrier d'Intensité")
        # Heatmap par Semaine vs Jour
        cal_data = df_filtered.groupby(['Week', 'DayOfWeek']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_cal = px.density_heatmap(
            cal_data, x='Week', y='DayOfWeek', z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale='Greens', # Vert type GitHub
            template='simple_white',
            title="Vue Calendrier (Semaines vs Jours)"
        )
        st.plotly_chart(fig_cal, use_container_width=True)

# --- TAB 5: MÉTHODOLOGIE ---
with tab_method:
    st.markdown("""
    ### 📝 Méthodologie du Projet
    
    **1. Transformation des Données ("Data Wrangling")**
    Pour passer d'un fichier de transactions (`Coffe_sales.csv`) à une analyse personnelle, j'ai appliqué un **échantillonnage aléatoire (15%)** pour simuler une consommation humaine réaliste (1-2 tasses/jour).
    
    **2. Enrichissement (Augmentation)**
    J'ai enrichi les données avec des estimations :
    * **Caféine :** Basée sur les standards (ex: Espresso = 63mg).
    * **Humeur & Sommeil :** Générés synthétiquement pour explorer les corrélations.
    
    **3. Choix de Design**
    * **Couleurs :** Palette Marron/Crème pour le thème Café.
    * **Visualisations :**
        * *Jauge* pour le suivi d'objectif budgétaire.
        * *Radar Chart* pour comparer les caractéristiques multidimensionnelles des types de café.
    """)
    
    # Données brutes et téléchargement
    st.markdown("---")
    col_d1, col_d2 = st.columns([3, 1])
    with col_d1:
        st.dataframe(df_filtered)
    with col_d2:
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger mes Données", data=csv, file_name='my_personal_coffee_log.csv', mime='text/csv')

st.markdown("---")
st.caption("Projet Visual Analytics | 2024")
