
# Description: This file contains functions for managing retail operations in a sharded MySQL database environment.
# The functions handle various tasks related to store management, item stocking, price adjustments,
# and item filtering across multiple shards.
#
# Functions: - get_shard(store_code): This function determines the correct shard based on the given store code. It
# calculates the shard ID using the modulo operation on the store code and the total number of shards.
#
# - connect_to_database(connection_params): This function establishes a database connection using the provided
# connection parameters. It uses the mysql.connector library to connect to the MySQL database.
#
# - insert_store(store_code, address, opening_time, closing_time): This function inserts a new store into both shard
# and central databases. It takes store details such as store code, address, opening time, and closing time as
# parameters and inserts them into the Stores table in both shard and central databases.
#
# - update_hours(store_code, opening_time, closing_time): This function updates the opening and closing hours of an
# existing store in both shard and central databases. It takes the store code, new opening time, and new closing time
# as parameters and updates the corresponding records in the Stores table in both shard and central databases.
#
# - stock_new_item(item_code, store_code, item_name, quantity, price): This function adds a new item to the Vendor
# table in the shard database and updates the Customer_Portal table based on its quantity. It inserts a new record
# into the Vendor table with details such as item code, store code, item name, quantity, and price. Additionally,
# it inserts a corresponding record into the Customer_Portal table with information about the item's availability.
#
# - restock_item(item_code, store_code, quantity): This function updates the quantity of an existing item in both the
# Vendor and Customer_Portal tables. It takes parameters such as item code, store code, and new quantity, and updates
# the quantity field in the Vendor table. It also updates the in_stock field in the Customer_Portal table based on
# the new quantity.
#
# - price_change(item_code, store_code, price): This function updates the price of an existing item in both the
# Vendor and Customer_Portal tables. It takes parameters such as item code, store code, and new price, and updates
# the price field in the Vendor table. It also updates the price field in the Customer_Portal table.
#
# - remove_item(item_code, store_code): This function removes an item from both the Vendor and Customer_Portal
# tables. It takes parameters such as item code and store code, and deletes the corresponding record from both tables.
#
# - filter_items(store_codes, item_codes, item_names, out_of_stock): This function filters items based on store
# codes, item codes, item names, and availability. It retrieves records from the Vendor table in the shard database
# based on the provided criteria and returns the filtered results.
#
# Note: This file assumes the existence of Vendor and Customer_Portal tables in each shard database,
# which are interconnected by store codes.


import mysql.connector
from config import shard_connections, central_db_params

# Function to get the correct shard based on store_code
def get_shard(store_code):
    # Assuming number of shards is equal to the length of shard_connections
    store_code = int(store_code)
    num_shards = len(shard_connections)
    return store_code % num_shards

# Function to establish a database connection
def connect_to_database(connection_params):
    try:
        connection = mysql.connector.connect(**connection_params)
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        return None

# Function to insert a new store
def insert_new_store(store_code, address, opening_time, closing_time, x, y):
    shard_id = get_shard(store_code)
    shard_connection_params = shard_connections.get(shard_id)  # Directly access connection params using shard ID
    central_connection_params = central_db_params

    shard_connection = connect_to_database(shard_connection_params)
    central_connection = connect_to_database(central_connection_params)

    if shard_connection and central_connection:
        shard_cursor = None
        central_cursor = None  # Initialize the variables outside the try block

        try:
            # Insert the values into the database

            # needs to be [25, 85]
            if float(y) not in range(25, 86):
                y = None
            # needs to be [-120, -50]
            if float(x) not in range(-120, -49):
                x = None
            # Insert into shard database
            shard_cursor = shard_connection.cursor()
            insert_store_query = """
            INSERT INTO Stores (store_code, address, opening_time, closing_time, x, y)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            shard_cursor.execute(insert_store_query, (store_code, address, opening_time, closing_time, x, y))
            shard_connection.commit()

            # Insert into central database
            central_cursor = central_connection.cursor()
            insert_central_query = """
            INSERT INTO Stores (store_code, address, opening_time, closing_time, x, y)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            central_cursor.execute(insert_central_query, (store_code, address, opening_time, closing_time, x, y))
            central_connection.commit()

            print("Store inserted successfully.")
        except mysql.connector.Error as err:
            print(f"Error inserting store: {err}")
        finally:
            if shard_cursor:
                shard_cursor.close()
            if central_cursor:
                central_cursor.close()
            if shard_connection:
                shard_connection.close()
            if central_connection:
                central_connection.close()



def get_stores():
    try:
        connection = mysql.connector.connect(**central_db_params)
        cursor = connection.cursor()

        # Execute the query to select store codes
        query = "SELECT store_code FROM stores"
        cursor.execute(query)

        # Fetch all rows
        store_records = cursor.fetchall()

        # Extract store codes from the fetched records
        store_codes = [record[0] for record in store_records]

        return store_codes

    except mysql.connector.Error as err:
        # Handle any database errors
        print(f"Error fetching store information: {err}")
        return []

    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Function to update existing store's hours
def update_store_hours(store_code, opening_time, closing_time):
    shard_id = get_shard(store_code)
    shard_connection_params = shard_connections[shard_id]
    central_connection_params = central_db_params

    shard_connection = connect_to_database(shard_connection_params)
    central_connection = connect_to_database(central_connection_params)

    if shard_connection and central_connection:
        try:
            # Update in shard database
            shard_cursor = shard_connection.cursor()
            update_hours_query = """
            UPDATE Stores
            SET opening_time = %s, closing_time = %s
            WHERE store_code = %s
            """
            shard_cursor.execute(update_hours_query, (opening_time, closing_time, store_code))
            shard_connection.commit()

            # Update in central database
            central_cursor = central_connection.cursor()
            update_central_query = """
            UPDATE Stores
            SET opening_time = %s, closing_time = %s
            WHERE store_code = %s
            """
            central_cursor.execute(update_central_query, (opening_time, closing_time, store_code))
            central_connection.commit()

            print("Store hours updated successfully.")
            return True  # Return True if the update is successful
        except mysql.connector.Error as err:
            print(f"Error updating store hours: {err}")
            return False  # Return False if there's an error
        finally:
            if shard_connection:
                shard_cursor.close()
                shard_connection.close()
            if central_connection:
                central_cursor.close()
                central_connection.close()
    else:
        return False  # Return False if the connections couldn't be established

def remove_store(store_code):
    shard_id = get_shard(store_code)
    shard_connection_params = shard_connections[shard_id]
    central_connection_params = central_db_params

    shard_connection = connect_to_database(shard_connection_params)
    central_connection = connect_to_database(central_connection_params)

    if shard_connection and central_connection:
        try:
            # Update in shard database
            shard_cursor = shard_connection.cursor()
            delete_store_query = """
            DELETE
            FROM Stores
            WHERE store_code = %s
            """
            shard_cursor.execute(delete_store_query, (store_code,))
            shard_connection.commit()

            # Update in central database
            central_cursor = central_connection.cursor()
            delete_central_query = """
            DELETE
            FROM Stores
            WHERE store_code = %s
            """
            central_cursor.execute(delete_central_query, (store_code,))
            central_connection.commit()

            print("Store deleted successfully.")
        except mysql.connector.Error as err:
            print(f"Error deleting store: {err}")
        finally:
            if shard_connection:
                shard_cursor.close()
                shard_connection.close()
            if central_connection:
                central_connection.close()


def stock_new_item(item_code, store_code, item_name, quantity, price):
    shard_id = get_shard(store_code)
    shard_connection_params = shard_connections[shard_id]

    shard_connection = connect_to_database(shard_connection_params)

    if shard_connection:
        try:
            # insert new item into shard table
            shard_cursor = shard_connection.cursor()
            insert_item_query = """
            INSERT INTO Vendor(item_code, store_code, item_name, quantity, price) VALUES(%s, %s, %s, %s, %s)
            """
            shard_cursor.execute(insert_item_query, (item_code, store_code, item_name, quantity, price))
            if quantity > 0:
                insert_item_query = """
                INSERT INTO Customer_Portal(item_code, store_code, item_name, price, in_stock) VALUES(%s, %s, %s, %s, %s)
                """
                shard_cursor.execute(insert_item_query, (item_code, store_code, item_name, price, True))
            else:
                insert_item_query = """
                INSERT INTO Customer_Portal(item_code, store_code, item_name, price, in_stock) VALUES(%s, %s, %s, %s, %s)
                """
                shard_cursor.execute(insert_item_query, (item_code, store_code, item_name, price, False))
            shard_connection.commit()

            print(f"{item_name} has been added to store {store_code}")
        except mysql.connector.Error as err:
            print(f"Error inserting item: {err}")
        finally:
            if shard_connection:
                shard_cursor.close()
                shard_connection.close()

def restock_item(item_code, store_code, quantity):
    shard_id = get_shard(store_code)
    shard_connection_params = shard_connections[shard_id]

    shard_connection = connect_to_database(shard_connection_params)

    if shard_connection:
        try:
            # Update quantity of existing goods in Vendor table
            shard_cursor = shard_connection.cursor()
            update_vendor_query = """
                UPDATE Vendor
                SET quantity = %s
                WHERE item_code = %s AND store_code = %s
                """
            shard_cursor.execute(update_vendor_query, (quantity, item_code, store_code))
            shard_connection.commit()

            # Update quantity of existing goods in Customer_Portal table
            update_customer_portal_query = """
                UPDATE Customer_Portal
                SET in_stock = %s
                WHERE item_code = %s AND store_code = %s
                """
            shard_cursor.execute(update_customer_portal_query, (quantity > 0, item_code, store_code))
            shard_connection.commit()

            print(f"{item_code}'s quantity has been updated in store {store_code}")
        except mysql.connector.Error as err:
            print(f"Error updating stock for item: {err}")
        finally:
            if shard_connection:
                shard_cursor.close()
                shard_connection.close()

def price_change(item_code, store_code, price):
    shard_id = get_shard(store_code)
    shard_connection_params = shard_connections[shard_id]

    shard_connection = connect_to_database(shard_connection_params)

    if shard_connection:
        try:
            # Update price of existing good in Vendor table
            shard_cursor = shard_connection.cursor()
            update_vendor_query = """
                UPDATE Vendor
                SET price = %s
                WHERE item_code = %s AND store_code = %s
                """
            shard_cursor.execute(update_vendor_query, (price, item_code, store_code))
            shard_connection.commit()

            # Update price of existing good in Customer_Portal table
            update_customer_portal_query = """
                UPDATE Customer_Portal
                SET price = %s
                WHERE item_code = %s AND store_code = %s
                """
            shard_cursor.execute(update_customer_portal_query, (price, item_code, store_code))
            shard_connection.commit()

            print(f"{item_code}'s price has been updated in store {store_code}")
        except mysql.connector.Error as err:
            print(f"Error updating price for item: {err}")
        finally:
            if shard_connection:
                shard_cursor.close()
                shard_connection.close()

def remove_item(item_code, store_code):
    shard_id = get_shard(store_code)
    shard_connection_params = shard_connections[shard_id]

    shard_connection = connect_to_database(shard_connection_params)

    if shard_connection:
        try:
            # Delete item from Customer_Portal table first
            shard_cursor = shard_connection.cursor()
            delete_customer_portal_query = """
                            DELETE FROM Customer_Portal
                            WHERE item_code = %s AND store_code = %s
                            """
            shard_cursor.execute(delete_customer_portal_query, (item_code, store_code))
            shard_connection.commit()

            # Delete item from Vendor table after Customer_Portal deletion
            delete_vendor_query = """
                            DELETE FROM Vendor
                            WHERE item_code = %s AND store_code = %s
                            """
            shard_cursor.execute(delete_vendor_query, (item_code, store_code))
            shard_connection.commit()

            print(f"{item_code} has been removed from store {store_code}")
        except mysql.connector.Error as err:
            print(f"Error removing item: {err}")
        finally:
            if shard_connection:
                shard_cursor.close()
                shard_connection.close()

def view_items(store_code, item_code, item_name):
    shard_id = get_shard(store_code)
    shard_connections_params = shard_connections[shard_id]

    shard_connection = connect_to_database(shard_connections_params)

    if shard_connection:
        try:
            shard_cursor = shard_connection.cursor()

            if not any([item_code, item_name]):
                # If none of the fields are entered, return all items from the specified store_code
                filter_items_query = """
                                    SELECT item_code, item_name, quantity, price FROM Vendor
                                    WHERE store_code = %s
                                    """
                shard_cursor.execute(filter_items_query, (store_code,))
            else:
                filter_items_query = """
                                    SELECT item_code, item_name, quantity, price FROM Vendor
                                    WHERE store_code = %s AND (item_code = %s OR item_name = %s)
                                    """
                shard_cursor.execute(filter_items_query, (store_code, item_code, item_name))

            items = shard_cursor.fetchall()
            shard_connection.commit()

            print(f"Filtering")
            return items
        except mysql.connector.Error as err:
            print(f"Error filtering: {err}")
            return []
        finally:
            if shard_connection:
                shard_cursor.close()
def get_points_from_database():
    shard_connection_params = central_db_params  # Assuming points are stored in the central database
    connection = connect_to_database(shard_connection_params)

    if connection:
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT x, y, address, opening_time, closing_time, store_code FROM Stores")
            points = cursor.fetchall()
            return points
        except mysql.connector.Error as err:
            print(f"Error fetching points from database: {err}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return []

def fetch_store_data(store_id):
    shard_id = get_shard(store_id)
    shard_connection_params = shard_connections[shard_id]

    connection = connect_to_database(shard_connection_params)

    if connection:
        try:
            cursor = connection.cursor()
            sql = "SELECT * FROM Stores WHERE store_code = %s"
            val = (store_id,)
            cursor.execute(sql, val)
            result = cursor.fetchall()
            return result
        except mysql.connector.Error as err:
            print(f"Error fetching store data: {err}")
            return []
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
    else:
        return []



