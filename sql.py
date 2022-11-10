"""
Creates entries in the database

Usage:
    Call when an event comes in that needs handling

Authentication:
    Requires permissions to access the database

Restrictions:
    Requires the 'pyodbc' module (install with pip)
    Requires a database to be available, as well as tables and fields (see sql-create.py script)

To Do:
    Add logging to text file if global DEBUG=True
    Add a teardown function to Flask to gracefully close this connection
    Add docstrings

Author:
    Luke Robertson - November 2022
"""

import pyodbc
from config import GLOBAL



# Connect to a database
#   Return the two SQL objects in a tuple
#   Return False if there's an error
def connect(server, db):
    '''
    Connects to an MSSQL database
    Pass the server name and the DB name
    Returns a connection object; This is a tuple containing the cursor and connection
    '''
    try:
        conn = pyodbc.connect (
            'Driver={SQL Server};'
            'Server=%s;'
            'Database=%s;'
            'Trusted_Connection=yes;'
            % (server, db))

    except pyodbc.DataError as e:
        print ("A data error has occurred")
        print (e)
        return False

    except pyodbc.OperationalError as e:
        print ("An operational error has occurred while connecting to the database")
        print ("Make sure the specified server is correct, and that you have permissions")

        # Parse the error code and message
        error = str(e).split(",", 1)[1].split(";")[0].split("[")
        code = error[1].replace("] ", "")
        message = error[4].split("]")[1].split(".")[0]

        # Print the error, and end the script
        print (f"Error code: {code}\n{message}")
        return False
        
    except pyodbc.IntegrityError as e:
        print ("An Integrity error has occurred")
        print (e)
        return False
        
    except pyodbc.InternalError as e:
        print ("An internal error has occurred")
        print (e)
        return False
        
    except pyodbc.ProgrammingError as e:
        print ("A programming error has occurred")
        print ("Check that the database name is correct, and that the database exists")

        # Parse the error code and message
        error = str(e).split(",", 1)[1].split(";")[0].split("[")
        code = error[1].replace("] ", "")
        message = error[4].split("]")[1].split(".")[0]

        # Print the error, and end the script
        print (f"Error code: {code}\n{message}")
        return False
        
    except pyodbc.NotSupportedError as e:
        print ("A 'not supported' error has occurred")
        print (e)
        return False
        
    except pyodbc.Error as e:
        print ("A generic error has occurred")
        print (e)
        return False

    cursor = conn.cursor ()

    return conn, cursor



# Neatly close the connection to the database
def close(connector):
    '''
    Neatly close the connection to the database
    Pass the connection object; The tuple with the connection and cursor objects
    '''
    connector[1].close()
    connector[0].close()


# Add data to a table
# Pass the table name and a dictionary of columns to update and their values
def add(table, fields, connector):
    '''
    Add data to a table
    Pass the table name, the fields to write, and the connector object of the database
    Returns True if successful, and False if not
    '''
    
    # Create empty strings for columns and corresponding values
    columns = ''
    values = '('

    # Populate the columns and values
    for field in fields:
        columns += field + ', '
        values += str(fields[field]) + ', '

    # Clean up the trailing comma, to make this valid
    columns = columns.strip(", ")
    values = values.strip(", ")

    # Build the correct string
    sql_string = f'INSERT INTO {table} ('
    sql_string += columns
    sql_string += ')'

    sql_string += '\nVALUES '
    sql_string += values + ');'

    if GLOBAL['flask_debug']:
        print ("DEBUG (sql.py):", sql_string)

    try:
        connector[1].execute(sql_string)
    except Exception as e:
        print ("SQL execution error")
        error = str(e).split(",", 1)[1].split(";")[0].split("[")
        code = error[1].replace("] ", "")

        print (code, error)

        if code == str(42000):
            print ("Programming error. Check that there are no typos in the SQL syntax")
        elif code == str(22001):
            print ("Check that the data you're writing fits the field (eg, putting a large string in a char(5)")
        elif code == str(22018):
            print ("Check that you're using a date object, not an integer")
        elif code == str(23000):
            print ("You're trying to write a primary key that already exists in the DB")
        return False

    try:
        connector[0].commit()
    except Exception as e:
        print ("SQL commit error")
        print (e)
        return False

    return True


