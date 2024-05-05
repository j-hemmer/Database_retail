# Description: This file contains a function for searching items in a sharded MySQL database environment. The
# search_items function allows users to search for items based on various criteria such as item name, store code,
# availability, price range, and sorting preferences.
#
# Functions: - get_shard(store_code): This function determines the correct shard based on the given store code. It
# calculates the shard ID using the modulo operation on the store code and the total number of shards.
#
# - search_items(item_name, store_code, in_stock, price_min=None, price_max=None, sort=0): This function searches for
# items in the Customer_Portal table based on the provided parameters. It constructs a SQL query dynamically based on
# the search criteria and executes it on the corresponding shard. The search criteria include item name, store code,
# availability status, price range, and sorting preferences. The function returns the search results, including item
# details such as store address, item name, price, and availability.
#
# Note: This file assumes the existence of Customer_Portal and Stores tables in each shard database,
# which are interconnected by store codes.



import mysql.connector
from config import shard_connections, central_db_params

# Function to get the correct shard based on store_code
def get_shard(store_code):
    # Assuming number of shards is equal to the length of shard_connections
    store_code = int(store_code)
    num_shards = len(shard_connections)
    return store_code % num_shards

def search_items(item_name, store_code, in_stock, price_min=None, price_max=None, sort=0):
    shard_id = get_shard(store_code)
    shard_connection_params = shard_connections[shard_id]

    # Construct the WHERE clause based on the provided parameters
    where_clause = "WHERE Customer_Portal.store_code = %s AND Customer_Portal.in_stock = %s"
    where_params = [store_code, in_stock]

    if item_name:
        where_clause += " AND Customer_Portal.item_name = %s"
        where_params.append(item_name)

    if price_min is not None:
        where_clause += " AND price >= %s"
        where_params.append(price_min)

    if price_max is not None:
        where_clause += " AND price <= %s"
        where_params.append(price_max)

    # Construct the ORDER BY clause based on the provided sort parameter
    if sort == 0:
        order_by_clause = "ORDER BY price DESC"
    elif sort == 1:
        order_by_clause = "ORDER BY price ASC"
    else:
        order_by_clause = ""

    # Construct the SQL query
    sql_query = f"""
        SELECT Stores.address, item_name, price, in_stock
        FROM Customer_Portal
        JOIN Stores ON Stores.store_code = Customer_Portal.store_code
        {where_clause}
        {order_by_clause}
    """

    # Execute the query and fetch the results
    try:
        shard_connection = mysql.connector.connect(**shard_connection_params)
        cursor = shard_connection.cursor()
        cursor.execute(sql_query, tuple(where_params))
        results = cursor.fetchall()
        return results
    except mysql.connector.Error as err:
        print(f"Error executing SQL query: {err}")
    finally:
        if cursor:
            cursor.close()
        if shard_connection:
            shard_connection.close()


# Modify get_store_options function to fetch both store ID and address
def get_store_options():
    try:
        connection = mysql.connector.connect(**central_db_params)
        cursor = connection.cursor()

        # Execute the query to select store codes and addresses
        query = "SELECT store_code, address FROM stores"
        cursor.execute(query)

        # Fetch all rows
        store_records = cursor.fetchall()

        return store_records

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