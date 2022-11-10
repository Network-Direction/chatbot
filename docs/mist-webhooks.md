# Mist Webhooks
Mist sends events via webhooks to /mist  

&nbsp;<br>
## Authentication
  By default, webhooks are sent unauthenticated  
  Mist supports including a secret, which this app requires  
  Mist will hash the body of the webhook message, with the secret, and attach it as the 'X-Mist-Signature-V2' header  
  Authenticating these messages is achieved by running the same algorithm (HMAC-SHA256), and comparing the hash with the header  

&nbsp;<br>
- - - -
## Event Types
  Mist support several event types. Webhooks can be configured to send only a subset of these as needed  
  This app currently supports:  
    - Alerts  
    - Audits  
    - Device Status  
    - Device Events  

&nbsp;<br>
- - - -
## Mist Configuration
  Webhooks can be enabled globally and/or per-site  
  Global webhooks apply to the entire tenant. For example, logins, changes to global config, etc  
  Site based webhooks send information about the site, such as device failures, etc  

&nbsp;<br>
### Global Settings
  In Organization > Settings > Webhooks, tick the 'Enable' box  
  Add a Name (anything is fine)  
  Set the URL to your App URL (eg, http://mydomain.com/mist)  
  Set the secret  
  Enable the events you need  

&nbsp;<br>
### Site Settings
  In Organization > Site Settings, select the site you want to enable webhooks for  
  Under 'Webhooks', tick the 'Enable'box  
  Set the Name, URL, and Secret (as described above)  
  Enable the events you want to monitor  
  

&nbsp;<br>
- - - -
## misthandler.py
### To Do
  (1) Some webhooks come through twice, duplicating logs; Try to filter these out  


&nbsp;<br>
### Global
  Creates an empty dictionary that contains the alert levels  
  

### auth_message()
  Arguments:  
    secret - The secret, as defined in the config.yaml file  
    webhook - The raw webhook, body and headers  
  Returns: A string  
    'success' - The hash matches the one sent by Mist  
    'fail' - The hash does not match  
    'unauthenticated' - Mist is not using a secret with webhooks  
  Purpose:   
    Authenticate the webhook sent by Mist  
    Mist will hash the secret with the message body; hmac(secret, body), and place the result in the 'X-Mist-Signature-V2' header  
    This function repeats the process, generating a hash, and compares it to the one in the header  
  

### get_alerts()
  Arguments: None  
  Returns: None  
  Purpose:   
    Reads the filter-mist.yaml file, to see what priorities should be assigned to each event  
    This can be used to filter what is sent to teams (eg, we probably don't want to know every port up/down event on an access switch)  
    Details are stored in the alert_levels variable  
  

### alert_priority()
  Arguments: event - The event from Mist, after it has been parsed  
  Returns: None  
  Purpose:   
    Determines if there is a priority defined for this event  
    If there is a priority defined, this function adds 'alert' to the event dictionary as appropriate  
    Unclassified events are considered to be priority 1  
  

### alert_parse()
  Arguments: raw_response - The raw webhook message from Mist  
  Returns: details - The message after it has been parsed  
  Purpose:   
    Normalizes the message format, so all messages can be handled in the same way  
    Some events don't have all the fields others do (eg, some don't have a 'text' field), so a field is added in to avoid errors later  
    Each event type (eg, alarm, audit, etc) is formatted differently, so they need to be parsed differently  
  

### handle_event()
  Arguments: raw_response - The raw webhook message from Mist  
  Returns: None  
  Purpose:   
    Decides what to do with a webhook message from Mist  
    (1) Calls alert_parse() to normalize the message  
    (2) If the mist-filter.yaml hasn't been read yet, it calls alert_levels()  
    (3) Filters out any strings that need to be ignored completely  
    (4) Handles each event type  
      - Within each type, each message is handled differently depending on the priority level  
      - Level 1 has all details sent to teams  
      - Level 2 has a summary sent to teams  
      - Level 3 logs to terminal only  
      - Level 4 is ignored completely  
      - Adjust the priority levels in filter-mist.yaml  
    (5) If needed, send a message to Teams
    (6) Log entries to SQL
  
  
## mist-config.yaml
A YAML formatted file used to configure the Mist plugin and filter events received from  
Configuration contains a field called 'debug
* This can be set to True or False
* If true, entries are logged to mist_debug-<date>.log
  
### Filtering
There are two ways events can be filtered:  
* A text string filter: Filters out any string that matches  
* Priority levels: Assigns levels to different events, so they can be handled in different ways  
Events can have a subpriority assigned
* For example, the SW_DOT1XD_USR_AUTHENTICATED may have a level of 3; However, there may be a sub priority of 1 assigned to 'vlan 10'
* This means that if the text 'vlan 10' exists in this event, it will get assigned to level 1

&nbsp;<br>
### Event Levels
  - Level 1 has all details sent to teams  
  - Level 2 has a summary sent to teams  
  - Level 3 logs to terminal only  
  - Level 4 is ignored completely  
  - Any event not listed is implicitly considered to be level 1  
  
&nbsp;<br>
### Assigning Levels
  The YAML file has heading for the supported event types  
  - device_event  
  - audit  
  - alarm  
  - updown  
  
  Under each of these are the event names. The field within the raw webhook that contains the even name varies depending on the event type  
  Each event name is paired with a value from 1 to 4, which represents the priority level  
  
&nbsp;<br>
### Filtering Strings
  The 'filter' heading is a list, with each member item being a string  
  Any string listed here is filtered out, regardless of the event level  
  This is useful to prevent the chatbot from sending certain events to Teams, so you don't get drowned in events  
  At this time, there is no support for regex. It's just a simple string  
  

