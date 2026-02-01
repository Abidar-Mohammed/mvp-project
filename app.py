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

# --- 3. FONCTIONS DE DONNÉES ROBUSTES ---
def generate_dummy_data():
    """Génère des données de secours si le CSV est absent."""
    dates = pd.date_range(start="2024-01-01", periods=300, freq="D")
    df = pd.DataFrame({'datetime': dates})
    df['Type'] = np.random.choice(['Latte', 'Americano', 'Espresso'], 300)
    df['Price'] = np.random.uniform(2, 5, 300)
    # Données perso simulées
    df['Mood Score'] = np.random.randint(5, 11, 300)
    df['Sleep Quality'] = np.random.normal(7.5, 1.0, 300).clip(4, 10)
    df['Caffeine_mg'] = 80
    df['Location'] = 'Home'
    return df

@st.cache_data
def load_data():
    # --- A. CHARGEMENT FICHIER ---
    file_name = "Coffe_sales.csv"
    df = None
    
    # Stratégies de recherche du fichier
    possible_paths = [
        file_name,
        os.path.join(os.path.dirname(__file__), file_name)
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            try:
                df = pd.read_csv(path)
                break
            except:
                continue
    
    if df is None:
        df = generate_dummy_data()

    # --- B. NETTOYAGE & RENOMMAGE ---
    df.columns = df.columns.str.strip()
    col_map = {
        'coffee_name': 'Type', 'coffee_type': 'Type', 
        'money': 'Price', 'price': 'Price',
        'Date': 'Date_Str', 'date': 'Date_Str', 'Time': 'Time_Str'
    }
    df = df.rename(columns=col_map)
    
    # Création colonne datetime robuste
    try:
        if 'Time_Str' in df.columns and 'Date_Str' in df.columns:
            # On convertit les deux en string pour éviter les erreurs de type
            df['datetime'] = pd.to_datetime(df['Date_Str'].astype(str) + ' ' + df['Time_Str'].astype(str), errors='coerce')
        elif 'Date_Str' in df.columns:
            df['datetime'] = pd.to_datetime(df['Date_Str'], errors='coerce')
        else:
            # Si pas de colonne date, on garde le datetime existant (cas dummy)
            if 'datetime' not in df.columns:
                 df['datetime'] = pd.to_datetime("2024-01-01")
    except:
        df = generate_dummy_data()

    # Supprimer les dates invalides
    df = df.dropna(subset=['datetime'])

    # --- C. ENRICHISSEMENT "PERSONAL DATA" ---
    df = df.sort_values('datetime')
    np.random.seed(42)
    
    # Echantillonnage (Simulation d'une personne unique)
    if len(df) > 800:
        df_personal = df.sample(frac=0.15).copy()
    else:
        df_personal = df.copy()
        
    df_personal = df_personal.sort_values('datetime')
    n = len(df_personal)
    
    # Ajout attributs persos (Si pas déjà présents)
    if 'Mood Score' not in df_personal.columns:
        df_personal['Mood Score'] = np.random.randint(4, 11, n)
    if 'Sleep Quality' not in df_personal.columns:
        df_personal['Sleep Quality'] = np.random.normal(7.2, 1.1, n).clip(4, 10).round(1)
    if 'Location' not in df_personal.columns:
        df_personal['Location'] = np.random.choice(['Home', 'Office', 'University', 'Cafe'], n, p=[0.3, 0.4, 0.2, 0.1])
    
    # Estimation Caféine
    caffeine_map = {
        'Latte': 75, 'Americano': 95, 'Espresso': 63, 'Cappuccino': 80, 
        'Cocoa': 5, 'Hot Chocolate': 5, 'Tea': 40
    }
    # Utilisation de .get pour éviter les erreurs si le type est inconnu
    if 'Caffeine_mg' not in df_personal.columns:
        df_personal['Caffeine_mg'] = df_personal['Type'].apply(lambda x: caffeine_map.get(str(x), 80))
    
    # --- D. COLONNES DÉRIVÉES ---
    df_personal['Date_Only'] = df_personal['datetime'].dt.date
    df_personal['Date_Str_Clean'] = df_personal['datetime'].dt.strftime('%Y-%m-%d')
    df_personal['Hour'] = df_personal['datetime'].dt.hour
    df_personal['DayOfWeek'] = df_personal['datetime'].dt.day_name()
    df_personal['Month'] = df_personal['datetime'].dt.to_period('M').astype(str)
    df_personal['Week'] = df_personal['datetime'].dt.isocalendar().week
    
    return df_personal

df = load_data()

# --- 4. SIDEBAR AVANCÉE ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/924/924514.png", width=70)
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    
    # Filtres
    if not df.empty:
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input("📅 Période", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        types = list(df['Type'].astype(str).unique())
        sel_types = st.multiselect("☕ Type de Café", types, default=types[:3] if len(types)>3 else types)
        
        st.markdown("---")
        st.markdown("### 🎯 Objectifs")
        budget_goal = st.slider("Budget Mensuel ($)", 20, 300, 100)
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
    fav_coffee = df_filtered['Type'].mode()[0] if not df_filtered.empty else "N/A"
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Tasses", f"{tot_cups}")
    c2.metric("Dépense Totale", f"${tot_spent:,.0f}")
    c3.metric("Humeur Moyenne", f"{avg_mood:.1f}/10")
    c4.metric("Café Favori", f"{fav_coffee}")
    
    st.markdown("---")
    
    # Insight Automatique
    if avg_mood > 7:
        st.success(f"🌟 **Insight:** Votre humeur est excellente sur cette période ! Le {fav_coffee} semble vous réussir.")
    else:
        st.info(f"💡 **Insight:** Humeur modérée. Avez-vous pensé à réduire la caféine l'après-midi ?")

    # Graphiques Principaux
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("🕰️ Habitudes (Heure vs Jour)")
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
        st.subheader("☕ Préférences")
        fig_pie = px.pie(
            df_filtered, values='Price', names='Type', 
            hole=0.4, 
            color_discrete_sequence=px.colors.sequential.RdBu,
            template='simple_white'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 2: SANTÉ ---
with tab_health:
    st.subheader("❤️ Suivi Caféine & Sommeil")
    
    c1, c2 = st.columns(2)
    
    with c1:
        daily_caf = df_filtered.groupby('Date_Str_Clean')['Caffeine_mg'].sum().reset_index()
        fig_caf = go.Figure()
        fig_caf.add_trace(go.Bar(x=daily_caf['Date_Str_Clean'], y=daily_caf['Caffeine_mg'], name='Ma Conso', marker_color='#6D4C41'))
        fig_caf.add_trace(go.Scatter(
            x=daily_caf['Date_Str_Clean'], y=[caffeine_limit]*len(daily_caf), 
            mode='lines', name='Limite Santé', line=dict(color='red', dash='dash')
        ))
        fig_caf.update_layout(title="Caféine Quotidienne vs Limite", template="simple_white", yaxis_title="mg")
        st.plotly_chart(fig_caf, use_container_width=True)
        
    with c2:
        fig_sleep = px.scatter(
            df_filtered, x='Hour', y='Sleep Quality',
            size='Caffeine_mg', color='Type',
            title="Caféine Tardive vs Qualité Sommeil",
            template='simple_white',
            labels={'Hour': 'Heure de consommation', 'Sleep Quality': 'Qualité Sommeil'}
        )
        # CORRECTION DU BUG ICI : Suppression de 'opacity' et utilisation de 'rgba' pour la couleur
        fig_sleep.add_shape(
            type="line", 
            x0=17, y0=9, x1=23, y1=5, 
            line=dict(color="rgba(255, 0, 0, 0.5)", width=2, dash="dot")
        )
        st.plotly_chart(fig_sleep, use_container_width=True)

# --- TAB 3: FINANCES ---
with tab_finance:
    st.subheader("💳 Analyse Budgétaire")
    
    col_f1, col_f2 = st.columns([1, 2])
    
    with col_f1:
        current_month = df_filtered['Month'].max()
        monthly_spend = df_filtered[df_filtered['Month'] == current_month]['Price'].sum()
        
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = monthly_spend,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Dépenses ce mois ({current_month})"},
            delta = {'reference': budget_goal},
            gauge = {
                'axis': {'range': [None, max(budget_goal * 1.5, monthly_spend * 1.1)]},
                'bar': {'color': "#4E342E"},
                'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': budget_goal}
            }
        ))
        st.plotly_chart(fig_gauge, use_container_width=True)
        
    with col_f2:
        df_filtered = df_filtered.sort_values('datetime')
        df_filtered['Cumul_Spend'] = df_filtered['Price'].cumsum()
        
        # Prédiction simple (Linéaire)
        last_val = df_filtered['Cumul_Spend'].iloc[-1]
        
        fig_trend = px.area(
            df_filtered, x='datetime', y='Cumul_Spend',
            title="Dépense Cumulée",
            color_discrete_sequence=['#8D6E63'],
            template="simple_white"
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# --- TAB 4: AVANCÉ ---
with tab_advanced:
    c_a1, c_a2 = st.columns(2)
    
    with c_a1:
        st.subheader("🕸️ Profil Multidimensionnel")
        radar_data = df_filtered.groupby('Type').agg({
            'Price': 'mean',
            'Mood Score': 'mean',
            'Sleep Quality': 'mean',
            'Caffeine_mg': 'mean'
        }).reset_index()
        
        # Normalisation 0-1
        for col in ['Price', 'Mood Score', 'Sleep Quality', 'Caffeine_mg']:
            max_val = radar_data[col].max()
            if max_val > 0:
                radar_data[col] = radar_data[col] / max_val
            
        categories = ['Prix', 'Humeur', 'Sommeil', 'Caféine']
        fig_radar = go.Figure()
        
        # Top 3 types
        top_types = df_filtered['Type'].value_counts().head(3).index.tolist()
        
        for t in top_types:
            if t in radar_data['Type'].values:
                d = radar_data[radar_data['Type'] == t].iloc[0]
                values = [d['Price'], d['Mood Score'], d['Sleep Quality'], d['Caffeine_mg']]
                fig_radar.add_trace(go.Scatterpolar(r=values, theta=categories, fill='toself', name=str(t)))
            
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), showlegend=True, height=400)
        st.plotly_chart(fig_radar, use_container_width=True)

    with c_a2:
        st.subheader("📅 Calendrier d'Intensité")
        cal_data = df_filtered.groupby(['Week', 'DayOfWeek']).size().reset_index(name='Count')
        
        fig_cal = px.density_heatmap(
            cal_data, x='Week', y='DayOfWeek', z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale='Greens',
            template='simple_white',
            title="Intensité par Semaine"
        )
        st.plotly_chart(fig_cal, use_container_width=True)

# --- TAB 5: MÉTHODOLOGIE ---
with tab_method:
    st.markdown("""
    ### 📝 Méthodologie du Projet
    
    **1. Transformation des Données**
    J'ai transformé un fichier brut de transactions pour l'adapter à un contexte personnel ("Quantified Self").
    * **Nettoyage :** Standardisation des dates et des noms de colonnes.
    * **Échantillonnage :** Sélection de 15% des données pour simuler une consommation humaine réaliste.
    
    **2. Enrichissement (Augmentation)**
    J'ai ajouté des variables synthétiques pour démontrer des capacités d'analyse avancées :
    * **Humeur & Sommeil :** Générés aléatoirement pour explorer les corrélations bien-être.
    * **Caféine :** Mappée selon le type de boisson.
    
    **3. Design & Interactions**
    * Utilisation de **Plotly** pour l'interactivité.
    * Système d'onglets pour organiser l'histoire des données.
    """)
    
    col_d1, col_d2 = st.columns([3, 1])
    with col_d1:
        st.dataframe(df_filtered)
    with col_d2:
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Télécharger CSV", data=csv, file_name='my_coffee_log.csv', mime='text/csv')

st.markdown("---")
st.caption("Projet Visual Analytics | 2024")
