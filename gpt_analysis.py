"""
gpt_analysis.py — AI Layer for analyzing natural language descriptions
Mock version that uses simple keywords for classification
"""

def analyze_ticket_with_gpt(description):
    """
    Mocks GPT output. In production, replace with an actual OpenAI API call.
    """
    import random

    # Simple heuristic for demonstration
    keywords = {
        "leak": "Plumbing",
        "heater": "Heating/Cooling",
        "lights": "Electricity",
        "bugs": "Pest",
        "wall": "Structural",
        "noise": "Other",
        "mold": "Other",
    }

    urgency = "High" if any(x in description.lower() for x in ["urgent", "asap", "flood"]) else "Medium"
    tone = "Frustrated" if any(x in description.lower() for x in ["again", "angry", "still broken"]) else "Neutral"

    issue_type = "Other"
    for word, category in keywords.items():
        if word in description.lower():
            issue_type = category
            break

    summary = f"Likely issue: {issue_type}. The user said: '{description[:60]}...'"

    return {
        "summary": summary,
        "issue_type": issue_type,
        "urgency": urgency,
        "tone": tone,
        "recommendation": "Auto-route to landlord and flag for review"
    }
