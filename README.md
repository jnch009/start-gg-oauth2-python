Instead of renewing the PAT token every year, I decided to add an OAuth application to the app to ensure the access token is rotated seamlessly. It prevents the need for remembering to update the PAT token every year. Current the implementation is done using Single user OAuth, but I will consider updating it to multi user OAuth in the future as a fun project.

Single User OAuth functionality:

1. Authorize the Start.GG OAuth application to access my account
2. The redirect URL at `/api/oauth_callback` gets hit which uses the authorization code to make the API request to retrieve the access_token/refresh_token
3. Stores that in KeyVault
4. The optional `/api/oauth_refresh` API runs on a timer trigger every 50 minutes to refresh the access token ensuring seamless rotation.

`oauth_callback` and `oauth_refresh` are run through an Azure Function App.
