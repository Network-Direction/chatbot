"""
Provides supporting functions to the Junos webhooks
Parses incoming webhooks, filters, and sends to teams

Usage:
    import 'junos' into the application

Restrictions:
    Needs access to the 'teamschat' module
    Does not support subfilters, as some other plugins do

To Do:
    TBA

Author:
    Luke Robertson - November 2022
"""


import yaml
from core import teamschat
from core import sql
import socket
import struct
from datetime import datetime


# Location of the config file
LOCATION = 'plugins\\junos\\junos-config.yaml'


# Junos handler class
class JunosHandler:
    def __init__(self):
        # Empty variables for later
        self.config = {}
        self.alert_levels = {}

        # Read the YAML file
        with open(LOCATION) as config:
            try:
                self.config = yaml.load(config, Loader=yaml.FullLoader)

            # Handle problems with YAML syntax
            except yaml.YAMLError as err:
                print('Error parsing config file, exiting')
                print('Check the YAML formatting at \
                    https://yaml-online-parser.appspot.com/')
                print(err)
                return False

        # Setup webhook authentication
        self.auth_header = self.config['config']['auth_header']
        self.webhook_secret = self.config['config']['webhook_secret']

        # Initialize alert levels
        self.alert_levels = self.config['events']

    # Handle the event as it comes in
    def handle_event(self, raw_response, src):
        # Add the sending IP to the event
        raw_response['source'] = src

        # Assign a priority to the event
        self.alert_priority(raw_response)

        # Cleanup the message string
        raw_response['message'] = \
            raw_response['message'].replace(raw_response['event'], "")
        raw_response['message'] = raw_response['message'].replace("'", "")

        # Depending on priority,
        # print event to terminal and prepare message for Teams
        match raw_response['level']:
            # Priority 1
            case 1:
                message = f"{raw_response['message']} on \
                    <span style=\"color:Lime\"><b> \
                    {raw_response['hostname']}</b></span>"
                self.log(message, raw_response)

            # Priority 2
            case 2:
                message = f"{raw_response['message']} on \
                    <span style=\"color:Lime\"><b> \
                    {raw_response['hostname']}</b></span>"
                self.log(message, raw_response)

            # Priority 3
            case 3:
                print('Junos event:', raw_response)

            # Any other priority (4, or some error has occurred)
            case _:
                pass

    # Assign a priority to an event
    def alert_priority(self, webhook):
        if webhook['event'] in self.alert_levels:
            webhook['level'] = self.alert_levels[webhook['event']]
        else:
            webhook['level'] = 1

    # Log to SQL and terminal
    def log(self, message, event):
        date = datetime.now().date()
        time = datetime.now().time().strftime("%H:%M:%S")

        chat_id = teamschat.send_chat(message)['id']
        print('Junos event:', event)

        fields = {
            'device': f"'{event['hostname']}'",
            'event': f"'{event['event']}'",
            'description': f"'{event['message']}'",
            'logdate': f"'{date}'",
            'logtime': f"'{time}'",
            'source': f"{ip2integer(event['source'])}",
            'message': f"'{chat_id}'"
        }

        sql_conn = sql.Sql()
        sql_conn.add('junos_events', fields)

    # Refresh the alert levels
    # Reread the config file
    def refresh(self):
        # Read the YAML file
        with open(LOCATION) as config:
            try:
                self.config = yaml.load(config, Loader=yaml.FullLoader)

            # Handle problems with YAML syntax
            except yaml.YAMLError as err:
                print('Error parsing config file, exiting')
                print('Check the YAML formatting at \
                    https://yaml-online-parser.appspot.com/')
                print(err)
                return False


def ip2integer(ip):
    """
    Convert an IP string to long integer
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]
