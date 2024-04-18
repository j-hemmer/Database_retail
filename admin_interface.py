import tkinter as tk
from tkinter import ttk, messagebox
from admin_actions import *
from customer_actions import *


def admin_interface():
    # Implement secure admin login functionality here (code omitted for brevity)
    # Assuming successful login, proceed to admin UI

    root = tk.Tk()
    root.title("Retail Store Management System - Admin")

    # Create tab container for separate sections (stores and items)
    tabControl = ttk.Notebook(root)
    store_management_tab = ttk.Frame(tabControl)
    item_management_tab = ttk.Frame(tabControl)
    tabControl.add(store_management_tab, text="Store Management")
    tabControl.add(item_management_tab, text="Item Management")
    tabControl.pack(fill=tk.BOTH, expand=True)

    # *** Store Management Tab ***

    # View Stores Section
    def view_stores():
        try:
            # Retrieve store data from central database
            stores = get_stores(True)  # Assuming this function retrieves stores from central DB

            # Clear existing data from the table
            for item in stores_table.get_children():
                stores_table.delete(item)

            # Insert the retrieved stores into the table
            for store in stores:
                stores_table.insert("", tk.END, values=store)

        except mysql.connector.Error as err:
            messagebox.showerror(title="Database Error", message=f"Error fetching stores: {err}")

    view_stores_label = ttk.Label(store_management_tab, text="View Stores:")
    view_stores_label.pack(pady=10)
    stores_table = ttk.Treeview(store_management_tab,
                                columns=("store_code", "address", "opening_time", "closing_time"))
    stores_table.heading("store_code", text="Store Code")
    stores_table.column("store_code", width=100, minwidth=100, stretch=False)
    stores_table.heading("address", text="Store Address")
    stores_table.column("address", width=200, minwidth=200, stretch=True)
    stores_table.heading("opening_time", text="Opening Time")
    stores_table.column("opening_time", width=100, minwidth=100, stretch=False)
    stores_table.heading("closing_time", text="Closing Time")
    stores_table.column("closing_time", width=100, minwidth=100, stretch=False)
    stores_table.pack()

    view_stores_button = tk.Button(store_management_tab, text="View Stores", command=view_stores)
    view_stores_button.pack(pady=10)

    # Add Store Section (same as before)
    add_store_label = ttk.Label(store_management_tab, text="Add Store:")
    add_store_label.pack(pady=10)

    store_code_label = ttk.Label(store_management_tab, text="Store Code:")
    store_code_entry = tk.Entry(store_management_tab)
    store_code_label.pack(pady=5)
    store_code_entry.pack(pady=5)

    address_label = ttk.Label(store_management_tab, text="Store Address:")
    address_entry = tk.Entry(store_management_tab)
    address_label.pack(pady=5)
    address_entry.pack(pady=5)

    opening_time_label = ttk.Label(store_management_tab, text="Opening Time (HH:MM):")
    opening_time_entry = tk.Entry(store_management_tab)
    opening_time_label.pack(pady=5)
    opening_time_entry.pack(pady=5)

    closing_time_label = ttk.Label(store_management_tab, text="Closing Time (HH:MM):")
    closing_time_entry = tk.Entry(store_management_tab)
    closing_time_label.pack(pady=5)
    closing_time_entry.pack(pady=5)

    def add_store():
        store_code = store_code_entry.get()
        address = address_entry.get()
        opening_time = opening_time_entry.get()
        closing_time = closing_time_entry.get()

        # Input validation and adding store code to avoid potential conflicts with delete_store
        if not store_code:
            messagebox.showerror(title="Error", message="Please enter a store code")
            return

        try:
            store_code = int(store_code)
        except ValueError:
            messagebox.showerror(title="Error", message="Invalid store code. Please enter an integer value.")
            return

        if not address:
            messagebox.showerror(title="Error", message="Please enter a store address")
            return

        if not (len(opening_time) == 5 and opening_time.count(":") == 1):
            messagebox.showerror(title="Error", message="Invalid opening time format (HH:MM)")
            return

        if not (len(closing_time) == 5 and closing_time.count(":") == 1):
            messagebox.showerror(title="Error", message="Invalid closing time format (HH:MM)")
            return

        try:
            insert_store(store_code, address, opening_time, closing_time)
            messagebox.showinfo(title="Success", message="Store added successfully")
            # Clear entry fields after successful addition (optional)
            store_code_entry.delete(0, tk.END)
            address_entry.delete(0, tk.END)
            opening_time_entry.delete(0, tk.END)
            closing_time_entry.delete(0, tk.END)
        except mysql.connector.Error as err:
            messagebox.showerror(title="Database Error", message=f"Error adding store: {err}")

    add_store_button = tk.Button(store_management_tab, text="Add Store", command=add_store)
    add_store_button.pack(pady=10)

    # Delete Store Section
    def delete_store_entry():
        store_code = store_code_entry.get()

        # Input validation
        if not store_code:
            messagebox.showerror(title="Error", message="Please enter a store code")
            return

        try:
            store_code = int(store_code)
        except ValueError:
            messagebox.showerror(title="Error", message="Invalid store code. Please enter an integer value.")
            return

        try:
            delete_store(store_code)
            messagebox.showinfo(title="Success", message="Store deleted successfully")
        except mysql.connector.Error as err:
            messagebox.showerror(title="Database Error", message=f"Error deleting store: {err}")

    delete_store_label = ttk.Label(store_management_tab, text="Delete Store:")
    delete_store_label.pack(pady=10)

    delete_store_button = tk.Button(store_management_tab, text="Delete Store", command=delete_store_entry)
    delete_store_button.pack(pady=10)

    # Update Hours Section
    def update_store_hours():
        store_code = store_code_entry.get()
        opening_time = opening_time_entry.get()
        closing_time = closing_time_entry.get()

        # Input validation
        if not store_code:
            messagebox.showerror(title="Error", message="Please enter a store code")
            return

        try:
            store_code = int(store_code)
        except ValueError:
            messagebox.showerror(title="Error", message="Invalid store code. Please enter an integer value.")
            return

        if not (len(opening_time) == 5 and opening_time.count(":") == 1):
            messagebox.showerror(title="Error", message="Invalid opening time format (HH:MM)")
            return

        if not (len(closing_time) == 5 and closing_time.count(":") == 1):
            messagebox.showerror(title="Error", message="Invalid closing time format (HH:MM)")
            return

        try:
            update_hours(store_code, opening_time, closing_time)
            messagebox.showinfo(title="Success", message="Store hours updated successfully")
        except mysql.connector.Error as err:
            messagebox.showerror(title="Database Error", message=f"Error updating store hours: {err}")

    update_hours_label = ttk.Label(store_management_tab, text="Update Store Hours:")
    update_hours_label.pack(pady=10)

    update_hours_button = tk.Button(store_management_tab, text="Update Hours", command=update_store_hours)
    update_hours_button.pack(pady=10)

    # *** Item Management Tab ***

    selected_store_code = None

    def select_store(event):
        global selected_store_code
        selected_store_index = store_dropdown.current()
        selected_store_code, selected_store_address = store_dropdown_values[selected_store_index]
        selected_store_code = int(selected_store_code)
        print("Selected Store Code:", selected_store_code)
        print("Selected Store Address:", selected_store_address)
        # Now you can use the selected store code in other functions

    store_dropdown_label = ttk.Label(item_management_tab, text="Select Store:")
    store_dropdown_label.pack(pady=10)

    store_dropdown_values = get_stores()  # Assuming this function retrieves store codes from central DB
    store_dropdown = ttk.Combobox(item_management_tab, values=store_dropdown_values)
    store_dropdown.bind("<<ComboboxSelected>>", select_store)
    store_dropdown.pack(pady=5)

    # Function to insert new item
    def insert_new_item():
        global selected_store_code

        item_code = item_code_entry.get()
        item_name = item_name_entry.get()
        quantity = quantity_entry.get()
        price = price_entry.get()

        print("Selected Store Code:", selected_store_code)
        # Ensure all fields are filled
        if not all([item_code, item_name, quantity, price]):
            messagebox.showerror(title="Error", message="Please fill in all fields")
            return

        try:
            item_code = int(item_code)
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            messagebox.showerror(title="Error", message="Invalid input format")
            return

        try:
            stock_new_item(item_code, selected_store_code, item_name, quantity, price)
            messagebox.showinfo(title="Success", message="New item stocked successfully")
        except mysql.connector.Error as err:
            messagebox.showerror(title="Database Error", message=f"Error stocking new item: {err}")

    # Function to restock item
    def restock_existing_item():
        global selected_store_code

        item_code = item_code_entry.get()
        quantity = quantity_entry.get()

        # Ensure all fields are filled
        if not all([item_code, quantity]):
            messagebox.showerror(title="Error", message="Please fill in all fields")
            return

        try:
            item_code = int(item_code)
            quantity = int(quantity)
        except ValueError:
            messagebox.showerror(title="Error", message="Invalid input format")
            return

        try:
            restock_item(item_code, selected_store_code, quantity)
            messagebox.showinfo(title="Success", message="Item restocked successfully")
        except mysql.connector.Error as err:
            messagebox.showerror(title="Database Error", message=f"Error restocking item: {err}")

    # Function to change item price
    def change_item_price():
        global selected_store_code

        item_code = item_code_entry.get()
        price = price_entry.get()

        # Ensure all fields are filled
        if not all([item_code, price]):
            messagebox.showerror(title="Error", message="Please fill in all fields")
            return

        try:
            item_code = int(item_code)
            price = float(price)
        except ValueError:
            messagebox.showerror(title="Error", message="Invalid input format")
            return

        try:
            price_change(item_code, selected_store_code, price)
            messagebox.showinfo(title="Success", message="Item price changed successfully")
        except mysql.connector.Error as err:
            messagebox.showerror(title="Database Error", message=f"Error changing item price: {err}")

    # Function to remove item
    def remove_existing_item():
        global selected_store_code

        item_code = item_code_entry.get()

        # Ensure all fields are filled
        if not item_code:
            messagebox.showerror(title="Error", message="Please fill in all fields")
            return

        try:
            item_code = int(item_code)
        except ValueError:
            messagebox.showerror(title="Error", message="Invalid input format")
            return

        try:
            remove_item(item_code, selected_store_code)
            messagebox.showinfo(title="Success", message="Item removed successfully")
        except mysql.connector.Error as err:
            messagebox.showerror(title="Database Error", message=f"Error removing item: {err}")

    # Define the items table
    items_table = ttk.Treeview(item_management_tab,
                               columns=("item_code", "item_name", "quantity", "price", "in_stock"))
    items_table.heading("item_code", text="Item Code")
    items_table.column("item_code", width=100, minwidth=100, stretch=False)
    items_table.heading("item_name", text="Item Name")
    items_table.column("item_name", width=200, minwidth=200, stretch=True)
    items_table.heading("quantity", text="Quantity")
    items_table.column("quantity", width=100, minwidth=100, stretch=False)
    items_table.heading("price", text="Price")
    items_table.column("price", width=100, minwidth=100, stretch=False)
    items_table.pack()

    def filter_items_view():
        global selected_store_code

        item_code = item_code_entry.get()
        item_name = item_name_entry.get()

        try:
            items = view_items(selected_store_code, item_code, item_name)
            print("Retrieved items:", items)  # Add this line to print retrieved items
            # Clear existing data from the table
            for item in items_table.get_children():
                items_table.delete(item)

            # Insert the retrieved items into the table
            for item in items:
                items_table.insert("", tk.END, values=item)

            messagebox.showinfo(title="Success", message="Items viewed successfully")
        except mysql.connector.Error as err:
            messagebox.showerror(title="Database Error", message=f"Error viewing items: {err}")

    # Button for viewing items
    view_items_button = tk.Button(item_management_tab, text="View Items", command=filter_items_view)
    view_items_button.pack(pady=5)

    # Entry fields for item details
    item_code_label = ttk.Label(item_management_tab, text="Item Code:")
    item_code_entry = tk.Entry(item_management_tab)
    item_code_label.pack(pady=5)
    item_code_entry.pack(pady=5)

    item_name_label = ttk.Label(item_management_tab, text="Item Name:")
    item_name_entry = tk.Entry(item_management_tab)
    item_name_label.pack(pady=5)
    item_name_entry.pack(pady=5)

    quantity_label = ttk.Label(item_management_tab, text="Quantity:")
    quantity_entry = tk.Entry(item_management_tab)
    quantity_label.pack(pady=5)
    quantity_entry.pack(pady=5)

    price_label = ttk.Label(item_management_tab, text="Price:")
    price_entry = tk.Entry(item_management_tab)
    price_label.pack(pady=5)
    price_entry.pack(pady=5)

    # Buttons for item management actions
    insert_new_button = tk.Button(item_management_tab, text="Insert New Item", command=insert_new_item)
    insert_new_button.pack(pady=5)

    restock_button = tk.Button(item_management_tab, text="Restock Item", command=restock_existing_item)
    restock_button.pack(pady=5)

    change_price_button = tk.Button(item_management_tab, text="Change Item Price", command=change_item_price)
    change_price_button.pack(pady=5)

    remove_item_button = tk.Button(item_management_tab, text="Remove Item", command=remove_existing_item)
    remove_item_button.pack(pady=5)

    filter_items_button = tk.Button(item_management_tab, text="View Items", command=filter_items_view)
    filter_items_button.pack(pady=5)

    root.mainloop()

