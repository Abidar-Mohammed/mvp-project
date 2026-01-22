import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =====================================================
# 1. CONFIGURATION PAGE
# =====================================================
st.set_page_config(
    page_title="Executive Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. STYLE CSS – PLUS COLORÉ & DATA-FOCUSED
# =====================================================
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Segoe UI', 'Inter', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #F4F6F8;
    border-right: 2px solid #E0E0E0;
}

/* KPI Cards */
div[data-testid="metric-container"] {
    background: linear-gradient(135deg, #ffffff, #f9f9f9);
    border-radius: 10px;
    padding: 20px;
    border-left: 6px solid #27AE60;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.05);
}

/* Section Titles */
.section-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 10px;
    color: #2C3E50;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. DONNÉES SIMULÉES (RICHES)
# =====================================================
@st.cache_data
def load_data():
    np.random.seed(42)

    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    n = 3500

    dates = np.random.choice(pd.date_range(start_date, end_date, freq="H"), n)

    df = pd.DataFrame({
        "Date": dates,
        "Product": np.random.choice(
            ["Enterprise Suite X1", "Cloud Storage Pro", "CyberSecurity Plus", "AI Consulting"],
            n
        ),
        "Country": np.random.choice(
            ["United States", "France", "Germany", "United Kingdom", "Japan", "India", "Canada", "Brazil"],
            n
        ),
        "Segment": np.random.choice(["Enterprise", "SMB", "Government"], n, p=[0.45, 0.4, 0.15]),
        "Status": np.random.choice(["Confirmed", "Pending", "Cancelled"], n, p=[0.82, 0.12, 0.06]),
        "Revenue": np.random.randint(2000, 25000, n)
    })

    df["Cost"] = df["Revenue"] * np.random.uniform(0.35, 0.7, n)
    df["Profit"] = df["Revenue"] - df["Cost"]
    df["Margin (%)"] = (df["Profit"] / df["Revenue"]) * 100

    return df.sort_values("Date")

df = load_data()

# =====================================================
# 4. HEADER ANALYTIQUE (SANS LOGO)
# =====================================================
st.markdown("""
<div style="background: linear-gradient(90deg, #2C3E50, #27AE60);
            padding: 25px;
            border-radius: 12px;
            color: white;">
    <h1 style="margin:0;">📊 Global Executive Performance Dashboard</h1>
    <p style="margin:0; opacity:0.9;">
        Financial performance • Geographic insights • Product & client analytics
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

# =====================================================
# 5. SIDEBAR – FILTRES
# =====================================================
st.sidebar.title("🎛️ Dashboard Controls")

date_range = st.sidebar.date_input(
    "Analysis Period",
    value=(df["Date"].min().date(), df["Date"].max().date())
)

countries = st.sidebar.multiselect(
    "Countries",
    df["Country"].unique(),
    default=df["Country"].unique()
)

segments = st.sidebar.multiselect(
    "Client Segments",
    df["Segment"].unique(),
    default=df["Segment"].unique()
)

df_f = df[
    (df["Date"].dt.date >= date_range[0]) &
    (df["Date"].dt.date <= date_range[1]) &
    (df["Country"].isin(countries)) &
    (df["Segment"].isin(segments)) &
    (df["Status"] == "Confirmed")
]

if df_f.empty:
    st.warning("No data for the selected filters.")
    st.stop()

# =====================================================
# 6. KPIs AVANCÉS
# =====================================================
total_revenue = df_f["Revenue"].sum()
total_profit = df_f["Profit"].sum()
avg_margin = df_f["Margin (%)"].mean()
deals = len(df_f)
avg_deal_size = total_revenue / deals

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("💰 Total Revenue", f"${total_revenue:,.0f}")
k2.metric("📈 Net Profit", f"${total_profit:,.0f}")
k3.metric("📊 Avg Margin", f"{avg_margin:.1f}%")
k4.metric("📦 Active Deals", f"{deals:,}")
k5.metric("🎯 Avg Deal Size", f"${avg_deal_size:,.0f}")

st.markdown("---")

# =====================================================
# 7. DASHBOARDS MULTIPLES
# =====================================================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Financial Trends",
    "🌍 Geographic Insights",
    "🧠 Product & Segment Analysis",
    "⏱️ Time Intelligence"
])

# ---------- TAB 1 ----------
with tab1:
    st.markdown('<div class="section-title">Revenue & Profit Over Time</div>', unsafe_allow_html=True)

    df_f["Month"] = df_f["Date"].dt.to_period("M").dt.start_time
    monthly = df_f.groupby("Month")[["Revenue", "Profit"]].sum().reset_index()

    fig = go.Figure()
    fig.add_bar(x=monthly["Month"], y=monthly["Revenue"], name="Revenue", marker_color="#3498DB")
    fig.add_scatter(x=monthly["Month"], y=monthly["Profit"],
                    name="Profit", mode="lines+markers",
                    line=dict(color="#27AE60", width=3))

    fig.update_layout(
        template="simple_white",
        height=420,
        legend=dict(orientation="h", y=1.15)
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------- TAB 2 ----------
with tab2:
    st.markdown('<div class="section-title">Global Revenue Distribution</div>', unsafe_allow_html=True)

    map_data = df_f.groupby("Country")["Revenue"].sum().reset_index()

    fig_map = px.choropleth(
        map_data,
        locations="Country",
        locationmode="country names",
        color="Revenue",
        color_continuous_scale="Viridis",
        template="simple_white"
    )

    fig_map.update_layout(height=500)
    st.plotly_chart(fig_map, use_container_width=True)

# ---------- TAB 3 ----------
with tab3:
    st.markdown('<div class="section-title">Product & Segment Deep Dive</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        fig_prod = px.bar(
            df_f.groupby("Product")["Revenue"].sum().reset_index(),
            x="Revenue", y="Product",
            orientation="h",
            color="Revenue",
            color_continuous_scale="Blues"
        )
        fig_prod.update_layout(height=400)
        st.plotly_chart(fig_prod, use_container_width=True)

    with c2:
        fig_seg = px.pie(
            df_f,
            values="Revenue",
            names="Segment",
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_seg.update_layout(height=400)
        st.plotly_chart(fig_seg, use_container_width=True)

# ---------- TAB 4 ----------
with tab4:
    st.markdown('<div class="section-title">Hourly & Weekly Sales Patterns</div>', unsafe_allow_html=True)

    df_f["Hour"] = df_f["Date"].dt.hour
    df_f["Weekday"] = df_f["Date"].dt.day_name()

    heat = df_f.pivot_table(
        index="Weekday",
        columns="Hour",
        values="Revenue",
        aggfunc="sum"
    )

    fig_heat = px.imshow(
        heat,
        color_continuous_scale="Inferno",
        aspect="auto"
    )

    fig_heat.update_layout(height=450)
    st.plotly_chart(fig_heat, use_container_width=True)

# =====================================================
# 8. FOOTER
# =====================================================
st.markdown("---")
st.caption("Advanced Executive Analytics Dashboard • Internal Use Only")
