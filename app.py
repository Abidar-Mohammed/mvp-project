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
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS "ULTRA WIDE" & DESIGN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
        background-color: #F4F7F6;
        color: #333;
    }

    /* PLEINE LARGEUR */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 100%;
    }

    /* HEADER AVEC IMAGE */
    .main-header-card {
        background: linear-gradient(rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.85)),
                    url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2072&auto=format&fit=crop'); 
        background-size: cover;
        background-position: center;
        border-radius: 20px;
        padding: 40px 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        text-align: center;
        margin-bottom: 25px;
        color: #FFFFFF;
        border: 1px solid #2C3E50;
    }
    .main-header-title {
        font-size: 40px;
        font-weight: 800;
        color: #FFFFFF;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 3px;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }
    .main-header-subtitle {
        font-size: 16px;
        color: #BDC3C7;
        margin-top: 10px;
        font-weight: 300;
    }

    /* KPIs */
    .kpi-card {
        padding: 20px 10px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 15px;
        transition: transform 0.2s;
    }
    .kpi-card:hover { transform: scale(1.02); }
    
    .card-blue { background: linear-gradient(135deg, #EBF5FB 0%, #D6EAF8 100%); }
    .card-green { background: linear-gradient(135deg, #E9F7EF 0%, #D4EFDF 100%); }
    .card-orange { background: linear-gradient(135deg, #FEF9E7 0%, #FDEBD0 100%); }
    .card-purple { background: linear-gradient(135deg, #F5EEF8 0%, #EBDEF0 100%); }

    .kpi-value { font-size: 28px; font-weight: 700; color: #2C3E50; margin: 0; }
    .kpi-label { font-size: 12px; font-weight: 600; color: #5D6D7E; text-transform: uppercase; letter-spacing: 1px; }

    /* TITRES */
    .custom-title {
        font-size: 18px;
        font-weight: 600;
        color: #34495E;
        padding: 10px 15px;
        background-color: #FFFFFF;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        border-left: 5px solid #ccc;
    }
    .title-blue { border-left-color: #3498DB; }
    .title-orange { border-left-color: #E67E22; }
    .title-green { border-left-color: #27AE60; }
    .title-purple { border-left-color: #8E44AD; }
    .title-red { border-left-color: #E74C3C; }

    /* GRAPHIQUES */
    .stPlotlyChart {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    [data-testid="stSidebar"] { background-color: #FFFFFF; }

</style>
""", unsafe_allow_html=True)

# --- 3. GÉNÉRATION DE DONNÉES ---
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

# --- 4. SIDEBAR ---
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

st.markdown("""
<div class="main-header-card">
    <h1 class="main-header-title">EXECUTIVE SALES HUB</h1>
    <p class="main-header-subtitle">Real-time analytics of global revenue, profitability trends, and product mix.</p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.error("No data available based on current filters.")
    st.stop()

# --- ROW 1: KPIs ---
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

st.write("") 

# --- ROW 2: CARTE (GRANDE) & DONUT (PETIT) ---
col_L, col_R = st.columns([3, 1]) 

with col_L:
    st.markdown('<div class="custom-title title-blue">🌍 Geographic Sales Distribution</div>', unsafe_allow_html=True)
    map_data = df_filtered.groupby('Region')['Sales'].sum().reset_index()
    fig_map = px.choropleth(map_data, locations="Region", locationmode="country names", color="Sales", color_continuous_scale="Blues", template="simple_white")
    fig_map.update_geos(showframe=False, projection_type='natural earth', bgcolor='rgba(0,0,0,0)')
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='rgba(0,0,0,0)', height=500)
    st.plotly_chart(fig_map, use_container_width=True)

with col_R:
    st.markdown('<div class="custom-title title-orange">📦 Categories</div>', unsafe_allow_html=True)
    fig_donut = px.pie(
        df_filtered, 
        values='Sales', 
        names='Category', 
        hole=0.4, 
        color_discrete_sequence=px.colors.qualitative.Bold, 
        template="simple_white"
    )
    fig_donut.update_traces(textposition='inside', textinfo='percent+label')
    fig_donut.update_layout(
        showlegend=False,
        margin=dict(t=10, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        height=500, 
        uniformtext_minsize=10, 
        uniformtext_mode='hide'
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# --- ROW 3: PROFIT & TRENDS ---
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

# --- ROW 4: HEATMAP & SUNBURST ---
st.write("")
col4_1, col4_2 = st.columns(2)

with col4_1:
    # CHANGEMENT ICI : HEATMAP à la place du Scatter
    st.markdown('<div class="custom-title title-red">🔥 Profit Heatmap (Region vs Category)</div>', unsafe_allow_html=True)
    
    fig_heat = px.density_heatmap(
        df_filtered,
        x="Region",
        y="Category",
        z="Profit",
        histfunc="sum",
        color_continuous_scale="Reds", # Échelle Rouge pour montrer l'intensité (Chaleur)
        template="simple_white"
    )
    
    fig_heat.update_layout(
        xaxis_title="Region",
        yaxis_title="Category",
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_heat, use_container_width=True)

with col4_2:
    st.markdown('<div class="custom-title title-blue">🌞 Hierarchy View (Sunburst)</div>', unsafe_allow_html=True)
    fig_sun = px.sunburst(
        df_filtered,
        path=['Region', 'Category'],
        values='Sales',
        color='Sales',
        color_continuous_scale='Blues',
        template="simple_white"
    )
    fig_sun.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        height=400,
        margin=dict(t=20, b=20, l=20, r=20)
    )
    st.plotly_chart(fig_sun, use_container_width=True)


# --- FOOTER ---
st.write("")
st.markdown("---")

with st.expander("📂 View Raw Source Data (Click to expand)", expanded=False):
    st.dataframe(df_filtered.sort_values('Date', ascending=False), use_container_width=True, hide_index=True)

st.markdown("<center style='color:#AAA; font-size:12px; margin-top:20px;'>Executive Analytics System | 2024 Internal Data</center>", unsafe_allow_html=True)
