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
    Requires pyyaml module to be installed (pip install pyyaml)
    Requires termcolor to be installed (pip install termcolor)
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

Author:
    Luke Robertson - January 2023
"""


from flask import Flask, request, Response
from core import azureauth
from core import crypto
from core import parse_chats
from config import GLOBAL
from config import PLUGINS, plugin_list
import importlib
from core import teamschat
import termcolor
from urllib.parse import urlparse, parse_qs
import threading


# Load plugins
def load_plugins(plugin_list):
    for plugin in PLUGINS:
        print(termcolor.colored(
            f"Loading plugin: {PLUGINS[plugin]['name']}",
            "green"))

        try:
            module = importlib.import_module(PLUGINS[plugin]['module'])
        except Exception as e:
            print(termcolor.colored(
                f"Error loading the {PLUGINS[plugin]['name']} plugin",
                "red"))
            print(f"{e} error while loading the module")
            continue
        print(module)

        try:
            handler = eval('module.' + PLUGINS[plugin]['class'])()
        except Exception as e:
            message = f"Error loading the {PLUGINS[plugin]['name']} plugin"
            print(termcolor.colored(message, "red"))
            print(f"{e} error while loading the class")
            teamschat.send_chat(message)
            continue

        plugin_entry = {
            'name': PLUGINS[plugin]['name'],
            'route': PLUGINS[plugin]['route'],
            'handler': handler,
        }
        plugin_list.append(plugin_entry)


# Import configuration details
WEB_PORT = GLOBAL['web_port']
WEBHOOK_SECRET = GLOBAL['webhook_secret']


# Initialise a Flask app
app = Flask(__name__)


# Setup the Mist handler object
load_plugins(plugin_list)
print(termcolor.colored(f"Plugins: {plugin_list}", "cyan"))


# Authenticate with Microsoft (for teams)
print('Calling client_auth')
azure = azureauth.AzureAuth()
azure.client_auth()


# Subscribe to the group chat, so we can see when people send messages
# The callback URL needs to be ready for this to work,
#   so this is run as a separate thread
thread = threading.Thread(target=teamschat.subscribe)
thread.start()


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
        azure.get_token(client_code)

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
    # The class must include a 'handle_event' and 'authenticate' method
    for plugin in plugin_list:
        # Confirm that a route exists for this plugin
        if handler == plugin['route']:
            # Authenticate the webhook
            if plugin['handler'].authenticate(request=request, plugin=plugin):
                # If authenticated, send this to the handler
                # print(termcolor.colored(request.headers, "cyan"))
                plugin['handler'].handle_event(raw_response=request.json,
                                               src=source_ip)

            # Return a positive response
            return ('Webhook received')

    return ('Invalid path')


# GraphAPI - Listens for change notifications
# This is when new messages are sent to the chatbot
@app.route("/chat", methods=['POST'])
def chat():
    # Check if this is a callback when subscribing
    url = request.url
    if 'validationToken' in url:
        parsed = urlparse(url)
        validation_string = parse_qs(parsed.query)['validationToken'][0]
        print(f"Validation String: {validation_string}")
        return Response(validation_string, status=200, mimetype='text/plain')

    # Or, is this a webhook
    else:
        # Extract the values we need from the webhook
        body_value = request.json['value']
        encrypted_session_key = body_value[0]['encryptedContent']['dataKey']
        signature = body_value[0]['encryptedContent']['dataSignature']
        data = body_value[0]['encryptedContent']['data']

        # Decrypt the symmetric key
        decrypted_symmetric_key = crypto.rsa_decrypt(encrypted_session_key)

        # Validate the signature - Tamper prevention
        if crypto.validate(decrypted_symmetric_key, data, signature):
            # Decrypt the message
            decrypted_payload = crypto.aes_decrypt(
                decrypted_symmetric_key,
                data
            )

            # Get key fields from the message, and parse it
            name = decrypted_payload['from']['user']['displayName']
            message = decrypted_payload['body']['content']
            parse_chats.parse(message=message, sender=name)

            # message = message.replace("<p>", "").replace("</p>", "")

            # # Confirm it's not the chatbot itself generating the message
            # if name != GLOBAL['chatbot_name']:
            #     if 'hi' in message:
            #         teamschat.send_chat("hi")
            #     elif 'tell me a joke' in message:
            #         teamschat.send_chat("I don't know any jokes")
            #     else:
            #         print(f"{name} says {message}")

        else:
            print("Validation failed")
            print("Data may have been tampered with")

        return ('received')


# Start the Flask app
if __name__ == '__main__':
    app.run(debug=GLOBAL['flask_debug'], host='0.0.0.0', port=WEB_PORT)
