# Configuration of the Network Assistant and Graph API
  There are several settings that are needed for Flask, and for Graph API  
  These are configured in config.yaml, and read by config.py  
  For example, web-server port number, API endpoint, etc  
  

## config.py
### Global
  (1) Creates two dictionaries:
    GRAPH - Contains settings for Graph API
    GLOBAL - Contains settings for the web-service
    
  (2) Reads config.yaml
    Stores setting in the dictionaries
    
  
## config.yaml
  This is a standard YAML file, which makes it easy for admins to configure
  There are two sections:
    global - Settings that apply to the web-service
    graph - Settings that apply to the Graph API
    
### Global
  web_port
    The port the web server runs on. Set to 8080 by default
  webhook_secret
    The secret (password) that must be set on webhook messages

### Graph
  base_url
    The base URL of the Graph API
    https://graph.microsoft.com/v1.0/ by default
  user_id
    The user ID for the user that sends messages to teams
  chat_id
    The chat ID of the Teams chat that messages are sent to
  


