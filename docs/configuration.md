# Global Configuration
  There are several settings that are needed for Flask, Graph API, and for plugins  
  These are configured in config.yaml, and read by config.py  
  For example, web-server port number, API endpoint, etc  
  

## config.py
### Global
(1) Creates three dictionaries:  
* GRAPH - Contains settings for Graph API  
* GLOBAL - Contains settings for the web-service  
* SMTP - Contains settings for the SMTP server
    
(2) Reads config.yaml  
* Stores setting in the dictionaries  
    
    
    
&nbsp;<br>
- - - -
## config.yaml
  This is a standard YAML file, which makes it easy for admins to configure  
  There are two sections:  
    global - Settings that apply to the web-service  
    graph - Settings that apply to the Graph API  

&nbsp;<br>
### Global
web_port  
* The port the web server runs on. Set to 8080 by default  
webhook_secret  
* The secret (password) that must be set on webhook messages  
flask_debug
* Enables debug mode
* This applies to Flask, as well as to SQL (log the query strings sent to the SQL server)
db_server
* The name or IP address of the database server
db_name
* The name of the database

&nbsp;<br>
### Plugins
* Contains a list of plugins
* Each plugin contains:
  * A name
  * A route (used with Flask)
  * A class (contains methods to handle the webhook messages)
  * A module (a method in the class that Flask will use when webhooks come in)

&nbsp;<br>
### Graph
base_url  
* The base URL of the Graph API  
* https://graph.microsoft.com/v1.0/ by default  
user_id  
* The user ID for the user that sends messages to teams  
chat_id  
* The chat ID of the Teams chat that messages are sent to  
  
&nbsp;<br>
### SMTP
This is used to send an email alert if there is a problem connecting to Teams  
This is not used for general notifications
&nbsp;<br>
server
* The name or IP address of the SMTP server
port
* The destination port of the SMTP server (eg, 25)
sender
* The sending email address
receivers
* A list of addresses that receive the alert


