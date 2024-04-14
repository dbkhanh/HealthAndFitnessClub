import tkinter as tk
from tkinter import messagebox
import psycopg2
from psycopg2 import sql
import trainer, member, staff

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            dbname="fitness_clb",
            user="postgres",
            password="postgres"
        )
        return conn
    except psycopg2.Error as e:
        print("Unable to connect to the database")
        print(e)
        return None
    

def register_user(first_name, last_name, email, password, contact, role, window):
    user_id = None
    if role == "Trainer":
        message, user_id = trainer.add_trainer(first_name, last_name, email, password, contact)
    elif role == "Member":
        message, user_id = member.add_member(first_name, last_name, email, password, contact) 
    elif role == "Staff":
        message, user_id = staff.add_staff(first_name, last_name, email, password, contact)  

    if "successfully" in message:
        messagebox.showinfo("Registration Successful", message)
        window.destroy()
        if user_id is not None:
            if role == "Trainer":
                trainer.main_menu(user_id)
            elif role == "Member":
                member.main_menu(user_id)
            elif role == "Staff":
                staff.main_menu(user_id)
    else:
        messagebox.showerror("Registration Failed", message)


def open_registration_form():
    register_window = tk.Toplevel(root)
    register_window.title("Register New User")

    # Entry for First Name
    tk.Label(register_window, text="First Name:").grid(row=0, column=0)
    first_name_entry = tk.Entry(register_window)
    first_name_entry.grid(row=0, column=1)

    # Entry for Last Name
    tk.Label(register_window, text="Last Name:").grid(row=1, column=0)
    last_name_entry = tk.Entry(register_window)
    last_name_entry.grid(row=1, column=1)

    # Entry for Email
    tk.Label(register_window, text="Email:").grid(row=2, column=0)
    email_entry = tk.Entry(register_window)
    email_entry.grid(row=2, column=1)

    # Entry for Password
    tk.Label(register_window, text="Password:").grid(row=3, column=0)
    password_entry = tk.Entry(register_window, show="*")
    password_entry.grid(row=3, column=1)

    # Entry for Phone (Only for Members)
    tk.Label(register_window, text="Contact Number:").grid(row=4, column=0)
    contact_entry = tk.Entry(register_window)
    contact_entry.grid(row=4, column=1)

    # Option Menu for Role
    tk.Label(register_window, text="Role:").grid(row=5, column=0)
    role_var = tk.StringVar(register_window)
    role_var.set("Trainer")  # default value
    tk.OptionMenu(register_window, role_var, "Member", "Trainer", "Staff").grid(row=5, column=1)

    # Registration Button
    tk.Button(register_window, text="Register", command=lambda: register_user(
        first_name_entry.get(), last_name_entry.get(), email_entry.get(), password_entry.get(),
        contact_entry.get(), role_var.get(), register_window)).grid(row=6, column=0, columnspan=2)
    
def login():
    email = email_entry.get()
    password = password_entry.get()
    role = role_var.get()
    
    conn = get_db_connection()
    if conn is None:
        messagebox.showerror("Database Error", "Failed to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        if role == "Staff":
            query = "SELECT * FROM Staffs WHERE email = %s AND password = %s"
        elif role == "Trainer":
            query = "SELECT * FROM Trainers WHERE email = %s AND password = %s"
        elif role == "Member":
            query = "SELECT * FROM Members WHERE email = %s AND password = %s"
        else:
            messagebox.showerror("Login Failed", "Invalid role specified.")
            return

        cursor.execute(query, (email, password))
        result = cursor.fetchone()
        if result:
            user_id = result[0]  
            messagebox.showinfo("Login Successful", f"Welcome {role}, {result[1]} {result[2]}!")
            root.destroy()  

            if role == "Trainer":
                trainer.main_menu(user_id)  
            elif role == "Member":
                member.main_menu(user_id)  
            elif role == "Staff":
                staff.main_menu(user_id) 
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")
    except psycopg2.Error as e:
        messagebox.showerror("Database Error", str(e))
    finally:
        cursor.close()
        conn.close()

# Setup the main window
root = tk.Tk()
root.title("Login Page")

# Layout configuration
root.grid_columnconfigure(0, weight=1)

# Create widgets
email_label = tk.Label(root, text="Email:")
email_label.grid(row=0, column=0, sticky=tk.W, padx=10, pady=10)

email_entry = tk.Entry(root)
email_entry.grid(row=0, column=1, padx=10, pady=10)

password_label = tk.Label(root, text="Password:")
password_label.grid(row=1, column=0, sticky=tk.W, padx=10, pady=10)

password_entry = tk.Entry(root, show="*")
password_entry.grid(row=1, column=1, padx=10, pady=10)

role_var = tk.StringVar(root)
role_var.set("Member")  # default value

role_label = tk.Label(root, text="Role:")
role_label.grid(row=2, column=0, sticky=tk.W, padx=10, pady=10)

role_option = tk.OptionMenu(root, role_var, "Member", "Trainer", "Staff")
role_option.grid(row=2, column=1, padx=10, pady=10)

login_button = tk.Button(root, text="Login", command=login)
login_button.grid(row=3, column=0, columnspan=2, pady=10)

register_button = tk.Button(root, text="Register New User", command=open_registration_form)
register_button.grid(row=4, column=0, columnspan=2, pady=10)

# Start the main event loop
root.mainloop()
