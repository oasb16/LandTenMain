"""
streamlit_app.py — Main UI Entry Point for LandTena (Streamlit Version)
"""

import streamlit as st
from auth import authenticate_user
from issue_flow import render_issue_flow

# ───────────────────────────────────────────────────────────────
# APP CONFIGURATION
# ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LandTena Portal",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏠 LandTena: Tenant-Landlord Issue Tracker")

# ───────────────────────────────────────────────────────────────
# AUTHENTICATION (AWS Cognito + Google Federated Login)
# ───────────────────────────────────────────────────────────────
user_info = authenticate_user()  # Ensures valid session or halts app

# Store user session
st.session_state.user_email = user_info.get("email")
st.session_state.user_name = user_info.get("name")

st.success(f"Welcome, {st.session_state.user_name}! ✨")

# ───────────────────────────────────────────────────────────────
# MAIN APP FLOW (Tenant ↔ Landlord ↔ Contractor)
# ───────────────────────────────────────────────────────────────
render_issue_flow(user_email=st.session_state.user_email)

# ───────────────────────────────────────────────────────────────
# FOOTER
# ───────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("© 2025 LandTena | Secure Tenant-Landlord Coordination")
