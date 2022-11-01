"""
Connects to the Microsoft Graph API, and interacts with MS-Teams chats

Usage:
    import 'teamschat' as a module

Authentication:
    OAuth 2.0
    Requires a valid bearer token

Restrictions:
    Requires the requests module (pip install requests)
    Requires a bearer token to be separately generated
    There is a limit to the API calls made to Graph before throttling occurs (https://learn.microsoft.com/en-us/graph/throttling)
    Uses the 'azureauth' custom module to attempt to refresh the token when necessary

To Do:
    Dynamically get the chat ID from somewhere
    Get the UserID dynamically
    Add a timestamp to events


Author:
    Luke Robertson - October 2022
"""


import requests
from config import GRAPH
import json
from  datetime import datetime


def send_chat(message):
    '''takes a message, and sends it to a teams chat
    requires that a bearer token has already been allocated, and saved in token.txt'''
    # Make sure authentication is complete first
    with open('token.txt') as f:
        data = str(f.read())
    
    full_token = json.loads(str(data))

    # Check that we have a token
    if full_token == '':
        print ('alert received, but we have no teams token')


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
        response = requests.post(endpoint + '/' + GRAPH['chat_id'] + '/messages', json = body, headers=headers)
    except Exception as e:
        print ('An error has occurred connecting to the Graph API')
        print ('error: ', e)


    # Handle responses
    jsonResponse = response.json()
    match response.status_code:
        case 200:
            pass

        case 201:
            pass

        case 401:
            print ('Error: Access to the Graph API (MS-Teams) has not been authorized')
            print ('Code: ', jsonResponse['error']['code'])
            print ('Message: ', jsonResponse['error']['message'])

        case 429:
            print ('Error: There have been too many calls to the Graph API')
            print ('Code: ', jsonResponse['error']['code'])
            print ('Message: ', jsonResponse['error']['message'])
            print (response.headers)

        case default:
            print ("Error. API Response code: ", response.status_code)
            print (jsonResponse)






