"""
Provides supporting functions to the Mist webhooks
Authenticates incoming webhook messages
Parses incoming webhooks, filters, and sends to teams

Usage:
    import 'misthandler' into the application

Authentication:
    Webhooks can be sent with a secret, which authenticates the source
    No authentication required to access functions in this module

Restrictions:
    Needs access to the 'teamschat' module

To Do:
    TBA

Author:
    Luke Robertson - October 2022
"""

import teamschat
import hmac, hashlib
import json



# Authenticate if a message was genuine
# Mist passes the 'X-Mist-Signature-v2' header, containing a hash; HMAC_SHA256(secret, body)
# Take the secret (as a string) and the complete webhook message
def auth_message(secret, webhook):
    # Check that Mist sent the signature in the header
    if 'X-Mist-Signature-V2' in webhook.headers:
        # Get the message body
        data = webhook.get_data()

        # Get the hash that Mist has sent
        mist_hash = webhook.headers['X-Mist-Signature-V2']

        # Generate our own hash
        hash = hmac.new(secret.encode(), data, hashlib.sha256).hexdigest()

        # Compare the Mist hash with our hash
        if mist_hash == hash:
            return ('success')
        else:
            return ('fail')
    
    # If Mist didn't send the signature, report it
    else:
        return ('unauthenticated')


# Handle an event, whatever it may be
def handle_event(event):
    # Make sure authentication is complete first
    with open('token.txt') as f:
        data = str(f.read())
    
    token = json.loads(str(data))
    
    if token == '':
        print ('alert received, but we have no teams token')
        return

    # Handle device events
    if event['event'] == 'device_event':
        if event['type'] != 'SW_PORT_UP' and event['type'] != 'SW_PORT_DOWN':
            teamschat.send_chat(token['token'], event['name'] + ' in the ' + event['site'] + ' site had a ' + event['type'] + ' event.\n' + event['text'])
    
    # Handle audit events
    elif event['event'] == 'audit':
        if 'Add WAN Edge' not in event['task']:
            if 'admin' in event and 'site' in event:
                teamschat.send_chat(token['token'], event['admin'] + ' just made a change to the ' + event['site'] + ' site.\nThe completed task was: ' + event['task'])
            else:
                teamschat.send_chat(token['token'], 'Audit event:\nThe completed task was: ' + event['task'])
    
    # Handle alarms
    elif event['event'] == 'alarm':
        teamschat.send_chat(token['token'], str(event['count']) + ' devices in the ' + event['site'] + ' site have raised an alarm\ndevices ' + str(event['devices']) + ' have the status ' + event['type'])
    
    # Handle device up/down events
    elif event['event'] == 'updown':
        teamschat.send_chat(token['token'], 'An ' + event['device'] + ' in the ' + event['site'] + ' site has changed status\nNew status: ' + event['err_type'])
    
    # Handle anything unexpected
    else:
        teamschat.send_chat(token['token'], event)
