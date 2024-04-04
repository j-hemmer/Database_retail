# central_creation.py
import mysql.connector
from config import central_db_params

def create_central_database():
    try:
        connection = mysql.connector.connect(**central_db_params)
        cursor = connection.cursor()

        create_database_query = "CREATE DATABASE IF NOT EXISTS central_db;"

        cursor.execute(create_database_query)
        connection.commit()

        print("Central database (central_db) created successfully.")
    except mysql.connector.Error as err:
        print(f"Error creating central database: {err}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def create_stores_table():
    try:
        connection = mysql.connector.connect(**central_db_params)
        cursor = connection.cursor()

        create_stores_table_query = """
        CREATE TABLE IF NOT EXISTS Stores (
            store_code VARCHAR(50) PRIMARY KEY,
            address TEXT,
            opening_time TIME,
            closing_time TIME
        )
        """

        cursor.execute(create_stores_table_query)
        connection.commit()

        print("Stores table created successfully in the central database (central_db).")
    except mysql.connector.Error as err:
        print(f"Error creating stores table: {err}")
    finally:
        if connection:
            cursor.close()
            connection.close()

create_central_database()
create_stores_table()
