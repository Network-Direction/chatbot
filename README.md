# chatbot
A simple chatbot that takes alerts and events, and sends them to teams


### Script Usage:
    Run this application with 'python web-service.py' to start a Flask instance
    Mist webhooks can be sent (POST) to /mist
    Test the application by browsing to /test
    Uses the MS Graph API to send chat messages to teams
    
### Authentication:
    This application needs to be registered in Microsoft Identity Centre, and a callback URL needs to be set
    Authentication uses OAuth 2.0; You need an application ID and a client secret
    The callback is set to /callback
    A teams user needs to login when the web-service runs, and approve access to teams

### Restrictions:
    Requires the Flask, msal, and requests modules to be installed with pip
    The MS bearer token is saved to disk, as read as needed
    HTTPS is not supported on the web service. Use a separate reverse proxy to add HTTPS
    Needs a public IP for webhooks to be sent to, and for the callback URL
    The public IP and port (tcp/8080 by default) needs to be allowed into the application (check firewall settings)

### To Do:
    - Add timestamps to events
    - See why a user sometimes gets prompted with two login pages
    - Find a more secure way to store the token
    - Find a more scalable way to filter output to teams
    - Enable Microsoft token refresh
    - Handle token errors (eg, a token can't be granted)
    - Check for errors when making API calls to Graph API (teams)
    - Dynamically get Chat ID and User ID, rather than hardcoding in a variable
    - Figure out how to make the teams chats look nicer

### Author:
    Luke Robertson - October 2022




