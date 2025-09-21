import logging
import os
import requests
import json
import azure.functions as func
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("OAuth callback triggered")

    # Get authorization code from query string
    code = req.params.get("code")
    if not code:
        return func.HttpResponse("Missing authorization code", status_code=400)
    try: 
        with open("oauth_callback_env.json") as f:
            config = json.load(f)
    except:
        logging.warning("Could not find local env file")

    KEY_VAULT_URL = "KEY_VAULT_URL"
    CLIENT_ID = "STARTGG_CLIENT_ID"
    CLIENT_SECRET = "STARTGG_CLIENT_SECRET"
    REDIRECT_URI = "STARTGG_REDIRECT_URI"

    # Environment variables
    key_vault_url = os.getenv(KEY_VAULT_URL) or config.get(KEY_VAULT_URL)
    client_id = os.getenv(CLIENT_ID) or config.get(CLIENT_ID)
    client_secret = os.getenv(CLIENT_SECRET) or config.get(CLIENT_SECRET)
    redirect_uri = os.getenv(REDIRECT_URI) or config.get(REDIRECT_URI)

    # Exchange authorization code for tokens
    token_url = "https://api.start.gg/oauth/access_token"
    payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    }

    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        logging.error(f"Token exchange failed: {response.text}")
        return func.HttpResponse("Token exchange failed", status_code=500)

    tokens = response.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")

    # Store tokens in Key Vault
    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_url, credential=credential)
    client.set_secret("startgg-access-token", access_token)
    client.set_secret("startgg-refresh-token", refresh_token)

    logging.info("Tokens stored in Key Vault successfully")

    return func.HttpResponse("OAuth tokens successfully stored.", status_code=200)
