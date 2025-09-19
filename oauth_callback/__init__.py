import logging
import os
import requests
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("OAuth2 callback triggered")

    # Get the authorization code from query parameters
    code = req.params.get("code")
    if not code:
        return func.HttpResponse(
            "Missing 'code' query parameter",
            status_code=400
        )

    # Exchange authorization code for access/refresh tokens
    token_url = "https://api.start.gg/oauth/token"
    client_id = os.getenv("STARTGG_CLIENT_ID")
    client_secret = os.getenv("STARTGG_CLIENT_SECRET")
    redirect_uri = os.getenv("STARTGG_REDIRECT_URI")

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello, {name}. This HTTP triggered function executed successfully.")
    else:
        return func.HttpResponse(
             "This HTTP triggered function executed successfully. Pass a name in the query string or in the request body for a personalized response.",
             status_code=200
        )
