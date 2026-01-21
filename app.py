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

# --- CUSTOM CSS FOR PROFESSIONAL UI ---
st.markdown("""
<style>
    /* Force white background and professional font styles */
    .stApp {
        background-color: #FFFFFF;
    }
    [data-testid="stSidebar"] {
        background-color: #F8F9FA;
        border-right: 1px solid #E9ECEF;
    }
    [data-testid="stMetricValue"] {
        font-size: 26px;
        font-family: 'Segoe UI', sans-serif;
        color: #2C3E50;
    }
    h1, h2, h3 {
        color: #2C3E50;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Style the metric cards */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #E9ECEF;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# --- 1. ADVANCED DATA GENERATION ---
@st.cache_data
def load_advanced_data():
    np.random.seed(42)
    # Generate dates for the last 365 days
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    # 2500 Samples for density
    n_samples = 2500
    date_range = pd.date_range(start=start_date, end=end_date, freq="H")
    random_dates = np.random.choice(date_range, n_samples)
    
    products = np.random.choice(['SaaS License', 'Consulting', 'Maintenance', 'Hardware Bundle'], n_samples)
    # Using real country names for the Map
    regions = np.random.choice(['United States', 'Germany', 'Japan', 'Brazil', 'United Kingdom', 'India'], n_samples)
    status = np.random.choice(['Completed', 'Pending', 'Refunded'], n_samples, p=[0.85, 0.1, 0.05])
    customer_type = np.random.choice(['Enterprise', 'SMB', 'Government'], n_samples)
    
    revenue = np.random.randint(500, 12000, n_samples)
    cost = revenue * np.random.uniform(0.3, 0.65, n_samples)
    
    df = pd.DataFrame({
        'Date': random_dates,
        'Product': products,
        'Country': regions, # Changed to Country for Map
        'Status': status,
        'Segment': customer_type,
        'Revenue': revenue,
        'Cost': cost
    })
    
    df['Profit'] = df['Revenue'] - df['Cost']
    df['Margin %'] = (df['Profit'] / df['Revenue']) * 100
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    
    return df.sort_values('Date')

df = load_advanced_data()

# --- 2. SIDEBAR CONFIGURATION ---
st.sidebar.title("Analytics Configuration")

# Section 1: Filters
st.sidebar.subheader("Filter Parameters")
country_filter = st.sidebar.multiselect("Country", df['Country'].unique(), default=df['Country'].unique())
segment_filter = st.sidebar.multiselect("Segment", df['Segment'].unique(), default=df['Segment'].unique())

# Section 2: Scenario Planner (New Feature)
st.sidebar.markdown("---")
st.sidebar.subheader("Scenario Simulator")
st.sidebar.info("Adjust projections to see impact on potential revenue.")
growth_rate = st.sidebar.slider("Projected Growth Rate (%)", min_value=-20, max_value=50, value=5, step=1)
margin_impact = st.sidebar.slider("Cost Efficiency Improvement (%)", min_value=0, max_value=10, value=0, step=1)

# Apply Filters
mask = (
    (df['Country'].isin(country_filter)) &
    (df['Segment'].isin(segment_filter))
)
df_filtered = df[mask]

# --- 3. DASHBOARD MAIN UI ---

st.title("Enterprise Analytics Suite")
st.markdown(f"**Data Status:** {len(df_filtered)} records analyzed | **Last Refresh:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# KPI ROW (Updated with Projections)
total_rev = df_filtered['Revenue'].sum()
projected_rev = total_rev * (1 + growth_rate/100)
total_profit = df_filtered['Profit'].sum()
# Logic: Improve margin by reducing cost
projected_profit = total_profit * (1 + (growth_rate/100)) + (total_rev * (margin_impact/100))

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Current Revenue", f"${total_rev:,.0f}")
with col2:
    st.metric("Projected Revenue", f"${projected_rev:,.0f}", f"{growth_rate}% Scenario")
with col3:
    st.metric("Current Profit", f"${total_profit:,.0f}")
with col4:
    st.metric("Projected Profit", f"${projected_profit:,.0f}", f"Efficiency +{margin_impact}%")

st.markdown("---")

# --- TABS FOR DETAILED ANALYSIS ---
tab1, tab2, tab3 = st.tabs(["Financial Performance", "Geospatial Intelligence", "Statistical Distribution"])

# TAB 1: FINANCIALS (Dual Axis + Forecasting)
with tab1:
    st.subheader("Revenue vs Profit Trajectory")
    
    # Aggregating data
    df_filtered['Period'] = df_filtered['Date'].dt.to_period('M').dt.start_time
    monthly = df_filtered.groupby('Period')[['Revenue', 'Profit']].sum().reset_index()
    
    fig_dual = go.Figure()
    
    # Revenue Bar
    fig_dual.add_trace(go.Bar(
        x=monthly['Period'], y=monthly['Revenue'], name='Actual Revenue',
        marker_color='#2C3E50'
    ))
    
    # Profit Line
    fig_dual.add_trace(go.Scatter(
        x=monthly['Period'], y=monthly['Profit'], name='Actual Profit',
        mode='lines+markers', line=dict(color='#18BC9C', width=3), yaxis='y2'
    ))
    
    # Projection Line (Dashed)
    if growth_rate != 0:
        fig_dual.add_trace(go.Scatter(
            x=monthly['Period'], y=monthly['Revenue'] * (1 + growth_rate/100),
            name=f'Projected Revenue ({growth_rate}%)',
            line=dict(color='#E74C3C', dash='dot'), opacity=0.7
        ))

    fig_dual.update_layout(
        template="simple_white",
        yaxis=dict(title="Revenue ($)", showgrid=True, gridcolor='#F0F2F6'),
        yaxis2=dict(title="Profit ($)", overlaying='y', side='right', showgrid=False),
        hovermode="x unified",
        legend=dict(orientation="h", y=1.1)
    )
    st.plotly_chart(fig_dual, use_container_width=True)

# TAB 2: GEOSPATIAL (Map)
with tab2:
    st.subheader("Global Sales Footprint")
    
    # Aggregate by country
    country_data = df_filtered.groupby('Country')[['Revenue', 'Profit']].sum().reset_index()
    
    c1, c2 = st.columns([2, 1])
    
    with c1:
        # Chloropleth Map
        fig_map = px.choropleth(
            country_data,
            locations='Country',
            locationmode='country names',
            color='Revenue',
            hover_name='Country',
            color_continuous_scale='Blues',
            template='simple_white',
            title='Revenue Density by Country'
        )
        fig_map.update_geos(showframe=False, showcoastlines=True, projection_type='equirectangular')
        fig_map.update_layout(margin={"r":0,"t":30,"l":0,"b":0})
        st.plotly_chart(fig_map, use_container_width=True)

    with c2:
        # Data Table next to Map
        st.markdown("#### Regional Metrics")
        st.dataframe(
            country_data.sort_values('Revenue', ascending=False).style.format({"Revenue": "${:,.0f}", "Profit": "${:,.0f}"}),
            use_container_width=True,
            hide_index=True
        )

# TAB 3: STATISTICAL DISTRIBUTION (Box Plot)
with tab3:
    st.subheader("Transaction Distribution & Outlier Detection")
    st.markdown("Use this view to analyze the spread of deal sizes and identify anomalies in specific product lines.")
    
    fig_box = px.box(
        df_filtered,
        x="Product",
        y="Revenue",
        color="Segment",
        points="outliers", # Only show outlier dots
        template="simple_white",
        color_discrete_sequence=px.colors.qualitative.G10
    )
    fig_box.update_layout(yaxis_title="Transaction Value ($)", xaxis_title="Product Line")
    st.plotly_chart(fig_box, use_container_width=True)

# --- EXPORT SECTION ---
st.markdown("---")
st.subheader("Data Export")
col_d1, col_d2 = st.columns([1, 4])
with col_d1:
    # CSV Download Button
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Report (CSV)",
        data=csv,
        file_name='executive_sales_report.csv',
        mime='text/csv',
    )
with col_d2:
    st.caption("Export contains all filtered records including raw timestamps, transaction IDs, and calculated margin metrics.")
