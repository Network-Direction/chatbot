# Change Log

&nbsp;<br>
## 0.6
### General
    Added colours to terminal logging
    Added support to send messages to the chatbot. This is very rudimentary at this stage, and is only used for testing
        Try typing 'hi' or 'tell me a joke'
    
### Azure Authentication
    Converted 'azureauth' to a class
    Added support for users other than the logged in one (configure in config.yaml)

### Plugins
    Added a template for plugins, to make plugin creation simpler
    Fixed a bug in the plugin loader

&nbsp;<br>
## 0.5
### General Updates
    Updated token read/write to use 'with'
    Moved teams details (secret, app ID, etc) from azureauth.py to a section in config.yaml
    Changed how plugins are loaded, so the list is available globally
    Enabled plugin config refresh as part of the regular Graph API token refresh
  
### SQL Improvements
    Moves SQL functions to a class
    Will now connect, process, and gracefully close the connection for each transaction
    Moved 'sql-create' to each plugins folder
  
### Added a Log Insight plugin
  
### Mist plugin improvements
    Removed sys.exit() on failure, so the whole app doesn't close
    Converted logging to a class
    Updated logging to use 'with'
    Added a 'refresh' method to read config changes
    Switch/Mist config changes will now only show the changes (diff) not the entire config
  
### Junos plugin improvements
    Removed sys.exit() on failure, so the whole app doesn't close
    Added an 'events' section to the config file, to support event filtering
    Added SQL logging
    Added a 'refresh' method to read config changes

- - - -
&nbsp;<br>
## 0.4
### Added PEP8 compliance in python code   

### Broke out project into folders   
    core - Core project files, including Azure authentication, SQL access, hashing, etc   
    plugins - contains various plugins that can be added or removed (eg, mist, junos)   
  
### Plugins   
    Added plugin list to the global config file (route, name, class)   
    Plugins will dynamically create a Flask route   
    No core components, other than the config file, have plugin specific code   
    Each plugin needs to have a class with a method called 'handle_event'   
    Webhool verification is part of the plugin   
    
### Separated hashing functions from Mist, and made it a core function   
  
### SQL   
    Added teams notifications for SQL errors
  
### Mist plugin:   
    Converted the handler to a class   
    
### Junos plugin:   
    Created a basic junos plugin   
    Requires an agent to be added to /var/db/scripts/events/ on the Junos device   
    Requires 'event-options' configuration   
    Authenticates webhooks based on a header   

&nbsp;<br>
- - - -
