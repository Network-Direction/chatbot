"""
Connects to Microsoft Identity Services and authenticates an app and a user

Usage:
    Import the azureauth module in your application
    Run azureauth.client_auth() to get a client code
        This will require a user to authenticate
        Take the resulting code (in the returned URL) and put it in the 'client_code' variable
    Run azureauth.get_token() to redeem a valid code for a token
        This will return a dictionary, containing:
            token - The bearer token
            expiry - The validity time in seconds
            user - The user this token has been generated for

Authentication:
    OAuth 2.0
    Requires a user to log in and authorize permissions on their account

Restrictions:
    Requires msal module to be installed (pip install msal)
    Requires an application to be registered in Identity Services
        Needs an App ID, Tenant ID, and Client Secret
        Needs a Callback URL configured (localhost is ok)

To Do:
    Enable token refresh
    Handle errors (eg, token fails due to invalid client code)

Author:
    Luke Robertson - October 2022
"""


import webbrowser
from msal import ConfidentialClientApplication



# Application info and required permissions
APPLICATION_ID = '8aaa79ec-e3c1-4ce6-ab9e-59d5ec2b0be9'
CLIENT_SECRET = 'ALY8Q~5C7VDtFSXj4AkoQD6niPpqsFuO-o-UmcKs'
TENANT = 'daa42918-f839-4b9d-8a49-4b2754de3590'
SCOPES = ['ChatMessage.Send', 'Chat.ReadWrite', 'Chat.ReadBasic', 'Chat.Read']

# The login URL for client authentication
login_url = 'https://login.microsoftonline.com/' + TENANT



# This generates the URL that user would use to authenticate and authorize the app based on the requested permissions
# We use the webbrowser module to pop up a request for the user
def client_auth ():
    request_url = app.get_authorization_request_url(SCOPES)
    webbrowser.open(request_url, new=True)



# This gets a token based on a previously retrieved client code
# Return a dictionary with the token, expiry, and authenticated user
def get_token (client_code):
    token_info = {}
    
    access_token = app.acquire_token_by_authorization_code (
        code = client_code,
        scopes = SCOPES
    )

    token_info['token'] = access_token['access_token']
    token_info['expiry'] = access_token['expires_in']
    token_info['user'] = access_token['id_token_claims']['name']

    return token_info



# Creating an application instance
app = ConfidentialClientApplication (
    client_id = APPLICATION_ID,
    client_credential = CLIENT_SECRET,
    authority = login_url
)

