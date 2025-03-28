import streamlit as st
import requests
import json
import urllib.parse
from jose import jwt

# ==== CONFIGURATION (Replace with your values) ====
COGNITO_DOMAIN = "YOUR_COGNITO_DOMAIN"  # e.g., your-app.auth.us-west-2.amazoncognito.com
CLIENT_ID = "YOUR_COGNITO_CLIENT_ID"
REDIRECT_URI = "http://localhost:8501/"  # Or deployed Streamlit URI
USER_POOL_ID = "YOUR_USER_POOL_ID"
REGION = "YOUR_AWS_REGION"  # e.g., us-west-2

# ========== URL Builders ==========

def build_login_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "token",
        "scope": "openid profile email",
        "redirect_uri": REDIRECT_URI
    }
    return f"https://{COGNITO_DOMAIN}/login?{urllib.parse.urlencode(params)}"

def decode_token(token):
    jwks_url = f"https://cognito-idp.{REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()
    return jwt.decode(token, jwks, algorithms=["RS256"], audience=CLIENT_ID)

# ========== Authentication ==========

def authenticate_user():
    query_params = st.experimental_get_query_params()
    fragment = st.experimental_get_query_params().get("fragment")

    if "id_token" not in st.session_state:
        st.markdown("### Login Required")
        login_url = build_login_url()
        st.markdown(f"[Login with Google via Cognito]({login_url})")
        st.stop()

    # Already authenticated
    user_info = decode_token(st.session_state["id_token"])
    return user_info
