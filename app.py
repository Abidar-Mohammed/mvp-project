import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from PIL import Image

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Compagnie Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS ESTHÉTIQUE & COLORÉ ---
st.markdown("""
<style>
    /* Police moderne */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
        background-color: #Fdfdfd;
        color: #333;
    }

    /* --- STYLES DES TITRES (ENCADRÉS/DÉCORÉS) --- */
    .custom-title {
        font-size: 20px;
        font-weight: 600;
        color: #2C3E50;
        padding: 10px 15px;
        border-left: 5px solid #3498DB; /* Barre bleue à gauche */
        background-color: #F4F6F7;
        border-radius: 0 10px 10px 0;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Variante pour d'autres sections */
    .title-green { border-left-color: #27AE60; }
    .title-orange { border-left-color: #E67E22; }
    .title-purple { border-left-color: #8E44AD; }

    /* --- CARTES KPIs (COLORÉES) --- */
    .kpi-card {
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        transition: transform 0.3s;
    }
    .kpi-card:hover { transform: scale(1.03); }
    
    /* Couleurs spécifiques par KPI */
    .card-blue { background: linear-gradient(135deg, #EBF5FB 0%, #D6EAF8 100%); border: 2px solid #3498DB; }
    .card-green { background: linear-gradient(135deg, #E9F7EF 0%, #D4EFDF 100%); border: 2px solid #27AE60; }
    .card-orange { background: linear-gradient(135deg, #FEF5E7 0%, #FDEBD0 100%); border: 2px solid #E67E22; }
    .card-purple { background: linear-gradient(135deg, #F4ECF7 0%, #E8DAEF 100%); border: 2px solid #8E44AD; }

    .kpi-value { font-size: 28px; font-weight: 700; color: #2C3E50; margin: 0; }
    .kpi-label { font-size: 14px; font-weight: 500; color: #555; text-transform: uppercase; letter-spacing: 1px; }

    /* --- GRAPHIQUES (BULLES) --- */
    .stPlotlyChart {
        background-color: #FFFFFF;
        border-radius: 20px;
        padding: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        border: 1px solid #EEEEEE;
    }

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #DDD;
    }
    /* Titres Sidebar stylisés */
    [data-testid="stSidebar"] h3 {
        color: #2C3E50;
        background-color: #E8F6F3;
        padding: 8px;
        border-radius: 5px;
        text-align: center;
        border: 1px solid #D1F2EB;
    }

</style>
""", unsafe_allow_html=True)

# --- 3. GÉNÉRATION DE DONNÉES (SCHEMA STRICT) ---
@st.cache_data
def load_data():
    np.random.seed(42)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    n_samples = 2500
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    random_dates = np.random.choice(date_range, n_samples)
    
    categories = ['Electronics', 'Furniture', 'Office Supplies', 'Technology']
    products_list = ['SmartPhone X', 'Ergo Chair', 'Desk Lamp', 'Laptop Pro', 'Monitor 4K', 'USB Hub', 'Headphones', 'Webcam HD']
    regions = ['USA', 'France', 'Germany', 'United Kingdom', 'Canada', 'Spain', 'Italy']
    cust_type = ['Corporate', 'Consumer', 'Home Office']
    
    df = pd.DataFrame({
        'Date': random_dates,
        'Category': np.random.choice(categories, n_samples),
        'Product': np.random.choice(products_list, n_samples),
        'Region': np.random.choice(regions, n_samples),
        'Customer_Type': np.random.choice(cust_type, n_samples),
        'Sales': np.random.randint(100, 5000, n_samples),
    })
    
    # Création du Profit (Marge variable selon catégorie)
    df['Profit'] = df['Sales'] * np.random.uniform(0.1, 0.45, n_samples)
    df['Date'] = pd.to_datetime(df['Date'])
    
    return df.sort_values('Date')

df = load_data()

# --- 4. SIDEBAR (LOGO GRAND & FILTRES) ---
with st.sidebar:
    # LOGO EN GRAND
    try:
        image = Image.open('LOGO.jpeg')
        # use_container_width=True prend toute la largeur dispo (donc grand)
        st.image(image, use_container_width=True) 
    except FileNotFoundError:
        st.warning("⚠️ Image 'LOGO.jpeg' introuvable.")
    
    st.markdown("---")
    st.write("### ⚙️ FILTER SETTINGS")
    
    # Filtres
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    date_range = st.date_input("📅 Date Range", value=(min_date, max_date))
    
    selected_cat = st.multiselect("📦 Category", df['Category'].unique(), default=df['Category'].unique())
    selected_region = st.multiselect("🌍 Region", df['Region'].unique(), default=df['Region'].unique())

# Filtrage
mask = (
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1]) &
    (df['Category'].isin(selected_cat)) &
    (df['Region'].isin(selected_region))
)
df_filtered = df[mask]

# --- 5. DASHBOARD PRINCIPAL ---

st.title("Compagnie Dashboard")
st.markdown("---")

if df_filtered.empty:
    st.error("No data available.")
    st.stop()

# --- ROW 1: KPIs COLORÉS (Cartes HTML Personnalisées) ---
total_sales = df_filtered['Sales'].sum()
total_profit = df_filtered['Profit'].sum()
avg_ticket = df_filtered['Sales'].mean()
nb_trans = len(df_filtered)

c1, c2, c3, c4 = st.columns(4)

# Utilisation de HTML pour créer les bordures colorées demandées
with c1:
    st.markdown(f"""
    <div class="kpi-card card-blue">
        <p class="kpi-label">Total Revenue</p>
        <p class="kpi-value">${total_sales:,.0f}</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="kpi-card card-green">
        <p class="kpi-label">Net Profit</p>
        <p class="kpi-value">${total_profit:,.0f}</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="kpi-card card-orange">
        <p class="kpi-label">Avg Order Value</p>
        <p class="kpi-value">${avg_ticket:.0f}</p>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="kpi-card card-purple">
        <p class="kpi-label">Transactions</p>
        <p class="kpi-value">{nb_trans:,}</p>
    </div>
    """, unsafe_allow_html=True)

st.write("") # Espaceur

# --- ROW 2: CARTE & DONUT CHART (Nouveau Mixed Category) ---
col_L, col_R = st.columns([2, 1])

with col_L:
    # Titre décoré
    st.markdown('<div class="custom-title title-blue">🌍 Geographic Sales Distribution</div>', unsafe_allow_html=True)
    
    map_data = df_filtered.groupby('Region')['Sales'].sum().reset_index()
    fig_map = px.choropleth(
        map_data,
        locations="Region",
        locationmode="country names",
        color="Sales",
        color_continuous_scale="Blues",
        template="simple_white"
    )
    fig_map.update_geos(showframe=False, projection_type='natural earth')
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

with col_R:
    # Remplacement du Treemap par un Donut Chart (plus esthétique)
    st.markdown('<div class="custom-title title-orange">📦 Sales by Category</div>', unsafe_allow_html=True)
    
    fig_donut = px.pie(
        df_filtered,
        values='Sales',
        names='Category',
        hole=0.6, # Effet Donut
        color_discrete_sequence=px.colors.qualitative.Bold, # Couleurs vives
        template="simple_white"
    )
    fig_donut.update_traces(textposition='inside', textinfo='percent')
    fig_donut.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.1))
    st.plotly_chart(fig_donut, use_container_width=True)

# --- ROW 3: PROFIT ANALYSIS (Nouveau) & TRENDS ---
col3_1, col3_2 = st.columns(2)

with col3_1:
    st.markdown('<div class="custom-title title-green">💎 Top 10 Profitable Products</div>', unsafe_allow_html=True)
    
    # Nouveau Graphique: Bar Chart Horizontal des Tops Produits
    top_products = df_filtered.groupby('Product')['Profit'].sum().sort_values(ascending=True).tail(10)
    
    fig_bar = px.bar(
        top_products,
        x=top_products.values,
        y=top_products.index,
        orientation='h',
        text_auto='.2s',
        color=top_products.values, # Dégradé de couleur selon la valeur
        color_continuous_scale='Greens',
        template="simple_white"
    )
    fig_bar.update_layout(
        xaxis_title="Total Profit ($)", 
        yaxis_title=None,
        coloraxis_showscale=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col3_2:
    st.markdown('<div class="custom-title title-purple">📈 Monthly Revenue Trend</div>', unsafe_allow_html=True)
    
    df_filtered['Month'] = df_filtered['Date'].dt.to_period('M').dt.start_time
    trend_data = df_filtered.groupby('Month')['Sales'].sum().reset_index()
    
    fig_line = px.area(
        trend_data, 
        x='Month', 
        y='Sales',
        line_shape='spline',
        color_discrete_sequence=['#8E44AD'] # Violet Pro
    )
    fig_line.update_layout(template="simple_white", yaxis_title="Revenue ($)")
    st.plotly_chart(fig_line, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("<center style='color:#AAA; font-size:12px;'>Compagnie Analytics 2024 | Internal Data</center>", unsafe_allow_html=True)
