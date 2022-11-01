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
    Currently no support for HTTPS natively; Use SSL offloading (eg, nginx, F5, NetScaler)
    A config file, config.yaml, must exist in the same directory as this script

To Do:
    Figure out why user gets two auth web pages
        Only happens when starting the service initially, not when refreshing
    Find an alternative to saving the token to a file
        Can't get variables to work between Flask routes
        My current solution is to save to disk, and read later

Author:
    Luke Robertson - October 2022
"""


from flask import Flask, request
import yaml, sys
import azureauth
import misthandler




# Import configuration details
try:
    f = open('config.yaml')
    try:
        config = yaml.load(f, Loader=yaml.FullLoader)
    except yaml.YAMLError as err:
        print('Error parsing config file, exiting')
        print('Check the YAML formatting at https://yaml-online-parser.appspot.com/')
        sys.exit()
except Exception as e:
    print ('Error opening the config file, exiting')
    print (e)
    sys.exit()

WEB_PORT = config['global']['web_port']
WEBHOOK_SECRET = config['global']['webhook_secret']


# Initialise a Flask app
app = Flask(__name__)


# Authenticate with Microsoft (for teams)
print ('Calling client_auth')
azureauth.client_auth()


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
@app.route("/mist", methods=['POST'])
def mist():
    # Check that this webhook has come from a legitimate resource
    auth_result = misthandler.auth_message(WEBHOOK_SECRET, request)
    if auth_result == 'fail':
        print ("Received a webhook with a bad secret")
        return ('Webhook received, bad auth')
    elif auth_result == 'unauthenticated':
        print ("Unauthenticated webhook received")
        return ('Webhook received, no auth')

    # Get the Mist handler module to decide what to do with the request
    misthandler.handle_event(request.json)
    
    return ('Webhook received')




# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=WEB_PORT)


