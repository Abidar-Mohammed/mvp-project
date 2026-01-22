import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Nexus Analytics | Executive Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. ADVANCED CSS STYLING (The "Look & Feel") ---
st.markdown("""
<style>
    /* 1. Force Professional Fonts */
    html, body, [class*="css"]  {
        font-family: 'Segoe UI', 'Helvetica Neue', 'Roboto', sans-serif;
        color: #333333;
    }
    
    /* 2. Sidebar Styling (Green Theme requested) */
    [data-testid="stSidebar"] {
        background-color: #F8F9FA; /* Light Grey Background */
        border-right: 1px solid #E0E0E0;
    }
    
    /* Sidebar Headers in Green */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #27AE60 !important; /* Emerald Green */
        font-weight: 700;
        text-transform: uppercase;
        font-size: 14px;
        letter-spacing: 1px;
    }

    /* 3. Main Title Styling */
    h1 {
        color: #2C3E50; /* Dark Blue-Grey */
        font-weight: 800;
    }
    
    h2, h3 {
        color: #2C3E50;
    }

    /* 4. KPI Cards Styling */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border-left: 5px solid #27AE60; /* Green Accent Bar */
        padding: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-radius: 5px;
    }

    [data-testid="stMetricValue"] {
        font-size: 26px;
        color: #2C3E50;
        font-weight: 700;
    }
    
    [data-testid="stMetricLabel"] {
        font-size: 14px;
        color: #7f8c8d;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA GENERATION (ENGLISH & DETAILED) ---
@st.cache_data
def load_data():
    np.random.seed(42)
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    n_samples = 3000
    date_range = pd.date_range(start=start_date, end=end_date, freq="H")
    random_dates = np.random.choice(date_range, n_samples)
    
    # English Data
    products = np.random.choice(['Enterprise Suite X1', 'Cloud Storage Pro', 'CyberSecurity Plus', 'AI Consultant Hour'], n_samples)
    regions = np.random.choice(['North America', 'EMEA (Europe)', 'APAC (Asia)', 'LATAM (South Am.)'], n_samples)
    status = np.random.choice(['Confirmed', 'Pending', 'Cancelled'], n_samples, p=[0.85, 0.1, 0.05])
    segments = np.random.choice(['Fortune 500', 'SMB', 'Government'], n_samples)
    
    revenue = np.random.randint(1500, 20000, n_samples)
    # Cost logic to create variable margins
    cost_factor = np.random.uniform(0.3, 0.7, n_samples)
    cost = revenue * cost_factor
    
    df = pd.DataFrame({
        'Date': random_dates,
        'Product': products,
        'Region': regions,
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

# --- 4. SIDEBAR CONFIGURATION (GREEN THEME) ---

# Dynamic Logo (Blue & Green)
st.sidebar.image("https://placehold.co/250x80/27AE60/FFFFFF?text=NEXUS+ANALYTICS", use_container_width=True)

st.sidebar.title("Filter Parameters")

# Date Filter
min_date = df['Date'].min().date()
max_date = df['Date'].max().date()
date_range = st.sidebar.date_input("Analysis Period", value=(min_date, max_date), min_value=min_date, max_value=max_date)

# Category Filters
region_filter = st.sidebar.multiselect("Geographic Region", df['Region'].unique(), default=df['Region'].unique())
segment_filter = st.sidebar.multiselect("Client Segment", df['Segment'].unique(), default=df['Segment'].unique())

# Advanced Filter (New)
st.sidebar.markdown("---")
st.sidebar.title("Threshold Settings")
min_rev = st.sidebar.slider("Min. Transaction Value ($)", 0, 5000, 0)

# Apply Filters
mask = (
    (df['Date'].dt.date >= date_range[0]) &
    (df['Date'].dt.date <= date_range[1]) &
    (df['Region'].isin(region_filter)) &
    (df['Segment'].isin(segment_filter)) &
    (df['Revenue'] >= min_rev) &
    (df['Status'] == 'Confirmed')
)
df_filtered = df[mask]

# --- 5. MAIN DASHBOARD ---

st.title("Executive Sales Overview")
st.markdown("""
**Dashboard Objective:** Monitor Year-to-Date sales performance across global territories. 
Use the sidebar (Green controls) to filter by segment and identify high-value opportunities.
""")
st.markdown("---")

if df_filtered.empty:
    st.error("No data available based on current filters. Please adjust settings.")
    st.stop()

# --- KPI SECTION ---
total_rev = df_filtered['Revenue'].sum()
total_profit = df_filtered['Profit'].sum()
avg_margin = df_filtered['Margin (%)'].mean()
count_trans = len(df_filtered)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Total Revenue", f"${total_rev:,.0f}")
with c2:
    st.metric("Net Profit", f"${total_profit:,.0f}")
with c3:
    st.metric("Avg Margin", f"{avg_margin:.1f}%")
with c4:
    st.metric("Transactions", f"{count_trans:,}")

st.markdown("### Detailed Analysis Modules")

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Financial Trends", "🌍 Regional Heatmap", "📦 Product Deep Dive"])

# TAB 1: FINANCIAL TRENDS (Clean & Pro)
with tab1:
    st.subheader("Revenue vs. Profitability Timeline")
    
    # Group by Month
    df_filtered['Month'] = df_filtered['Date'].dt.to_period('M').dt.start_time
    monthly = df_filtered.groupby('Month')[['Revenue', 'Profit']].sum().reset_index()
    
    fig_dual = go.Figure()
    
    # Bar Chart (Revenue)
    fig_dual.add_trace(go.Bar(
        x=monthly['Month'], y=monthly['Revenue'],
        name="Revenue ($)",
        marker_color='#2C3E50' # Dark Blue
    ))
    
    # Line Chart (Profit)
    fig_dual.add_trace(go.Scatter(
        x=monthly['Month'], y=monthly['Profit'],
        name="Net Profit ($)",
        yaxis='y2',
        mode='lines+markers',
        line=dict(color='#27AE60', width=3) # Green line
    ))
    
    fig_dual.update_layout(
        template="simple_white",
        yaxis=dict(title="Revenue", showgrid=True, gridcolor='#F1F1F1'),
        yaxis2=dict(title="Profit", overlaying='y', side='right', showgrid=False),
        legend=dict(orientation="h", y=1.1),
        height=450
    )
    st.plotly_chart(fig_dual, use_container_width=True)

# TAB 2: MAP
with tab2:
    st.subheader("Sales Intensity by Region")
    
    # Aggregate
    region_data = df_filtered.groupby('Region')[['Revenue']].sum().reset_index()
    
    # NOTE: Since we are using fake regions like "North America", we map them to ISO codes for the chart
    # In a real app, you would use country names.
    
    c_map, c_table = st.columns([2, 1])
    
    with c_map:
        # Simple Bar for regions (More accurate than map for broad regions)
        fig_bar = px.bar(
            region_data, x='Region', y='Revenue',
            color='Revenue',
            color_continuous_scale=['#D5F5E3', '#27AE60', '#145A32'], # Light Green to Dark Green
            template="simple_white",
            text_auto='.2s'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c_table:
        st.markdown("**Regional Breakdown**")
        st.dataframe(
            region_data.sort_values('Revenue', ascending=False).style.format({"Revenue": "${:,.0f}"}),
            use_container_width=True,
            hide_index=True
        )

# TAB 3: PRODUCT DEEP DIVE (Detailed as requested)
with tab3:
    st.subheader("Product Portfolio Performance")
    
    # 1. Pareto Analysis (80/20 Rule)
    st.markdown("##### Pareto Analysis (Cumulative Revenue)")
    prod_pareto = df_filtered.groupby('Product')['Revenue'].sum().sort_values(ascending=False).reset_index()
    prod_pareto['Cumulative %'] = 100 * (prod_pareto['Revenue'].cumsum() / prod_pareto['Revenue'].sum())
    
    fig_pareto = go.Figure()
    fig_pareto.add_trace(go.Bar(
        x=prod_pareto['Product'], y=prod_pareto['Revenue'], name='Revenue',
        marker_color='#2C3E50'
    ))
    fig_pareto.add_trace(go.Scatter(
        x=prod_pareto['Product'], y=prod_pareto['Cumulative %'], name='Cumulative %',
        yaxis='y2', mode='lines+markers', line=dict(color='#E74C3C', width=2)
    ))
    fig_pareto.update_layout(
        template="simple_white",
        yaxis2=dict(overlaying='y', side='right', range=[0, 110]),
        legend=dict(orientation="h", y=1.1),
        height=400
    )
    st.plotly_chart(fig_pareto, use_container_width=True)
    
    st.markdown("---")
    
    # 2. Detailed Scorecard Table
    st.markdown("##### Product Scorecard")
    
    # Complex aggregation
    scorecard = df_filtered.groupby('Product').agg(
        Total_Revenue=('Revenue', 'sum'),
        Avg_Margin=('Margin (%)', 'mean'),
        Transaction_Count=('Date', 'count'),
        Avg_Deal_Size=('Revenue', 'mean')
    ).reset_index()
    
    # Using Streamlit Column Config for visual bars in table
    st.dataframe(
        scorecard.sort_values('Total_Revenue', ascending=False),
        column_config={
            "Total_Revenue": st.column_config.ProgressColumn(
                "Total Revenue",
                help="Total contribution to Top Line",
                format="$%f",
                min_value=0,
                max_value=scorecard['Total_Revenue'].max(),
            ),
            "Avg_Margin": st.column_config.NumberColumn(
                "Avg Margin",
                format="%.1f%%"
            ),
            "Avg_Deal_Size": st.column_config.NumberColumn(
                "Avg Deal Value",
                format="$%.0f"
            )
        },
        use_container_width=True,
        hide_index=True
    )

# --- 6. EXPORT ---
st.markdown("---")
col_bottom_1, col_bottom_2 = st.columns([4, 1])

with col_bottom_1:
    st.caption("Confidential: For Internal Use Only. Nexus Analytics System v2.1")

with col_bottom_2:
    csv = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name='nexus_sales_report.csv',
        mime='text/csv'
    )
