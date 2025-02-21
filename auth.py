import os
import base64
import hashlib
import secrets
from dotenv import load_dotenv
from requests_oauthlib import OAuth2Session

load_dotenv()

class EtsyAuth:
    def __init__(self):
        self.client_id = os.getenv('ETSY_CLIENT_ID')
        self.client_secret = os.getenv('ETSY_CLIENT_SECRET')
        self.redirect_uri = 'http://localhost:8080/callback'
        self.scopes = ['transactions_r']
        self.token_path = '.etsy_token'
        self.code_verifier = secrets.token_urlsafe(64)
        self.code_challenge = self._generate_code_challenge()

    def _generate_code_challenge(self):
        hashed = hashlib.sha256(self.code_verifier.encode()).digest()
        return base64.urlsafe_b64encode(hashed).decode().rstrip('=')

    def get_auth_url(self):
        oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scopes
        )
        return oauth.authorization_url(
            'https://www.etsy.com/oauth/connect',
            code_challenge=self.code_challenge,
            code_challenge_method='S256'
        )[0]

    def fetch_token(self, redirect_response):
        oauth = OAuth2Session(
            self.client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scopes
        )
        token = oauth.fetch_token(
            'https://api.etsy.com/v3/public/oauth/token',
            authorization_response=redirect_response,
            code_verifier=self.code_verifier,
            client_secret=self.client_secret
        )
        return oauth