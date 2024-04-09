import tkinter as tk
from tkinter import messagebox
import mysql.connector

def connect_to_database():
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

# Gets all of the data so far
fetch_button = tk.Button(root, text="Fetch Data", command=fetch_data)
fetch_button.pack(pady=10)

# Exits the GUI
exit_button = tk.Button(root, text="Exit", command=root.quit)
exit_button.pack(pady=10)

root.mainloop()
