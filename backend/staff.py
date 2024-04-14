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
    
def add_staff(first_name, last_name, email, password, phone):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                # Check if the email already exists to avoid duplicate entries
                cur.execute("SELECT * FROM Staffs WHERE Email = %s", (email,))
                if cur.fetchone():
                    return "Email already exists. Please use a different email.", None

                # Insert new staff and return the new Staff ID
                cur.execute(
                    "INSERT INTO Staffs (FirstName, LastName, Email, Password, Phone) VALUES (%s, %s, %s, %s, %s) RETURNING StaffID",
                    (first_name, last_name, email, password, phone)
                )
                staff_id = cur.fetchone()[0]  
                conn.commit()
                return "Staff registered successfully.", staff_id
        except psycopg2.Error as e:
            return f"Error registering staff: {e}", None
        finally:
            conn.close()
    else:
        return "Connection error", None


def update_trainer_info(staff_id, first_name=None, last_name=None, email=None, phone=None):
    """Updates staff information based on given details."""
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
                query = sql.SQL("UPDATE Staffs SET {} WHERE StaffID = %s").format(
                    sql.SQL(', ').join(map(sql.SQL, updates))
                )
                params.append(staff_id)
                with conn.cursor() as cur:
                    cur.execute(query, tuple(params))
                    conn.commit()
                    if cur.rowcount:
                        print("Staff info updated successfully")
                    else:
                        print("No staff info was updated.")
            else:
                print("No updates provided.")
        except psycopg2.Error as e:
            print("Error updating staff info")
            print(e)
        finally:
            conn.close()
    else:
        print("Connection error")

def get_staff_by_id(staff_id):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM Staffs WHERE StaffID = %s", (staff_id,))
                row = cur.fetchone()
                if row:
                    columns = ['staffid', 'firstname', 'lastname', 'email', 'password', 'phone']
                    staff_info = dict(zip(columns, row))
                    print(f"Staff ID: {staff_info['staffid']}, First Name: {staff_info['firstname']}, "
                          f"Last Name: {staff_info['lastname']}, Email: {staff_info['email']}, "
                          f"Password: {staff_info['password']}, Phone: {staff_info['phone']}")
                else:
                    print("Staff not found")
        except psycopg2.Error as e:
            print("Error retrieving staff details")
            print(e)
        finally:
            conn.close()
    else:
        print("Connection error")


def manage_room_booking(action, booking_id=None, room_id=None, start_time=None, end_time=None, description=None, staff_id=None):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                if action == 'add':
                    if None in (room_id, start_time, end_time, description, staff_id):
                        print("All fields must be provided for adding a booking.")
                        return
                    cur.execute(
                        "INSERT INTO RoomBookings (RoomID, StartTime, EndTime, Description, StaffID) VALUES (%s, %s, %s, %s, %s)",
                        (room_id, start_time, end_time, description, staff_id)
                    )
                    print("Room booking added successfully.")

                elif action == 'update':
                    if not booking_id:
                        print("Booking ID is required for updating.")
                        return
                    updates = []
                    params = []
                    if room_id:
                        updates.append("RoomID = %s")
                        params.append(room_id)
                    if start_time:
                        updates.append("StartTime = %s")
                        params.append(start_time)
                    if end_time:
                        updates.append("EndTime = %s")
                        params.append(end_time)
                    if description:
                        updates.append("Description = %s")
                        params.append(description)
                    params.append(booking_id)
                    if updates:
                        query = sql.SQL("UPDATE RoomBookings SET " + ", ".join(updates) + " WHERE BookingID = %s")
                        cur.execute(query, params)
                        print("Room booking updated successfully.")
                    else:
                        print("No updates provided.")

                elif action == 'cancel':
                    if not booking_id:
                        print("Booking ID is required for cancellation.")
                        return
                    cur.execute("DELETE FROM RoomBookings WHERE BookingID = %s", (booking_id,))
                    print("Room booking canceled successfully.")

                else:
                    print("Invalid action specified.")
                conn.commit()
        except psycopg2.Error as e:
            print(f"Error managing room booking: {e}")
        finally:
            conn.close()
    else:
        print("Connection error")

def log_equipment_maintenance(equipment_id, maintenance_date, description, is_resolved, staff_id):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO EquipmentMaintenance (EquipmentID, MaintenanceDate, Description, IsResolved, StaffID) VALUES (%s, %s, %s, %s, %s)",
                    (equipment_id, maintenance_date, description, is_resolved, staff_id)
                )
                conn.commit()
                print("Maintenance record added successfully.")
        except psycopg2.Error as e:
            print("Error logging equipment maintenance:", e)
        finally:
            conn.close()
    else:
        print("Connection error")

def update_equipment_maintenance(maintenance_id, is_resolved):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE EquipmentMaintenance SET IsResolved = %s WHERE MaintenanceID = %s",
                    (is_resolved, maintenance_id)
                )
                conn.commit()
                print("Maintenance record updated successfully.")
        except psycopg2.Error as e:
            print("Error updating equipment maintenance:", e)
        finally:
            conn.close()
    else:
        print("Connection error")

def manage_class_schedule(action, start_time=None, end_time=None, room_id=None, trainer_id=None):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                if action == 'schedule':
                    # Check if the room is available
                    cur.execute(
                        "SELECT 1 FROM ClassSchedules WHERE RoomID = %s AND NOT (EndTime <= %s OR StartTime >= %s)",
                        (room_id, start_time, end_time)
                    )
                    if cur.fetchone():
                        print("Room is not available during the specified times.")
                        return

                    # Check if the trainer is available
                    cur.execute(
                        """
                        SELECT 1 FROM TrainerSchedules
                        WHERE TrainerID = %s AND AvailableFrom <= %s AND AvailableUntil >= %s
                        """,
                        (trainer_id, start_time, end_time)
                    )
                    if not cur.fetchone():
                        print("Trainer is not available during the specified times.")
                        return

                    # Insert the new schedule if no conflicts
                    cur.execute(
                        "INSERT INTO ClassSchedules (StartTime, EndTime, RoomID, TrainerID) VALUES (%s, %s, %s, %s)",
                        (start_time, end_time, room_id, trainer_id)
                    )
                    conn.commit()
                    print("Class schedule added successfully.")

                elif action == 'reschedule':
                    # Assume you determine which class to reschedule based on room and time
                    cur.execute(
                        "UPDATE ClassSchedules SET StartTime = %s, EndTime = %s WHERE RoomID = %s AND StartTime = %s",
                        (start_time, end_time, room_id, start_time)
                    )
                    if cur.rowcount == 0:
                        print("No class found to reschedule.")
                        return

                    conn.commit()
                    print("Class schedule rescheduled successfully.")

                elif action == 'cancel':
                    # Assume cancellation is based on room and start time
                    cur.execute(
                        "DELETE FROM ClassSchedules WHERE RoomID = %s AND StartTime = %s",
                        (room_id, start_time)
                    )
                    if cur.rowcount == 0:
                        print("No class found to cancel.")
                        return

                    conn.commit()
                    print("Class schedule canceled successfully.")

                else:
                    print("Invalid action specified.")

        except psycopg2.Error as e:
            print("Error managing class schedule:", e)
        finally:
            conn.close()
    else:
        print("Failed to connect to the database")


def view_all_members():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM Members")
                members = cur.fetchall()
                if members:
                    print("MemberID, FirstName, LastName, Email, Password, Phone Number")
                    for member in members:
                        print(f"{member[0]}, {member[1]}, {member[2]}, {member[3]}, {member[4]}, {member[5]}")
                else:
                    print("No members found.")
        except psycopg2.Error as e:
            print("Error retrieving members:", e)
        finally:
            conn.close()
    else:
        print("Connection error")


def view_all_trainers():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM Trainers")
                trainers = cur.fetchall()
                if trainers:
                    print("TrainerID, FirstName, LastName, Email, Password, Phone")
                    for trainer in trainers:
                        print(f"{trainer[0]}, {trainer[1]}, {trainer[2]}, {trainer[3]}, {trainer[4]}, {trainer[5]}")
                else:
                    print("No trainers found.")
        except psycopg2.Error as e:
            print("Error retrieving trainers:", e)
        finally:
            conn.close()
    else:
        print("Connection error")

def view_all_classes():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                # Retrieving personal training sessions
                cur.execute("SELECT * FROM PersonalTrainingSessions")
                personal_sessions = cur.fetchall()
                if personal_sessions:
                    print("Personal Training Sessions:")
                    print("SessionID, MemberID, TrainerID, Session Date")

                    # Assume the columns are properly ordered
                    for session in personal_sessions:
                        print(f"{session[0]}, {session[1]}, {session[2]}, {session[3]}")
                else:
                    print("No personal training sessions found.")
                
                # Retrieving group class schedules
                cur.execute("SELECT * FROM ClassSchedules")
                class_schedules = cur.fetchall()
                if class_schedules:
                    print("Group Class Schedules:")
                    print("ClassID, Start Date, End Date, RoomID, TrainerID")
                    for schedule in class_schedules:
                        print(f"{schedule[0]}, {schedule[1]}, {schedule[2]}, {schedule[3]}, {schedule[4]}")
                else:
                    print("No group class schedules found.")
        except psycopg2.Error as e:
            print("Error retrieving classes:", e)
        finally:
            conn.close()
    else:
        print("Connection error")

def view_all_room_bookings():
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM RoomBookings")
                bookings = cur.fetchall()
                if bookings:
                    print("Room Bookings:")
                    print("BookingID, RoomID, Start Date, End Date, Description, StaffID")
                    for booking in bookings:
                        print(f"{booking[0]}, {booking[1]}, {booking[2]}, {booking[3]}, {booking[4]}, {booking[5]}")
                else:
                    print("No room bookings found.")
        except psycopg2.Error as e:
            print("Error retrieving room bookings:", e)
        finally:
            conn.close()
    else:
        print("Connection error")


def view_payments():
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM BillingPayments")
                records = cur.fetchall()
                if records:
                    print("TransactionID, MemberID, Amount, TransactionDate, PaymentStatus, Description, StaffID")
                    for record in records:
                        print(f"{record[0]}, {record[1]}, {record[2]}, {record[3]}, {record[4]}, {record[5]}, {record[6]}")
                else:
                    print("No payments found.")
        except psycopg2.Error as e:
            print(f"Error retrieving payments: {e}")
        finally:
            conn.close()
    else:
        print("Connection error")

def view_all_staffs():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT StaffID, FirstName, LastName, Email, Phone FROM Staffs ORDER BY LastName, FirstName")
        staffs = cur.fetchall()
        print("List of All Staff Members:")
        for staff in staffs:
            print(f"ID: {staff[0]}, Name: {staff[1]} {staff[2]}, Email: {staff[3]}, Phone: {staff[4]}")
    except psycopg2.Error as e:
        print("An error occurred:", e)
    finally:
        cur.close()
        conn.close()

def main_menu(staff_id):
    while True:
        print(f"\nStaff Management System for Staff ID {staff_id}")
        print("1. Update Staff Info")
        print("2. View Staff Info")
        print("3. Manage Room Booking")
        print("4. Manage Class Schedule")
        print("5. Log Equipment Maintenance")
        print("6. Update Equipment Maintenance")
        print("7. View Membership Payment")
        print("8. View all Trainers")
        print("9. View all Members")
        print("10. View all Classes (Personal and Group)")
        print("11. View all Room Bookings")
        print("12. View all Staffs") 
        print("13. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            staff_id = input("Enter Staff ID (press enter to skip): ")
            first_name = input("Enter First Name (press enter to skip): ")
            last_name = input("Enter Last Name (press enter to skip): ")
            email = input("Enter Email (press enter to skip): ")
            phone = input("Enter Phone (press enter to skip): ")
            update_trainer_info(staff_id, first_name, last_name, email, phone)
        elif choice == '2':
            get_staff_by_id(staff_id)
        elif choice == '3':
            action = input("Enter action (add/update/cancel): ")
            if action in ['add', 'update', 'cancel']:
                booking_id = input("Enter Booking ID: " if action == 'update' or action == 'cancel' else None)
                room_id = input("Enter Room ID: ")
                start_time = input("Enter Start Time (YYYY-MM-DD): ")
                end_time = input("Enter End Time (YYYY-MM-DD): ")
                description = input("Enter Description: ")
                staff_id = input("Enter Staff ID: ")
                manage_room_booking(action, booking_id, room_id, start_time, end_time, description, staff_id)
            else:
                print("Invalid action specified.")
        elif choice == '4':
            action = input("Enter action (schedule/reschedule/cancel): ")
            if action in ['schedule', 'reschedule', 'cancel']:
                class_id = input("Enter Class ID: " if action == 'reschedule' or action == 'cancel' else None)
                start_time = input("Enter Start Time (YYYY-MM-DD): ")
                end_time = input("Enter End Time (YYYY-MM-DD): ")
                room_id = input("Enter Room ID: ")
                trainer_id = input("Enter Trainer ID: ")
                manage_class_schedule(action, start_time, end_time, room_id, trainer_id)
            else:
                print("Invalid action specified.")
        elif choice == '5':
            equipment_id = input("Enter Equipment ID: ")
            maintenance_date = input("Enter Maintenance Date (YYYY-MM-DD): ")
            description = input("Enter Description: ")
            is_resolved = input("Is Resolved (True/False): ")
            staff_id = input("Enter Staff ID: ")
            log_equipment_maintenance(equipment_id, maintenance_date, description, is_resolved, staff_id)
        elif choice == '6':
            maintenance_id = input("Enter Maintenance ID: ")
            is_resolved = input("Is Resolved (True/False): ")
            update_equipment_maintenance(maintenance_id, is_resolved)
        elif choice == '7':
             view_payments()
        elif choice == '8':
            view_all_trainers()
        elif choice == '9':
            view_all_members()
        elif choice == '10':
            view_all_classes()
        elif choice == '11':
            view_all_room_bookings()
        elif choice == '12':
            view_all_staffs()
        elif choice == '13':
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice. Please enter a number between 1 and 12.")
