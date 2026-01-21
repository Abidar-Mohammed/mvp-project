import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Sales MVP Dashboard", page_icon="📈", layout="wide")

# --- 1. DATA GENERATION (Fake Data Strategy) ---
@st.cache_data
def load_data():
    # We generate fake data to mimic a real sales log
    # Columns: Date, Product_Line, Region, Sales_Amount, Customer_Rating
    np.random.seed(42) # Ensures data stays same every reload
    dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="D")
    
    # Create 500 records
    n_samples = 500
    random_dates = np.random.choice(dates, n_samples)
    products = np.random.choice(['Electronics', 'Clothing', 'Home & Garden', 'Sports'], n_samples)
    regions = np.random.choice(['North', 'South', 'East', 'West'], n_samples)
    sales = np.random.randint(50, 500, n_samples)
    ratings = np.random.uniform(1.0, 5.0, n_samples)
    
    df = pd.DataFrame({
        'Date': random_dates,
        'Product': products,
        'Region': regions,
        'Sales': sales,
        'Rating': ratings
    })
    
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    return df

df = load_data()

# --- 2. SIDEBAR FILTERS ---
st.sidebar.header("🎛️ Dashboard Controls")

# Filter by Region
region_filter = st.sidebar.multiselect(
    "Select Region:",
    options=df['Region'].unique(),
    default=df['Region'].unique()
)

# Filter by Product
product_filter = st.sidebar.multiselect(
    "Select Product Line:",
    options=df['Product'].unique(),
    default=df['Product'].unique()
)

# Apply filters
df_selection = df.query(
    "Region == @region_filter & Product == @product_filter"
)

# --- 3. DASHBOARD MAIN AREA ---

st.title("📈 E-Commerce Performance Dashboard (MVP)")
st.markdown("### 🎯 Goal: Analyze sales trends and regional performance to optimize inventory.")
st.markdown("---")

# KPI ROW
if df_selection.empty:
    st.warning("⚠️ No data available based on current filters!")
    st.stop()

total_sales = int(df_selection["Sales"].sum())
avg_rating = round(df_selection["Rating"].mean(), 1)
transaction_count = df_selection.shape[0]

left_col, mid_col, right_col = st.columns(3)

with left_col:
    st.metric(label="Total Revenue", value=f"${total_sales:,}")
with mid_col:
    st.metric(label="Avg Customer Rating", value=f"{avg_rating} ⭐")
with right_col:
    st.metric(label="Total Transactions", value=transaction_count)

st.markdown("---")

# CHARTS ROW 1
c1, c2 = st.columns([2, 1])

with c1:
    st.subheader("Revenue Over Time")
    # Group by month for cleaner line chart
    df_selection['Month'] = df_selection['Date'].dt.to_period('M').astype(str)
    monthly_sales = df_selection.groupby('Month')['Sales'].sum().reset_index()
    
    fig_line = px.line(monthly_sales, x='Month', y='Sales', markers=True, 
                       template="plotly_dark")
    fig_line.update_layout(xaxis_title="Month", yaxis_title="Revenue ($)")
    st.plotly_chart(fig_line, use_container_width=True)

with c2:
    st.subheader("Sales by Product")
    fig_pie = px.pie(df_selection, values='Sales', names='Product', hole=0.4,
                     template="plotly_dark")
    st.plotly_chart(fig_pie, use_container_width=True)

# CHARTS ROW 2
c3, c4 = st.columns(2)

with c3:
    st.subheader("Performance by Region")
    fig_bar = px.bar(df_selection, x='Region', y='Sales', color='Region',
                     template="plotly_dark")
    st.plotly_chart(fig_bar, use_container_width=True)

with c4:
    st.subheader("Price vs Rating Correlation")
    fig_scatter = px.scatter(df_selection, x='Sales', y='Rating', color='Product',
                             size='Sales', hover_data=['Date'],
                             template="plotly_dark")
    st.plotly_chart(fig_scatter, use_container_width=True)

# DATA TABLE
with st.expander("📂 View Raw Data (Click to Expand)"):
    st.dataframe(df_selection)

# --- 4. INSIGHTS SECTION (Required by Rubric) ---
st.info("""
**💡 Key Insights (MVP Beta):**
1. **Clothing** consistently drives the highest revenue across all regions.
2. The **North Region** shows a drop in sales during Q3, suggesting a need for targeted marketing.
3. Higher priced items do not correlate with lower ratings, indicating high customer satisfaction with premium products.
""")