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

To Do:
    Add try/except to API calls
    Dynamically get the chat ID from somewhere
    Get the UserID dynamically
    Figure out how to handle new lines in strings
        Teams is ignoring '\n'

Author:
    Luke Robertson - October 2022
"""


import requests

BASE_URL = 'https://graph.microsoft.com/v1.0/'
endpoint = BASE_URL + 'chats'


def send_chat(token, message):
    headers = {"Content-Type": "application/json", "Authorization": token}
    user_id = '1f53061b-8d51-49ac-9c8a-bbf1cebd5ab6'
    chat_id = '19:847516a419864851b24cb9f7e8a6426b@thread.v2'

    body = {
        "body": {
            "content": message
        }
    }

    response = requests.post(endpoint + '/' + chat_id + '/messages', json = body, headers=headers)

    print ("Response: ", response.status_code)
    jsonResponse = response.json()
    print (jsonResponse)






