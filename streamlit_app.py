"""
streamlit_app.py — Entry point for the LandTena AI-First App
Ensures user is authenticated, then calls issue_flow.render_issue_flow()
"""

import streamlit as st
from auth import authenticate_user  # AWS Cognito + Google
from issue_flow import render_issue_flow

# ───────────────────────────────────────────────────────────────
# Streamlit page config
# ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LandTena 2.0 AI-Agentic",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🏠 LandTena 2.0 — AI-Agentic Tenant Issue Portal")

# ───────────────────────────────────────────────────────────────
# Authentication: retrieve or prompt for AWS Cognito login
# ───────────────────────────────────────────────────────────────
user_info = authenticate_user()  # Will handle redirect if not logged in

# We store the user’s email in st.session_state
st.session_state.user_email = user_info.get("email", "unknown@example.com")
st.markdown(f"**Welcome:** {st.session_state.user_email}")

# ───────────────────────────────────────────────────────────────
# Render the main AI-based issue flow
# ───────────────────────────────────────────────────────────────
render_issue_flow(st.session_state.user_email)

st.markdown("---")
st.caption("© 2025 LandTena — AI-First Multi-Role Maintenance System")
