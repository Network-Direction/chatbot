"""
Connects to the Microsoft Graph API, and interacts with MS-Teams chats

Usage:
    import 'teamschat' as a module
    Returns the chat ID of the teams message if successful
    Returns False if unsuccessful

Authentication:
    OAuth 2.0
    Requires a valid bearer token

Restrictions:
    Requires the requests module (pip install requests)
    Requires a bearer token to be separately generated
    There is a limit to the API calls made to Graph before throttling occurs
        (https://learn.microsoft.com/en-us/graph/throttling)
    Uses the 'azureauth' custom module to attempt to
        refresh the token when necessary

To Do:
    Dynamically get the chat ID from somewhere
    Get the UserID dynamically


Author:
    Luke Robertson - October 2022
"""


import requests
from config import GRAPH
import json
from datetime import datetime
from core import smtp


def send_chat(message):
    '''
    takes a message, and sends it to a teams chat
    requires that a bearer token has already been allocated,
    and saved in token.txt
    '''

    # Make sure authentication is complete first
    with open('token.txt') as f:
        data = str(f.read())

    full_token = json.loads(str(data))

    # Check that we have a token
    if full_token == '':
        print('alert received, but we have no teams token')

    # Setup standard REST details for the API call
    time = datetime.now().strftime("%I:%M%p").lower()

    headers = {
        "Content-Type": "application/json",
        "Authorization": full_token['access_token']
            }
    endpoint = GRAPH['base_url'] + 'chats'

    body = {
        "body": {
            "contentType": "html",
            "content": f"({time}): {message}"
        }
    }

    # Attempt sending to the Graph API
    try:
        response = requests.post(endpoint + '/' + GRAPH['chat_id']
                                 + '/messages', json=body, headers=headers)
    except Exception as e:
        print('An error has occurred connecting to the Graph API')
        print('error: ', e)

    chat_id = json.loads(response.content)

    # Handle responses
    jsonResponse = response.json()
    match response.status_code:
        case 200:
            return chat_id

        case 201:
            return chat_id

        case 401:
            print('Error: Access to the Graph API (MS-Teams) \
                has not been authorized')
            print('Code: ', jsonResponse['error']['code'])
            print('Message: ', jsonResponse['error']['message'])
            smtp.send_mail("Network Assistant cannot send to teams; \
                Not Authorized\n")
            return False

        case 429:
            print('Error: There have been too many calls to the Graph API')
            print('Code: ', jsonResponse['error']['code'])
            print('Message: ', jsonResponse['error']['message'])
            print(response.headers)
            return False

        case _:
            print("Error. API Response code: ", response.status_code)
            print(jsonResponse)
            return False
