# Change Log

&nbsp;<br>
## 0.4
  Added PEP8 compliance in python code   

  Broke out project into folders   
    core - Core project files, including Azure authentication, SQL access, hashing, etc   
    plugins - contains various plugins that can be added or removed (eg, mist, junos)   
  
  Plugins   
    Added plugin list to the global config file (route, name, class)   
    Plugins will dynamically create a Flask route   
    No core components, other than the config file, have plugin specific code   
    Each plugin needs to have a class with a method called 'handle_event'   
    Webhool verification is part of the plugin   
    
  Separated hashing functions from Mist, and made it a core function   
  
  SQL   
    Added teams notifications for SQL errors
  
  Mist plugin:   
    Converted the handler to a class   
    
  Junos plugin:   
    Created a basic junos plugin   
    Requires an agent to be added to /var/db/scripts/events/ on the Junos device   
    Requires 'event-options' configuration   
    Authenticates webhooks based on a header   

&nbsp;<br>
- - - -
