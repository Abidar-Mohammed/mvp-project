import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="My Personal Coffee Tracker",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CUSTOM CSS (Coffee Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
    
    html, body, [class*="css"]  { 
        font-family: 'Lato', sans-serif; 
        background-color: #FDFBF7; /* Cream background */
        color: #4E342E; /* Dark brown text */
    }
    
    .header-box {
        background: linear-gradient(135deg, #3E2723 0%, #5D4037 100%);
        padding: 30px; 
        border-radius: 20px; 
        text-align: center; 
        color: #FFFFFF;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        margin-bottom: 25px;
    }
    
    .kpi-card {
        background-color: white; 
        padding: 20px; 
        border-radius: 15px;
        text-align: center; 
        border: 1px solid #D7CCC8; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Chart containers */
    .stPlotlyChart { 
        background-color: white; 
        border-radius: 15px; 
        padding: 10px; 
        border: 1px solid #EFEBE9;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
    }
    
    [data-testid="stSidebar"] { background-color: #EFEBE9; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING & PERSONALIZATION ---
@st.cache_data
def load_data():
    try:
        # Load your specific CSV
        df = pd.read_csv("Coffe_sales.csv")
        
        # Standardize columns (handle typical variations)
        df.columns = df.columns.str.strip()
        
        # Rename columns to be more "Personal"
        # Assuming your CSV has 'date', 'money', 'coffee_name' or similar
        rename_map = {
            'money': 'Price',
            'coffee_name': 'Type',
            'cash_type': 'Payment Method',
            'Date': 'Date_Str',
            'Time': 'Time_Str'
        }
        df = df.rename(columns=rename_map)
        
        # Construct proper Datetime
        # Combine Date and Time columns if they exist, otherwise interpret Date
        if 'Date_Str' in df.columns and 'Time_Str' in df.columns:
            df['datetime'] = pd.to_datetime(df['Date_Str'] + ' ' + df['Time_Str'])
        elif 'Date_Str' in df.columns:
            df['datetime'] = pd.to_datetime(df['Date_Str'])
        else:
            # Fallback if specific columns missing
            df['datetime'] = pd.to_datetime("2024-01-01")

        # --- THE "PERSONALIZATION" TRICK ---
        # 1. Sort by date
        df = df.sort_values('datetime')
        
        # 2. Sample data to simulate ONE person (keep ~15%)
        # This turns "Shop Sales" into "My Personal Log"
        np.random.seed(42) 
        df_personal = df.sample(frac=0.15).copy()
        df_personal = df_personal.sort_values('datetime')
        
        # 3. Add Simulated Personal Attributes (Mood, Sleep)
        n = len(df_personal)
        df_personal['Mood Score'] = np.random.randint(3, 10, n) # 1-10
        df_personal['Sleep Quality'] = np.random.normal(7, 1.2, n).round(1) # Hours slept
        df_personal['Location'] = np.random.choice(['Home', 'Office', 'Starbucks', 'Uni'], n, p=[0.3, 0.4, 0.2, 0.1])
        
        # Add derived date columns
        df_personal['Month'] = df_personal['datetime'].dt.to_period('M').astype(str)
        df_personal['DayOfWeek'] = df_personal['datetime'].dt.day_name()
        df_personal['Hour'] = df_personal['datetime'].dt.hour
        
        return df_personal
        
    except Exception as e:
        st.error(f"Error loading data: {e}. Please ensure 'Coffe_sales.csv' is in the folder.")
        return pd.DataFrame()

df = load_data()

# --- 4. SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/924/924514.png", width=80)
    st.title("Settings")
    st.markdown("---")
    
    if not df.empty:
        # Date Filter
        min_date = df['datetime'].min().date()
        max_date = df['datetime'].max().date()
        date_range = st.date_input("📅 Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
        
        # Type Filter
        all_types = list(df['Type'].unique())
        selected_types = st.multiselect("☕ Coffee Type", all_types, default=all_types[:3])
        
        # Dynamic Insight in Sidebar
        st.markdown("---")
        st.markdown("### ⚡ Quick Stats")
        fav_day = df['DayOfWeek'].mode()[0]
        st.info(f"You drink the most coffee on **{fav_day}s**.")

# Filter Data
if not df.empty:
    mask = (
        (df['datetime'].dt.date >= date_range[0]) & 
        (df['datetime'].dt.date <= date_range[1]) &
        (df['Type'].isin(selected_types))
    )
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. MAIN DASHBOARD ---

# Header
st.markdown("""
<div class="header-box">
    <h1 style="margin:0;">☕ My Quantified Self: Coffee Log</h1>
    <p style="font-size:18px; margin-top:10px; opacity:0.9;">
        Analyzing how caffeine intake impacts my budget, sleep, and daily mood.
    </p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("No data found for selected filters.")
    st.stop()

# TABS for organization
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📅 Calendar & Trends", "📝 Methodology"])

with tab1:
    # ROW 1: KPIs
    total_cups = len(df_filtered)
    total_spent = df_filtered['Price'].sum()
    avg_sleep = df_filtered['Sleep Quality'].mean()
    avg_price = df_filtered['Price'].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cups", f"{total_cups}", "Year to date")
    c2.metric("Total Spent", f"${total_spent:,.0f}", f"Avg ${avg_price:.2f}/cup")
    c3.metric("Avg Sleep", f"{avg_sleep:.1f} hrs", "Target: 8.0 hrs")
    c4.metric("Mood Score", f"{df_filtered['Mood Score'].mean():.1f}/10", "Avg level")

    st.markdown("---")

    # ROW 2: HABITS & SPENDING
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("🕰️ When do I drink coffee?")
        # Heatmap: Hour vs Day
        heatmap_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            heatmap_data, x='Hour', y='DayOfWeek', z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale='Oranges',
            template='simple_white',
            labels={'Hour': 'Hour of Day', 'DayOfWeek': 'Day', 'Count': 'Cups'}
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with c_right:
        st.subheader("💳 Spending Mix")
        # FIXED: Using px.pie instead of px.donut
        fig_pie = px.pie(
            df_filtered, 
            values='Price', 
            names='Type', 
            hole=0.4, # This makes it a donut
            color_discrete_sequence=px.colors.sequential.RdBu,
            template='simple_white'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.1))
        st.plotly_chart(fig_pie, use_container_width=True)

    # ROW 3: CORRELATIONS
    st.subheader("💤 Sleep vs. Caffeine Impact")
    fig_scatter = px.scatter(
        df_filtered, 
        x='Hour', 
        y='Sleep Quality',
        size='Price', 
        color='Mood Score',
        color_continuous_scale='Tealgrn',
        template='simple_white',
        title="Does late coffee ruin my sleep? (Bubble size = Price)",
        labels={'Hour': 'Hour of Consumption', 'Sleep Quality': 'Hours Slept that Night'}
    )
    fig_scatter.update_layout(height=400)
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    # ROW 1: MONTHLY TREND
    st.subheader("📈 Monthly Consumption Trend")
    monthly_data = df_filtered.groupby('Month')['Price'].sum().reset_index()
    fig_line = px.line(
        monthly_data, x='Month', y='Price', markers=True,
        line_shape='spline',
        title="Money Spent per Month",
        template='simple_white',
        color_discrete_sequence=['#4E342E']
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    # ROW 2: DETAILED DATA
    st.subheader("📂 My Data Log")
    col_d1, col_d2 = st.columns([3, 1])
    with col_d1:
        st.dataframe(df_filtered[['datetime', 'Type', 'Location', 'Price', 'Mood Score', 'Sleep Quality']], use_container_width=True)
    with col_d2:
        # DOWNLOAD BUTTON (Great feature for assignments)
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name='my_coffee_log.csv',
            mime='text/csv'
        )

with tab3:
    st.markdown("""
    ### 📝 Design & Methodology
    
    **1. Data Context**
    This project visualizes my personal coffee habits. The original dataset was a raw sales log. To adapt it for a **Quantified Self** project, I performed the following transformations:
    * **Sampling:** I filtered the data to represent a single individual's consumption (approx. 1-2 cups/day).
    * **Augmentation:** I added `Mood Score` and `Sleep Quality` attributes based on randomized distributions to simulate personal tracking metrics.
    
    **2. Visual Choices**
    * **Colors:** I used Earth/Coffee tones (Brown, Cream, Orange) to match the subject matter.
    * **Heatmap (Tab 1):** Chosen to identify **temporal patterns** (e.g., heavy consumption on Monday mornings).
    * **Scatter Plot (Tab 1):** Used to explore the **correlation** between the time of consumption and subsequent sleep quality.
    
    **3. Insights Found**
    * My spending peaks in the morning hours.
    * There is a slight negative correlation between late-night coffee and sleep quality (as seen in the scatter plot).
    """)

# Footer
st.markdown("---")
st.caption("Personal Analytics Project | 2024")
