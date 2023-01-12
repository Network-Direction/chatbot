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
    Only one public/private key-pair supported for encrypted chats

To Do:
    None


Author:
    Luke Robertson - January 2023
"""


import requests
from config import GRAPH, GLOBAL
import json
from datetime import datetime, timedelta
import termcolor
import threading


public_key = ''
private_key = ''


# Check teams token is available
def check_token():
    '''
    Checks there is a token available, and returns it
    If it's not available, return an empty string
    '''
    with open('token.txt') as f:
        data = str(f.read())

    full_token = json.loads(str(data))

    # Check that we have a token
    if full_token == '':
        print(termcolor.colored(
            'alert received, but we have no teams token',
            "red"))

    return full_token


# Get a new expiry time (now + 1 hour)
# Used for subscriptions
def get_expiry():
    time = str(datetime.utcnow() + timedelta(hours=1))
    return time.replace(" ", "T") + 'Z'


# Send a messages to a teams chat
def send_chat(message):
    '''
    takes a message, and sends it to a teams chat
    requires that a bearer token has already been allocated,
    and saved in token.txt
    '''

    # Check if this is during a 'quiet time'
    # If it is, we won't send this to Teams
    wake = datetime.strptime(GLOBAL['wake_time'], '%H:%M:%S')
    sleep = datetime.strptime(GLOBAL['sleep_time'], '%H:%M:%S')
    if not (datetime.now().time() > wake.time() and
            datetime.now().time() < sleep.time()):
        print(termcolor.colored(
            "Quiet time: Suppressing message", "blue"
        ))
        value = {'id': '0'}
        return value

    # Make sure authentication is complete first
    full_token = check_token()

    # Setup standard REST details for the API call
    headers = {
        "Content-Type": "application/json",
        "Authorization": full_token['access_token']
    }
    endpoint = GRAPH['base_url'] + 'chats'

    body = {
        "body": {
            "contentType": "html",
            "content": message
        }
    }

    # API Call
    response = requests.post(endpoint + '/' + GRAPH['chat_id']
                             + '/messages', json=body, headers=headers)
    response.raise_for_status()
    chat_id = json.loads(response.content)

    match response.status_code:
        case 200 | 201:
            return chat_id
        case _:
            return False


# Subscribe to the group chat, so we can see when people send messages
def subscribe():
    '''
    Subscribes to a Teams group for change notifications
    Does not take any parameters
    '''

    # Schedule a refresh of the subscription
    schedule_refresh()

    # Make sure authentication is complete first
    full_token = check_token()

    # Read public and private keys
    global public_key, private_key
    with open('core\\public.pem', 'r') as file:
        public_key = file.read()
    with open('core\\private.pem', 'r') as file:
        private_key = file.read()

    # Strip back to raw keys
    public_key = public_key.replace("-----BEGIN CERTIFICATE-----\n", "")
    public_key = public_key.replace("\n-----END CERTIFICATE-----\n", "")
    private_key = private_key.replace("-----BEGIN PRIVATE KEY-----\n", "")
    private_key = private_key.replace("\n-----END PRIVATE KEY-----\n", "")

    # Setup standard REST details for the API call
    headers = {
        "Content-Type": "application/json",
        "Authorization": full_token['access_token']
    }
    endpoint = GRAPH['base_url']
    id = GRAPH['chat_id']

    # Check that we don't already have a subscription
    if check_sub(f'/chats/{id}/messages'):
        return

    body = {
        'resource': f'/chats/{id}/messages',
        'notificationUrl': GRAPH['chat_url'],
        'changeType': 'created',
        'expirationDateTime': get_expiry(),
        'encryptionCertificate': public_key,
        'encryptionCertificateId': GRAPH['key_id'],
        'includeResourceData': 'true'
    }

    # API Call
    response = requests.post(
        endpoint + '/subscriptions', json=body, headers=headers
    )
    response.raise_for_status()

    returns = json.loads(response.content)
    if 'error' in returns:
        print(termcolor.colored(
            f"An error has occurred subscribing to the teams chat:\n \
            {returns['error']['code']}: {returns['error']['message']}",
            "red"
        ))
    else:
        print(termcolor.colored(
            f"Subscribed to Teams chat: {returns['resource']}\n \
            Expiry: {returns['expirationDateTime']}",
            "green"
        ))


# Check if a subscription to the group chat already exists
# We don't want to create extras if they're not needed
def check_sub(id):
    '''
    Checks if there is already a subscription to a Teams group
    Takes the resource ID to check
    '''
    # Make sure authentication is complete first
    full_token = check_token()

    # Setup standard REST details for the API call
    headers = {
        "Content-Type": "application/json",
        "Authorization": full_token['access_token']
    }
    endpoint = GRAPH['base_url']

    # API Call
    response = requests.get(
        endpoint + '/subscriptions', headers=headers
    )
    response.raise_for_status()

    returns = json.loads(response.content)

    # Check if we've already subscribed to this resource
    value = returns['value']
    for item in value:
        if id == item['resource']:
            print(termcolor.colored(
                "Already subscribed for change notifications",
                "yellow"
            ))

            print(termcolor.colored(
                f"Resource: {item['resource']}\n \
                    Expiry: {item['expirationDateTime']}\n \
                    ID: {item['id']}",
                "yellow"
            ))

            # Refresh the expiry time while we're here
            body = {
                'expirationDateTime': get_expiry()
            }
            response = requests.patch(
                endpoint + f"/subscriptions/{item['id']}",
                json=body,
                headers=headers
            )
            print(termcolor.colored(
                f"Resource Update: {response.json()['resource']}\n \
                    Expiry: {response.json()['expirationDateTime']}\n \
                    ID: {response.json()['id']}",
                "yellow"
            ))

            return True

    print(termcolor.colored(
        "Not subscribed yet, subscribing now...",
        "yellow"
    ))
    return False


# Schedule a refresh of the subscription
def schedule_refresh():
    '''
    Schedules a refresh of the subscription
    takes the expiry time in seconds, and the refresh token
    '''

    print(termcolor.colored('starting subscription refresh thread', "green"))
    start_time = threading.Timer(3300, subscribe)
    start_time.start()
