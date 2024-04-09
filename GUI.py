import tkinter as tk
from tkinter import messagebox
import mysql.connector
from config import shard_connections, central_db_params
from datetime import datetime


def get_shard(store_code):
    # Assuming number of shards is equal to the length of shard_connections
    # Store code needs to be an integer
    # Num shards is 2 I believe
    # just going to use 2
    # num_shards = len(shard_connections)
    return (int(store_code) % 2)+ 1

def connect_to_database(shard):
    # Connects to the central_db database
    try:
        global mydb
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dsci551",
            database=f"shard{shard}_db"
        )
        # Message shows which database it is going into
        messagebox.showinfo("Success", f"Using: shard{shard}_db")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error connecting to MySQL database: {err}")

def insert_store():
    #When user clicks insert store, it comes up with the entry boxes
    #When they click the insert store button, it connects to the appropriate database based on the defined shard function

    global store_code_entry, address_entry, opening_time_entry, closing_time_entry

    # Hide the insert button
    insert_button.pack_forget()

    # Entry fields for store information
    tk.Label(root, text="Store Code:").pack()
    store_code_entry = tk.Entry(root)
    store_code_entry.pack()

    tk.Label(root, text="Address:").pack()
    address_entry = tk.Entry(root)
    address_entry.pack()

    tk.Label(root, text="Opening Time (HH:MM:SS):").pack()
    opening_time_entry = tk.Entry(root)
    opening_time_entry.pack()

    tk.Label(root, text="Closing Time (HH:MM:SS):").pack()
    closing_time_entry = tk.Entry(root)
    closing_time_entry.pack()

    
    # Insert store information button
    insert_store_button = tk.Button(root, text="Insert Store Information", command=perform_store_insertion)
    insert_store_button.pack(pady=10)

def perform_store_insertion():
    # After entering the values, inserts the information for the store code

    try:
        store_code = store_code_entry.get()
        # Get the shard based on the store_code
        shard = get_shard(store_code)
        address = address_entry.get()
        opening_time = opening_time_entry.get()
        closing_time = closing_time_entry.get()
        connect_to_database(shard)
        cursor = mydb.cursor()
        sql = "INSERT INTO Stores (store_code, address, opening_time, closing_time) VALUES (%s, %s, %s, %s)"
        val = (store_code, address, opening_time, closing_time)
        cursor.execute(sql, val)
        mydb.commit()
        closing_time_entry.delete(0, tk.END)
        opening_time_entry.delete(0, tk.END)
        address_entry.delete(0, tk.END)

        messagebox.showinfo("Success", "Store information inserted successfully!")
        cursor.close()
        mydb.close()
        reset_gui()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error inserting store information into MySQL database: {err}")

#Update hours
# Sets up the boxes for user to insert the store code, opening and closing hours
#Confirmation button activates the sql query
def update_hours():
    global store_id_entry, opening_hours_entry, closing_hours_entry
    # Hide the update button
    update_button.pack_forget()

    # Entry fields for store ID, opening hours, and closing hours
    tk.Label(root, text="Store ID:").pack()
    store_id_entry = tk.Entry(root)
    store_id_entry.pack()

    tk.Label(root, text="Opening Hours (HH:MM:SS):").pack()
    opening_hours_entry = tk.Entry(root)
    opening_hours_entry.pack()

    tk.Label(root, text="Closing Hours (HH:MM:SS):").pack()
    closing_hours_entry = tk.Entry(root)
    closing_hours_entry.pack()

    update_hours_button = tk.Button(root, text="Update Store Hours", command=update_store_hours)
    update_hours_button.pack(pady=10)

def update_store_hours():
    try:
        shard_id = get_shard(store_id_entry.get())
        connect_to_database(shard_id)
        cursor = mydb.cursor()
        store_id = store_id_entry.get()
        opening_hours = str(opening_hours_entry.get())
        closing_hours = str(closing_hours_entry.get())
        sql = "UPDATE Stores SET opening_time = %s, closing_time = %s WHERE store_code = %s"
        val = (f'{opening_hours}', f'{closing_hours}', f'{store_id}')
        cursor.execute(sql, val)
        mydb.commit()
        messagebox.showinfo("Store hours updated successfully")
        cursor.close()
        mydb.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error updating store hours in MySQL database: {err}")


def fetch_data():
    global store_id_entry, result_label, confirm_button, store_id_label

    # Hide the fetch button
    fetch_button.pack_forget()

    # Entry field for store ID
    tk.Label(root, text="Store ID:").pack()
    # store_id_label.pack()
    store_id_entry = tk.Entry(root)
    store_id_entry.pack()

    # Confirm button
    confirm_button = tk.Button(root, text="Confirm", command=confirm_fetch)
    confirm_button.pack(pady=10)

    
    result_label = tk.Label(root, text="")
    result_label.pack()


def confirm_fetch():
    # store_id_label.pack_forget()
    confirm_button.pack_forget()
    store_id_entry.pack_forget()
    try:
        store_id = store_id_entry.get()
        # Connects to appropriate db based on store id
        shard_id = get_shard(store_id)
        connect_to_database(shard_id)
        

        cursor = mydb.cursor()
        
        sql = "SELECT * FROM Stores WHERE store_code = %s"
        val = (store_id,)
        cursor.execute(sql, val)
        result = cursor.fetchall()


        if result:
            # Add in the column names
            column_names = [description[0] for description in cursor.description]

            
            
            store_id_entry.delete(0, tk.END)
            
            data_text = f"Data fetched successfully for Store ID: {store_id}\nColumns: "
            #Make it a string for each one and add it to the data text
            for column in column_names:
                data_text += str(column)
                data_text += " "
            data_text += "\n"
            for data in result[0]:
                data = str(data)
                data_text += data
                data_text += " "
            result_label.config(text=data_text)
            cursor.close()
            mydb.close()
            
        else:
            store_id_entry.delete(0, tk.END)
            messagebox.showwarning("Warning", f"No data found for Store ID: {store_id}")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error fetching data from MySQL database: {err}")

def reset_gui():
    for widget in root.winfo_children():
        widget.destroy()
    reset()

def reset():
    #Uses the same window, but recreates all of the buttons
    #Had to repeat the code because the variables are used from above
    #Didn't want to make a bunch of global variables

    # home_button
    home_button = tk.Button(root, text="Home", command=reset_gui)
    home_button.pack(pady=10)

    # Update hours button
    update_button = tk.Button(root, text="Update Store Hours", command=update_hours)
    update_button.pack(pady=10)

    # Insert store information button
    insert_button = tk.Button(root, text="Insert Store Information", command=insert_store)
    insert_button.pack(pady=10)

    # Get data from one of the stores
    fetch_button = tk.Button(root, text="Get data from a store", command=fetch_data)
    fetch_button.pack(pady=10)

    #Exits
    exit_button = tk.Button(root, text="Exit", command=root.quit)
    exit_button.pack(pady=10)

    root.mainloop()


# Create main window
root = tk.Tk()
root.title("MySQL GUI")
root.geometry("700x700")

# home_button
home_button = tk.Button(root, text="Home", command=reset_gui)
home_button.pack(pady=10)

# Update hours button
update_button = tk.Button(root, text="Update Store Hours", command=update_hours)
update_button.pack(pady=10)

# Insert store information button
insert_button = tk.Button(root, text="Insert Store Information", command=insert_store)
insert_button.pack(pady=10)

# Get data from one of the stores
fetch_button = tk.Button(root, text="Get data from a store", command=fetch_data)
fetch_button.pack(pady=10)

#Exits
exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=10)

root.mainloop()
