import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from PIL import Image

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="Executive Sales Hub",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS ESTHÉTIQUE (LE STYLE DES BULLES) ---
st.markdown("""
<style>
    /* Police moderne */
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
        background-color: #F8F9FA; /* Fond légèrement gris */
        color: #333;
    }

    /* --- NOUVEAU : STYLE DE L'EN-TÊTE PRINCIPAL (GRANDE BULLE) --- */
    .main-header-card {
        background-color: #FFFFFF;
        border-radius: 25px; /* Très arrondi */
        padding: 30px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.08); /* Ombre portée */
        border: 1px solid #EFEFEF;
        text-align: center; /* Titre centré */
        margin-bottom: 30px;
    }
    .main-header-title {
        font-size: 36px;
        font-weight: 800;
        color: #2C3E50;
        margin: 0;
        background: linear-gradient(90deg, #2C3E50, #3498DB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .main-header-subtitle {
        font-size: 16px;
        color: #7F8C8D;
        margin-top: 10px;
        font-weight: 400;
    }

    /* --- STYLES DES TITRES DE SECTION (Petites barres colorées) --- */
    .custom-title {
        font-size: 20px;
        font-weight: 600;
        color: #2C3E50;
        padding: 12px 20px;
        border-left: 6px solid #3498DB;
        background-color: #FFFFFF;
        border-radius: 15px; /* Arrondi aussi */
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
    }
    .title-blue { border-left-color: #3498DB; }
    .title-orange { border-left-color: #E67E22; }
    .title-green { border-left-color: #27AE60; }
    .title-purple { border-left-color: #8E44AD; }

    /* --- CARTES KPIs (Petites Bulles Colorées) --- */
    .kpi-card {
        padding: 25px 20px;
        border-radius: 20px; /* Arrondi */
        text-align: center;
        box-shadow: 0 6px 15px rgba(0,0,0,0.06);
        margin-bottom: 20px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
        background-color: #FFFFFF;
    }
    .kpi-card:hover { transform: translateY(-5px); box-shadow: 0 12px 25px rgba(0,0,0,0.1); }
    
    .card-blue { border-color: #D6EAF8; }
    .card-green { border-color: #D4EFDF; }
    .card-orange { border-color: #FDEBD0; }
    .card-purple { border-color: #E8DAEF; }

    .kpi-value { font-size: 32px; font-weight: 700; color: #2C3E50; margin: 5px 0; }
    .kpi-label { font-size: 14px; font-weight: 600; color: #95A5A6; text-transform: uppercase; letter-spacing: 1.2px; }

    /* --- GRAPHIQUES (Grosses Bulles) --- */
    .stPlotlyChart {
        background-color: #FFFFFF;
        border-radius: 25px; /* Arrondi */
        padding: 15px;
        box-shadow: 0 6px 15px rgba(0,0,0,0.06);
        border: 1px solid #EFEFEF;
    }

    /* --- SIDEBAR --- */
    [data-testid="stSidebar"] { background-color: #FFFFFF; border-right: none; box-shadow: 5px 0 15px rgba(0,0,0,0.03); }
    [data-testid="stSidebar"] h3 { color: #2C3E50; font-weight: 700; }

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
    
    df['Profit'] = df['Sales'] * np.random.uniform(0.1, 0.45, n_samples)
    df['Date'] = pd.to_datetime(df['Date'])
    
    return df.sort_values('Date')

df = load_data()

# --- 4. SIDEBAR (LOGO GRAND & FILTRES) ---
with st.sidebar:
    try:
        image = Image.open('LOGO.jpeg')
        st.image(image, use_container_width=True) 
    except FileNotFoundError:
        st.warning("⚠️ LOGO.jpeg missing.")
    
    st.markdown("---")
    st.write("### ⚙️ CONTROLS")
    
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    date_range = st.date_input("📅 Date Range", value=(min_date, max_date))
    
    selected_cat = st.multiselect("📦 Category", df['Category'].unique(), default=df['Category'].unique())
    selected_region = st.multiselect("🌍 Region", df['Region'].unique(), default=df['Region'].unique())

mask = (
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1]) &
    (df['Category'].isin(selected_cat)) &
    (df['Region'].isin(selected_region))
)
df_filtered = df[mask]

# --- 5. DASHBOARD PRINCIPAL ---

# --- NOUVEL EN-TÊTE (HEADER) EN FORME DE BULLE ---
# Au lieu de st.title, on utilise une div HTML stylisée
st.markdown("""
<div class="main-header-card">
    <h1 class="main-header-title">Executive Sales & Performance Hub</h1>
    <p class="main-header-subtitle">Real-time analytics of global revenue, profitability trends, and product mix.</p>
</div>
""", unsafe_allow_html=True)


if df_filtered.empty:
    st.error("No data available based on current filters.")
    st.stop()

# --- ROW 1: KPIs COLORÉS (Petites Bulles) ---
total_sales = df_filtered['Sales'].sum()
total_profit = df_filtered['Profit'].sum()
avg_ticket = df_filtered['Sales'].mean()
nb_trans = len(df_filtered)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""<div class="kpi-card card-blue"><p class="kpi-label">Total Revenue</p><p class="kpi-value">${total_sales:,.0f}</p></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="kpi-card card-green"><p class="kpi-label">Net Profit</p><p class="kpi-value">${total_profit:,.0f}</p></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="kpi-card card-orange"><p class="kpi-label">Avg Order Value</p><p class="kpi-value">${avg_ticket:.0f}</p></div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="kpi-card card-purple"><p class="kpi-label">Transactions</p><p class="kpi-value">{nb_trans:,}</p></div>""", unsafe_allow_html=True)

st.write("") # Espaceur

# --- ROW 2: CARTE & DONUT (Grosses Bulles) ---
col_L, col_R = st.columns([2, 1])

with col_L:
    st.markdown('<div class="custom-title title-blue">🌍 Geographic Sales Distribution</div>', unsafe_allow_html=True)
    map_data = df_filtered.groupby('Region')['Sales'].sum().reset_index()
    fig_map = px.choropleth(map_data, locations="Region", locationmode="country names", color="Sales", color_continuous_scale="Blues", template="simple_white")
    fig_map.update_geos(showframe=False, projection_type='natural earth', bgcolor='rgba(0,0,0,0)')
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_map, use_container_width=True)

with col_R:
    st.markdown('<div class="custom-title title-orange">📦 Sales by Category</div>', unsafe_allow_html=True)
    fig_donut = px.pie(df_filtered, values='Sales', names='Category', hole=0.65, color_discrete_sequence=px.colors.qualitative.Bold, template="simple_white")
    fig_donut.update_traces(textposition='inside', textinfo='percent')
    fig_donut.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.2), paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_donut, use_container_width=True)

# --- ROW 3: PROFIT & TRENDS (Grosses Bulles) ---
col3_1, col3_2 = st.columns(2)

with col3_1:
    st.markdown('<div class="custom-title title-green">💎 Top 10 Profitable Products</div>', unsafe_allow_html=True)
    top_products = df_filtered.groupby('Product')['Profit'].sum().sort_values(ascending=True).tail(10)
    fig_bar = px.bar(top_products, x=top_products.values, y=top_products.index, orientation='h', text_auto='.2s', color=top_products.values, color_continuous_scale='Greens', template="simple_white")
    fig_bar.update_layout(xaxis_title="Total Profit ($)", yaxis_title=None, coloraxis_showscale=False, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_bar, use_container_width=True)

with col3_2:
    st.markdown('<div class="custom-title title-purple">📈 Monthly Revenue Trend</div>', unsafe_allow_html=True)
    df_filtered['Month'] = df_filtered['Date'].dt.to_period('M').dt.start_time
    trend_data = df_filtered.groupby('Month')['Sales'].sum().reset_index()
    fig_line = px.area(trend_data, x='Month', y='Sales', line_shape='spline', color_discrete_sequence=['#8E44AD'], template="simple_white")
    fig_line.update_layout(yaxis_title="Revenue ($)", paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig_line, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("<center style='color:#AAA; font-size:12px; font-weight:500;'>Executive Analytics System | 2024 Internal Data</center>", unsafe_allow_html=True)
