"""
Runs a small web server, using Flask
Listen for announcements from Mist (webhooks)

Usage:
    Add config to the 'config.yaml' file
    Base URL is something like http://localhost:{PORT}
    Test the web server - Browse to /test
    Test the mist webhook - GET /mist
    Send a Mist webhook - POST /mist

Authentication:
    Mist - Not required, as this service passively receives webhooks

Restrictions:
    Requires Flask module to be installed (pip install flask)
    Requires pyyaml modeult to be installed (pip install pyyaml)
    Requires a public IP and FW rules (for webhooks to send to)
        TCP port is set in the WEB_PORT variable
    No support for HTTPS; Use SSL offloading (eg, nginx, F5, NetScaler)
    A config file, config.yaml, must exist in the same directory as this script
    NOTE: When using Flask debug mode, the authentication window opens twice;
        Apparently a known Flask issue

To Do:
    Find an alternative to saving the token to a file
        Can't get variables to work between Flask routes
        My current solution is to save to disk, and read later
    Move webhook authentication to be per-plugin

Author:
    Luke Robertson - November 2022
"""


from flask import Flask, request
from core import azureauth, sql, hash
from config import GLOBAL
from config import PLUGINS
import importlib
from core import teamschat


# Load plugins
def load_plugins():
    plugin_list = []

    for plugin in PLUGINS:
        print(f"Loading plugin: {PLUGINS[plugin]['name']}")

        try:
            module = importlib.import_module(PLUGINS[plugin]['module'])
        except Exception as e:
            print(f"Error loading the {PLUGINS[plugin]['name']} plugin")
            print(e)
            break
        print(module)

        try:
            handler = eval('module.' + PLUGINS[plugin]['class'])()
        except Exception as e:
            message = f"Error loading the {PLUGINS[plugin]['name']} plugin"
            print(message)
            print(e)
            teamschat.send_chat(message)
            break

        plugin_entry = {
            'name': PLUGINS[plugin]['name'],
            'route': PLUGINS[plugin]['route'],
            'handler': handler,
        }
        plugin_list.append(plugin_entry)

    return plugin_list


# Import configuration details
WEB_PORT = GLOBAL['web_port']
WEBHOOK_SECRET = GLOBAL['webhook_secret']


# Initialise a Flask app
app = Flask(__name__)


# Authenticate with Microsoft (for teams)
print('Calling client_auth')
azureauth.client_auth()


# Connect to the SQL database
sql_connector = sql.connect(GLOBAL['db_server'], GLOBAL['db_name'])


# Setup the Mist handler object
plugin_list = load_plugins()
print(f"Plugins: {plugin_list}")


# Test URL - Used to confirm the service is running
@app.route("/test")
def test():
    message = "Web Service is running on port " + str(WEB_PORT)
    return message


# Callback URL; Used for MS Identity authentication
# When a user authenticates, a code is returned here
@app.route("/callback", methods=['GET'])
def callback():
    client_code = (request.args['code'])
    if client_code == '':
        return ('There has been a problem retrieving the client code')
    else:
        # Get the token from Microsoft
        azureauth.get_token(client_code)

        return ('Thankyou for authenticating, this window can be closed')


# Mist web service - Listens for webhooks
@app.route('/<handler>', methods=['POST'])
def webhook_handler(handler):
    # Get the source IP - Use X-Forwarded-For header if it's available
    if 'X-Forwarded-For' in request.headers:
        source_ip = request.headers['X-Forwarded-For']
    else:
        source_ip = request.remote_addr

    # Get the plugin handler module to decide what to do with the request
    # The class must include a 'handle_event' method
    for plugin in plugin_list:
        if handler == plugin['route']:
            # Check if this plugin requires authentication
            if plugin['handler'].auth_header != '':
                # Check that this webhook has come from a legitimate resource
                auth_result = hash.auth_message(
                    header=plugin['handler'].auth_header,
                    secret=plugin['handler'].webhook_secret,
                    webhook=request
                )

                if auth_result == 'fail':
                    print("Received a webhook with a bad secret")
                    return ('Webhook received, bad auth')

                elif auth_result == 'unauthenticated':
                    print("Unauthenticated webhook received")
                    return ('Webhook received, no auth')
            else:
                print('Unauthenticated webhook')

            # Send this to the handler
            plugin['handler'].handle_event(raw_response=request.json,
                                           src=source_ip,
                                           sql_connector=sql_connector)

            # Return a positive response
            return ('Webhook received')

    return ('Invalid path')


# Start the Flask app
if __name__ == '__main__':
    app.run(debug=GLOBAL['flask_debug'], host='0.0.0.0', port=WEB_PORT)
