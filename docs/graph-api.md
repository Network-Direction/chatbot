# Teams Chat
MS Teams uses the MS Graph API  

## Overview
  To send chat messages to teams, we must first be authenticated. See ms-identity.txt to understand this process  
  There is a simple function called send_chat() which will send a message to the Graph API, along with the bearer token  
    
## teamschat.py
### To Do
  (1) Dynamically get the chat ID  
  (2) Dynamically get the user ID  

### send_chat()
  Arguments: message  
    This is the text that we want to send to teams, formatted as HTML  
  Returns: None  
  Purpose:  
    (1) Reads the token from token.txt, and confirms it is valid  
    (2) Connect to the Graph API using the requests module  
    (3) Check the response, and handle 401 and 429 errors  
  
