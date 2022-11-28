"""
Creates entries in the database

Usage:
    Call when an event comes in that needs handling

Authentication:
    Requires permissions to access the database

Restrictions:
    Requires the 'pyodbc' module (install with pip)
    Requires a database to be available, as well as tables and fields
        (see sql-create.py script)

To Do:
    Add logging to text file if global DEBUG=True
    Add a teardown function to Flask to gracefully close this connection

Author:
    Luke Robertson - November 2022
"""

import pyodbc
from config import GLOBAL
from core import teamschat


class Sql():
    def __init__(self):
        self.server = GLOBAL['db_server']
        self.db = GLOBAL['db_name']

    def add(self, table, fields):
        # Create empty strings for columns and corresponding values
        columns = ''
        values = '('

        # Populate the columns and values
        for field in fields:
            columns += field + ', '
            values += str(fields[field]) + ', '
        # print(f"DEBUG (Values): {values}")

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
            print("DEBUG (sql.py):", sql_string)

        # Connect to db using 'with' (gracefully closes when done)
        with pyodbc.connect(
                'Driver={SQL Server};'
                'Server=%s;'
                'Database=%s;'
                'Trusted_Connection=yes;'
                % (self.server, self.db)) as self.conn:
            self.cursor = self.conn.cursor()

            try:
                self.cursor.execute(sql_string)
            except Exception as e:
                print("SQL execution error")
                print(e)
                teamschat.send_chat(
                    "An error has occurred while writing to SQL"
                )
                return False

            try:
                self.conn.commit()
            except Exception as e:
                print("SQL commit error")
                print(e)
                teamschat.send_chat(
                    "An error has occurred while writing to SQL"
                )
                return False
        return True
