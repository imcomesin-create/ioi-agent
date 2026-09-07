import streamlit as st
import pandas as pd
from ioi_engine import IOIAgent
from supabase import create_client
import json

# --- Page Config ---
st.set_page_config(page_title="IOI Agent | Internship Intelligence", layout="wide")
st.title("🏹 Internship Outreach Intelligence (IOI)")

# --- Secret Management ---
try:
    GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
    SUPABASE_URL = st.secrets["SUPABASE_URL"]
    SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    agent = IOIAgent(GEMINI_KEY)
except Exception as e:
    st.error(f"Configuration Error: Please check your Streamlit Secrets. Error details: {e}")
    st.stop()

# --- Sidebar: Profile Management ---
with st.sidebar:
    st.header("👤 Candidate Profile")
    cv_file = st.file_uploader("Upload CV (PDF)", type="pdf")
    if cv_file:
        if st.button("AI Parse CV"):
            with st.spinner("Extracting Positioning..."):
                profile_data = agent.parse_cv(cv_file)
                st.session_state.profile = profile_data
                st.success("Profile Structured!")
    
    if 'profile' in st.session_state:
        st.expander("Current AI Positioning").write(st.session_state.profile)

# --- Main Tabs ---
tabs = st.tabs(["🔍 Lead Discovery", "📝 Outreach Queue", "📊 CRM Pipeline"])

# TAB 1: DISCOVERY
with tabs[0]:
    col1, col2 = st.columns(2)
    with col1:
        industry = st.selectbox("Industry", ["Private Equity", "Venture Capital", "Asset Management", "Big 4", "Consulting", "Startups"])
    with col2:
        location = st.text_input("Geography", "London, UK")

    if st.button("🚀 Execute Research Grounding"):
        with st.spinner(f"Agent researching {industry} signals in {location}..."):
            leads_json = agent.search_high_signal_leads(industry, location, st.session_state.get('profile', ''))
            st.markdown("### 🎯 Discovery Results")
            st.write(leads_json)
            st.info("Copy the firm details you like and add them to your CRM.")

# TAB 3: CRM PIPELINE
with tabs[2]:
    st.header("📊 Internship Pipeline")
    try:
        res = supabase.table("leads").select("*").execute()
        if res.data:
            df = pd.DataFrame(res.data)
            st.dataframe(df)
        else:
            st.info("CRM is currently empty.")
    except Exception as e:
        st.error("Could not connect to CRM database. Did you run the SQL in Supabase?")
