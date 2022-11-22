'''
[edit system]
scripts {
    language python3;
}

[edit event-options]
policy Webhooks {
    events LICENSE_EXPIRED_KEY_DELETED;
    then {
        event-script junos-agent.py {
            arguments {
                url <DESTINATION>;          <<< The URL to send webhooks to
                secret <SECRET>;            <<< The webhooks secret
            }
        }
    }
}
event-script {
    file junos-agent.py {
        python-script-user admin;
        checksum sha-256 xxxx;              <<< use 'file checksum sha-256 FILENAME' to get the checksum of this file
    }
}

https://www.juniper.net/documentation/us/en/software/junos/automation-scripting/topics/concept/junos-script-automation-event-script-input.html


Assumes junos 21.2R1 and later

'''


import requests
import json
import argparse
import hmac
import hashlib

from junos import Junos_Trigger_Event


# Create a hash, using the body of the request, and a secret
def create_hash(body, secret):
    return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()


# Setup arguments
helpmsg = "Junos webhooks agent"
parser = argparse.ArgumentParser(description=helpmsg)

parser.add_argument("-url", help="URL to send webhooks to")
parser.add_argument("-secret", help="URL to send webhooks to")
args = parser.parse_args()


# Data to send
event = Junos_Trigger_Event.xpath('//trigger-event/id')[0].text
process = Junos_Trigger_Event.xpath('//trigger-event/process/name')[0].text
message = Junos_Trigger_Event.xpath('//trigger-event/message')[0].text
hostname = Junos_Trigger_Event.xpath('//trigger-event/hostname')[0].text


data = {
    'event': event,
    'process': process,
    'message': message,
    'hostname': hostname,
}
body = json.dumps(data)
auth_header = create_hash(body, args.secret)


# Send information as a webhook
req = requests.post(
    args.url,
    data=body,
    headers={
        'Content-type': 'application/json',
        'Junos-Auth': auth_header
    }
)
