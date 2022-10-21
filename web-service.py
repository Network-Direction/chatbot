"""
Runs a small web server, using Flask
Listen for announcements from Mist (webhooks)

Usage:
    Base URL is something like http://localhost:{PORT}
    Test the web server - Browse to /test
    Test the mist webhook - GET /mist
    Send a Mist webhook - POST /mist

Authentication:
    Mist - Not required, as this service passively receives webhooks

Restrictions:
    Requires Flask module to be installed (pip install flask)
    Requires a public IP and FW rules (for webhooks to send to)
        TCP port is set in the WEB_PORT variable
    Currently no support for HTTPS natively; Use SSL offloading (eg, nginx, F5, NetScaler)

To Do:
    Add a timestamp to events
    Figure out why user gets two auth web pages
        Only happens when starting the service initially, not when refreshing
    Find an alternative to saving the token to a file
        Can't get variables to work between Flask routes
        My current solution is to save to disk, and read later
    Find a better way to filter output to teams

Author:
    Luke Robertson - October 2022
"""


from flask import Flask, request
import hmac, hashlib
import json
import azureauth
import teamschat
import misthandler


# Authenticate if a message was genuine
# Mist passes the 'X-Mist-Signature-v2' header, containing a hash; HMAC_SHA256(secret, body)
# Take the secret (as a string) and the complete webhook message





# Entry point
# Variables
WEB_PORT = 8080
WEBHOOK_SECRET = 'Password00'
client_code = ''


# Initialise a Flask app
app = Flask(__name__)


# Authenticate with Microsoft (for teams)
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
        ms_token = azureauth.get_token(client_code)

        # Change single quotes to double quotes (valid JSON)
        temp = str(ms_token).replace("'", "\"")

        # Write the token information to a file
        f = open("token.txt", "w")
        f.write(temp)
        f.close()

        return ('Thankyou for authenticating, this window can be closed')


# Mist web service - Listens for webhooks
@app.route("/mist", methods=['POST', 'GET'])
def mist():
    if request.method == 'POST':
        details = {}

        # Check that this webhook has come from a legitimate resource
        auth_result = misthandler.auth_message(WEBHOOK_SECRET, request)
        if auth_result == 'fail':
            print ("Received a webhook with a bad secret")
            return ('Webhook received, bad auth')
        elif auth_result == 'unauthenticated':
            print ("Unauthenticated webhook received")
            return ('Webhook received, no auth')

        # Parse the message
        match request.json['topic']:
            case 'device-events':
                for event in request.json['events']:
                    details['event'] = 'device_event'
                    details['name'] = event['device_name']
                    details['type'] = event['device_type']
                    details['mac'] = event['mac']
                    details['site'] = event['site_name']
                    details['type'] = event['type']
                    if 'text' in event:
                        details['text'] = event['text']
                    else:
                        details['text'] = 'no additional details available'
                    misthandler.handle_event(details)

            case 'alarms':
                for event in request.json['events']:
                    details['event'] = 'alarm'
                    details['count'] = event['count']
                    details['devices'] = event['hostnames']
                    details['site'] = event['site_name']
                    details['type'] = event['type']
                    misthandler.handle_event(details)

            case 'audits':
                for event in request.json['events']:
                    details['event'] = 'audit'
                    if 'admin_name' in event:
                        details['admin'] = event['admin_name']
                    details['task'] = event['message']
                    if 'site_name' in event:
                        details['site'] = event['site_name']
                    misthandler.handle_event(details)

            case 'device-updowns':
                for event in request.json['events']:
                    details['event'] = 'updown'
                    details['name'] = event['device_name']
                    details['device'] = event['device_type']
                    details['mac'] = event['mac']
                    details['site'] = event['site_name']
                    details['err_type'] = event['type']
                    misthandler.handle_event(details)

            case default:
                topic = request.json['topic']
                for event in request.json['events']:
                    details['event'] = topic
                    details['data'] = event
                    misthandler.handle_event(details)
                    print (request.json)

        return ('Webhook received')

    elif request.method == 'GET':
        return ('Web service is running. Please use the POST method to send a webhook')




# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=WEB_PORT)


