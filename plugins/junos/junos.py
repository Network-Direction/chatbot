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


# import yaml
from core import teamschat
from core import plugin
from datetime import datetime
import termcolor


# Location of the config file
LOCATION = 'plugins\\junos\\junos-config.yaml'


# Junos handler class
class JunosHandler(plugin.PluginTemplate):
    def __init__(self):
        super().__init__(LOCATION)

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
        if webhook['event'] in self.config['events']:
            webhook['level'] = self.config['events'][webhook['event']]
        else:
            webhook['level'] = 1

    # Log to SQL and terminal
    def log(self, message, event):
        date = datetime.now().date()
        time = datetime.now().time().strftime("%H:%M:%S")

        chat_id = teamschat.send_chat(message)['id']
        print(termcolor.colored(f"Junos event: {event}", "yellow"))

        fields = {
            'device': f"'{event['hostname']}'",
            'event': f"'{event['event']}'",
            'description': f"'{event['message']}'",
            'logdate': f"'{date}'",
            'logtime': f"'{time}'",
            'source': f"{self.ip2integer(event['source'])}",
            'message': f"'{chat_id}'"
        }

        self.sql_write(
            database=self.config['config']['sql_table'],
            fields=fields
        )
