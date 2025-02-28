import sys
from threading import Thread
from urllib.parse import parse_qs, urlparse
import os
import base64
import hashlib
import secrets

from flask import Flask, request, redirect, session, url_for
import requests
from dotenv import load_dotenv, set_key

load_dotenv()  # Load .env variables

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "fallback_secret")

# Read Etsy credentials/scopes from environment
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")  # Might not be used with PKCE
SCOPES = os.getenv("SCOPES", "transactions_r")
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:5000/callback")

ENV_FILE = ".env"

cert_dir = os.path.join(os.path.dirname(__file__), 'cert')
ssl_context = (
    os.path.join(cert_dir, 'cert.pem'),
    os.path.join(cert_dir, 'key.pem')
)

# ---------------------------------------------------------
# Helpers: PKCE code_verifier, code_challenge generation & key cleaner
# ---------------------------------------------------------
def generate_code_verifier(length=64):
    """
    Generate a random code_verifier string, per RFC 7636,
    which must be between 43 and 128 chars of [A-Za-z0-9._~-].
    """
    # 32 bytes of randomness => 43-char URL-safe base64
    code = secrets.token_urlsafe(length)
    return code[:128]  # ensure max length 128 if needed

def generate_code_challenge(code_verifier):
    """
    SHA256 of code_verifier, base64-url-encoded (no padding).
    """
    code_hash = hashlib.sha256(code_verifier.encode("ascii")).digest()
    code_challenge = base64.urlsafe_b64encode(code_hash).decode("ascii")
    return code_challenge.rstrip("=")

def save_token(key, value):
    # Remove existing quotes and whitespace
    cleaned_value = value.strip().strip('"')  
    # Save without quotes
    set_key(ENV_FILE, key, cleaned_value, quote_mode='never')

# ---------------------------------------------------------
# Step 1: Start Auth - Redirect user to Etsy with PKCE
# ---------------------------------------------------------
@app.route("/start_auth")
def start_auth():
    # Generate a code_verifier (store in session so we can use it in callback)
    code_verifier = generate_code_verifier()
    session["code_verifier"] = code_verifier

    # Generate code_challenge
    code_challenge = generate_code_challenge(code_verifier)
    session["code_challenge"] = code_challenge

    # Generate a random state for CSRF protection
    state = secrets.token_urlsafe(16)
    session["oauth_state"] = state

    # Build the Etsy OAuth URL
    etsy_oauth_url = (
        "https://www.etsy.com/oauth/connect?"
        f"response_type=code"
        f"&client_id={CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        f"&scope={SCOPES.replace(' ', '%20')}"
        f"&state={state}"
        f"&code_challenge={code_challenge}"
        f"&code_challenge_method=S256"
    )

    return redirect(etsy_oauth_url)

# ---------------------------------------------------------
# Step 2: OAuth Callback - Exchange code for Access/Refresh Token
# ---------------------------------------------------------
@app.route("/callback")
def callback():
    # Etsy redirects back with ?code=xxx&state=yyy
    auth_code = request.args.get("code")
    returned_state = request.args.get("state")

    # Verify state
    if not auth_code or not returned_state:
        return "Missing code or state.", 400

    if returned_state != session.get("oauth_state"):
        return "Invalid state parameter (possible CSRF).", 400

    # Retrieve the code_verifier we stored in session
    code_verifier = session.get("code_verifier")
    if not code_verifier:
        return "No code_verifier found in session. Restart flow.", 400

    # Exchange auth_code for access_token
    url = "https://api.etsy.com/v3/public/oauth/token"

    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "code": auth_code,
        "code_verifier": code_verifier,
    }

    headers = {
        "x-api-key": CLIENT_ID,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # Note: Etsy docs typically do NOT require Basic Auth with PKCE,
    # but if needed, you could do auth=(CLIENT_ID, CLIENT_SECRET).
    response = requests.post(url, data=payload, headers=headers)

    if response.status_code != 200:
        return f"Token exchange failed: {response.status_code} {response.text}", 400

    token_data = response.json()
    # Example response:
    # {
    #   "access_token": "1234..."
    #   "token_type": "Bearer",
    #   "expires_in": 3600,
    #   "refresh_token": "1234...",
    #   ...
    # }

    # Extract & save in .env
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    if not access_token:
        return f"Invalid token response: {token_data}", 400

    save_token("ACCESS_TOKEN", access_token)
    if refresh_token:
        save_token("REFRESH_TOKEN", refresh_token)

    return "OAuth flow complete! Access token (and refresh token) saved to .env."

# ---------------------------------------------------------
# Refresh token endpoint
# ---------------------------------------------------------
@app.route("/refresh_token")
def refresh_token():
    # Read current refresh token from .env
    current_refresh = os.getenv("REFRESH_TOKEN")
    if not current_refresh:
        return "No REFRESH_TOKEN in .env. You must authorize first.", 400

    url = "https://api.etsy.com/v3/public/oauth/token"

    payload = {
        "grant_type": "refresh_token",
        "client_id": CLIENT_ID,
        "refresh_token": current_refresh
    }

    headers = {
        "x-api-key": CLIENT_ID,
        "Content-Type": "application/x-www-form-urlencoded"
    }

    resp = requests.post(url, data=payload, headers=headers)
    if resp.status_code != 200:
        return f"Refresh failed: {resp.status_code} {resp.text}", 400

    data = resp.json()
    new_access_token = data.get("access_token")
    new_refresh_token = data.get("refresh_token")

    if not new_access_token:
        return f"Invalid refresh response: {data}", 400

    # Persist new tokens in .env
    save_token("ACCESS_TOKEN", new_access_token)
    if new_refresh_token:
        save_token("REFRESH_TOKEN", new_refresh_token)
    else:
        save_token("REFRESH_TOKEN", "")  # Clear if empty

    return "Token refreshed and saved in .env."

# ---------------------------------------------------------
# Quick test route: shows your current .env tokens
# ---------------------------------------------------------
@app.route("/show_tokens")
def show_tokens():
    return {
        "ACCESS_TOKEN": os.getenv("ACCESS_TOKEN"),
        "REFRESH_TOKEN": os.getenv("REFRESH_TOKEN"),
    }

# Add this class at the bottom before the __main__ block
class EtsyAuthManager:
    @staticmethod
    def get_valid_token():
        """
        Returns valid access token, refreshes if needed
        Starts OAuth flow if no valid tokens exist
        """
        access_token = os.getenv("ACCESS_TOKEN", "").strip('"')
        refresh_token = os.getenv("REFRESH_TOKEN", "").strip('"')

        if not access_token:
            EtsyAuthManager._full_oauth_flow()
            return os.getenv("ACCESS_TOKEN").strip('"')

        try:
            # Simple token validation by making a test request
            test_url = f"https://api.etsy.com/v3/application/shops/{os.getenv('SHOP_ID')}/receipts?limit=1"
            response = requests.get(
                test_url,
                headers={
                    "x-api-key": os.getenv("CLIENT_ID"),
                    "Authorization": f"Bearer {access_token}"
                }
            )
            response.raise_for_status()
            return access_token
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                return EtsyAuthManager._refresh_token_flow()
            raise

    @staticmethod
    def _refresh_token_flow():
        """Handle token refresh via a real Flask test client request."""
        current_refresh = os.getenv("REFRESH_TOKEN", "").strip('"')
        if not current_refresh:
            # If we have no refresh token, do the full flow
            return EtsyAuthManager._full_oauth_flow()
        
        try:
            with app.test_client() as c:
                # Make a GET request to /refresh_token
                resp = c.get("/refresh_token")
                
                # If refresh fails, /refresh_token route will return 400 or some non-200 code
                if resp.status_code != 200:
                    raise ValueError(
                        f"Refresh failed with status {resp.status_code}: {resp.data.decode()}"
                    )
                
            # After refresh, .env has the new tokens. Reload them in-memory:
            load_dotenv()
            
            # Return the new access token
            return os.getenv("ACCESS_TOKEN", "").strip('"')
        
        except Exception as e:
            print(f"Error refreshing token: {e}")
            # If refresh fails for any reason, fall back to full OAuth flow
            return EtsyAuthManager._full_oauth_flow()


    @staticmethod
    def _full_oauth_flow():
        """Run full OAuth flow"""
        print("Starting OAuth flow...")
        flask_thread = Thread(target=app.run, kwargs={'ssl_context': ssl_context})
        flask_thread.start()
        
        # Open auth URL in browser
        import webbrowser
        webbrowser.open("https://localhost:5000/start_auth")
        
        flask_thread.join()
        return os.getenv("ACCESS_TOKEN").strip('"')

# ---------------------------------------------------------
# Run the Flask app (for local testing)
# ---------------------------------------------------------
if __name__ == "__main__":
    # Get absolute path to cert files
    cert_dir = os.path.join(os.path.dirname(__file__), 'cert')
    ssl_context = (
        os.path.join(cert_dir, 'cert.pem'),
        os.path.join(cert_dir, 'key.pem')
    )
    
    app.run(
        host='localhost',
        port=5000,
        debug=True,
        ssl_context=ssl_context
    )