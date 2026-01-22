import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Board de Direction | Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. INJECTION CSS (DESIGN PREMIUM) ---
# C'est ici qu'on change le style, la police et qu'on retire l'aspect "basic"
st.markdown("""
<style>
    /* Import de la police Google Fonts (Roboto) pour un look pro */
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Roboto', sans-serif;
        color: #333333;
    }
    
    /* Couleur de fond générale */
    .stApp {
        background-color: #F5F7F9; /* Gris très pâle "Bureautique" */
    }

    /* Style du Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E0E0E0;
    }

    /* Style des Titres */
    h1, h2, h3 {
        color: #0F2027; /* Bleu nuit très sombre */
        font-weight: 700;
    }

    /* Création de cartes pour les KPIs (Key Performance Indicators) */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E0E0E0;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04); /* Ombre douce */
        text-align: center;
    }

    /* Taille des chiffres */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        color: #203A43; /* Bleu pétrole */
    }

    /* Etiquettes des métriques */
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #7f8c8d;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. GÉNÉRATION DE DONNÉES (SIMULATION) ---
@st.cache_data
def load_data():
    # Simulation d'une base de données d'entreprise
    np.random.seed(42)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    n_samples = 3000
    date_range = pd.date_range(start=start_date, end=end_date, freq="H")
    random_dates = np.random.choice(date_range, n_samples)
    
    # Données réalistes
    products = np.random.choice(['Solution SaaS Premium', 'Maintenance Annuelle', 'Audit & Conseil', 'Formation Équipe'], n_samples)
    regions = np.random.choice(['France', 'Allemagne', 'Royaume-Uni', 'Espagne', 'Italie', 'Benelux'], n_samples)
    status = np.random.choice(['Validé', 'En attente', 'Annulé'], n_samples, p=[0.85, 0.1, 0.05])
    segments = np.random.choice(['Grand Compte', 'PME', 'Start-up'], n_samples)
    
    revenue = np.random.randint(2000, 25000, n_samples)
    cost = revenue * np.random.uniform(0.4, 0.7, n_samples) # Marge variable
    
    df = pd.DataFrame({
        'Date': random_dates,
        'Product': products,
        'Region': regions,
        'Status': status,
        'Segment': segments,
        'Revenue': revenue,
        'Cost': cost
    })
    
    # Calculs additionnels
    df['Profit'] = df['Revenue'] - df['Cost']
    df['Marge_Pct'] = (df['Profit'] / df['Revenue']) * 100
    df['Date'] = pd.to_datetime(df['Date'])
    
    return df.sort_values('Date')

df = load_data()

# --- 4. BARRE LATÉRALE (Filtres & Logo) ---

# Logo (Placeholder - Remplace l'URL par ton logo plus tard)
st.sidebar.image("https://placehold.co/200x80/203A43/FFF?text=CORP+DATA", use_container_width=True)
st.sidebar.markdown("---")

st.sidebar.subheader("Paramètres de Filtrage")

# Filtres
region_filter = st.sidebar.multiselect("Zone Géographique", df['Region'].unique(), default=df['Region'].unique())
segment_filter = st.sidebar.multiselect("Segment Client", df['Segment'].unique(), default=df['Segment'].unique())

# Filtre Date
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input("Période d'Analyse", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# Application des filtres
mask = (
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1]) &
    (df['Region'].isin(region_filter)) &
    (df['Segment'].isin(segment_filter)) &
    (df['Status'] == 'Validé') # On ne regarde que les ventes validées par défaut
)
df_filtered = df[mask]

# --- 5. CORPS PRINCIPAL DU DASHBOARD ---

# En-tête Contextuelle
st.title("Rapport de Performance Commerciale")
st.markdown("""
**Contexte & Objectifs :** Ce tableau de bord permet au comité de direction de piloter la rentabilité par zone géographique et par ligne de produit.  
L'objectif est d'identifier les leviers de croissance pour le prochain trimestre et de surveiller l'évolution des marges opérationnelles.
""")
st.markdown("---")

if df_filtered.empty:
    st.error("Aucune donnée disponible pour les filtres sélectionnés.")
    st.stop()

# SECTION KPIs (CHIFFRES CLÉS)
total_ca = df_filtered['Revenue'].sum()
total_marge = df_filtered['Profit'].sum()
marge_moyenne = df_filtered['Marge_Pct'].mean()
panier_moyen = df_filtered['Revenue'].mean()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Chiffre d'Affaires Total", value=f"{total_ca:,.0f} €")
with col2:
    st.metric(label="Marge Nette", value=f"{total_marge:,.0f} €")
with col3:
    st.metric(label="Taux de Marge Moyen", value=f"{marge_moyenne:.1f} %")
with col4:
    st.metric(label="Panier Moyen", value=f"{panier_moyen:,.0f} €")

st.markdown("### Analyse Détaillée")

# ONGLETS D'ANALYSE
tab1, tab2, tab3 = st.tabs(["📈 Tendance & Prévision", "🌍 Répartition Géographique", "📦 Performance Produits"])

# ONGLET 1 : TENDANCES
with tab1:
    st.subheader("Évolution Temporelle du CA vs Marge")
    
    # Agrégation par mois
    df_filtered['Mois'] = df_filtered['Date'].dt.to_period('M').dt.start_time
    monthly_data = df_filtered.groupby('Mois')[['Revenue', 'Profit']].sum().reset_index()
    
    # Graphique Double Axe (Propre et Corporate)
    fig_trend = go.Figure()
    
    # Barres pour le CA
    fig_trend.add_trace(go.Bar(
        x=monthly_data['Mois'], y=monthly_data['Revenue'],
        name="Chiffre d'Affaires",
        marker_color='#203A43' # Bleu sombre
    ))
    
    # Ligne pour la Marge
    fig_trend.add_trace(go.Scatter(
        x=monthly_data['Mois'], y=monthly_data['Profit'],
        name="Marge Nette",
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#2C5364', width=3) # Bleu pétrole plus clair
    ))
    
    fig_trend.update_layout(
        template="simple_white",
        yaxis=dict(title="CA (€)", showgrid=True, gridcolor='#F0F0F0'),
        yaxis2=dict(title="Marge (€)", overlaying='y', side='right', showgrid=False),
        legend=dict(orientation="h", y=1.1),
        margin=dict(l=0, r=0, t=0, b=0),
        height=400
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# ONGLET 2 : CARTE
with tab2:
    col_map1, col_map2 = st.columns([2, 1])
    
    # Agrégation par pays
    country_data = df_filtered.groupby('Region')[['Revenue']].sum().reset_index()
    
    with col_map1:
        st.markdown("**Cartographie des Ventes (Europe)**")
        fig_map = px.choropleth(
            country_data,
            locations='Region',
            locationmode='country names', # Fonctionne mieux avec les noms anglais standard, ici on simule
            color='Revenue',
            scope='europe',
            color_continuous_scale='Blues',
            template='simple_white'
        )
        fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
    
    with col_map2:
        st.markdown("**Top Régions**")
        st.dataframe(
            country_data.sort_values('Revenue', ascending=False).style.format({"Revenue": "{:,.0f} €"}),
            use_container_width=True,
            hide_index=True
        )

# ONGLET 3 : PRODUITS (MATRICE)
with tab3:
    st.subheader("Matrice Rentabilité par Produit")
    st.markdown("Ce graphique permet de distinguer les produits 'Vaches à lait' (Gros volumes, forte marge) des produits à risque.")
    
    prod_data = df_filtered.groupby('Product').agg({
        'Revenue': 'sum',
        'Marge_Pct': 'mean',
        'Date': 'count' # Nombre de transactions
    }).reset_index()
    
    fig_bubble = px.scatter(
        prod_data,
        x="Revenue",
        y="Marge_Pct",
        size="Date", # Taille de la bulle = Volume de ventes
        color="Product",
        hover_name="Product",
        text="Product",
        template="simple_white",
        color_discrete_sequence=px.colors.qualitative.G10
    )
    fig_bubble.update_traces(textposition='top center')
    fig_bubble.update_layout(
        xaxis_title="Chiffre d'Affaires Total (€)",
        yaxis_title="Marge Moyenne (%)",
        showlegend=False,
        height=450
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

# --- 6. EXPORT DES DONNÉES ---
st.markdown("---")
col_d1, col_d2 = st.columns([3, 1])
with col_d1:
    st.caption("Document généré automatiquement par le système central. Données confidentielles.")
with col_d2:
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Exporter le Rapport (CSV)",
        data=csv,
        file_name='rapport_direction_Q1.csv',
        mime='text/csv'
    )
