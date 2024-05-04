import mysql.connector
from config import central_db_params

def create_central_database():
    connection = None  # Initialize connection variable
    try:
        # Establish a connection to the MySQL server without specifying a database
        connection = mysql.connector.connect(
            host=central_db_params["host"],
            user=central_db_params["user"],
            password=central_db_params["password"]
        )
        cursor = connection.cursor()

        # Create the central_db database if it doesn't exist
        create_database_query = "CREATE DATABASE IF NOT EXISTS central_db;"
        cursor.execute(create_database_query)

        # Commit the transaction
        connection.commit()

        # Close the cursor and connection
        cursor.close()
        connection.close()

        print("Central database (central_db) created successfully.")
    except mysql.connector.Error as err:
        print(f"Error creating or connecting to central database: {err}")

def create_stores_table():
    connection = None
    try:
        # Establish a connection to the central database
        connection = mysql.connector.connect(**central_db_params)
        cursor = connection.cursor()

        create_stores_table_query = """
            CREATE TABLE IF NOT EXISTS Stores (
                store_code VARCHAR(50) PRIMARY KEY,
                address TEXT,
                opening_time TIME,
                closing_time TIME,
                x FLOAT,
                y FLOAT
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

# Call the functions to create the central database and stores table
create_central_database()
create_stores_table()
