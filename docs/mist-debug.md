# Enabling debugging in Mist
Each plugin can optionally have a method to log information for debugging  
Logging can be enabled or disabled in mist-config.yaml  
A log file, mist_debug-<date>.log is created for each day  
  

## mistdebug.py
### logging_init()
Arguments: None  
Returns: A log file object  
Purpose: Creates a log, or opens an existing log for editing  
  
  
&nbsp;<br>
### log_cleanup()
Arguments: A log file object  
Returns: None  
Purpose: Gracefully close the log file  
  
  
&nbsp;<br>
### log_entry()
Arguments:  
  * message: The message to be logged  
  * file: An object representing an open file to write to  
Returns: None  
Purpose: Write a log entry to the open log file
  

    
    
