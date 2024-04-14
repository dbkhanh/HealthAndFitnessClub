import psycopg2
from psycopg2 import sql
import sys

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

def add_trainer(first_name, last_name, email, password, phone):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                # Check if email already exists
                cur.execute("SELECT * FROM Trainers WHERE Email = %s", (email,))
                if cur.fetchone():
                    return "Email already exists. Please use a different email.", None

                # Insert new trainer and return the new Trainer ID
                cur.execute(
                    "INSERT INTO Trainers (FirstName, LastName, Email, Password, Phone) VALUES (%s, %s, %s, %s, %s) RETURNING TrainerID",
                    (first_name, last_name, email, password, phone)
                )
                trainer_id = cur.fetchone()[0]  
                conn.commit()
                return "Trainer registered successfully.", trainer_id
        except psycopg2.Error as e:
            return f"Error registering trainer: {e}", None
        finally:
            conn.close()
    else:
        return "Connection error", None



def update_trainer_info(trainer_id, first_name=None, last_name=None, email=None, phone=None):
    """Updates trainer information based on given details."""
    conn = get_db_connection()
    if conn is not None:
        try:
            updates = []
            params = []
            if first_name:
                updates.append("FirstName = %s")
                params.append(first_name)
            if last_name:
                updates.append("LastName = %s")
                params.append(last_name)
            if email:
                updates.append("Email = %s")
                params.append(email)
            if phone:
                updates.append("Phone = %s")
                params.append(phone)

            if updates:
                query = sql.SQL("UPDATE Trainers SET {} WHERE TrainerID = %s").format(
                    sql.SQL(', ').join(map(sql.SQL, updates))
                )
                params.append(trainer_id)
                with conn.cursor() as cur:
                    cur.execute(query, tuple(params))
                    conn.commit()
                    if cur.rowcount:
                        print("Trainer info updated successfully")
                    else:
                        print("No trainer info was updated.")
            else:
                print("No updates provided.")
        except psycopg2.Error as e:
            print("Error updating trainer info")
            print(e)
        finally:
            conn.close()
    else:
        print("Connection error")

def get_trainer_by_id(trainer_id):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM Trainers WHERE TrainerID = %s", (trainer_id,))
                trainer = cur.fetchone()
                if trainer:
                    print(f"TrainerID: {trainer[0]}, FirstName: {trainer[1]}, LastName: {trainer[2]}, "
                          f"Email: {trainer[3]}, Password: {trainer[4]}, Phone: {trainer[5]}")
                else:
                    print("Trainer not found")
        except psycopg2.Error as e:
            print("Error retrieving trainer details")
            print(e)
        finally:
            conn.close()
    else:
        print("Connection error")



def manage_trainer_schedule(trainer_id, available_from, available_until, action, new_available_from=None, new_available_until=None):
    """Manages the availability of a trainer including setting, updating, and canceling schedules."""
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                if action == 'set':
                    # Setting a new schedule
                    cur.execute(
                        "INSERT INTO TrainerSchedules (TrainerID, AvailableFrom, AvailableUntil) VALUES (%s, %s, %s)",
                        (trainer_id, available_from, available_until)
                    )
                    print("Trainer schedule set successfully.")

                elif action == 'update':
                    # Checking for existing class bookings before updating
                    cur.execute(
                        """
                        SELECT COUNT(*) FROM ClassSchedules
                        WHERE TrainerID = %s AND (StartTime BETWEEN %s AND %s OR EndTime BETWEEN %s AND %s)
                        """,
                        (trainer_id, available_from, available_until, available_from, available_until)
                    )
                    if cur.fetchone()[0] > 0:
                        print("Cannot update schedule as there are existing class bookings.")
                    elif new_available_from and new_available_until:
                        # Updating an existing schedule
                        cur.execute(
                            """
                            UPDATE TrainerSchedules
                            SET AvailableFrom = %s, AvailableUntil = %s
                            WHERE TrainerID = %s AND AvailableFrom = %s AND AvailableUntil = %s
                            """,
                            (new_available_from, new_available_until, trainer_id, available_from, available_until)
                        )
                        if cur.rowcount > 0:
                            print("Trainer schedule updated successfully.")
                        else:
                            print("No existing schedule matches the provided times; update failed.")
                    else:
                        print("New dates for update not provided.")

                elif action == 'cancel':
                    # Canceling an existing schedule
                    cur.execute(
                        """
                        DELETE FROM TrainerSchedules
                        WHERE TrainerID = %s AND AvailableFrom = %s AND AvailableUntil = %s
                        """,
                        (trainer_id, available_from, available_until)
                    )
                    if cur.rowcount > 0:
                        print("Trainer schedule canceled successfully.")
                    else:
                        print("No existing schedule found to cancel.")

                conn.commit()
        except psycopg2.Error as e:
            print("Error managing trainer schedule")
            print(e)
        finally:
            conn.close()
    else:
        print("Connection error")



def view_member_profile_by_name(name):
    """Searches for member profiles by name."""
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM Members WHERE FirstName LIKE %s OR LastName LIKE %s",
                    ('%' + name + '%', '%' + name + '%',)
                )
                profiles = cur.fetchall()
                if profiles:
                    print("Member profiles found:")
                    for profile in profiles:
                        print(f"MemberID: {profile[0]}, FirstName: {profile[1]}, LastName: {profile[2]}, "
                              f"Email: {profile[3]}, Password: {profile[4]}, Phone: {profile[5]}")
                else:
                    print("No member profiles found with that name.")
        except psycopg2.Error as e:
            print("Error retrieving member profiles")
            print(e)
        finally:
            conn.close()
    else:
        print("Connection error")


def main_menu(trainer_id):
    while True:
        print(f"\nTrainer Management System for Trainer ID {trainer_id}")
        print("1. Update My Information")
        print("2. Get My Details")
        print("3. Set Availability Schedule")
        print("4. View Member Profile by Name")
        print("5. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            first_name = input("Enter new first name (leave blank if no update): ")
            last_name = input("Enter new last name (leave blank if no update): ")
            email = input("Enter new email (leave blank if no update): ")
            phone = input("Enter new phone number (leave blank if no update): ")
            update_trainer_info(trainer_id, first_name or None, last_name or None, email or None, phone or None)
        elif choice == '2':
            get_trainer_by_id(trainer_id)
        elif choice == '3':
            action = input("Choose action (set, update, cancel): ").strip().lower()
            if action not in ['set', 'update', 'cancel']:
                print("Invalid action specified. Please choose 'set', 'update', or 'cancel'.")
            else:
                available_from = input("Enter current available from datetime (YYYY-MM-DD): ")
                available_until = input("Enter current available until datetime (YYYY-MM-DD): ")
                if action == 'update':
                    new_available_from = input("Enter new available from datetime (YYYY-MM-DD): ")
                    new_available_until = input("Enter new available until datetime (YYYY-MM-DD): ")
                    manage_trainer_schedule(trainer_id, available_from, available_until, action, new_available_from, new_available_until)
                else:
                    manage_trainer_schedule(trainer_id, available_from, available_until, action)
        elif choice == '4':
            name = input("Enter the name to search for: ")
            view_member_profile_by_name(name)
        elif choice == '5':
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")
