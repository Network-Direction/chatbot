"""
Logs webhooks to a file on disk
A log file is created in the root applicaiton directory

Usage:
    import 'mistdebug' into the misthandler

Authentication:
    None

Restrictions:
    None

To Do:
    None

Author:
    Luke Robertson - November 2022
"""

from datetime import datetime
from config import GRAPH


# This is the start of the filename
PRELUDE = 'mist_debug-'


# Log results and errors to a file
def log_entry (message, file):
    '''
    Takes a message as a string, and a file object
    Logs an entry to this file
    '''
    file.write ('\n' + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + ' ' + message)


# Cleanup and exit when there's errors, or the script finishes
def log_cleanup(logfile):
    '''Gracefully closes the log file'''
    logfile.close()


# Prepare logging
def logging_init():
    '''
    Initializes a logfile, using the current data
    Returns the file object
    '''
    date = datetime.today().date()
    log = open(PRELUDE + str(date) + '.log', 'a+')
    log_entry ("Begin logging", log)
    
    # Return the log object
    return log



