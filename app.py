import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Nexus Analytics | Executive Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. STYLE CSS (Thème Vert & Pro) ---
st.markdown("""
<style>
    /* Police d'écriture professionnelle */
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', 'Helvetica Neue', 'Roboto', sans-serif;
    }
    
    /* Barre du haut personnalisée (Header) */
    .top-bar {
        background-color: #27AE60; /* Vert Pro */
        padding: 15px;
        border-radius: 10px;
        color: white;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
    }
    
    /* Couleur du Sidebar */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E0E0E0;
    }
    
    /* Titres du Sidebar en Vert */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #27AE60 !important;
    }

    /* Cartes KPIs avec bordure verte */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border-left: 5px solid #27AE60;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. GÉNÉRATION DE DONNÉES (Adaptée pour la Carte) ---
@st.cache_data
def load_data():
    np.random.seed(42)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    n_samples = 3000
    date_range = pd.date_range(start=start_date, end=end_date, freq="H")
    random_dates = np.random.choice(date_range, n_samples)
    
    products = np.random.choice(['Enterprise Suite X1', 'Cloud Storage Pro', 'CyberSecurity Plus', 'AI Consultant Hour'], n_samples)
    
    # IMPORTANT: J'utilise des vrais pays pour que la CARTE fonctionne
    countries = np.random.choice(['United States', 'France', 'Germany', 'Japan', 'Brazil', 'United Kingdom', 'India', 'Canada'], n_samples)
    
    status = np.random.choice(['Confirmed', 'Pending', 'Cancelled'], n_samples, p=[0.85, 0.1, 0.05])
    segments = np.random.choice(['Fortune 500', 'SMB', 'Government'], n_samples)
    
    revenue = np.random.randint(1500, 20000, n_samples)
    cost = revenue * np.random.uniform(0.3, 0.7, n_samples)
    
    df = pd.DataFrame({
        'Date': random_dates,
        'Product': products,
        'Country': countries, # Renommé pour la carte
        'Status': status,
        'Segment': segments,
        'Revenue': revenue,
        'Cost': cost
    })
    
    df['Profit'] = df['Revenue'] - df['Cost']
    df['Margin (%)'] = (df['Profit'] / df['Revenue']) * 100
    df['Date'] = pd.to_datetime(df['Date'])
    
    return df.sort_values('Date')

df = load_data()

# --- 4. EN-TÊTE PERSONNALISÉE (HEADER) ---
# Ceci crée la barre tout en haut avec le logo fictif et la description
col_logo, col_text = st.columns([1, 5])

with col_logo:
    # Logo Placeholder (Carré vert avec texte blanc)
    st.image("https://placehold.co/150x150/27AE60/FFFFFF?text=NEXUS+Logo", use_container_width=True)

with col_text:
    st.markdown("""
    <div style="background-color: #f0f2f6; padding: 20px; border-radius: 10px; border-left: 5px solid #27AE60;">
        <h2 style="color: #2C3E50; margin:0;">Nexus Analytics | Global Command Center</h2>
        <p style="margin:0; color: #555;">
            <b>Objectif :</b> Pilotage en temps réel de la performance commerciale, surveillance des marges par pays et analyse de la rentabilité produit.
        </p>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Petit espace

# --- 5. SIDEBAR (FILTRES VERTS) ---

st.sidebar.title("Configuration")

# Filtre Date
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input("Période d'Analyse", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# Filtres Catégories
country_filter = st.sidebar.multiselect("Pays / Zone", df['Country'].unique(), default=df['Country'].unique())
segment_filter = st.sidebar.multiselect("Segment Client", df['Segment'].unique(), default=df['Segment'].unique())

# Application des filtres
mask = (
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1]) &
    (df['Country'].isin(country_filter)) &
    (df['Segment'].isin(segment_filter)) &
    (df['Status'] == 'Confirmed')
)
df_filtered = df[mask]

if df_filtered.empty:
    st.error("Aucune donnée pour cette sélection.")
    st.stop()

# --- 6. KPIs ---
total_rev = df_filtered['Revenue'].sum()
total_profit = df_filtered['Profit'].sum()
avg_margin = df_filtered['Margin (%)'].mean()

c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total Revenue", f"${total_rev:,.0f}")
with c2: st.metric("Net Profit", f"${total_profit:,.0f}")
with c3: st.metric("Avg Margin", f"{avg_margin:.1f}%")
with c4: st.metric("Active Deals", f"{len(df_filtered):,}")

st.markdown("---")

# --- 7. ONGLETS D'ANALYSE ---
tab1, tab2, tab3 = st.tabs(["📈 Financial Trends", "🌍 Geographic Map", "📦 Product Scorecard"])

# TAB 1: TENDANCES
with tab1:
    st.subheader("Revenue vs Profit Evolution")
    df_filtered['Month'] = df_filtered['Date'].dt.to_period('M').dt.start_time
    monthly = df_filtered.groupby('Month')[['Revenue', 'Profit']].sum().reset_index()
    
    fig_dual = go.Figure()
    fig_dual.add_trace(go.Bar(x=monthly['Month'], y=monthly['Revenue'], name="Revenue", marker_color='#2C3E50'))
    fig_dual.add_trace(go.Scatter(x=monthly['Month'], y=monthly['Profit'], name="Profit", yaxis='y2', mode='lines+markers', line=dict(color='#27AE60', width=3)))
    
    fig_dual.update_layout(
        template="simple_white",
        yaxis=dict(title="Revenue ($)"),
        yaxis2=dict(title="Profit ($)", overlaying='y', side='right'),
        legend=dict(orientation="h", y=1.1),
        height=400
    )
    st.plotly_chart(fig_dual, use_container_width=True)

# TAB 2: CARTE GÉOGRAPHIQUE (RESTAURÉE)
with tab2:
    st.subheader("Global Sales Intensity")
    
    # Agrégation par Pays
    map_data = df_filtered.groupby('Country')[['Revenue']].sum().reset_index()
    
    col_map, col_data = st.columns([3, 1])
    
    with col_map:
        # Utilisation de Choropleth Map (Ce que vous aimiez)
        fig_map = px.choropleth(
            map_data,
            locations="Country",
            locationmode="country names", # Important pour que Plotly reconnaisse 'France', 'United States'...
            color="Revenue",
            color_continuous_scale="Greens", # Thème Vert
            template="simple_white",
            title="Revenue Density by Country"
        )
        fig_map.update_geos(showframe=False, projection_type='natural earth')
        fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)
        
    with col_data:
        st.markdown("**Top Countries**")
        st.dataframe(
            map_data.sort_values('Revenue', ascending=False),
            column_config={
                "Revenue": st.column_config.NumberColumn(format="$%d")
            },
            hide_index=True,
            use_container_width=True
        )

# TAB 3: PRODUCT SCORECARD (CORRIGÉ & SÉCURISÉ)
with tab3:
    st.subheader("Product Performance Matrix")
    
    # Calculs
    scorecard = df_filtered.groupby('Product').agg(
        Total_Revenue=('Revenue', 'sum'),
        Profit_Margin=('Margin (%)', 'mean'),
        Sales_Count=('Date', 'count')
    ).reset_index()

    # NOTE IMPORTANTE : Si cette partie plante, mettez à jour streamlit : pip install --upgrade streamlit
    # J'ai simplifié la configuration pour éviter les erreurs de type
    try:
        st.dataframe(
            scorecard.sort_values('Total_Revenue', ascending=False),
            column_config={
                "Product": "Product Name",
                "Total_Revenue": st.column_config.ProgressColumn(
                    "Total Revenue",
                    help="Contribution to sales",
                    format="$%f",
                    min_value=0,
                    max_value=int(scorecard['Total_Revenue'].max()) # Force en entier pour éviter bugs
                ),
                "Profit_Margin": st.column_config.NumberColumn(
                    "Margin",
                    format="%.1f%%"
                ),
                "Sales_Count": st.column_config.NumberColumn(
                    "Volume Sold",
                    format="%d deals"
                )
            },
            hide_index=True,
            use_container_width=True
        )
    except Exception as e:
        # Fallback en cas d'erreur de version (Ancien Streamlit)
        st.warning("Affichage simplifié (Mettez à jour Streamlit pour voir les barres de progression)")
        st.dataframe(scorecard)

# --- PIED DE PAGE ---
st.markdown("---")
st.caption("Nexus Analytics System v3.0 | Confidential Data")
