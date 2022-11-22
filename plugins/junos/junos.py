"""
Provides supporting functions to the Junos webhooks
Parses incoming webhooks, filters, and sends to teams

Usage:
    import 'junos' into the application

Restrictions:
    Needs access to the 'teamschat' module

To Do:
    TBA

Author:
    Luke Robertson - November 2022
"""


import sys
import yaml
from core import teamschat


# Location of the config file
LOCATION = 'plugins\\junos\\junos-config.yaml'


# Junos handler class
class JunosHandler:
    def __init__(self):
        # Empty variables for later
        self.config = {}

        # Read the YAML file
        try:
            f = open(LOCATION)

            # Load the contents into alert_levels
            try:
                self.config = yaml.load(f, Loader=yaml.FullLoader)

            # Handle problems with YAML syntax
            except yaml.YAMLError as err:
                print('Error parsing config file, exiting')
                print('Check the YAML formatting at \
                    https://yaml-online-parser.appspot.com/')
                print(err)
                sys.exit()

        # Handle an error reading the file
        except Exception as e:
            print('Error opening the config file, exiting')
            print(e)
            sys.exit()

        # Setup webhook authentication
        self.auth_header = self.config['config']['auth_header']
        self.webhook_secret = self.config['config']['webhook_secret']

    def handle_event(self, raw_response, src, sql_connector):
        # print(raw_response)
        # print(src)

        print('Junos event:', raw_response)
        message = f"{raw_response['message']} on \
            <span style=\"color:Lime\"><b> \
            {raw_response['hostname']}</b></span>"

        teamschat.send_chat(message)
