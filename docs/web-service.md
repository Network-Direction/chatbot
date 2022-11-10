# Web Service
  A web service runs continually, and listens for webhooks and authentication details  
  The web service is built in Flask  

## Routes
### /test
  Method: GET, HEAD  
  A simple route, used to test if the service is up  
  This can be polled by a monitoring solution  
   

&nbsp;<br>
### /mist
Method: POST  
This is where Mist webhooks are sent 
This also tracks the IP address of the webhook sender
* Uses the X-Forwarded-For header, if it exists (good if there's a reverse proxy in the path)
* Uses the IP address that sends to Flask, if the X-Forwarded-For header is not there


&nbsp;<br>
### /callback
  Method: GET  
  This is the callback point for authentication with the MS Identify Platform  
  During authentication, the client code will be sent here  
  This URL needs to be registered in the application on the Identity Platform (see ms-identity.txt)  


&nbsp;<br>
- - - -
## web-service.py
### To Do
  (1) Find out why users get presented with two authentication web screens when the process first starts  
  (2) Find an alternative to saving the token in a file; Variables don't work simply between Flask routes  


&nbsp;<br>
### Global
  (1) Read configuration file (using config.py), and set variables  
  (2) Initialize a Flask app  
  (3) Begin authentication  
  (4) Start the Flask routes  
