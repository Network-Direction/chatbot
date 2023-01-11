# Teams Chat
MS Teams uses the MS Graph API  

&nbsp;<br>
## Sending Messages
    To send chat messages to teams from the chatbot, we must first be authenticated. See ms-identity.txt to understand this process  
    There is a simple function called send_chat() which will send a message to the Graph API, along with the bearer token  
    
## Talking to the Chatbot
    Users can send messages to the chatbot; This only has rudimentary functionality at this time (v0.6) for testing
    
### Change Notifications
    This requires us to subscribe to 'change notifications' for the resource (chat or group)
    When someone writes to the chat, the chatbot will get a notification via webhook
    Each resource requires its own subscription
    The subscription contains a callback URL that the webhook should be sent to
    When subscribing, GraphAPI will send authentication information to the callback URL to authenticate the subscription
    
### Refreshing
    Subscriptions are valid for up to an hour
      We select a duration while subscribing
    Before this expires, we need to request an extention
    This is done by sending a PATCH message to the API with a new renewal time

### Encrypted Webhooks
    The webhook contains the contents of the message in an encrypted format
    During the subscription process, we pass a public key to Graph API
      Message contents are encrypted with this public key
      We can decrypt the messages with our private key
    MS will create a session key and encrypt the message with that
      The session key is different for each message
    The session key is encrypted with our public key        


&nbsp;<br>
- - - -
## teamschat.py
### send_chat()
Arguments: message  
* This is the text that we want to send to teams, formatted as HTML  
Returns: None  
Purpose:  
  (1) Reads the token from token.txt, and confirms it is valid  
  (2) Connect to the Graph API using the requests module  
  (3) Check the response, and handle 401 and 429 errors  
  


&nbsp;<br>
- - - -
## crypto.py


&nbsp;<br>
- - - -
## parse_chats.py


&nbsp;<br>
- - - -
## smtp.py
Used to alert someone if there's problems sending over teams  
This is not intended to be used for regular notifications  

### send_mail()
Arguments: message  
* The message that should be converted to an email  

Returns: None  
Purpose: Takes a message, and converts it to MIMEText. Then sends email using the details in config.yaml  



