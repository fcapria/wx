#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
from sqlite3 import Error 
 
def create_connection(db_file):
    # create connection to SQLite database
    con = None
    try:
        con = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)

    return con

def create_table(con, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = con.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

dbConnection = create_connection(r'test.db')


dbConnection.close()