import streamlit as st
import pandas as pd
from ioi_engine import IOIAgent
from supabase import create_client
import json

# --- Page Config ---
st.set_page_config(page_title="IOI Agent | Internship Intelligence", layout="wide")
st.title("🏹 Internship Outreach Intelligence (IOI)")

# --- Secret Management ---
GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
agent = IOIAgent(GEMINI_KEY)

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
    col1, col2, col3 = st.columns(3)
    with col1:
        industry = st.selectbox("Industry", ["Private Equity", "Venture Capital", "Asset Management", "Big 4", "Consulting", "Startups"])
    with col2:
        location = st.text_input("Geography", "London, UK")
    with col3:
        n_leads = st.slider("Leads to find", 5, 20, 5)

    if st.button("🚀 Execute Research Grounding"):
        with st.spinner(f"Agent researching {industry} signals in {location}..."):
            leads_json = agent.search_high_signal_leads(industry, location, st.session_state.get('profile', ''))
            # Note: In production, add a JSON parser helper here
            st.markdown("### 🎯 Discovery Results")
            st.write(leads_json)
            st.info("Review the research above. Use the CRM tab to track progress.")

# TAB 2: OUTREACH QUEUE
with tabs[1]:
    st.header("✉️ Personalized Outreach Queue")
    # Fetch Leads from Supabase that are in 'DRAFTED' status
    response = supabase.table("leads").select("*").eq("status", "DRAFTED").execute()
    leads = response.data

    if not leads:
        st.info("No leads in queue. Use the Discovery tab to find targets.")
    
    for lead in leads:
        with st.expander(f"{lead['company_name']} - {lead['contact_name']} (Score: {lead['lead_score']})"):
            st.write(f"**Signal:** {lead['opportunity_signal']}")
            st.write(f"**AI Reasoning:** {lead['why']}")
            
            # Generate personalized text on the fly if not exists
            if st.button("Generate Final Drafts", key=f"gen_{lead['id']}"):
                drafts = agent.generate_outreach(lead, st.session_state.profile)
                st.text_area("Final Drafts", drafts, height=200)
                
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Approve for CRM", key=f"app_{lead['id']}"):
                        supabase.table("leads").update({"status": "APPROVED"}).eq("id", lead['id']).execute()
                        st.success("Moved to CRM Pipeline")
                with c2:
                    st.button("🔗 Open LinkedIn Search", on_click=lambda: st.write(f"Searching for {lead['contact_name']} {lead['company_name']}"))

# TAB 3: CRM PIPELINE
with tabs[2]:
    st.header("📊 Internship Pipeline")
    res = supabase.table("leads").select("*").execute()
    if res.data:
        df = pd.DataFrame(res.data)
        st.dataframe(df[['company_name', 'contact_name', 'lead_score', 'status', 'created_at']])