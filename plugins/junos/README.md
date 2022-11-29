# Mist plugin
Handles webhooks from the Juniper (junos) devices

# Using the plugin
### Enabling Webhooks
    This requires an agent on Junos devices
    Take the junos-agent file, and deploy it to /var/db/scripts/event/ on each device that you want to monitor
    Enable python on the device with 'set system scripts language python3'
    Add configuration to event-options to call scripts when certain system events occur. For example:
    
```Junos
[edit event-options]
policy Webhooks {
    events LICENSE_EXPIRED_KEY_DELETED;
    then {
        event-script junos-agent.py {
            arguments {
                url <DESTINATION>;          <<< The URL to send webhooks to
                secret <SECRET>;            <<< The webhooks secret
            }
        }
    }
}
event-script {
    file junos-agent.py {
        python-script-user admin;
        checksum sha-256 xxxx;              <<< use 'file checksum sha-256 FILENAME' to get the checksum of this file
    }
}
```

### Authentication
    Junos authentication uses HMAC-SHA-256
    It adds a 'Junos-Auth' header, containing a hash of the body and the secret

### Configuration
    Plugin configuration is in the 'junos-config.yaml' file
    the 'events' section can be used to assign priority levels and filter events
    
#### Global Config
    Set 'webhook_secret' to the secret, as set in the junos event-options configuration
    Set the 'auth_header' to Junos-Auth; This is how the main program knows which header to check for authentication



- - - -
## Files
### sql-create.py
    A standalone script that connects to the SQL server, as globally defined in the app
    Created the table and fields

### junos.py
    The JunosHandler class that handles events as they are received
    
#### __init__()
    Loads the config file
    
#### handle_event(raw_response, src)
    Handles a webhook when it arrives
        'raw_response' is the raw webhook
        'src' is the IP that sent the webhook
    Sends the event to alert_priority() to assign a priority
    Prepares a message to send to teams
    Sends the message and event to log()
    
#### alert_priority()
    Assigns a priority to each alert, to affect how its handled

#### log()
    Sends the message to teams (if needed)
    Prints the event to the terminal
    Writes the event to SQL

#### refresh()
    Rereads the config
    This allows config changes to be made without restarting Flask

### junos-agent.py
    The agent script that is added to the Junos devices
    This is passed an event from 'event-options'
    This will send the event as a webhook to the chatbot
    
