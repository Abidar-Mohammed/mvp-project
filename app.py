import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Executive Performance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# GLOBAL STYLE – EXECUTIVE / CONSULTING
# =====================================================
st.markdown("""
<style>
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #F5F7FA;
    border-right: 1px solid #E1E5EA;
}

/* KPI Cards */
div[data-testid="metric-container"] {
    background-color: white;
    border-radius: 12px;
    padding: 18px;
    border-left: 6px solid #2ECC71;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.06);
}

/* Section titles */
.section-title {
    font-size: 20px;
    font-weight: 600;
    margin-bottom: 12px;
    color: #1F2933;
}

/* Card containers */
.card {
    background-color: white;
    padding: 18px;
    border-radius: 14px;
    box-shadow: 0px 6px 18px rgba(0,0,0,0.06);
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# DATA GENERATION
# =====================================================
@st.cache_data
def load_data():
    np.random.seed(42)
    n = 3500
    end = datetime.today()
    start = end - timedelta(days=365)

    df = pd.DataFrame({
        "Date": np.random.choice(pd.date_range(start, end, freq="H"), n),
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
        "Revenue": np.random.randint(2500, 26000, n)
    })

    df["Cost"] = df["Revenue"] * np.random.uniform(0.35, 0.7, n)
    df["Profit"] = df["Revenue"] - df["Cost"]
    df["Margin (%)"] = (df["Profit"] / df["Revenue"]) * 100

    return df.sort_values("Date")

df = load_data()

# =====================================================
# HEADER WITH SINGLE REAL COMPANY LOGO
# =====================================================
c_logo, c_title = st.columns([1, 6])

with c_logo:
    st.image(
        "https://upload.wikimedia.org/wikipedia/commons/7/7e/Accenture.svg",
        use_container_width=True
    )

with c_title:
    st.markdown("""
    <div style="padding:10px 0;">
        <h1 style="margin-bottom:5px;">Global Performance Command Center</h1>
        <p style="color:#4B5563; margin-top:0;">
            Financial, geographic and product-level analytics for executive decision-making
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =====================================================
# SIDEBAR FILTERS
# =====================================================
st.sidebar.title("Analysis Settings")

date_range = st.sidebar.date_input(
    "Period",
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
    st.stop()

# =====================================================
# KPI SECTION
# =====================================================
total_rev = df_f["Revenue"].sum()
total_profit = df_f["Profit"].sum()
avg_margin = df_f["Margin (%)"].mean()
deals = len(df_f)
avg_deal = total_rev / deals

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Total Revenue", f"${total_rev:,.0f}")
k2.metric("Net Profit", f"${total_profit:,.0f}")
k3.metric("Average Margin", f"{avg_margin:.1f}%")
k4.metric("Confirmed Deals", f"{deals:,}")
k5.metric("Avg Deal Size", f"${avg_deal:,.0f}")

st.markdown("---")

# =====================================================
# DASHBOARD TABS
# =====================================================
tab1, tab2, tab3 = st.tabs([
    "Financial Trends",
    "Geographic Overview",
    "Product & Segment Analysis"
])

# ---------------- TAB 1 ----------------
with tab1:
    st.markdown('<div class="section-title">Revenue & Profit Evolution</div>', unsafe_allow_html=True)

    df_f["Month"] = df_f["Date"].dt.to_period("M").dt.start_time
    monthly = df_f.groupby("Month")[["Revenue", "Profit"]].sum().reset_index()

    fig = go.Figure()
    fig.add_bar(x=monthly["Month"], y=monthly["Revenue"], name="Revenue", marker_color="#1F77B4")
    fig.add_scatter(x=monthly["Month"], y=monthly["Profit"],
                    name="Profit", mode="lines+markers",
                    line=dict(color="#2ECC71", width=3))

    fig.update_layout(template="simple_white", height=420)
    st.plotly_chart(fig, use_container_width=True)

# ---------------- TAB 2 ----------------
with tab2:
    st.markdown('<div class="section-title">Revenue by Country</div>', unsafe_allow_html=True)

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

# ---------------- TAB 3 ----------------
with tab3:
    st.markdown('<div class="section-title">Product & Client Mix</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        fig_prod = px.bar(
            df_f.groupby("Product")["Revenue"].sum().reset_index(),
            x="Revenue",
            y="Product",
            orientation="h",
            color="Revenue",
            color_continuous_scale="Blues"
        )
        fig_prod.update_layout(height=420)
        st.plotly_chart(fig_prod, use_container_width=True)

    with c2:
        fig_seg = px.pie(
            df_f,
            values="Revenue",
            names="Segment",
            hole=0.5,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_seg.update_layout(height=420)
        st.plotly_chart(fig_seg, use_container_width=True)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption("Executive Analytics Dashboard – Internal Use Only")
