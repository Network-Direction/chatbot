# Web Service
  A web service runs continually, and listens for webhooks and authentication details  
  The web service is built in Flask  

## Routes
### /test
  Method: GET, HEAD  
  A simple route, used to test if the service is up  
  This can be polled by a monitoring solution  
   

&nbsp;<br>
### <handler>
Method: POST  
This is a dynamic route, which is created based on plugins   
Webhooks are sent to this location, and then authenticated using a header, as specified by the plugin   
The plugins handler method is called to deal with the webhook


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
  Find an alternative to saving the token in a file; Variables don't work simply between Flask routes  


&nbsp;<br>
### Global
  (1) Read configuration file (using config.py), and set variables  
  (2) Initialize a Flask app  
  (3) Begin authentication  
  (4) Load plugins
  (5) Start the Flask routes  
