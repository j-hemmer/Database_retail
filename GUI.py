import tkinter as tk
from tkinter import messagebox
import mysql.connector

def connect_to_database():
    # Connects to the central_db database
    try:
        global mydb
        mydb = mysql.connector.connect(
            host="localhost",
            user="root",
            password="dsci551",
            database="central_db"
        )
        messagebox.showinfo("Success", "Connected to MySQL database successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error connecting to MySQL database: {err}")

def insert_store():
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
    try:
        store_code = store_code_entry.get()
        address = address_entry.get()
        opening_time = opening_time_entry.get()
        closing_time = closing_time_entry.get()

        cursor = mydb.cursor()
        sql = "INSERT INTO Stores (store_code, address, opening_time, closing_time) VALUES (%s, %s, %s, %s)"
        val = (store_code, address, opening_time, closing_time)
        cursor.execute(sql, val)
        mydb.commit()
        messagebox.showinfo("Success", "Store information inserted successfully!")
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error inserting store information into MySQL database: {err}")
# def insert_store():
#     try:
#         store_code = store_code_entry.get()
#         address = address_entry.get()
#         opening_time = opening_time_entry.get()
#         closing_time = closing_time_entry.get()

#         cursor = mydb.cursor()
#         sql = "INSERT INTO Stores (store_code, address, opening_time, closing_time) VALUES (%s, %s, %s, %s)"
#         val = (store_code, address, opening_time, closing_time)
#         cursor.execute(sql, val)
#         mydb.commit()
#         messagebox.showinfo("Success", "Store information inserted successfully!")
#     except mysql.connector.Error as err:
#         messagebox.showerror("Error", f"Error inserting store information into MySQL database: {err}")


def fetch_data():
    try:
        cursor = mydb.cursor()
        cursor.execute("SELECT * FROM Stores")
        rows = cursor.fetchall()
        display_data(rows)
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error fetching data from MySQL database: {err}")

def display_data(rows):
    top = tk.Toplevel()
    top.title("Data from MySQL")
    for i, row in enumerate(rows):
        for j, value in enumerate(row):
            label = tk.Label(top, text=value)
            label.grid(row=i, column=j)

# Create main window
root = tk.Tk()
root.title("MySQL GUI")
root.geometry("700x400")

# Creates a button that connects to the database
connect_button = tk.Button(root, text="Connect to Database", command=connect_to_database)
connect_button.pack(pady=10)


#Insert store information button
insert_button = tk.Button(root, text="Insert Store Information", command=insert_store)
insert_button.pack(pady=10)

# Gets all of the data so far
fetch_button = tk.Button(root, text="Fetch Data", command=fetch_data)
fetch_button.pack(pady=10)



# Exits the GUI
exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=10)

root.mainloop()
