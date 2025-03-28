"""
issue_flow.py — Agentic AI-first SmartTicket Lifecycle
Fully integrated version for Tenant, Landlord, Contractor flows
"""

import streamlit as st
from datetime import datetime
from uuid import uuid4
from gpt_analysis import analyze_ticket_with_gpt

# ───────────────────────────────────────────────────────────────
# Memory-safe SmartTicket store (can replace with DB later)
# ───────────────────────────────────────────────────────────────
if "smart_tickets" not in st.session_state:
    st.session_state.smart_tickets = []

# ───────────────────────────────────────────────────────────────
# Universal SmartTicket creation function with AI analysis
# ───────────────────────────────────────────────────────────────
def create_smart_ticket(user_email, raw_description, media_files):
    timestamp = datetime.now().isoformat()
    ticket_id = str(uuid4())[:8]

    # Run GPT-based analysis for classification, urgency, tone, etc.
    ai_data = analyze_ticket_with_gpt(raw_description)

    ticket = {
        "ticket_id": ticket_id,
        "created_by": user_email,
        "raw_description": raw_description,
        "gpt_summary": ai_data["summary"],
        "issue_type": ai_data["issue_type"],
        "urgency": ai_data["urgency"],
        "tone": ai_data["tone"],
        "recommended_action": ai_data.get("recommendation", "Review by landlord"),
        "media": media_files,
        "status": "Submitted",        # can be Submitted, In Progress, Resolved, Closed, Reopened, etc.
        "submitted_at": timestamp,
        "assigned_to": "landlord@example.com",  # default assignment for demo
        "contractor_email": "",
        "task_id": "",
        "resolved": False,
        "closed": False,
        "reopened": False,
        "updates": [
            {"event": "SmartTicket submitted via AI", "timestamp": timestamp},
            {"event": f"AI Summary: {ai_data['summary']}", "timestamp": timestamp}
        ]
    }
    return ticket

# ───────────────────────────────────────────────────────────────
# Main entry point: Decide which agent UI to render
# ───────────────────────────────────────────────────────────────
def render_issue_flow(user_email):
    """
    Renders the entire lifecycle based on role:
      - Tenant (AI-based creation, reviews own tickets)
      - Landlord (Triages, assigns contractor, requests more info)
      - Contractor (Marks tickets as resolved)
    """
    role = "tenant"
    if user_email.endswith("@landlord.com"):
        role = "landlord"
    elif user_email.endswith("@contractor.com"):
        role = "contractor"

    st.info(f"🔐 Role detected: {role.title()}")

    if role == "tenant":
        render_tenant_agent_ui(user_email)
    elif role == "landlord":
        render_landlord_agent_ui(user_email)
    elif role == "contractor":
        render_contractor_agent_ui(user_email)

# ───────────────────────────────────────────────────────────────
# 1. Tenant Agent UI — AI-based issue submission + quick listing
# ───────────────────────────────────────────────────────────────
def render_tenant_agent_ui(user_email):
    st.header("Tenant Portal (AI-Assisted)")
    st.write(
        "Describe your maintenance issue in plain language below. "
        "Our system will analyze it with AI to classify and prioritize."
    )

    with st.form("tenant_form"):
        raw_input = st.text_area("Describe the issue or problem here", height=150)
        media_files = st.file_uploader("Attach images/videos (optional)", accept_multiple_files=True)
        submit = st.form_submit_button("Submit to AI")

        if submit and raw_input.strip():
            new_ticket = create_smart_ticket(user_email, raw_input, media_files)
            st.session_state.smart_tickets.append(new_ticket)

            st.success(f"SmartTicket #{new_ticket['ticket_id']} submitted!")
            st.write("**AI Summary:**", new_ticket["gpt_summary"])
            st.write("**Issue Type:**", new_ticket["issue_type"])
            st.write("**Urgency:**", new_ticket["urgency"])
            st.write("**Tone:**", new_ticket["tone"])
            st.write("**Recommended Action:**", new_ticket["recommended_action"])
            st.balloons()

    st.markdown("---")

    # Show existing tickets for tenant
    tenant_tickets = [t for t in st.session_state.smart_tickets if t["created_by"] == user_email]
    if tenant_tickets:
        st.subheader("Your AI-Powered SmartTickets")
        for ticket in tenant_tickets:
            with st.expander(f"#{ticket['ticket_id']} — {ticket['issue_type']} ({ticket['status']})"):
                show_ticket_details(ticket)

                # If ticket is resolved but not closed, let tenant confirm or reopen
                if ticket["status"] == "Resolved" and not ticket["closed"]:
                    with st.form(f"verify_res_{ticket['ticket_id']}"):
                        satisfaction = st.radio("Is your issue fully resolved?", ["Yes", "No"])
                        confirm_btn = st.form_submit_button("Confirm")
                        if confirm_btn:
                            if satisfaction == "Yes":
                                ticket["status"] = "Closed"
                                ticket["closed"] = True
                                add_ticket_update(ticket, "Tenant confirmed issue resolved")
                                st.success("Ticket is now closed. Thank you!")
                            else:
                                ticket["status"] = "Reopened"
                                ticket["reopened"] = True
                                add_ticket_update(ticket, "Tenant reopened ticket")
                                st.warning("Ticket reopened. Landlord will be notified.")

# ───────────────────────────────────────────────────────────────
# 2. Landlord Agent UI — Triage, assign to contractor, request info
# ───────────────────────────────────────────────────────────────
def render_landlord_agent_ui(user_email):
    st.header("Landlord Portal (AI-Orchestrated Triage)")
    st.write("View all submitted or reopened tickets, assign contractors, or request tenant info.")

    # Landlord sees tickets that are: 
    #   1) assigned to them, or 
    #   2) status in ['Submitted', 'Reopened'] if no assigned_to or assigned_to=landlord
    #   (This is flexible; adapt as needed.)
    landlord_tickets = [
        t for t in st.session_state.smart_tickets
        if (t["assigned_to"] == user_email or t["status"] in ["Submitted", "Reopened"]) and not t["closed"]
    ]
    if not landlord_tickets:
        st.info("No new or reopened tickets found.")
        return

    for ticket in landlord_tickets:
        highlight_urgent = (ticket["urgency"] == "High" or ticket["tone"] == "Frustrated")
        prefix = "🚨" if highlight_urgent else "📩"
        with st.expander(f"{prefix} #{ticket['ticket_id']} from {ticket['created_by']}"):
            show_ticket_details(ticket)

            # If ticket is Submitted or Reopened, landlord can assign a contractor or ask for tenant info
            if ticket["status"] in ["Submitted", "Reopened"]:
                st.subheader("Assign Contractor or Request Info")
                with st.form(f"landlord_{ticket['ticket_id']}"):
                    contractor_email = st.text_input("Contractor Email", value=ticket["contractor_email"])
                    task_id = st.text_input("Task ID (optional)", value=ticket["task_id"])
                    action_choice = st.radio("Action", ["Assign to Contractor", "Request More Info from Tenant"])
                    do_action = st.form_submit_button("Submit Action")

                    if do_action:
                        if action_choice == "Assign to Contractor":
                            ticket["contractor_email"] = contractor_email
                            ticket["task_id"] = task_id
                            ticket["assigned_to"] = user_email  # landlord stays as overall assigned
                            ticket["status"] = "In Progress"
                            add_ticket_update(ticket, f"Landlord assigned to contractor {contractor_email}")
                            st.success("Contractor assigned. Ticket moved to In Progress.")
                        else:
                            # Request info means status goes to "Awaiting Tenant Info" (or remain submitted if you prefer).
                            ticket["status"] = "Awaiting Tenant Info"
                            add_ticket_update(ticket, "Landlord requested more info from tenant")
                            st.info("Tenant is prompted for more info now.")

            elif ticket["status"] == "Awaiting Tenant Info":
                st.info("Waiting for tenant's additional details. No further action yet.")

            elif ticket["status"] == "In Progress":
                st.info("Contractor assigned and in progress. Check again once contractor resolves.")

            elif ticket["status"] == "Resolved":
                st.info("Waiting for tenant to confirm resolution.")

# ───────────────────────────────────────────────────────────────
# 3. Contractor Agent UI — sees assigned tickets, can mark resolved
# ───────────────────────────────────────────────────────────────
def render_contractor_agent_ui(user_email):
    st.header("Contractor Portal")
    st.write("View assigned tasks and mark them resolved.")

    assigned_tickets = [
        t for t in st.session_state.smart_tickets
        if t["contractor_email"] == user_email and not t["closed"]
    ]
    if not assigned_tickets:
        st.info("No tickets assigned to you at this time.")
        return

    for ticket in assigned_tickets:
        with st.expander(f"#{ticket['ticket_id']} - {ticket['issue_type']} ({ticket['status']})"):
            show_ticket_details(ticket)

            if ticket["status"] == "In Progress":
                with st.form(f"resolve_form_{ticket['ticket_id']}"):
                    st.write("Confirm you have completed the repair or maintenance.")
                    done = st.form_submit_button("Mark as Resolved")
                    if done:
                        ticket["status"] = "Resolved"
                        ticket["resolved"] = True
                        add_ticket_update(ticket, "Contractor marked issue resolved")
                        st.success("Ticket marked as resolved. Tenant will verify or reopen.")
            else:
                st.info("Ticket not in progress. No contractor action at this stage.")

# ───────────────────────────────────────────────────────────────
# Reusable method: show ticket details in an expander
# ───────────────────────────────────────────────────────────────
def show_ticket_details(ticket):
    st.write(f"**Submitted:** {ticket['submitted_at']}")
    st.write(f"**AI Summary:** {ticket['gpt_summary']}")
    st.write(f"**Issue Type:** {ticket['issue_type']}")
    st.write(f"**Urgency:** {ticket['urgency']}")
    st.write(f"**Tone:** {ticket['tone']}")
    st.write(f"**Status:** {ticket['status']}")
    if ticket['media']:
        for file_obj in ticket['media']:
            if file_obj.type.startswith('image'):
                st.image(file_obj)
            elif file_obj.type.startswith('video'):
                st.video(file_obj)

    st.write("**Updates:**")
    for update in ticket["updates"]:
        st.markdown(f"- {update['event']} at {update['timestamp']}")

# ───────────────────────────────────────────────────────────────
# Reusable helper: add new event to ticket updates
# ───────────────────────────────────────────────────────────────
def add_ticket_update(ticket, event_description):
    timestamp = datetime.now().isoformat()
    ticket["updates"].append({"event": event_description, "timestamp": timestamp})
