# main.py

import tkinter as tk
from tkinter import ttk
from admin_interface import admin_interface
from customer_interface import app as customer_app  # Import the Flask app instance

def login_window():
    root = tk.Tk()
    root.title("Retail Store Management System - Login")

    def login_selection():
        selection = input("Login as (Admin/Customer): ").strip().capitalize()
        if selection == "Admin":
            root.destroy()
            admin_interface()
        elif selection == "Customer":
            root.destroy()
            customer_app.run(debug=True, port=8080)  # Run the Flask app directly

    login_button = ttk.Button(root, text="Login", command=login_selection)
    login_button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    login_window()  # Start by displaying the login window
