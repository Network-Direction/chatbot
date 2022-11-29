# SQL Database
Events are written to a database as they are received 
This is intended to be queried by a future module to find patterns, etc 
Currently tested with MSSQL only

&nbsp;<br>
## DB design
This can vary per plugin, but most will follow a design similar to this

Table Fields
------------

Event ID (primary key)  
* A unique ID to associate with each event  
* Type: char(12)  
* Allow null: no  

Device  
* The name of the device, if applicable, that generated the event  
* Type: text  
* Allow null: yes  

Site  
* The name of the site, if applicable, that the event was raised in  
* Type: text  
* Allow null: yes  

Event  
* The event itself, eg 'SW_CONNECTED'  
* Type: text  
* Allow null: no  

Description  
* A more detailed description of what happened (not all events will have these)  
* Type: text  
* Allow null: yes  

LogDate  
* The date of the event  
* Type: date  
* Allow null: no  

LogTime  
* The time of the event  
* Type: time  
* Allow null: no  

Source IP (only supports v4 for now)  
* The IP address that sent the alert  
* Type: binary(4)  
* Allow null: no  

Chat message ID  
* The ID, as set by the Graph API of the message sent to teams (not all will have a message sent)  
* Type: text  
* Allow null: yes  


&nbsp;<br>
- - - -
## sql.py
  Contains the Sql class, for writing events to the database.
  The methods are outlined below

&nbsp;<br>
### __init__()
  Gets the server name and DB name from the config file

### add()
Arguments:  
* table: The table to write to  
* fields: The entries to write  
Returns:  True if successful, False if not
Purpose:  
  Connect to the SQL server/database  
  Write entries to the database
  Gracefully close the connection
