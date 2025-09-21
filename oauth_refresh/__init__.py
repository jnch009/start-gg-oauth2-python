import datetime
import logging
import os
import azure.functions as func
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

        KEY_VAULT_URL = "KEY_VAULT_URL"
        CLIENT_ID = "STARTGG_CLIENT_ID"
        CLIENT_SECRET = "STARTGG_CLIENT_SECRET"
        REDIRECT_URI = "STARTGG_REDIRECT_URI"

        # Get refresh token from Key Vault
        key_vault_url = os.getenv(KEY_VAULT_URL)
        client_id = os.getenv(CLIENT_ID)
        client_secret = os.getenv(CLIENT_SECRET)
        redirect_uri = os.getenv(REDIRECT_URI)
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=key_vault_url, credential=credential)

        try:
            refresh_token = client.get_secret("startgg-refresh-token")
        except:
            logging.error(f"Token refresh failed: not found")
            return

        # API call to refresh tokens
        refresh_url = "https://api.start.gg/oauth/refresh"
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scopes": "user.identity user.email",
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri
        }

        response = requests.post(refresh_url, data=payload)
        if response.status_code != 200:
            logging.error(f"Token refresh failed: {response.text}")
            return
    
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")

        # Store tokens in Key Vault
        client.set_secret("startgg-access-token", access_token)
        client.set_secret("startgg-refresh-token", refresh_token)
        logging.info("Tokens stored in Key Vault successfully")


    logging.info('Python timer trigger function successfully ran at %s', utc_timestamp)
