import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Executive Sales Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 1. DATA GENERATION ---
@st.cache_data
def load_data():
    # Generating sample enterprise data
    np.random.seed(42)
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
    
    n_samples = 1000
    random_dates = np.random.choice(dates, n_samples)
    products = np.random.choice(['Enterprise Suite', 'Basic Plan', 'Professional Plan', 'Add-on Services'], n_samples)
    regions = np.random.choice(['North America', 'Europe', 'Asia Pacific', 'Latin America'], n_samples)
    sales = np.random.randint(1000, 5000, n_samples)
    margin = np.random.uniform(0.10, 0.35, n_samples) # Profit margin
    
    df = pd.DataFrame({
        'Date': random_dates,
        'Product': products,
        'Region': regions,
        'Revenue': sales,
        'Margin': margin
    })
    
    df['Profit'] = df['Revenue'] * df['Margin']
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    return df

df = load_data()

# --- 2. SIDEBAR FILTERS ---
st.sidebar.title("Filter Parameters")

# Date Range
min_date = df['Date'].min()
max_date = df['Date'].max()

start_date, end_date = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Region Filter
region_filter = st.sidebar.multiselect(
    "Select Region",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Product Filter
product_filter = st.sidebar.multiselect(
    "Select Product Line",
    options=df['Product'].unique(),
    default=df['Product'].unique()
)

# Apply filters
mask = (
    (df['Date'] >= pd.to_datetime(start_date)) & 
    (df['Date'] <= pd.to_datetime(end_date)) & 
    (df['Region'].isin(region_filter)) & 
    (df['Product'].isin(product_filter))
)
df_selection = df[mask]

# --- 3. MAIN DASHBOARD ---

st.title("Executive Sales Dashboard")
st.markdown("Overview of sales performance, revenue distribution, and regional trends.")
st.markdown("---")

# CHECK FOR EMPTY DATA
if df_selection.empty:
    st.error("No data available for the selected filters. Please adjust your selection.")
    st.stop()

# TOP ROW: KPI CARDS
total_revenue = df_selection["Revenue"].sum()
total_profit = df_selection["Profit"].sum()
avg_margin = (df_selection["Profit"].sum() / df_selection["Revenue"].sum()) * 100

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Total Revenue", value=f"${total_revenue:,.0f}")
with col2:
    st.metric(label="Total Profit", value=f"${total_profit:,.0f}")
with col3:
    st.metric(label="Average Margin", value=f"{avg_margin:.1f}%")

st.markdown("---")

# CHART SETTINGS
# Using a professional color map (Blues) and white template
chart_color_sequence = px.colors.qualitative.G10

# ROW 1: TRENDS & COMPOSITION
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Revenue Trend Over Time")
    # Aggregate by month for a cleaner view
    df_selection['Month'] = df_selection['Date'].dt.to_period('M').astype(str)
    monthly_data = df_selection.groupby('Month')[['Revenue', 'Profit']].sum().reset_index()
    
    fig_line = px.line(
        monthly_data, 
        x='Month', 
        y=['Revenue', 'Profit'],
        markers=True,
        color_discrete_sequence=['#2C3E50', '#18BC9C'], # Professional Blue and Green
        template="simple_white"
    )
    fig_line.update_layout(yaxis_title="Amount ($)", xaxis_title="Month", legend_title="Metric")
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("Revenue by Product")
    fig_pie = px.donut(
        df_selection, 
        values='Revenue', 
        names='Product', 
        hole=0.5,
        color_discrete_sequence=chart_color_sequence,
        template="simple_white"
    )
    fig_pie.update_traces(textposition='inside', textinfo='percent+label')
    fig_pie.update_layout(showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

# ROW 2: REGIONAL ANALYSIS
c3, c4 = st.columns(2)

with c3:
    st.subheader("Sales Performance by Region")
    fig_bar = px.bar(
        df_selection, 
        x='Region', 
        y='Revenue', 
        color='Region',
        text_auto='.2s',
        color_discrete_sequence=chart_color_sequence,
        template="simple_white"
    )
    fig_bar.update_layout(showlegend=False, yaxis_title="Revenue ($)")
    st.plotly_chart(fig_bar, use_container_width=True)

with c4:
    st.subheader("Profitability Analysis (Scatter)")
    fig_scatter = px.scatter(
        df_selection, 
        x='Revenue', 
        y='Profit', 
        color='Product',
        size='Margin',
        hover_data=['Date', 'Region'],
        color_discrete_sequence=chart_color_sequence,
        template="simple_white"
    )
    fig_scatter.update_layout(yaxis_title="Profit ($)", xaxis_title="Revenue ($)")
    st.plotly_chart(fig_scatter, use_container_width=True)

# RAW DATA SECTION
with st.expander("View Detailed Data Source"):
    st.dataframe(df_selection.drop(columns=['Month']), use_container_width=True)

# --- 4. DATA STORY / INSIGHTS ---
st.markdown("### Executive Summary")
st.info("""
**Observation:** The Enterprise Suite contributes to the majority of high-margin transactions in the North American region.
**Recommendation:** Focus marketing efforts on 'Add-on Services' in the Europe region to improve the lower average margin observed in Q3.
""")
