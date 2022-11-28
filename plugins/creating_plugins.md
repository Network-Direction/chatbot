# Creating plugins
Customised plugins can be written for any service that can send webhooks   
While much of this is customized, there are some guidelines that must be followed


### Plugin Location:
    All plugins are located in their own folder under the 'plugins' folder
    Within the plugin folder, be sure to create an __init__.py file
    The __init__.py may be left empty
    
    
### Configuration File
    Each plugin should have a YAML file for configuration
    The file name can be flexible, but something like 'config.yaml' is suggested
    The config file should have a 'config' section
    Under the config section there should be:
        'webhook_secret' - Set a secret here, or leave blank for unauthenticated
        'auth_header' - The name of the header that contains the authentication information
    Additional plugin specific configuration can also be stored here
    
    
### Python files
    The plugin will need to have at least one python file. 
    The name of the file is flexible, as long as it doesn't conflict with other imports
    Optionally, consider creating a standalone SQL script to create tables and fields in an SQL DB
    
    
### Class
    The plugin will need a class with these methods as a minimum (names can be customised):
        __init__() - Reads the configuration file
        handle_event(raw_response, src) - Process webhooks when they arrive
            'raw_response' is the unedited webhook
            'src' is the IP address of the sender
        refresh() - Reread the config file when needed
        
    Optionally, the plugin may want to support methods to:
        Log information to SQL
        Assign priorities to events, to improve handling
        Filter events
        Log debugging information to a text file
        

### Registering the Plugin
    To be loaded, the plugin needs to be registered. This is done in the config.yaml file in the main app
    Under the 'plugins' section, create a new entry. This needs to contain:
        name - The friendly name of the plugin
        route - The Flask route (URL) that the app listens on 
        class - The name of the class, as defined in the plugin
        module - The module that gets imported. This includes these fields
            'plugins' - Represents the plugins folder (do not change)
            plugin folder - The folder the plugin is stored in
            module - The mpodule name (the python file to import into the app)
