# Mist plugin
Handles webhooks from the Juniper (junos) devices

# Using the plugin
### Enabling Webhooks
    This requires an agent on Junos devices
    Take the junos-agent file, and deploy it to /var/db/scripts/event/ on each device that you want to monitor
    Enable python on the device with 'set system scripts language python3'
    Add configuration to event-options to call scripts when certain system events occur. For example:
    
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

### Authentication
    Junos authentication uses HMAC-SHA-256
    It adds a 'Junos-Auth' header, containing a hash of the body and the secret

### Configuration
    Plugin configuration is in the 'junos-config.yaml' file
    This plugin is low featured at this time
    
#### Global Config
    Set 'webhook_secret' to the secret, as set in the junos event-options configuration
    Set the 'auth_header' to Junos-Auth; This is how the main program knows which header to check for authentication



- - - -
## Files
### junos.py
    The JunosHandler class that handles events as they are received
    Loads the config file
    Has a 'handle_event' method, which is called when a webhool arrives

### junos-agent.py
    The agent script that is added to the Junos devices
    This is passed an event from 'event-options'
    This will send the event as a webhook to the chatbot
    
