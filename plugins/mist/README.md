# Mist plugin
Handles webhooks from the Juniper Mist cloud

# Using the plugin
### Enabling Webhooks
    Webhooks need to be enabled in the Mist platform. This can be done for the entire Org, or per site
    Set the URL (the IP or name of the chatbot with the route)
    Set a secret, for authentication

### Authentication
    Mist authentication uses HMAC-SHA-256
    It adds a 'X-Mist-Signature-V2' header, containing a hash of the body and the secret

### Configuration
    Plugin configuration is in the 'mist-config.yaml' file
    
#### Global Config
    Set 'debug' to True to log events to a text file
    Set 'webhook_secret' to the secret, as set in the Mist webhook configuration
    Set the 'auth_header' to X-Mist-Signature-V2; This is how the main program knows which header to check for authentication

#### Event Filtering
    Mist supports lots of different event types. Currently supported events are 'device_event', 'audit', 'alarm', and 'updown'
    Each of these categories contain many different events.
    The configuration file has a list of these (although the list may not be exhaustive), and priority levels
      * level-1: A critical alert, all details on teams
      * level-2: An important alert, send a summary on teams
      * level-3: Not so important alert, log only, no teams
      * level-4: Ignore completely
    Each of these can have optional sub-priorities, assigned based on additional keywords found in the event
    There is also a 'filter' section to completely filter certain events out, if they contain given keywords
    

- - - -
## Files
### sql_create.py
    Standalone script that connects to the SQL server (as globally defined in the app)
    Creates the table and required fields

### misthandler.py
    The main class of the plugin (MistHandler)
    
#### __init__()
    Loads the configuration file
    Sets up the framework for webhook authentication
    
#### alert_priority()
    Takes an event, and adds an alert level, based on the configuration file
    Default is level 1, unless a specific entry exists

#### alert_parse()
    Takes the events, and puts them into a standard dictionary for better handling
    Events, alerts, up/down, etc, can have slightly different fields, so this normalizes them to prevent errors

#### handle_event()
    The function that the main program calls when a webhook is received
    This uses other methods to parse, filter, and normalize events
    It creates a human readable message, which is sent to the user over teams
    It writes events to SQL
    
#### refresh()
       Reads the config file again
       This allows config to be updated without restarting Flask


