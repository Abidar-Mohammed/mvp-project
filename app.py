# --- 6. METHODOLOGY BUTTON (CORRECTED) ---
col_info1, col_info2, col_info3 = st.columns([1, 2, 1])
with col_info2:
    show_methodology = st.button("ℹ️ VIEW PROJECT METHODOLOGY & REPORT", use_container_width=True)

if show_methodology:
    st.info("👇 ACADEMIC REPORT DISPLAYED BELOW")
    
    # On utilise un conteneur stylisé pour tout le bloc
    with st.container():
        st.markdown("""
        <div style="background-color: rgba(20, 20, 20, 0.9); padding: 30px; border-radius: 15px; border: 1px solid #D4AF37;">
            <h2 style="color: #D4AF37; text-align: center; margin-bottom: 30px; font-family: 'Playfair Display', serif;">PROJECT METHODOLOGY & DESIGN CHOICES</h2>
            
            <h3 style="color: #FFF8E1; border-bottom: 1px solid #555; padding-bottom: 10px;">1. Data & Motivations</h3>
            <ul style="color: #B0BEC5; font-family: 'Montserrat', sans-serif; line-height: 1.6;">
                <li><strong>Data Source:</strong> Simulated dataset (<code>my_coffee_life.csv</code>) based on realistic physiological models to enable a "Quantified Self" analysis.</li>
                <li><strong>Goal:</strong> Move beyond descriptive statistics (how many?) to explanatory analytics (why am I tired?).</li>
            </ul>

            <br>

            <h3 style="color: #FFF8E1; border-bottom: 1px solid #555; padding-bottom: 10px;">2. Structure & Layout</h3>
            <ul style="color: #B0BEC5; font-family: 'Montserrat', sans-serif; line-height: 1.6;">
                <li><strong>Single-Page Layout:</strong> Chosen to create a seamless narrative flow ("Scrollytelling") rather than disjointed tabs. It guides the user from the general (Overview) to the specific (Biological Impact).</li>
                <li><strong>Screenspace Use:</strong> High data-ink ratio. Charts are maximized, and text is kept concise. The 4-column KPI row provides an immediate "At a glance" summary.</li>
            </ul>

            <br>

            <h3 style="color: #FFF8E1; border-bottom: 1px solid #555; padding-bottom: 10px;">3. Visual Encodings & Justifications</h3>
            <ul style="color: #B0BEC5; font-family: 'Montserrat', sans-serif; line-height: 1.6;">
                <li><strong>Heatmap (Overview):</strong> Selected because temporal habits are cyclical. It reveals density patterns (Monday morning vs. Weekend) better than a line chart.</li>
                <li><strong>Sankey / Parallel Categories (Context):</strong> Chosen to visualize the <em>flow</em> and complex relationships between categorical variables (Social -> Location -> Product).</li>
                <li><strong>Scatter Plot with Annotations (Biology):</strong> Used to show correlation. The added "Red Zone" (>4PM) is a pre-attentive attribute that draws the eye immediately to the insight regarding sleep disruption.</li>
                <li><strong>Gold/Dark Theme:</strong> A dark background reduces eye strain (useful for data-heavy apps) and the Gold/Amber palette semantically links to the coffee theme while providing high contrast for accessibility.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
