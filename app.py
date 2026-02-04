import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# --- 1. PAGE CONFIGURATION ---
st.set_page_config(
    page_title="The Quantified Coffee | Ultimate",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. ULTIMATE CSS (Dark Luxury Theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600&family=Playfair+Display:wght@700&display=swap');

    /* BACKGROUND */
    .stApp {
        background-image: linear-gradient(rgba(0, 0, 0, 0.9), rgba(15, 10, 5, 0.95)), 
                          url("https://images.unsplash.com/photo-1497935586351-b67a49e012bf?q=80&w=2671&auto=format&fit=crop");
        background-attachment: fixed;
        background-size: cover;
    }

    /* GLASSMORPHISM CONTAINER */
    .main .block-container {
        background: rgba(20, 20, 20, 0.85);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 3rem 4rem;
        max-width: 1200px !important;
        margin: 0 auto;
        box-shadow: 0 0 50px rgba(0,0,0,0.8);
    }

    /* TYPOGRAPHY */
    h1, h2, h3, h4 {
        font-family: 'Playfair Display', serif;
        color: #D4AF37 !important; /* Metallic Gold */
        text-transform: uppercase;
        letter-spacing: 1.5px;
    }
    
    p, label, span, div, li {
        font-family: 'Montserrat', sans-serif;
        color: #B0BEC5;
    }

    /* TITLES */
    .main-title {
        text-align: center;
        margin-bottom: 20px;
        border-bottom: 1px solid rgba(212, 175, 55, 0.3);
        padding-bottom: 40px;
    }
    .main-title h1 {
        font-size: 4rem;
        background: -webkit-linear-gradient(#FDD835, #D4AF37);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .main-title p {
        font-size: 1.1rem;
        letter-spacing: 4px;
        text-transform: uppercase;
        color: #757575 !important;
        margin-top: 10px;
    }

    /* SECTIONS */
    .section-header {
        border-left: 4px solid #D4AF37;
        padding-left: 20px;
        margin-top: 80px;
        margin-bottom: 30px;
        font-size: 2rem;
        color: #F5F5F5;
        font-family: 'Playfair Display', serif;
        background: linear-gradient(90deg, rgba(212, 175, 55, 0.1), transparent);
        padding-top: 10px;
        padding-bottom: 10px;
    }
    
    .section-separator {
        border-bottom: 1px solid rgba(212, 175, 55, 0.3);
        margin-top: 60px;
        margin-bottom: 30px;
        padding-bottom: 10px;
        font-size: 1.5rem;
        color: #F9F9F9;
        font-family: 'Playfair Display', serif;
    }

    /* KPI CARDS */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 0px;
        padding: 20px;
        text-align: center;
        transition: transform 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-5px);
        border-color: #D4AF37;
    }
    div[data-testid="metric-container"] label {
        color: #90A4AE !important;
        font-size: 0.85rem;
        letter-spacing: 1px;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #FFF8E1 !important;
        font-family: 'Playfair Display', serif;
        font-size: 2.2rem;
    }

    /* CHARTS */
    .stPlotlyChart {
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. DATA LOADING & PROCESSING ---
@st.cache_data
def load_data():
    file_name = "my_coffee_life.csv"
    
    # Robust file finding
    path = None
    possible_paths = [file_name, os.path.join(os.path.dirname(__file__), file_name)]
    
    for p in possible_paths:
        if os.path.exists(p):
            path = p
            break
            
    if not path:
        # Fallback Generator (if csv is missing)
        dates = pd.date_range(start="2024-01-01", periods=200)
        df = pd.DataFrame({
            'datetime': dates,
            'location': np.random.choice(['Home', 'Work', 'Coffee Shop'], 200),
            'social_context': np.random.choice(['Alone', 'Friends', 'Colleagues'], 200),
            'activity': np.random.choice(['Working', 'Reading', 'Socializing'], 200),
            'coffee_type': np.random.choice(['Espresso', 'Latte', 'Cappuccino'], 200),
            'price': np.random.uniform(0, 6, 200),
            'caffeine_mg': np.random.randint(50, 150, 200),
            'mood_before': np.random.randint(3, 8, 200),
            'mood_after': np.random.randint(5, 10, 200),
            'sleep_hours_next_night': np.random.uniform(5, 9, 200)
        })
    else:
        df = pd.read_csv(path)
        df['datetime'] = pd.to_datetime(df['datetime'])

    # Feature Engineering
    df['Hour'] = df['datetime'].dt.hour
    df['DayOfWeek'] = df['datetime'].dt.day_name()
    df['Date_Only'] = df['datetime'].dt.date
    df['Mood_Boost'] = df['mood_after'] - df['mood_before']
    df['Cumul_Spend'] = df['price'].cumsum()
    
    # Safety Check for columns
    cols = ['weather', 'social_context', 'location', 'activity', 'stress_level', 'pleasure_score']
    for c in cols:
        if c not in df.columns: df[c] = "Unknown" if c in ['weather', 'social_context', 'location'] else 0

    return df

df = load_data()

# --- 4. SIDEBAR ---
with st.sidebar:
    st.markdown("### ◆ SETTINGS")
    if not df.empty:
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input("Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        social_opts = list(df['social_context'].unique())
        social_filter = st.multiselect("Social Context", social_opts, default=social_opts)

    st.markdown("---")
    st.info("Visual Analytics Project | 2024")

if not df.empty:
    mask = (df['datetime'].dt.date >= date_range[0]) & (df['datetime'].dt.date <= date_range[1])
    if social_filter:
        mask = mask & (df['social_context'].isin(social_filter))
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. DASHBOARD HEADER ---
st.markdown("""
<div class="main-title">
    <h1>THE QUANTIFIED COFFEE</h1>
    <p>A Personal Data Story: Habits, Context & Biological Impact</p>
</div>
""", unsafe_allow_html=True)

# --- 6. METHODOLOGY BUTTON (FIXED INDENTATION) ---
col_info1, col_info2, col_info3 = st.columns([1, 2, 1])
with col_info2:
    show_methodology = st.button("ℹ️ VIEW PROJECT METHODOLOGY & REPORT", use_container_width=True)

if show_methodology:
    st.info("👇 ACADEMIC REPORT DISPLAYED BELOW")
    
    # Using raw HTML without indentation to ensure Markdown parsing works correctly in Streamlit
    st.markdown("""
<div style="background: rgba(255,255,255,0.05); padding: 30px; border-radius: 15px; border: 1px solid #D4AF37;">
<h2 style="color: #D4AF37; text-align: center; font-family: 'Playfair Display', serif; margin-bottom: 30px;">PROJECT METHODOLOGY & DESIGN CHOICES</h2>
<h3 style="color: #FFF; border-bottom: 1px solid #555; padding-bottom: 10px;">1. Data & Motivations</h3>
<ul style="color: #B0BEC5; font-family: 'Montserrat', sans-serif; line-height: 1.6;">
<li><strong>Data Source:</strong> Simulated dataset (<code>my_coffee_life.csv</code>) based on realistic physiological models to enable a "Quantified Self" analysis.</li>
<li><strong>Goal:</strong> Move beyond descriptive statistics (how many?) to explanatory analytics (why am I tired?).</li>
</ul>
<br>
<h3 style="color: #FFF; border-bottom: 1px solid #555; padding-bottom: 10px;">2. Structure & Layout</h3>
<ul style="color: #B0BEC5; font-family: 'Montserrat', sans-serif; line-height: 1.6;">
<li><strong>Single-Page Layout:</strong> Chosen to create a seamless narrative flow ("Scrollytelling") rather than disjointed tabs. It guides the user from the general (Overview) to the specific (Biological Impact).</li>
<li><strong>Screenspace Use:</strong> High data-ink ratio. Charts are maximized, and text is kept concise. The 4-column KPI row provides an immediate "At a glance" summary.</li>
</ul>
<br>
<h3 style="color: #FFF; border-bottom: 1px solid #555; padding-bottom: 10px;">3. Visual Encodings & Justifications</h3>
<ul style="color: #B0BEC5; font-family: 'Montserrat', sans-serif; line-height: 1.6;">
<li><strong>Heatmap (Overview):</strong> Selected because temporal habits are cyclical. It reveals density patterns (Monday morning vs. Weekend) better than a line chart.</li>
<li><strong>Sankey / Parallel Categories (Context):</strong> Chosen to visualize the <em>flow</em> and complex relationships between categorical variables (Social -> Location -> Product).</li>
<li><strong>Scatter Plot with Annotations (Biology):</strong> Used to show correlation. The added "Red Zone" (>4PM) is a pre-attentive attribute that draws the eye immediately to the insight regarding sleep disruption.</li>
<li><strong>Gold/Dark Theme:</strong> A dark background reduces eye strain (useful for data-heavy apps) and the Gold/Amber palette semantically links to the coffee theme while providing high contrast for accessibility.</li>
</ul>
</div>
""", unsafe_allow_html=True)


# Common Plotly Layout for Dark Theme
dark_layout = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(color='#cfd8dc', family="Montserrat"),
    margin=dict(t=30, l=10, r=10, b=10)
)

# --- 01. EXECUTIVE SUMMARY ---
st.markdown('<div class="section-header">01. EXECUTIVE SUMMARY</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)
c1.metric("TOTAL CUPS", len(df_filtered), "Volume")
c2.metric("TOTAL SPEND", f"${df_filtered['price'].sum():.0f}", "USD")
c3.metric("CAFFEINE", f"{df_filtered['caffeine_mg'].sum()/1000:.1f} g", "Total Intake")
c4.metric("AVG SLEEP", f"{df_filtered['sleep_hours_next_night'].mean():.1f} h", "Next Night")

st.write("") 

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("##### ◆ WEEKLY RHYTHM (Heatmap)")
    st.caption("Identifying high-intensity consumption windows.")
    hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    
    fig_heat = px.density_heatmap(
        hm_data, x='Hour', y='DayOfWeek', z='Count',
        category_orders={'DayOfWeek': days_order},
        color_continuous_scale='Oranges',
    )
    fig_heat.update_layout(**dark_layout)
    fig_heat.update_coloraxes(colorbar_bgcolor="rgba(0,0,0,0)", colorbar_title="")
    st.plotly_chart(fig_heat, use_container_width=True)

with col2:
    st.markdown("##### ◆ PREFERENCES (Donut)")
    st.caption("Distribution of budget by coffee type.")
    fig_pie = px.pie(
        df_filtered, 
        values='price', 
        names='coffee_type', 
        hole=0.7,
        color_discrete_sequence=px.colors.sequential.Brwnyl
    )
    fig_pie.update_traces(textposition='outside', textinfo='percent')
    fig_pie.update_layout(showlegend=False, **dark_layout)
    st.plotly_chart(fig_pie, use_container_width=True)


# --- 02. LIFESTYLE & CONTEXT FLOW ---
st.markdown('<div class="section-header">02. LIFESTYLE & CONTEXT FLOW</div>', unsafe_allow_html=True)
st.caption("How does my environment influence my consumption choices?")

st.markdown("##### ◆ THE CONTEXTUAL FLOW (Parallel Categories)")
st.caption("Tracing the path: Who I am with -> Where I am -> What I drink.")

# Parallel Categories (Sankey-like)
fig_parcat = px.parallel_categories(
    df_filtered, 
    dimensions=['social_context', 'location', 'coffee_type'],
    color="price", 
    color_continuous_scale=px.colors.sequential.Inferno,
    labels={'social_context': 'SOCIAL', 'location': 'LOCATION', 'coffee_type': 'COFFEE'}
)
fig_parcat.update_layout(**dark_layout, height=450)
st.plotly_chart(fig_parcat, use_container_width=True)

col_ctx1, col_ctx2 = st.columns(2)
with col_ctx1:
    st.markdown("##### ◆ ACTIVITY BREAKDOWN")
    fig_tree = px.treemap(
        df_filtered, 
        path=['activity', 'coffee_type'], 
        values='price',
        color='activity',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_tree.update_layout(**dark_layout)
    st.plotly_chart(fig_tree, use_container_width=True)

with col_ctx2:
    st.markdown("##### ◆ PRICE DISTRIBUTION")
    fig_box = px.box(
        df_filtered, x='location', y='price',
        color='location',
        color_discrete_sequence=px.colors.qualitative.Antique
    )
    fig_box.update_layout(**dark_layout, showlegend=False)
    st.plotly_chart(fig_box, use_container_width=True)


# --- 03. FINANCIAL VELOCITY ---
st.markdown('<div class="section-separator"></div>', unsafe_allow_html=True)
st.markdown('<div class="section-header">03. FINANCIAL VELOCITY</div>', unsafe_allow_html=True)

st.markdown("##### ◆ CUMULATIVE SPENDING OVER TIME")
st.caption("Tracking the rate of expenditure throughout the year.")
fig_area = px.area(
    df_filtered.sort_values('datetime'), 
    x='datetime', y='Cumul_Spend',
    color_discrete_sequence=['#D4AF37']
)
fig_area.update_layout(**dark_layout, showlegend=False, yaxis_title="Cumulative Spend ($)")
st.plotly_chart(fig_area, use_container_width=True)


# --- 04. BIOLOGICAL IMPACT (The "Why") ---
st.markdown('<div class="section-header">04. BIOLOGICAL IMPACT</div>', unsafe_allow_html=True)
st.caption("Quantifying the effects of caffeine on sleep quality and mood regulation.")

col_b1, col_b2 = st.columns([3, 2])

with col_b1:
    st.markdown("##### ◆ THE CAFFEINE CURFEW (Scatter)")
    st.caption("Correlation between Hour of Intake (X) and Sleep Duration (Y). Note the red zone.")
    fig_scatter = px.scatter(
        df_filtered, x='Hour', y='sleep_hours_next_night',
        size='caffeine_mg', color='location',
        color_discrete_sequence=px.colors.qualitative.Bold,
        labels={'sleep_hours_next_night': 'Sleep (Hours)', 'Hour': 'Hour of Day'}
    )
    # Visual Storytelling: The Danger Zone
    fig_scatter.add_vrect(
        x0=16, x1=24, 
        fillcolor="red", opacity=0.1, line_width=0,
        annotation_text="CRITICAL ZONE (>4PM)", annotation_position="top left", annotation_font_color="#EF5350"
    )
    fig_scatter.update_layout(**dark_layout)
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_b2:
    st.markdown("##### ◆ MOOD SHIFT (Arrow Plot)")
    st.caption("Average mood score Before vs. After coffee.")
    
    # Calculate averages
    mood_agg = df_filtered.groupby('activity')[['mood_before', 'mood_after']].mean().reset_index()
    
    fig_dumbell = go.Figure()
    for i, row in mood_agg.iterrows():
        # Line
        fig_dumbell.add_trace(go.Scatter(
            x=[row['mood_before'], row['mood_after']], y=[row['activity'], row['activity']],
            mode='lines', line=dict(color='#80CBC4', width=2), showlegend=False
        ))
        # Points
        fig_dumbell.add_trace(go.Scatter(
            x=[row['mood_before']], y=[row['activity']], mode='markers', 
            marker=dict(color='#B0BEC5', size=8), name='Before' if i==0 else ""
        ))
        fig_dumbell.add_trace(go.Scatter(
            x=[row['mood_after']], y=[row['activity']], mode='markers', 
            marker=dict(color='#FFD54F', size=12), name='After' if i==0 else ""
        ))

    fig_dumbell.update_layout(title="", xaxis_title="Mood Score (1-10)", **dark_layout)
    st.plotly_chart(fig_dumbell, use_container_width=True)

# --- 05. LOCATION PROFILING (Radar) ---
st.markdown('<div class="section-separator"></div>', unsafe_allow_html=True)
st.markdown("##### ◆ LOCATION PROFILING (Multidimensional)")
st.caption("Comparing different consumption locations across multiple metrics.")

cols_radar = ['price', 'caffeine_mg', 'mood_after', 'sleep_hours_next_night']
# Normalize
radar_df = df_filtered.groupby('location')[cols_radar].mean().reset_index()
for c in cols_radar:
    if radar_df[c].max() > 0:
        radar_df[c] = radar_df[c] / radar_df[c].max()

fig_radar = go.Figure()
for i, row in radar_df.iterrows():
    fig_radar.add_trace(go.Scatterpolar(
        r=[row[c] for c in cols_radar],
        theta=['COST', 'CAFFEINE', 'MOOD', 'SLEEP'],
        fill='toself', 
        name=row['location'],
        line_width=1.5
    ))

fig_radar.update_layout(
    polar=dict(
        radialaxis=dict(visible=True, showticklabels=False, linecolor='#444'),
        bgcolor='rgba(255,255,255,0.02)'
    ),
    **dark_layout,
    height=450,
    showlegend=True
)
st.plotly_chart(fig_radar, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("""
<div style="text-align: center; font-size: 0.8rem; color: #757575; margin-top: 50px;">
    VISUAL ANALYTICS PROJECT 2024 | DESIGNED WITH STREAMLIT & PLOTLY | SINGLE PAGE APPLICATION
</div>
""", unsafe_allow_html=True)
