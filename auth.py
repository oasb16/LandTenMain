"""
auth.py — AWS Cognito + Google SSO integration for Streamlit
Minimal example that stores id_token in st.session_state
"""

import streamlit as st
import requests
import urllib.parse
from jose import jwt

# TODO: Replace with your Cognito + Google Federation details
COGNITO_DOMAIN = "YOUR_COGNITO_DOMAIN.auth.us-west-2.amazoncognito.com"
CLIENT_ID = "YOUR_COGNITO_CLIENT_ID"
REDIRECT_URI = "http://localhost:8501"  # Adjust if deployed
USER_POOL_ID = "YOUR_USER_POOL_ID"
AWS_REGION = "us-west-2"

def authenticate_user():
    # Check if we already have an ID token
    if "id_token" not in st.session_state:
        # Try to parse the URL hash fragment if user was redirected
        parse_cognito_redirect()
    if "id_token" not in st.session_state:
        # If still no token, show login link
        login_url = build_login_url()
        st.markdown(f"### [Login with Google via Cognito]({login_url})")
        st.stop()  # Stop execution until user logs in
    return decode_id_token(st.session_state["id_token"])

def build_login_url():
    params = {
        "client_id": CLIENT_ID,
        "response_type": "token",
        "scope": "openid profile email",
        "redirect_uri": REDIRECT_URI
    }
    return f"https://{COGNITO_DOMAIN}/login?{urllib.parse.urlencode(params)}"

def parse_cognito_redirect():
    # Attempt to read the token from the hash fragment in the URL
    fragment = st.experimental_get_query_params().get("fragment")
    if fragment:
        # The fragment might contain something like 'id_token=...&access_token=...'
        token_data = parse_fragment(fragment[0])
        if "id_token" in token_data:
            st.session_state["id_token"] = token_data["id_token"]

def parse_fragment(fragment_str):
    # Parse a URL fragment into key-value pairs
    parts = fragment_str.split("&")
    data = {}
    for part in parts:
        key, val = part.split("=")
        data[key] = val
    return data

def decode_id_token(token):
    # Retrieve the public keys (JWKS) from Cognito to verify token
    jwks_url = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"
    jwks_data = requests.get(jwks_url).json()
    # Verify signature and claims
    decoded = jwt.decode(token, jwks_data, algorithms=["RS256"], audience=CLIENT_ID)
    return {
        "email": decoded.get("email"),
        "sub": decoded.get("sub"),
        "name": decoded.get("name", "")
    }
