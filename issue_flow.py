"""
issue_flow.py — Handles Tenant > Landlord > Contractor ticket lifecycle
Part 1: Ticket Creation & State Initialization
"""

import streamlit as st
from datetime import datetime
import uuid

# ───────────────────────────────────────────────────────────────
# Session-based in-memory issue store (replace with DB later)
# ───────────────────────────────────────────────────────────────
if "tickets" not in st.session_state:
    st.session_state.tickets = []  # Each ticket is a dict

# ───────────────────────────────────────────────────────────────
# Tenant Ticket Submission UI
# ───────────────────────────────────────────────────────────────
def render_issue_flow(user_email):
    st.subheader("📬 Report an Issue")

    with st.form("new_ticket_form"):
        issue_type = st.selectbox("Type of Issue", [
            "Plumbing", "Electricity", "Heating/Cooling",
            "Pest", "Structural", "Other"
        ])

        issue_description = st.text_area("Describe the problem")

        uploaded_files = st.file_uploader("Upload Images or Videos", accept_multiple_files=True)

        submit = st.form_submit_button("Submit Ticket")

        if submit:
            ticket_id = str(uuid.uuid4())[:8]
            timestamp = datetime.now().isoformat()

            new_ticket = {
                "ticket_id": ticket_id,
                "created_by": user_email,
                "status": "Submitted",
                "issue_type": issue_type,
                "description": issue_description,
                "media": uploaded_files,
                "submitted_at": timestamp,
                "updates": [
                    {"event": "Ticket submitted", "timestamp": timestamp}
                ]
            }

            st.session_state.tickets.append(new_ticket)
            st.success(f"Ticket #{ticket_id} submitted successfully!")
            st.balloons()

    st.markdown("---")
    render_ticket_list(user_email)

# ───────────────────────────────────────────────────────────────
# Render Ticket List (For This User Only)
# ───────────────────────────────────────────────────────────────
def render_ticket_list(user_email):
    st.subheader("🧾 Your Submitted Tickets")

    user_tickets = [t for t in st.session_state.tickets if t["created_by"] == user_email]

    if not user_tickets:
        st.info("No tickets submitted yet.")
        return

    for ticket in user_tickets:
        with st.expander(f"🔧 {ticket['issue_type']} — #{ticket['ticket_id']} [{ticket['status']}]"):
            st.markdown(f"**Description:** {ticket['description']}")
            st.markdown(f"**Submitted At:** {ticket['submitted_at']}")

            if ticket.get("media"):
                for file in ticket["media"]:
                    if file.type.startswith("image"):
                        st.image(file)
                    elif file.type.startswith("video"):
                        st.video(file)

            st.markdown("**Update History:**")
            for update in ticket["updates"]:
                st.markdown(f"- {update['event']} at {update['timestamp']}")
