import streamlit as st
import pandas as pd
import json
import os
import time
from google import genai
from datetime import datetime

# ==========================================
# PAGE CONFIGURATION & INITIAL SETUP
# ==========================================
st.set_page_config(page_title="BusinessIntelligence.ai", layout="wide", page_icon="📊")

# Custom CSS for polished UI and Badges
st.markdown("""
    <style>
    .badge-math { background-color: #1E88E5; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .badge-ai { background-color: #8E24AA; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
    .telemetry-card { background-color: #f0f2f6; padding: 15px; border-radius: 8px; border-left: 4px solid #4CAF50; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# Helper function to gracefully load data
@st.cache_data
def load_data(path):
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame() # Return empty if not found

# ==========================================
# HEADER & GLOBAL GOVERNANCE BANNER
# ==========================================
st.title("BusinessIntelligence.ai")
st.subheader("Autonomous KPI Intelligence Engine")

col1, col2 = st.columns([1, 1])
with col1:
    st.markdown('<span class="badge-math">⚙️ Deterministic Math Engine: Pure Python</span>', unsafe_allow_html=True)
with col2:
    st.markdown('<span class="badge-ai">✨ Generative Synthesis: Gemini 3.6 Flash</span>', unsafe_allow_html=True)

st.write("") # Spacer

# Expandable Semantic Contract
with st.expander("📄 View Semantic Contract (Governance Layer)"):
    contract_path = "semantic_contract.json"
    if os.path.exists(contract_path):
        with open(contract_path, "r") as f:
            st.json(json.load(f))
    else:
        st.json({
            "kpi_name": "Revenue",
            "formula": "Traffic * Conversion Rate * AOV",
            "update_frequency": "Daily",
            "owner": "VP of E-Commerce",
            "role_based_access": {"Executive": "Full", "Store Analyst": "Filtered", "Associate": "Redacted"}
        })

# ==========================================
# SIDEBAR CONTROLS & TELEMETRY
# ==========================================
with st.sidebar:
    st.header("Control Panel")
    api_key_input = st.text_input("Gemini API Key", value=os.environ.get("GEMINI_API_KEY", ""), type="password")
    persona = st.radio("Select Persona", ["VP of E-Commerce", "Regional Operations Lead"])
    
    st.divider()
    st.header("Live Telemetry")
    # Telemetry placeholders to be updated after runs
    tel_time = st.empty()
    tel_tokens = st.empty()
    tel_cost = st.empty()
    
    # Initialize default telemetry values
    tel_time.metric("Latency", "-- ms")
    tel_tokens.metric("Tokens (In/Out)", "-- / --")
    tel_cost.metric("Est. Query Cost", "$0.00000")
    
    st.divider()
    st.header("Feedback Loop")
    with st.form("feedback_form"):
        st.write("Was this insight accurate?")
        col_up, col_down = st.columns(2)
        sentiment = st.radio("Sentiment", ["👍 Good", "👎 Bad"], horizontal=True, label_visibility="collapsed")
        fb_text = st.text_area("Correction / Notes")
        if st.form_submit_button("Submit Feedback"):
            # Append to local JSON store
            fb_data = {"timestamp": str(datetime.now()), "sentiment": sentiment, "notes": fb_text}
            with open("feedback_store.json", "a") as f:
                f.write(json.dumps(fb_data) + "\n")
            st.success("Feedback logged!")

# ==========================================
# MAIN DASHBOARD (4 SCENARIO TABS)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs([
    "1. Multi-Factor Drop", 
    "2. Low-Confidence / Abstain", 
    "3. Sparse History", 
    "4. Role-Based Security"
])

# ------------------------------------------
# TAB 1: Multi-Factor KPI Movement
# ------------------------------------------
with tab1:
    st.markdown("### Scenario 1: Northeast Revenue Anomaly (Aug 24, 2026)")
    
    # KPI Summary Cards
    c1, c2, c3 = st.columns(3)
    c1.metric("Revenue Variance", "-$484.23", "-8.2%")
    c2.metric("Volume Impact (Glitch)", "-$447.47", "92.4% contribution")
    c3.metric("Price Impact (Competitor)", "-$36.76", "7.6% contribution")
    
    # Render line chart (Simulating the 30-day baseline vs actual)
    df_orders = load_data("data/orders_daily.csv")
    if not df_orders.empty:
        df_ne = df_orders[df_orders['region'] == 'Northeast'].copy()
        df_ne['order_date'] = pd.to_datetime(df_ne['order_date'])
        df_ne = df_ne.set_index('order_date').sort_index().tail(30)
        df_ne['30_Day_Baseline'] = df_ne['revenue'].rolling(7, min_periods=1).mean() + 200 # simulated baseline
        st.line_chart(df_ne[['revenue', '30_Day_Baseline']])
    else:
        st.info("Chart placeholder: 'data/orders_daily.csv' not found.")

    if st.button("Run AI Synthesis 🚀", type="primary"):
        if not api_key_input:
            st.error("Please enter a Gemini API Key in the sidebar.")
        else:
            with st.spinner("Synthesizing insights..."):
                start_time = time.time()
                
                # Setup Client
                client = genai.Client(api_key=api_key_input)
                
                # Construct Prompt
                prompt = f"""
                You are a BI AI. Generate a narrative for the '{persona}'.
                Math: Revenue dropped $484.23 (92.4% Volume drop, 7.6% Price drop).
                Logs: [Incident: Checkout payment failure / gateway glitch], [Competitor Alert: Flash sale on winter apparel].
                Rule: Do NOT invent numbers. 
                Structure recommendations exactly as: Driver -> Controllable Lever -> Action -> Expected Impact -> Owner -> Confidence -> Monitoring Plan.
                """
                
                try:
                    response = client.models.generate_content(
                        model='gemini-3.6-flash',
                        contents=prompt
                    )
                    end_time = time.time()
                    
                    # Update Telemetry in Sidebar
                    latency_ms = round((end_time - start_time) * 1000)
                    in_tokens = response.usage_metadata.prompt_token_count if response.usage_metadata else 150
                    out_tokens = response.usage_metadata.candidates_token_count if response.usage_metadata else 300
                    cost = (in_tokens / 1000 * 0.000075) + (out_tokens / 1000 * 0.0003)
                    
                    tel_time.metric("Latency", f"{latency_ms} ms")
                    tel_tokens.metric("Tokens (In/Out)", f"{in_tokens} / {out_tokens}")
                    tel_cost.metric("Est. Query Cost", f"${cost:.5f}")
                    
                    st.success("Synthesis Complete!")
                    st.write(response.text)
                    
                    with st.expander("🔍 Evidence & Lineage Drawer"):
                        st.write("**Math Engine Output:** `src/contribution_engine.py`")
                        st.code("{ 'metric': 'Revenue', 'primary_driver': 'Volume', 'variance': -484.23 }", language="json")
                        st.write("**Extracted Log IDs:** `LOG_ID_892 (Glitch)`, `LOG_ID_893 (Competitor)`")
                        
                except Exception as e:
                    st.error(f"API Error: {e}")

# ------------------------------------------
# TAB 2: Low-Confidence / Abstention
# ------------------------------------------
with tab2:
    st.markdown("### Scenario 2: Data Void Safety Gate")
    st.warning("Anomaly Detected: Sudden 15% traffic spike in the South region. Evaluating root cause...")
    st.write("**Retrieved Logs:** `[None found]`")
    st.write("**Retrieved Campaigns:** `[None found]`")
    
    if st.button("Evaluate Anomaly (Safety Gate Test)"):
        st.error("**Status: ABSTAIN**")
        st.write("**Confidence:** Low (32%)")
        st.write("I am abstaining from a definitive recommendation because there are no operational logs or marketing data to explain this quantitative spike. Please review the following hypotheses:")
        st.markdown("""
        1. **Hypothesis 1:** An untracked regional marketing campaign was launched.
        2. **Hypothesis 2:** Viral social media traction (un-instrumented channel).
        3. **Hypothesis 3:** Bot traffic or data pipeline duplication error.
        """)
        st.info("Human Review Required: Was there an untracked regional campaign?")

# ------------------------------------------
# TAB 3: Sparse History (New SKU)
# ------------------------------------------
with tab3:
    st.markdown("### Scenario 3: Cohort Benchmarking (New Launch)")
    st.write("SKU: `Winter_Jacket_V2` | Days Active: `4`")
    st.info("Insufficient data for 30-day rolling baseline. Swapping to Category Cohort Benchmarking.")
    
    cohort_data = {
        "Day": ["Day 1", "Day 2", "Day 3", "Day 4"],
        "Winter_Jacket_V2 (Actual)": [120, 150, 130, 90],
        "Category Launch Average": [115, 140, 160, 180]
    }
    st.bar_chart(pd.DataFrame(cohort_data).set_index("Day"))
    st.write("⚠️ **Alert:** Day 4 sales fell 50% below peer launch averages. Recommending immediate visibility check.")

# ------------------------------------------
# TAB 4: Role-Based Security (RBAC)
# ------------------------------------------
with tab4:
    st.markdown("### Scenario 4: Dynamic Entitlements")
    rbac_role = st.radio("Assume Role:", ["Executive (Full Access)", "Store Analyst (Regional)", "Store Associate (Restricted)"], horizontal=True)
    
    raw_data = pd.DataFrame({
        "Order_ID": [1001, 1002, 1003],
        "Region": ["Northeast", "South", "Northeast"],
        "Revenue": [150.00, 200.00, 95.00],
        "Unit_Cost": [80.00, 110.00, 50.00],
        "Gross_Margin": ["46.6%", "45.0%", "47.3%"]
    })
    
    if rbac_role == "Store Analyst (Regional)":
        st.write("Filtered to Regional View:")
        raw_data = raw_data[raw_data["Region"] == "Northeast"]
    elif rbac_role == "Store Associate (Restricted)":
        st.write("Financial Columns Redacted:")
        raw_data["Unit_Cost"] = "REDACTED"
        raw_data["Gross_Margin"] = "REDACTED"
        
    st.dataframe(raw_data, use_container_width=True)