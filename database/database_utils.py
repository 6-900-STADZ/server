import sqlite3

def connect_to_database(db):
    conn = sqlite3.connect(db) # connect to the database (will create if it doesn't exist)
    cursor = conn.cursor() # move cursor into database (allows us to execute commands)
    return conn, cursor

def close_db_connection(conn):
    conn.close() # close connection to database 