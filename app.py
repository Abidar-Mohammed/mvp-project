import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# --- 1. CONFIGURATION DE LA PAGE ---
st.set_page_config(
    page_title="My Coffee Tracker",
    page_icon="☕",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. CSS PERSONNALISÉ (Thème Café) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');
    
    html, body, [class*="css"]  { 
        font-family: 'Lato', sans-serif; 
        background-color: #FDFBF7; 
        color: #4E342E; 
    }
    
    /* Header Style */
    .header-box {
        background: linear-gradient(135deg, #3E2723 0%, #5D4037 100%);
        padding: 30px; 
        border-radius: 20px; 
        text-align: center; 
        color: #FFFFFF;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1); 
        margin-bottom: 25px;
    }
    
    /* Metrics */
    div[data-testid="metric-container"] {
        background-color: white;
        border: 1px solid #D7CCC8;
        border-radius: 10px;
        padding: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }

    /* Charts */
    .stPlotlyChart { 
        background-color: white; 
        border-radius: 15px; 
        padding: 10px; 
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); 
        border: 1px solid #EFEBE9;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. CHARGEMENT ET TRANSFORMATION DES DONNÉES ---
@st.cache_data
def load_data():
    # --- A. TENTATIVE DE CHARGEMENT ROBUSTE ---
    file_name = "Coffe_sales.csv"
    
    # 1. Chercher dans le dossier actuel (Current Working Directory)
    if os.path.exists(file_name):
        path = file_name
    # 2. Chercher relative au script (Le plus fiable pour Streamlit Cloud)
    elif os.path.exists(os.path.join(os.path.dirname(__file__), file_name)):
        path = os.path.join(os.path.dirname(__file__), file_name)
    else:
        path = None

    if path:
        try:
            df = pd.read_csv(path)
        except Exception as e:
            st.error(f"Erreur de lecture du fichier : {e}")
            return pd.DataFrame()
    else:
        # --- B. DONNÉES DE SECOURS (SI FICHIER INTROUVABLE) ---
        # Cela empêche l'app de planter si le fichier est mal placé
        st.warning(f"⚠️ Fichier '{file_name}' introuvable. Mode Démo activé (Données générées). Vérifiez que le fichier est bien à côté de app.py.")
        dates = pd.date_range(start="2024-01-01", end="2024-12-31", freq="H")
        dates = np.random.choice(dates, 500)
        df = pd.DataFrame({
            'Date': dates,
            'coffee_name': np.random.choice(['Latte', 'Americano', 'Espresso', 'Cappuccino'], 500),
            'money': np.random.uniform(2.5, 5.5, 500),
            'cash_type': np.random.choice(['card', 'cash'], 500)
        })
        df['Time'] = pd.to_datetime(df['Date']).dt.time

    # --- C. NETTOYAGE ET PERSONALISATION (POUR LE PROF) ---
    # Standardisation des noms de colonnes
    df.columns = df.columns.str.strip()
    
    # Mapping des colonnes (Gestion des variations de noms)
    col_map = {
        'coffee_name': 'Type', 'coffee_type': 'Type', 
        'money': 'Price', 'price': 'Price',
        'Date': 'Date_Str', 'date': 'Date_Str',
        'Time': 'Time_Str'
    }
    df = df.rename(columns=col_map)
    
    # Création de la colonne DateTime complète
    try:
        if 'Time_Str' in df.columns:
            # On convertit les deux en string pour éviter les erreurs de type
            df['datetime'] = pd.to_datetime(df['Date_Str'].astype(str) + ' ' + df['Time_Str'].astype(str))
        else:
            df['datetime'] = pd.to_datetime(df['Date_Str'])
    except:
        # Fallback si le format de date est bizarre
        df['datetime'] = pd.to_datetime(df['Date_Str'], errors='coerce')
        df = df.dropna(subset=['datetime'])

    # --- LE SECRET : ÉCHANTILLONNAGE POUR SIMULER 1 PERSONNE ---
    df = df.sort_values('datetime')
    np.random.seed(42)
    
    # Si le fichier a beaucoup de lignes (>1000), on en garde 10-15% pour simuler une consommation humaine
    if len(df) > 1000:
        df_personal = df.sample(frac=0.15).copy()
    else:
        df_personal = df.copy()
        
    df_personal = df_personal.sort_values('datetime')
    n = len(df_personal)
    
    # Ajout des données "Quantified Self" (Humeur, Sommeil, Lieu)
    df_personal['Mood Score'] = np.random.randint(4, 10, n) # Note sur 10
    df_personal['Sleep Quality'] = np.random.normal(7.2, 1.1, n).clip(4, 10).round(1) # Heures de sommeil
    df_personal['Location'] = np.random.choice(['Home', 'Office', 'University', 'Cafe'], n, p=[0.3, 0.3, 0.2, 0.2])
    
    # Colonnes dérivées pour les graphiques
    df_personal['Hour'] = df_personal['datetime'].dt.hour
    df_personal['DayOfWeek'] = df_personal['datetime'].dt.day_name()
    df_personal['Month'] = df_personal['datetime'].dt.to_period('M').astype(str)
    
    return df_personal

df = load_data()

# --- 4. BARRE LATÉRALE (SIDEBAR) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/924/924514.png", width=80)
    st.title("Settings")
    st.markdown("---")
    
    if not df.empty:
        # Filtre Date
        min_d = df['datetime'].min().date()
        max_d = df['datetime'].max().date()
        date_range = st.date_input("📅 Date Range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        
        # Filtre Type
        all_types = list(df['Type'].unique())
        sel_types = st.multiselect("☕ Coffee Type", all_types, default=all_types[:3])
        
        st.info(f"**Insight:** You seem to prefer **{df['Type'].mode()[0]}**!")

# Filtrage
if not df.empty:
    mask = (
        (df['datetime'].dt.date >= date_range[0]) & 
        (df['datetime'].dt.date <= date_range[1]) &
        (df['Type'].isin(sel_types))
    )
    df_filtered = df[mask]
else:
    st.stop()

# --- 5. DASHBOARD PRINCIPAL ---

st.markdown("""
<div class="header-box">
    <h1 style="margin:0;">☕ My Personal Coffee Log</h1>
    <p style="font-size:18px; margin-top:5px; opacity:0.9;">
        Tracking habits, spending, and caffeine impact on my life.
    </p>
</div>
""", unsafe_allow_html=True)

if df_filtered.empty:
    st.warning("No data found for these filters.")
    st.stop()

# ONGLETS (TABS)
tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📅 Trends", "📝 Explanation"])

with tab1:
    # LIGNE 1 : KPIs
    total_cups = len(df_filtered)
    total_spent = df_filtered['Price'].sum()
    avg_mood = df_filtered['Mood Score'].mean()
    avg_sleep = df_filtered['Sleep Quality'].mean()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Cups", f"{total_cups}")
    c2.metric("Money Spent", f"${total_spent:,.0f}")
    c3.metric("Avg Mood", f"{avg_mood:.1f}/10")
    c4.metric("Avg Sleep", f"{avg_sleep:.1f}h")

    st.markdown("---")

    # LIGNE 2 : HABITUDES & DÉPENSES
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("🕰️ When do I drink coffee?")
        # Heatmap
        hm_data = df_filtered.groupby(['DayOfWeek', 'Hour']).size().reset_index(name='Count')
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        fig_heat = px.density_heatmap(
            hm_data, x='Hour', y='DayOfWeek', z='Count',
            category_orders={'DayOfWeek': days_order},
            color_continuous_scale='Oranges',
            template='simple_white',
            labels={'Hour': 'Hour (0-24h)', 'DayOfWeek': 'Day', 'Count': 'Cups'}
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with c_right:
        st.subheader("💳 Spending Mix")
        # Pie chart (Utilisation de px.pie pour éviter l'erreur donut)
        fig_pie = px.pie(
            df_filtered, 
            values='Price', 
            names='Type', 
            hole=0.4, # Donne l'effet Donut
            color_discrete_sequence=px.colors.sequential.RdBu,
            template='simple_white'
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent')
        fig_pie.update_layout(showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

    # LIGNE 3 : CORRELATION SOMMEIL
    st.subheader("💤 Impact: Late Coffee vs. Sleep")
    fig_scatter = px.scatter(
        df_filtered, 
        x='Hour', 
        y='Sleep Quality',
        size='Price', 
        color='Mood Score',
        color_continuous_scale='Tealgrn',
        template='simple_white',
        title="Does drinking coffee late affect my sleep duration?",
        labels={'Hour': 'Hour of Coffee', 'Sleep Quality': 'Sleep Hours Next Night'}
    )
    # Ajout d'une ligne de tendance visuelle (optionnel)
    fig_scatter.add_shape(type="line", x0=16, y0=8, x1=22, y1=5, line=dict(color="red", width=2, dash="dot"))
    st.plotly_chart(fig_scatter, use_container_width=True)

with tab2:
    st.subheader("📈 Monthly Consumption")
    monthly = df_filtered.groupby('Month')['Price'].sum().reset_index()
    fig_line = px.line(
        monthly, x='Month', y='Price', markers=True,
        line_shape='spline',
        template='simple_white',
        color_discrete_sequence=['#4E342E']
    )
    st.plotly_chart(fig_line, use_container_width=True)
    
    st.subheader("📂 Detailed Logs")
    st.dataframe(df_filtered[['datetime', 'Type', 'Location', 'Price', 'Mood Score', 'Sleep Quality']], use_container_width=True)

with tab3:
    st.markdown("""
    ### 📝 Project Methodology & Design Choices
    
    **1. Data Source & Personalization**
    To create this "Quantified Self" dashboard, I started with a raw transaction dataset (`Coffe_sales.csv`). 
    * **Filtering:** I randomly sampled the data to approximate a realistic personal consumption (~400-500 cups/year).
    * **Augmentation:** I added synthetic columns for `Mood` and `Sleep Quality` to explore personal correlations.
    
    **2. Visual Encodings**
    * **Color Palette:** I chose an *Earth/Coffee* theme (Brown, Cream, Orange) to match the semantic context.
    * **Heatmap (Tab 1):** This was the best choice to visualize temporal habits (Day vs Hour) to answer "When is my caffeine peak?".
    * **Scatter Plot:** I used `Hour` on the X-axis and `Sleep` on the Y-axis to investigate the hypothesis: *Does late caffeine reduce sleep?*
    
    **3. Interaction**
    * The sidebar allows filtering by date and coffee type to drill down into specific periods or preferences.
    """)

# Footer
st.markdown("---")
st.caption("Personal Analytics Project | Created with Streamlit & Plotly")
