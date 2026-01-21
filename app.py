import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Enterprise Analytics Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS FOR PROFESSIONAL LOOK ---
# This forces white background and styled cards for metrics
st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 24px;
        color: #2C3E50;
    }
    [data-testid="stMetricDelta"] {
        font-size: 16px;
    }
    .stCard {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 5px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- 1. ADVANCED DATA GENERATION ---
@st.cache_data
def load_advanced_data():
    np.random.seed(42)
    # Generate dates for the last 365 days, including hours for detail
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    date_range = pd.date_range(start=start_date, end=end_date, freq="H")
    
    # Select 2000 random timestamps
    n_samples = 2000
    random_dates = np.random.choice(date_range, n_samples)
    
    products = np.random.choice(['SaaS License', 'Consulting', 'Maintenance', 'Hardware Bundle'], n_samples)
    regions = np.random.choice(['North America', 'EMEA', 'APAC', 'LATAM'], n_samples)
    status = np.random.choice(['Completed', 'Pending', 'Refunded'], n_samples, p=[0.85, 0.1, 0.05])
    customer_type = np.random.choice(['Enterprise', 'SMB', 'Government'], n_samples)
    
    revenue = np.random.randint(500, 10000, n_samples)
    cost = revenue * np.random.uniform(0.4, 0.7, n_samples)
    
    df = pd.DataFrame({
        'Date': random_dates,
        'Product': products,
        'Region': regions,
        'Status': status,
        'Segment': customer_type,
        'Revenue': revenue,
        'Cost': cost
    })
    
    df['Profit'] = df['Revenue'] - df['Cost']
    df['Margin %'] = (df['Profit'] / df['Revenue']) * 100
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    df['DayOfWeek'] = df['Date'].dt.day_name()
    df['Hour'] = df['Date'].dt.hour
    
    return df.sort_values('Date')

df = load_advanced_data()

# --- 2. SIDEBAR CONTROLS ---
st.sidebar.title("Configuration")
st.sidebar.markdown("---")

# Filters
region_filter = st.sidebar.multiselect("Region", df['Region'].unique(), default=df['Region'].unique())
segment_filter = st.sidebar.multiselect("Customer Segment", df['Segment'].unique(), default=df['Segment'].unique())
status_filter = st.sidebar.multiselect("Order Status", df['Status'].unique(), default=['Completed', 'Pending'])

# Date Filter
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input("Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# Apply Filters
mask = (
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1]) &
    (df['Region'].isin(region_filter)) &
    (df['Segment'].isin(segment_filter)) &
    (df['Status'].isin(status_filter))
)
df_filtered = df[mask]

# --- 3. DASHBOARD LOGIC ---

st.title("Enterprise Analytics Suite")
st.markdown("Detailed breakdown of financial performance and operational metrics.")

if df_filtered.empty:
    st.error("No data found matching these filters.")
    st.stop()

# --- KPI SECTION WITH DELTAS ---
# Logic: Compare selected period vs entire history average (simulated 'target')
total_rev = df_filtered['Revenue'].sum()
total_profit = df_filtered['Profit'].sum()
avg_margin = df_filtered['Margin %'].mean()

# Simulated previous period for "Delta" calculation
prev_rev = total_rev * 0.92 
prev_profit = total_profit * 0.88
prev_margin = avg_margin - 1.2

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.metric("Total Revenue", f"${total_rev:,.0f}", f"{((total_rev-prev_rev)/prev_rev)*100:.1f}% vs last period")
with c2:
    st.metric("Gross Profit", f"${total_profit:,.0f}", f"{((total_profit-prev_profit)/prev_profit)*100:.1f}% vs last period")
with c3:
    st.metric("Avg Margin", f"{avg_margin:.1f}%", f"{avg_margin-prev_margin:.1f}% pts")
with c4:
    st.metric("Transaction Count", f"{len(df_filtered)}", "Active")

st.markdown("---")

# --- TABBED INTERFACE ---
tab1, tab2, tab3 = st.tabs(["Overview", "Regional Intelligence", "Operational Detail"])

# TAB 1: OVERVIEW (Dual Axis Chart)
with tab1:
    st.subheader("Financial Trajectory")
    
    # Group by week for cleaner chart
    df_chart = df_filtered.copy()
    df_chart['Week'] = df_chart['Date'].dt.to_period('W').dt.start_time
    weekly = df_chart.groupby('Week')[['Revenue', 'Profit']].sum().reset_index()
    
    # Create Dual Axis Chart using Graph Objects
    fig_dual = go.Figure()
    
    # Bar for Revenue
    fig_dual.add_trace(go.Bar(
        x=weekly['Week'], y=weekly['Revenue'], 
        name='Revenue', marker_color='#2C3E50'
    ))
    
    # Line for Profit
    fig_dual.add_trace(go.Scatter(
        x=weekly['Week'], y=weekly['Profit'], 
        name='Profit', mode='lines+markers', 
        marker_color='#18BC9C', yaxis='y2'
    ))
    
    fig_dual.update_layout(
        template="simple_white",
        yaxis=dict(title="Revenue ($)", showgrid=True),
        yaxis2=dict(title="Profit ($)", overlaying='y', side='right', showgrid=False),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_dual, use_container_width=True)
    
    # Recent Transactions Table
    st.subheader("Recent Transactions")
    display_cols = ['Date', 'Product', 'Region', 'Segment', 'Revenue', 'Status']
    st.dataframe(
        df_filtered[display_cols].sort_values('Date', ascending=False).head(10),
        use_container_width=True,
        hide_index=True
    )

# TAB 2: REGIONAL (Sunburst & Breakdown)
with tab2:
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.subheader("Regional Hierarchy")
        st.markdown("*Click segments to drill down*")
        # Sunburst: Region -> Country (simulated via Segment) -> Product
        fig_sun = px.sunburst(
            df_filtered, 
            path=['Region', 'Segment', 'Product'], 
            values='Revenue',
            color='Revenue',
            color_continuous_scale='Blues',
        )
        fig_sun.update_layout(template="simple_white")
        st.plotly_chart(fig_sun, use_container_width=True)
        
    with col_b:
        st.subheader("Segment Analysis")
        # Horizontal Bar Chart
        fig_bar = px.bar(
            df_filtered.groupby('Segment')['Revenue'].sum().reset_index(),
            x='Revenue', y='Segment', orientation='h',
            text_auto='.2s',
            color_discrete_sequence=['#34495E'],
            template="simple_white"
        )
        st.plotly_chart(fig_bar, use_container_width=True)

# TAB 3: OPERATIONAL (Heatmap)
with tab3:
    st.subheader("Operational Heatmap: Sales Density")
    st.markdown("Analyze peak transaction times by day of week and hour.")
    
    # Pivot for Heatmap
    heatmap_data = df_filtered.groupby(['DayOfWeek', 'Hour'])['Revenue'].count().reset_index()
    
    # Order days correctly
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    fig_heat = px.density_heatmap(
        heatmap_data, 
        x='Hour', 
        y='DayOfWeek', 
        z='Revenue', 
        color_continuous_scale='Greys',
        category_orders={"DayOfWeek": days_order},
        template="simple_white"
    )
    fig_heat.update_layout(xaxis_dtick=2) # Show every 2nd hour
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.info("Insight: High density observed on Tuesday/Wednesday mornings suggests optimal time for maintenance downtime is weekends.")
