# shard_creation.py
import mysql.connector
from config import shard_connections

def connect_to_shard(connection_params):
    try:
        connection = mysql.connector.connect(**connection_params)
        print(f"Connected to {connection_params['database']} successfully.")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to {connection_params['database']}: {err}")
        return None

def create_database(connection_params):
    try:
        connection = mysql.connector.connect(
            host=connection_params['host'],
            user=connection_params['user'],
            password=connection_params['password']
        )
        cursor = connection.cursor()

        create_database_query = f"CREATE DATABASE IF NOT EXISTS {connection_params['database']};"
        cursor.execute(create_database_query)
        connection.commit()

        print(f"Database {connection_params['database']} created successfully.")
    except mysql.connector.Error as err:
        print(f"Error creating database {connection_params['database']}: {err}")
    finally:
        if connection:
            cursor.close()
            connection.close()

def create_table(connection, table_query):
    try:
        cursor = connection.cursor()
        cursor.execute(table_query)
        connection.commit()
        print(f"Table created successfully.")
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")
    finally:
        if connection:
            cursor.close()

def create_databases_and_tables():
    for shard_id, connection_params in shard_connections.items():
        create_database(connection_params)
        connection = connect_to_shard(connection_params)
        if connection:
            try:
                create_table_queries = [
                    """
                    CREATE TABLE IF NOT EXISTS Stores (
                        store_code VARCHAR(50) PRIMARY KEY,
                        address TEXT,
                        opening_time TIME,
                        closing_time TIME
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS Vendor (
                        item_code VARCHAR(50),
                        store_code VARCHAR(50),
                        item_name VARCHAR(50),
                        quantity INT,
                        price DECIMAL(6, 2),
                        PRIMARY KEY(item_code, store_code),
                        FOREIGN KEY(store_code) REFERENCES Stores(store_code)
                    )
                    """,
                    """
                    CREATE TABLE IF NOT EXISTS Customer_Portal (
                        item_code VARCHAR(50),
                        store_code VARCHAR(50),
                        item_name VARCHAR(50),
                        price DECIMAL(6, 2),
                        in_stock BOOLEAN,
                        PRIMARY KEY(item_code, store_code),
                        FOREIGN KEY(store_code) REFERENCES Stores(store_code),
                        FOREIGN KEY(item_code) REFERENCES Vendor(item_code)
                    )
                    """
                ]
                for query in create_table_queries:
                    create_table(connection, query)
            finally:
                connection.close()

create_databases_and_tables()
