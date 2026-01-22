import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from PIL import Image

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Compagnie Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. AESTHETIC CSS (Bubbles & Colors) ---
st.markdown("""
<style>
    /* Professional Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
        background-color: #F4F6F9;
        color: #333;
    }

    /* --- BUBBLE EFFECT (Card Design) --- */
    .stPlotlyChart, div[data-testid="metric-container"], div.stDataFrame {
        background-color: #FFFFFF;
        border-radius: 15px;
        padding: 15px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #EFF2F7;
        transition: all 0.3s ease;
    }

    /* Hover Effect */
    .stPlotlyChart:hover, div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.1);
        border-color: #3498DB;
    }

    /* --- SIDEBAR STYLING --- */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E1E4E8;
    }
    
    /* Sidebar Headers */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h3 {
        color: #2C3E50;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 13px;
        letter-spacing: 1px;
    }

    /* --- METRIC COLORS --- */
    [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
        color: #2C3E50;
    }
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #7F8C8D;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA GENERATION (MATCHING YOUR SCHEMA) ---
@st.cache_data
def load_data():
    # Simulating the EXACT columns I asked you to create
    np.random.seed(42)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    n_samples = 2000
    date_range = pd.date_range(start=start_date, end=end_date, freq="D")
    random_dates = np.random.choice(date_range, n_samples)
    
    # 1. Product & Category
    categories = ['Electronics', 'Furniture', 'Office Supplies', 'Technology']
    products_list = ['SmartPhone X', 'Ergo Chair', 'Desk Lamp', 'Laptop Pro', 'Monitor 4K', 'USB Hub']
    
    cat_data = np.random.choice(categories, n_samples)
    prod_data = np.random.choice(products_list, n_samples)
    
    # 2. Region (Countries for the Map)
    regions = np.random.choice(['USA', 'France', 'Germany', 'United Kingdom', 'Canada', 'Spain', 'Italy'], n_samples)
    
    # 3. Customer Type
    cust_type = np.random.choice(['Corporate', 'Consumer', 'Home Office'], n_samples)
    
    # 4. Financials
    sales = np.random.randint(100, 5000, n_samples)
    profit = sales * np.random.uniform(0.1, 0.4, n_samples) # Profit is 10% to 40% of sales
    
    df = pd.DataFrame({
        'Date': random_dates,
        'Category': cat_data,
        'Product': prod_data,
        'Region': regions,
        'Customer_Type': cust_type,
        'Sales': sales,
        'Profit': profit
    })
    
    df['Date'] = pd.to_datetime(df['Date'])
    return df.sort_values('Date')

df = load_data()

# --- 4. SIDEBAR (LOGO & FILTERS) ---
with st.sidebar:
    # LOGO HANDLING (Smaller size as requested)
    try:
        # Looking for LOGO.jpeg
        image = Image.open('LOGO.jpeg')
        # width=100 makes it small and elegant
        st.image(image, width=120) 
    except FileNotFoundError:
        st.warning("⚠️ Add 'LOGO.jpeg'")
    
    st.write("## COMPAGNIE ANALYTICS")
    st.markdown("---")
    
    st.write("### ⚙️ Filters")
    
    # Date Filter
    min_date = df['Date'].min()
    max_date = df['Date'].max()
    date_range = st.date_input("Select Period", value=(min_date, max_date))
    
    # Category Filter
    selected_cat = st.multiselect("Category", df['Category'].unique(), default=df['Category'].unique())
    
    # Region Filter
    selected_region = st.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())

# FILTERING LOGIC
mask = (
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1]) &
    (df['Category'].isin(selected_cat)) &
    (df['Region'].isin(selected_region))
)
df_filtered = df[mask]

# --- 5. MAIN DASHBOARD CONTENT ---

st.title("Compagnie | Sales Performance")
st.markdown(f"**Data Overview:** {len(df_filtered)} transactions analyzed.")
st.markdown("---")

if df_filtered.empty:
    st.error("No data available based on current filters.")
    st.stop()

# --- ROW 1: KPIs (Clean & Factual) ---
total_sales = df_filtered['Sales'].sum()
total_profit = df_filtered['Profit'].sum()
profit_margin = (total_profit / total_sales) * 100
avg_ticket = df_filtered['Sales'].mean()

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Revenue", f"${total_sales:,.0f}", delta="vs Year Avg")
with c2:
    st.metric("Total Profit", f"${total_profit:,.0f}", delta=f"{profit_margin:.1f}% Margin")
with c3:
    st.metric("Avg Order Value", f"${avg_ticket:.0f}")
with c4:
    st.metric("Transactions", f"{len(df_filtered):,}")

st.write("") # Spacer

# --- ROW 2: MAP & TREEMAP (Visuals) ---
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("🌍 Geographic Distribution")
    # Aggregating for Map
    map_data = df_filtered.groupby('Region')['Sales'].sum().reset_index()
    
    fig_map = px.choropleth(
        map_data,
        locations="Region",
        locationmode="country names",
        color="Sales",
        # Beautiful Teal/Blue Scale
        color_continuous_scale="Teal", 
        template="simple_white"
    )
    fig_map.update_geos(showframe=False, projection_type='natural earth')
    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

with col_right:
    st.subheader("📦 Category Mix")
    # Treemap replaces the unrealistic Funnel
    # It shows which Categories are biggest
    fig_tree = px.treemap(
        df_filtered,
        path=['Category', 'Product'],
        values='Sales',
        color='Sales',
        color_continuous_scale='Blues', # Clean Blue gradient
        template="simple_white"
    )
    fig_tree.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig_tree, use_container_width=True)

# --- ROW 3: TRENDS & SCATTER (Analysis) ---
col3_1, col3_2 = st.columns(2)

with col3_1:
    st.subheader("📈 Sales Trend Over Time")
    # Group by Month
    df_filtered['Month'] = df_filtered['Date'].dt.to_period('M').dt.start_time
    trend_data = df_filtered.groupby('Month')['Sales'].sum().reset_index()
    
    fig_line = px.area(
        trend_data, 
        x='Month', 
        y='Sales',
        line_shape='spline', # Makes the line curved/smooth
        color_discrete_sequence=['#3498DB'] # Professional Blue
    )
    fig_line.update_layout(template="simple_white", yaxis_title="Revenue ($)")
    st.plotly_chart(fig_line, use_container_width=True)

with col3_2:
    st.subheader("💎 Profitability Analysis")
    # Scatter plot: Sales vs Profit (Real analysis of data)
    fig_scat = px.scatter(
        df_filtered,
        x="Sales",
        y="Profit",
        color="Category",
        size="Sales", # Bubble size = Sales amount
        opacity=0.6,
        template="simple_white",
        color_discrete_sequence=px.colors.qualitative.Bold # Nice distinct colors
    )
    fig_scat.update_layout(yaxis_title="Profit ($)", xaxis_title="Sales Amount ($)")
    st.plotly_chart(fig_scat, use_container_width=True)

# --- ROW 4: RAW DATA ---
with st.expander("📂 View Raw Transaction Data"):
    st.dataframe(
        df_filtered.sort_values('Date', ascending=False),
        use_container_width=True,
        hide_index=True
    )

# Footer
st.markdown("---")
st.markdown("<center style='color:#888;'>Compagnie Analytics System | Powered by Python</center>", unsafe_allow_html=True)
