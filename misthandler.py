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
    Some webhooks come through twice; Only send one to teams
        eg: Level 2 event: {'event': 'alarm', 'count': 1, 'devices': ['EDG-NET-WAP-1'], 'site': 'Edgeworth Library', 'type': 'device_reconnected', 'level': 2}

Author:
    Luke Robertson - October 2022
"""

import teamschat
import hmac, hashlib
import yaml
import sys


# Empty dictionary for alert levels
alert_levels = {}


# Authenticate if a message was genuine
# Mist passes the 'X-Mist-Signature-v2' header, containing a hash; HMAC_SHA256(secret, body)
# Take the secret (as a string) and the complete webhook message
def auth_message(secret, webhook):
    '''Takes a secret, and the webook sent by Mist
    Creates a hash of the secret and webhook body (HMAC SHA256) and compares the result'''
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



# Assign a priority to each alert (1-4)
# definitions are in filter-mist.yaml
def get_alerts():
    '''Reads the filter-mist.yaml file, to learn the priorities assigned to each alert'''
    global alert_levels

    # Read the YAML file
    try:
        f = open('filter-mist.yaml')
        
        # Load the contents into alert_levels
        try:
            alert_levels = yaml.load(f, Loader=yaml.FullLoader)
        
        # Handle problems with YAML syntax
        except yaml.YAMLError as err:
            print('Error parsing config file, exiting')
            print('Check the YAML formatting at https://yaml-online-parser.appspot.com/')
            sys.exit()
    
    # Handle an error reading the file
    except Exception as e:
        print ('Error opening the config file, exiting')
        print (e)
        sys.exit()



# Each alert has a different priority, which admins assign
# These priorities are defined in filter-mist.yaml
def alert_priority(event):
    '''Takes given events, and adds a priority level'''
    match event['event']:
        case 'device_event':
            if event['type'] in alert_levels['device_event']:
                event['level'] = alert_levels['device_event'][event['type']]
            else:
                event['level'] = 1

        case 'audit':
            # Some audit events don't have an 'admin' (user) field, so we will inject one
            if 'admin' not in event:
                event['admin'] = 'system'
            
            # Some audit events don't have an 'site' field, so we will inject one
            if 'site' not in event:
                event['site'] = 'global'
            
            # Split the 'task' field, to just read the part before the description; This matches the entry in the YAML file
            if event['task'].split(' "')[0] in alert_levels['audit']:
                event['level'] = alert_levels['audit'][event['task'].split(' "')[0]]
            else:
                event['level'] = 1

        case 'alarm':
            if event['type'] in alert_levels['alarm']:
                event['level'] = alert_levels['alarm'][event['type']]
            else:
                event['level'] = 1
        
        case 'updown':
            if event['err_type'] in alert_levels['updown']:
                event['level'] = alert_levels['updown'][event['err_type']]
            else:
                event['level'] = 1

        case 'default':
            event['level'] = 1


# Parse the alerts into a standard dictionary format that we can use
# If fields are missing, add them in
def alert_parse(raw_response):
    '''Takes a raw event from Mist, and parses it into something we can use'''
    details = {}
    match raw_response['topic']:
        case 'device-events':
            for event in raw_response['events']:
                details['event'] = 'device_event'
                details['name'] = event['device_name']
                details['type'] = event['device_type']
                details['mac'] = event['mac']
                details['site'] = event['site_name']
                details['type'] = event['type']
                if 'text' in event:
                    details['text'] = event['text']
                else:
                    details['text'] = 'no additional details available'

        case 'alarms':
            for event in raw_response['events']:
                details['event'] = 'alarm'
                details['count'] = event['count']
                details['devices'] = event['hostnames']
                details['site'] = event['site_name']
                details['type'] = event['type']

        case 'audits':
            for event in raw_response['events']:
                details['event'] = 'audit'
                details['task'] = event['message']
                
                if 'before' in event:
                    details['before'] = event['before']
                
                if 'after' in event:
                    details['after'] = event['after']
                
                if 'admin_name' in event:
                    details['admin'] = event['admin_name']
                
                if 'site_name' in event:
                    details['site'] = event['site_name']

        case 'device-updowns':
            for event in raw_response['events']:
                details['event'] = 'updown'
                details['name'] = event['device_name']
                details['device'] = event['device_type']
                details['mac'] = event['mac']
                details['site'] = event['site_name']
                details['err_type'] = event['type']

        case default:
            topic = raw_response['topic']
            for event in raw_response['events']:
                details['event'] = topic
                details['data'] = event
                print (raw_response)

    return details


# Handle an event, whatever it may be
# Takes the event, which needs parsing
def handle_event(raw_response):
    '''takes a raw event from Mist, and handles it as appropriate
    This includes parsing the event, assigning a priority, and possibly sending it to teams'''
    # Parse the message
    event = alert_parse(raw_response)

    # Read the YAML file to find out how to handle certain events
    # Only do this the first time, don't repeat it every time
    if alert_levels == {}:
        print ('reading YAML for the first time')
        get_alerts()


    # Filter events
    # These are just keywords that we want to avoid
    for item in alert_levels['filter']:
        if item in str(event):
            print ('filtering out an event')
            return



    # Add the event level (1-4) to the 'event'
    alert_priority(event)


    # Handle device events
    message = ''
    if event['event'] == 'device_event':
        match event['level']:
            case 1:
                message = f"<b><span style=\"color:Yellow\">{event['name']}</span></b> in the <span style=\"color:Lime\"><b>{event['site']}</b></span> site had a <b><span style=\"color:Orange\">{event['type']}</span></b> event. <br> {event['text']}"
                print ('Level 1 event:', event)

            case 2:
                message = f"<b><span style=\"color:Yellow\">{event['name']}</span></b> in the <span style=\"color:Lime\"><b>{event['site']}</b></span> site had a <b><span style=\"color:Orange\">{event['type']}</span></b> event"
                print ('Level 2 event:', event)
            
            case 3:
                print ('Level 3 event:', event)
        
    
    # Handle audit events
    elif event['event'] == 'audit':
        match event['level']:
            case 1:
                if 'before' in event:
                    message = f"<b><span style=\"color:Yellow\">{event['admin']}</span></b> just made a change to the <span style=\"color:Lime\"><b>{event['site']}</b></span> site<br> The completed task was: <b><span style=\"color:Orange\">{event['task']}</span></b>.<br> Previous config: {event['before']}<br> New config: {event['after']}"
                else:
                    message = f"<b><span style=\"color:Yellow\">{event['admin']}</span></b> just made a change to the <span style=\"color:Lime\"><b>{event['site']}</b></span> site.<br> The completed task was: <b><span style=\"color:Orange\">{event['task']}</span></b>"
                print ('Level 1 event:', event)
            
            case 2:
                message = f"<b><span style=\"color:Yellow\">{event['admin']}</span></b> just made a change to the <span style=\"color:Lime\"><b>{event['site']}</b></span> site."
                print ('Level 2 event:', event)
            
            case 3:
                print ('Level 3 event:', event)

    
    # Handle alarms
    elif event['event'] == 'alarm':
        match event['level']:
            case 1:
                message = f"{str(event['count'])} devices in the <span style=\"color:Lime\"><b>{event['site']}</b></span> site have raised an alarm<br> devices {str(event['devices'])} have the status <b><span style=\"color:Orange\">{event['type']}</span></b>"
                print ('Level 1 event:', event)

            case 2:
                message = f"One or more devices in the <span style=\"color:Lime\"><b>{event['site']}</b></span> site have raised non-critical alarms (<b><span style=\"color:Orange\">{event['type']}</span></b>)"
                print ('Level 2 event:', event)

            case 3:
                print ('Level 3 event:', event)


    # Handle device up/down events
    elif event['event'] == 'updown':
        match event['level']:
            case 1:
                message = f"A/An <b><span style=\"color:Yellow\">{event['device']}</span></b> in the <span style=\"color:Lime\"><b>{event['site']}</b></span> site ({event['name']}) has changed status<br> New status: <b><span style=\"color:Orange\">{event['err_type']}</span></b>"
                print ('Level 1 event:', event)
            
            case 2:
                message = f"A/An <b><span style=\"color:Yellow\">{event['device']}</span></b> in the <span style=\"color:Lime\"><b>{event['site']}</b></span> site has changed status"
                print ('Level 2 event:', event)
            
            case 3:
                print ('Level 3 event:', event)

   
    # Handle anything unexpected
    else:
        message = event
        print (event)


    # Send the message to Teams
    if message:
        teamschat.send_chat(message)


