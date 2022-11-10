# SQL Database
Events are written to a database as they are received 
This is intended to be queried by a future module to find patterns, etc 
Currently tested with MSSQL only

&nbsp;<br>
## DB design
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
## sql-create.py
A standalone script to create the table and fields
The server and database information is taken from config.yaml

### connect()
Arguments:  
* server: The SQL server to connect to  
* db: The database to connect to  
Returns:  'conn' and 'cursor' as a tuple  
* conn: The connection object to the SQL database  
* cursor: The object that commits changes  
Purpose:  Connect to an SQL server  

### close()
Arguments:  connector (the conn and cursor objects as a tuple)  
Returns:  none  
Purpose:  Gracefully close the connection to the SQL server/database  

### create_table()
Arguments:  
* table: The table to write to  
* fields: The fields (as a dictionary) to create  
* connector: The sql connection object (as a tuple)  
Returns:  True if successful, or False  
Purpose:  Creates the table and fields


&nbsp;<br>
- - - -
## sql.py
### To Do
  (1) Add logging to text file if global DEBUG=True  
  (2) Add a teardown function to Flask to gracefully close this connection  

&nbsp;<br>
### connect()
Arguments:  
* server: The SQL server to connect to  
* db: The database to connect to  
Returns:  'conn' and 'cursor' as a tuple  
* conn: The connection object to the SQL database  
* cursor: The object that commits changes  
Purpose:  Connect to an SQL server  

&nbsp;<br>
### close()
Arguments:  connector (the conn and cursor objects as a tuple)  
Returns:  none  
Purpose:  Gracefully close the connection to the SQL server/database  

&nbsp;<br>
### add()
Arguments:  
* table: The table name to write to  
* fields: The columns and values, passed as a dictionary  
* connector: The connection object (as a tuple) for the SQL server/DB  
Returns: True if successful, or False  
Purpose: Add event entries to the SQL server  
  
