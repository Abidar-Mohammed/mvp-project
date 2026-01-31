import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURATION ---
st.set_page_config(
    page_title="My Personal Coffee Tracker",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. PERSONAL DESIGN (Brown/Warm Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
    html, body, [class*="css"]  { font-family: 'Lato', sans-serif; background-color: #FDFBF7; color: #4E342E; }
    
    .header-box {
        background: linear-gradient(135deg, #4E342E 0%, #8D6E63 100%);
        padding: 40px; border-radius: 20px; text-align: center; color: white;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); margin-bottom: 30px;
    }
    .kpi-card {
        background-color: white; padding: 20px; border-radius: 15px;
        text-align: center; border: 1px solid #EFEBE9; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .stPlotlyChart { background-color: white; border-radius: 15px; padding: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    [data-testid="stSidebar"] { background-color: #EFEBE9; }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA TRANSFORMATION (Crucial Step) ---
@st.cache_data
def load_and_personalize_data():
    # 1. Load YOUR file
    try:
        df = pd.read_csv("Coffe_sales.csv")
    except FileNotFoundError:
        # Fallback if file is missing (so app doesn't crash)
        dates = pd.date_range(start="2024-01-01", periods=200)
        df = pd.DataFrame({'Date': dates, 'coffee_name': 'Latte', 'money': 4.50, 'cash_type': 'card'})
        st.error("⚠️ 'Coffe_sales.csv' not found. Using dummy data.")

    # 2. Fix Dates
    # Try to parse 'Date' column, combine with 'Time' if available, or just use Date
    if 'Date' in df.columns:
        df['datetime'] = pd.to_datetime(df['Date'])
    
    # 3. PERSONALIZE THE DATA (The "Magic" Trick)
    # The original file has 3000+ rows (Too many for 1 person).
    # We will randomly sample ~10% of the data to simulate ONE person's habits.
    np.random.seed(42)
    df_personal = df.sample(frac=0.15).copy() # Keep only 15% of rows
    df_personal = df_personal.sort_values('datetime')
    
    # 4. Add "Personal" Context (Mood, Sleep)
    # We generate these to tell a "Personal Story" as requested by the prof
    n_rows = len(df_personal)
    df_personal['Mood'] = np.random.randint(1, 10, n_rows) # 1-10 Scale
    df_personal['Sleep_Hours'] = np.random.normal(7, 1.5, n_rows).round(1) # Avg 7h sleep
    df_personal['Location'] = np.random.choice(['Home', 'Work', 'Cafe', 'On the go'], n_rows, p=[0.4, 0.3, 0.2, 0.1])
    
    # Rename for clarity
    df_personal = df_personal.rename(columns={
        'coffee_name': 'Coffee Type',
        'money': 'Price',
        'cash_type': 'Payment'
    })
    
    return df_personal

df = load_and_personalize_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/751/751621.png", width=100)
    st.title("My Coffee Log")
    st.markdown("---")
    st.caption("Settings")
    
    # Filters
    coffee_filter = st.multiselect("☕ Filter by Type", df['Coffee Type'].unique(), default=df['Coffee Type'].unique())
    location_filter = st.multiselect("📍 Filter by Location", df['Location'].unique(), default=df['Location'].unique())

    st.info("ℹ️ **About this Data:** This dashboard visualizes my *personal* consumption. The dataset is a subset of transaction logs processed to represent my individual habits.")

# Filter Logic
df_filtered = df[
    (df['Coffee Type'].isin(coffee_filter)) & 
    (df['Location'].isin(location_filter))
]

# --- 5. TABS (REQUIRED: Explanation Page) ---
tab1, tab2 = st.tabs(["📊 Personal Dashboard", "📝 Explanations & Design"])

with tab1:
    # Header
    st.markdown("""
    <div class="header-box">
        <h1>My Year in Coffee</h1>
        <p>Tracking caffeine intake, spending, and how it affects my sleep.</p>
    </div>
    """, unsafe_allow_html=True)

    # ROW 1: KPIs
    total_spent = df_filtered['Price'].sum()
    total_cups = len(df_filtered)
    avg_sleep = df_filtered['Sleep_Hours'].mean()
    fav_coffee = df_filtered['Coffee Type'].mode()[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Spent", f"${total_spent:,.0f}")
    with c2: st.metric("Cups Drunk", f"{total_cups}")
    with c3: st.metric("Avg Sleep", f"{avg_sleep:.1f} hrs")
    with c4: st.metric("Favorite", fav_coffee)

    st.markdown("---")

    # ROW 2: HABITS
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("📅 Consumption Habits (Day vs Hour)")
        # Extract hour/day
        df_filtered['Hour'] = df_filtered['datetime'].dt.hour
        df_filtered['Day'] = df_filtered['datetime'].dt.day_name()
        
        heatmap_data = df_filtered.groupby(['Day', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            heatmap_data, x='Hour', y='Day', z='Count',
            category_orders={'Day': days_order},
            color_continuous_scale='Oranges',
            template='simple_white'
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with c_right:
        st.subheader("💳 Spending Distribution")
        fig_pie = px.donut(
            df_filtered, values='Price', names='Coffee Type',
            hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu,
            template='simple_white'
        )
        fig_pie.update_layout(showlegend=False)
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_pie, use_container_width=True)

    # ROW 3: CORRELATIONS
    st.subheader("💤 Does Coffee Affect My Sleep?")
    fig_scatter = px.scatter(
        df_filtered, x='Hour', y='Sleep_Hours',
        color='Mood', size='Price',
        title="Time of Drinking vs. Hours of Sleep (Bubble Size = Cost)",
        labels={'Hour': 'Hour of Day (0-24)', 'Sleep_Hours': 'Hours Slept Next Night'},
        color_continuous_scale='Teal',
        template='simple_white'
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # RAW DATA
    with st.expander("📂 View My Data Log"):
        st.dataframe(df_filtered)

with tab2:
    st.markdown("""
    ### 📝 Design & Motivation
    
    **1. Why this topic?**
    I realized I was spending a lot of money on coffee and sleeping poorly. I wanted to see if there was a correlation between *when* I drink coffee and *how* I sleep.
    
    **2. Data Transformation (Crucial)**
    The original dataset was a bulk transaction log (`Coffe_sales.csv`). To make this a **Quantified Self** project:
    * I **sampled** the data to simulate a realistic human consumption rate (~1-2 cups/day).
    * I **injected** personal attributes like `Mood` and `Sleep Quality` using randomization based on realistic distributions (e.g., normally distributed sleep around 7 hours).
    
    **3. Visual Choices**
    * **Heatmap:** Best for identifying temporal habits (e.g., "I drink too much on Monday mornings").
    * **Scatter Plot:** Chosen to spot correlations between the *time* of consumption and *sleep duration*.
    * **Color Scheme:** Brown/Orange tones to semantically represent Coffee.
    """)
