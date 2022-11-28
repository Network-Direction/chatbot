"""
Provides supporting functions to the Log Insight webhooks
Parses incoming webhooks, filters, and sends to teams

Usage:
    import 'log_insight' into the application

Restrictions:
    Needs access to the 'teamschat' module

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
LOCATION = 'plugins\\loginsight\\config.yaml'


class LogInsight:
    def __init__(self):
        '''Initialise the class, load config'''
        # Empty variables for later
        self.config = {}

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

    def handle_event(self, raw_response, src):
        '''Handle webhooks when the are sent'''
        # Add the sending IP to the event
        raw_response['source'] = src

        # Cleanup the message
        event = self.parse_message(raw_response)
        message = event
        message = f"<span style=\"color:yellow\"><b>{event['hostname']} \
            </span></b> had a <span style=\"color:orange\"><b> \
            {message['alert']} </span></b>event.<br> {event['description']} \
            <br><span style=\"color:lime\">{event['recommendation']}</span> \
            <br><a href={message['url']}>See more logs here</a>"

        # Log the message, and send to teams
        self.log(message, raw_response)

    def parse_message(self, event):
        message = {}
        message['source'] = event['source']
        message['alert'] = event['alert_name']
        message['time'] = event['timestamp']
        message['hostname'] = event['messages'][0]['fields'][0]['content']
        message['description'] = event['messages'][0]['text']
        if event['recommendation'] == 'null':
            message['recommendation'] = 'No recommended actions'
        else:
            message['recommendation'] = event['recommendation']
        message['url'] = event['url']
        return message

    def refresh(self):
        '''Refresh the config file on request'''
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

    def log(self, message, event):
        date = datetime.now().date()
        time = datetime.now().time().strftime("%H:%M:%S")

        chat_id = teamschat.send_chat(message)['id']
        print('Log Insight event:', event)

        description = event['messages'][0]['text'].replace("'", "")
        fields = {
            'device': f"'{event['messages'][0]['fields'][0]['content']}'",
            'event': f"'{event['source']}'",
            'description': f"'{description}'",
            'logdate': f"'{date}'",
            'logtime': f"'{time}'",
            'source': f"{ip2integer(event['source'])}",
            'message': f"'{chat_id}'"
        }

        sql_conn = sql.Sql()
        sql_conn.add('loginsight_events', fields)


def ip2integer(ip):
    """
    Convert an IP string to long integer
    """
    packedIP = socket.inet_aton(ip)
    return struct.unpack("!L", packedIP)[0]
