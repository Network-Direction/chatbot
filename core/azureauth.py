"""
Connects to Microsoft Identity Services and authenticates an app and a user

Usage:
    Import the azureauth module in your application
    Run azureauth.client_auth() to get a client code
        This will require a user to authenticate
        Take the resulting code (in the returned URL)
            and put it in the 'client_code' variable
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
    Move App ID, Secret, Tenant to config file
        Not sure how to do this with the app scope yet
    Retry token refresh if it fails

Author:
    Luke Robertson - October 2022
"""


import webbrowser
from msal import ConfidentialClientApplication
import threading


# Application info and required permissions
APPLICATION_ID = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
CLIENT_SECRET = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
TENANT = 'xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx'
SCOPES = ['ChatMessage.Send', 'Chat.ReadWrite', 'Chat.ReadBasic', 'Chat.Read']

# The login URL for client authentication
login_url = 'https://login.microsoftonline.com/' + TENANT


# This generates the URL that user would use to authenticate and
# authorize the app based on the requested permissions
# We use the webbrowser module to pop up a request for the user
def client_auth():
    '''Generate the URL that a user would use to authenticate
    Opens a webbrowser to get them to accept'''
    request_url = app.get_authorization_request_url(SCOPES)
    webbrowser.open(request_url, new=True)


# This gets a token based on a previously retrieved client code
# Return a dictionary with the token, expiry, and authenticated user
def get_token(client_code):
    '''Take the client code, and convert it to a token'''
    # Get the access token
    access_token = app.acquire_token_by_authorization_code(
        code=client_code,
        scopes=SCOPES
    )

    save_token(access_token)
    schedule_refresh(access_token['expires_in'], access_token['refresh_token'])


# Refresh the token to Graph API
def refresh_token(token):
    '''Takes a token and refreshes it'''
    # Using the MSAL library
    access_token = app.acquire_token_by_refresh_token(
        refresh_token=token,
        scopes=SCOPES
    )

    if 'error' in access_token:
        print('An error occurred while trying to refresh the token')
        print(access_token['error_description'])

    else:
        print('Graph API token refresh successful')
        save_token(access_token)
        schedule_refresh(access_token['expires_in'],
                         access_token['refresh_token'])


# Save the token to a file
def save_token(access_token):
    '''Saves the given access token to token.txt'''
    # Change single quotes to double quotes (valid JSON)
    temp = str(access_token).replace("'", "\"")

    # Write the token information to a file (overwrite previous contents)
    f = open("token.txt", "w")
    f.write(temp)
    f.close()


# Schedule a token refresh, 5 minutes before the current one expires
def schedule_refresh(expiry, token):
    '''Schedules a refresh of the token
    takes the expiry time in seconds, and the refresh token'''
    print('starting token refresh thread')
    start_time = threading.Timer((expiry - 300), refresh_token, [token])
    start_time.start()


# Creating an application instance
app = ConfidentialClientApplication(
    client_id=APPLICATION_ID,
    client_credential=CLIENT_SECRET,
    authority=login_url
)
