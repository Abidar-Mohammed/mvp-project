import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from PIL import Image
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Nexus Analytics | Pro",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS AVANCÉ (EFFET "BULLES" & DESIGN) ---
st.markdown("""
<style>
    /* Import police Google (Poppins) pour un look moderne */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
        background-color: #F0F2F5; /* Fond gris très doux */
    }

    /* --- STYLE DES "BULLES" (CARTES) --- */
    /* On cible les conteneurs de graphiques et métriques pour les arrondir */
    .stPlotlyChart, div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border-radius: 20px; /* L'effet "Boule/Arrondi" */
        padding: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.05); /* Ombre douce 3D */
        transition: transform 0.3s ease; /* Petit effet d'animation au survol */
        border: 1px solid #FFFFFF;
    }

    /* Effet "Pop" quand on passe la souris dessus */
    div[data-testid="metric-container"]:hover, .stPlotlyChart:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        border: 1px solid #27AE60;
    }

    /* --- COULEURS DU SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E0E0E0;
    }
    
    /* Titres Sidebar en dégradé */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        background: -webkit-linear-gradient(45deg, #11998e, #38ef7d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
    }

    /* --- HEADER (EN-TÊTE) --- */
    .header-style {
        background: linear-gradient(90deg, #2C3E50 0%, #4CA1AF 100%);
        padding: 20px;
        border-radius: 25px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    /* Style des gros chiffres (Metrics) */
    [data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: #2C3E50;
    }
    
    /* Petits labels */
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #888;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. GÉNÉRATION DE DONNÉES ---
@st.cache_data
def load_data():
    np.random.seed(42)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    n_samples = 3000
    date_range = pd.date_range(start=start_date, end=end_date, freq="H")
    random_dates = np.random.choice(date_range, n_samples)
    
    products = np.random.choice(['Enterprise Suite X1', 'Cloud Storage Pro', 'CyberSecurity Plus', 'AI Consultant Hour'], n_samples)
    countries = np.random.choice(['United States', 'France', 'Germany', 'Japan', 'Brazil', 'United Kingdom', 'India', 'Canada'], n_samples)
    status = np.random.choice(['Confirmed', 'Pending', 'Negotiation', 'Lost'], n_samples, p=[0.7, 0.15, 0.1, 0.05])
    segments = np.random.choice(['Fortune 500', 'SMB', 'Government', 'Startup'], n_samples)
    
    revenue = np.random.randint(2000, 25000, n_samples)
    cost = revenue * np.random.uniform(0.3, 0.7, n_samples)
    satisfaction = np.random.randint(60, 100, n_samples) # Score de 0 à 100
    
    df = pd.DataFrame({
        'Date': random_dates,
        'Product': products,
        'Country': countries,
        'Status': status,
        'Segment': segments,
        'Revenue': revenue,
        'Cost': cost,
        'CSAT': satisfaction
    })
    
    df['Profit'] = df['Revenue'] - df['Cost']
    df['Margin (%)'] = (df['Profit'] / df['Revenue']) * 100
    df['Date'] = pd.to_datetime(df['Date'])
    
    return df.sort_values('Date')

df = load_data()

# --- 4. SIDEBAR AVEC LOGO ---
try:
    # On cherche le fichier LOGO.jpeg
    image = Image.open('LOGO.jpeg')
    st.sidebar.image(image, use_container_width=True)
except FileNotFoundError:
    # Fallback si le fichier n'est pas encore là
    st.sidebar.warning("⚠️ Fichier 'LOGO.jpeg' introuvable.")
    st.sidebar.info("Mets le fichier dans le dossier pour voir le logo !")

st.sidebar.markdown("---")
st.sidebar.title("🎛️ Panneau de Contrôle")

# Filtres
date_range = st.sidebar.date_input("📅 Période", value=(df['Date'].min(), df['Date'].max()))
country_filter = st.sidebar.multiselect("🌍 Pays", df['Country'].unique(), default=['United States', 'France', 'Germany'])
segment_filter = st.sidebar.multiselect("🏢 Segment", df['Segment'].unique(), default=df['Segment'].unique())

mask = (
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1]) &
    (df['Country'].isin(country_filter)) &
    (df['Segment'].isin(segment_filter))
)
df_filtered = df[mask]

if df_filtered.empty:
    st.error("🚫 Oups ! Aucune donnée avec ces filtres.")
    st.stop()

# --- 5. EN-TÊTE PRINCIPALE ---
st.markdown("""
<div class="header-style">
    <h1>🚀 Nexus Command Center</h1>
    <p>Pilotage Stratégique & Analyse de Performance IA</p>
</div>
""", unsafe_allow_html=True)

# --- 6. KPIs (Les Bulles Chiffrées) ---
total_rev = df_filtered['Revenue'].sum()
total_profit = df_filtered['Profit'].sum()
avg_margin = df_filtered['Margin (%)'].mean()
avg_csat = df_filtered['CSAT'].mean()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("💸 Chiffre d'Affaires", f"${total_rev:,.0f}", "+12% ↗")
with c2:
    st.metric("💰 Bénéfice Net", f"${total_profit:,.0f}", "+8% ↗")
with c3:
    st.metric("📊 Marge Moyenne", f"{avg_margin:.1f}%", "-2% ↘")
with c4:
    st.metric("❤️ Satisfaction Client", f"{avg_csat:.0f}/100", "Top !")

st.write("") # Espace

# --- 7. CONTENU VISUEL (Les Bulles Graphiques) ---

# LIGNE 1 : CARTE + TUNNEL DE VENTE
col_L1_1, col_L1_2 = st.columns([2, 1])

with col_L1_1:
    st.subheader("🌍 Intensité des Ventes (Monde)")
    # Carte
    fig_map = px.choropleth(
        df_filtered.groupby('Country')['Revenue'].sum().reset_index(),
        locations="Country",
        locationmode="country names",
        color="Revenue",
        color_continuous_scale="Tealgrn", # Dégradé Vert/Bleu sympa
        template="simple_white"
    )
    fig_map.update_geos(showframe=False, projection_type='natural earth')
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)

with col_L1_2:
    st.subheader("🔻 Tunnel de Vente")
    # Graphique en Entonnoir (Funnel)
    funnel_data = df_filtered.groupby('Status')['Revenue'].count().reset_index().sort_values('Revenue', ascending=False)
    fig_funnel = px.funnel(
        funnel_data, 
        x='Revenue', 
        y='Status',
        color='Status',
        color_discrete_sequence=px.colors.qualitative.Pastel # Couleurs douces
    )
    fig_funnel.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_funnel, use_container_width=True)

# LIGNE 2 : TENDANCES + JAUGE
col_L2_1, col_L2_2 = st.columns([2, 1])

with col_L2_1:
    st.subheader("📈 Évolution Financière & Prédictions")
    # Graphique combiné (Aire + Ligne)
    daily = df_filtered.set_index('Date').resample('W')[['Revenue', 'Profit']].sum().reset_index()
    
    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=daily['Date'], y=daily['Revenue'], fill='tozeroy', 
        name='Revenu', line=dict(color='#1ABC9C', width=0) # Vert d'eau
    ))
    fig_trend.add_trace(go.Scatter(
        x=daily['Date'], y=daily['Profit'], 
        name='Profit', line=dict(color='#2C3E50', width=3) # Bleu foncé
    ))
    fig_trend.update_layout(
        template="simple_white", 
        hovermode="x unified",
        paper_bgcolor='rgba(0,0,0,0)',
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_trend, use_container_width=True)

with col_L2_2:
    st.subheader("🎯 Objectif Annuel")
    # Jauge (Gauge Chart)
    current_val = total_rev
    target_val = 60000000 # Exemple d'objectif : 60 Millions
    
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current_val,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Progression vs Cible"},
        delta = {'reference': target_val},
        gauge = {
            'axis': {'range': [None, target_val]},
            'bar': {'color': "#27AE60"},
            'steps' : [
                {'range': [0, target_val*0.5], 'color': "#E8F8F5"},
                {'range': [target_val*0.5, target_val*0.8], 'color': "#D1F2EB"}
            ],
            'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': target_val}
        }
    ))
    fig_gauge.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=300)
    st.plotly_chart(fig_gauge, use_container_width=True)

# LIGNE 3 : DÉTAILS PRODUITS (TABLEAU AVANCÉ)
st.subheader("📦 Top Produits (Détails)")
prod_stats = df_filtered.groupby('Product').agg(
    CA_Total=('Revenue', 'sum'),
    Marge_Moy=('Margin (%)', 'mean'),
    Ventes=('Date', 'count')
).reset_index()

st.dataframe(
    prod_stats.sort_values('CA_Total', ascending=False),
    column_config={
        "CA_Total": st.column_config.ProgressColumn("Chiffre d'Affaires", format="$%f", min_value=0, max_value=int(prod_stats['CA_Total'].max())),
        "Marge_Moy": st.column_config.NumberColumn("Marge", format="%.1f %%"),
        "Ventes": st.column_config.NumberColumn("Volume", format="%d 🛒")
    },
    use_container_width=True,
    hide_index=True
)

# PIED DE PAGE AVEC PETIT EFFET
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888; padding: 20px;">
    ✨ <b>Nexus Analytics v4.0</b> | Design par IA | 🔒 Données Sécurisées
</div>
""", unsafe_allow_html=True)
