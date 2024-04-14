import datetime
import psycopg2
from psycopg2 import sql
from datetime import datetime
from datetime import date
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
    
def add_member(first_name, last_name, email, password, contact_number):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                # Check if the email already exists to avoid duplicate entries
                cur.execute("SELECT * FROM Members WHERE Email = %s", (email,))
                if cur.fetchone():
                    return "Email already exists. Please use a different email.", None

                # Insert new member
                cur.execute(
                    "INSERT INTO Members (FirstName, LastName, Email, Password, ContactNumber) VALUES (%s, %s, %s, %s, %s) RETURNING MemberID",
                    (first_name, last_name, email, password, contact_number)
                )
                member_id = cur.fetchone()[0]  # Capture the new Member ID

                # Insert a new billing transaction for the new member
                transaction_date = date.today() 
                cur.execute(
                    "INSERT INTO BillingPayments (MemberID, Amount, TransactionDate, PaymentStatus, Description, StaffID) VALUES (%s, %s, %s, %s, %s, %s)",
                    (member_id, 20, transaction_date, "Pending", "Initial membership fee", 1)
                )

                conn.commit()
                return "Member registered successfully.", member_id
        except psycopg2.Error as e:
            conn.rollback() 
            return f"Error registering member: {e}", None
        finally:
            conn.close()
    else:
        return "Connection error", None


def update_member_profile(member_id, first_name=None, last_name=None, email=None, contact_number=None):
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
            if contact_number:
                updates.append("ContactNumber = %s")
                params.append(contact_number)

            if updates:
                query = sql.SQL("UPDATE Members SET {} WHERE MemberID = %s").format(
                    sql.SQL(', ').join(map(sql.SQL, updates))
                )
                params.append(member_id)
                with conn.cursor() as cur:
                    cur.execute(query, tuple(params))
                    conn.commit()
                    if cur.rowcount:
                        print("Profile updated successfully")
                    else:
                        print("No profile was updated.")
            else:
                print("No updates provided.")
        except psycopg2.Error as e:
            print("Error updating member profile")
            print(e)
        finally:
            conn.close()
    else:
        print("Connection error")


def get_member_details(member_id):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM Members WHERE MemberID = %s", (member_id,))
                member = cur.fetchone()
                if member:
                    print(f"MemberID: {member[0]}, FirstName: {member[1]}, LastName: {member[2]}, "
                          f"Email: {member[3]}, Password: {member[4]}, Phone: {member[5]}")
                else:
                    print("Member not found")
        except psycopg2.Error as e:
            print("Error retrieving member data")
            print(e)
        finally:
            conn.close()
    else:
        print("Connection error")


def manage_fitness_goal(member_id, weight_goal_kg=None, time_goal_months=None):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT GoalID FROM FitnessGoals WHERE MemberID = %s",
                    (member_id,)
                )
                goal = cur.fetchone()
                if goal:
                    updates = []
                    params = []
                    if weight_goal_kg is not None:
                        updates.append("WeightGoalKG = %s")
                        params.append(weight_goal_kg)
                    if time_goal_months is not None:
                        updates.append("TimeGoalMonths = %s")
                        params.append(time_goal_months)
                    if updates:
                        params.append(goal[0])
                        query = sql.SQL("UPDATE FitnessGoals SET {} WHERE GoalID = %s").format(
                            sql.SQL(', ').join(map(sql.SQL, updates))
                        )
                        cur.execute(query, params)
                        conn.commit()
                        print("Fitness goal updated successfully.")
                else:
                    cur.execute(
                        "INSERT INTO FitnessGoals (MemberID, WeightGoalKG, TimeGoalMonths) VALUES (%s, %s, %s)",
                        (member_id, weight_goal_kg, time_goal_months)
                    )
                    conn.commit()
                    print("Fitness goal added successfully.")
        except psycopg2.Error as e:
            print("Error managing fitness goal:", e)
        finally:
            conn.close()
    else:
        print("Connection error")

def manage_health_metric(member_id, weight_kg=None, height_cm=None, recorded_date=None):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT MetricID FROM HealthMetrics WHERE MemberID = %s ORDER BY RecordedDate DESC LIMIT 1",
                    (member_id,)
                )
                metric = cur.fetchone()
                if metric:
                    updates = []
                    params = []
                    if weight_kg is not None:
                        updates.append("WeightKG = %s")
                        params.append(weight_kg)
                    if height_cm is not None:
                        updates.append("HeightCM = %s")
                        params.append(height_cm)
                    if recorded_date is not None:
                        updates.append("RecordedDate = %s")
                        params.append(recorded_date)
                    
                    if updates:
                        params.append(metric[0])
                        query = sql.SQL("UPDATE HealthMetrics SET {} WHERE MetricID = %s").format(
                            sql.SQL(', ').join(map(sql.SQL, updates))
                        )
                        cur.execute(query, params)
                        conn.commit()
                        print("Health metric updated successfully.")
                else:
                    cur.execute(
                        "INSERT INTO HealthMetrics (MemberID, WeightKG, HeightCM, RecordedDate) VALUES (%s, %s, %s, %s)",
                        (member_id, weight_kg, height_cm, recorded_date)
                    )
                    conn.commit()
                    print("Health metric added successfully.")
        except psycopg2.Error as e:
            print("Error managing health metric:", e)
        finally:
            conn.close()
    else:
        print("Connection error")


def display_member_dashboard(member_id):
    conn = get_db_connection()
    if conn is not None:
        try:
            dashboard_data = {}
            with conn.cursor() as cur:
                # Update query for Fitness Goals to reflect new schema
                cur.execute("""
                    SELECT WeightGoalKG, TimeGoalMonths 
                    FROM FitnessGoals 
                    WHERE MemberID = %s
                    """, (member_id,))
                fitness_goals = cur.fetchall()
                dashboard_data['Fitness Goals'] = [
                    f"Weight Goal: {goal[0]}kg, Time Goal: {goal[1]} months" for goal in fitness_goals
                ]
                # Get Health Metrics query remains appropriate
                cur.execute("""
                    SELECT WeightKG, HeightCM, RecordedDate 
                    FROM HealthMetrics 
                    WHERE MemberID = %s 
                    ORDER BY RecordedDate DESC
                    """, (member_id,))
                health_metrics = cur.fetchall()
                dashboard_data['Health Metrics'] = [
                    f"Weight: {metric[0]}kg, Height: {metric[1]}cm, Date: {metric[2]}" for metric in health_metrics
                ]
                # Print the aggregated dashboard data
                print("Member Dashboard Data:")
                for key, value in dashboard_data.items():
                    print(f"{key}:")
                    for item in value:
                        print(item)
        except psycopg2.Error as e:
            print("Error retrieving dashboard data")
            print(e)
        finally:
            conn.close()
    else:
        print("Connection error")


def manage_personal_training_schedule(member_id, trainer_id, session_date, action, old_session_date=None):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                # Check for pending payments first
                cur.execute("""
                    SELECT COUNT(*) FROM BillingPayments 
                    WHERE MemberID = %s AND PaymentStatus = 'Pending'
                    """, (member_id,))
                if cur.fetchone()[0] > 0:
                    print("Payment pending. Cannot manage training sessions.")
                    return

                if action == 'schedule':
                    # Check if the trainer is available at the specified date and time
                    cur.execute(
                        """
                        SELECT * FROM TrainerSchedules
                        WHERE TrainerID = %s
                        AND AvailableFrom <= %s
                        AND AvailableUntil >= %s
                        """,
                        (trainer_id, session_date, session_date)
                    )
                    if cur.fetchone():
                        # If the trainer is available, schedule the new session
                        cur.execute(
                            "INSERT INTO PersonalTrainingSessions (MemberID, TrainerID, SessionDate) VALUES (%s, %s, %s)",
                            (member_id, trainer_id, session_date)
                        )
                        conn.commit()
                        print("Session scheduled successfully")
                    else:
                        print("Trainer is not available at the selected time.")

                elif action == 'reschedule':
                    # Assumes old_session_date is provided to identify which session to reschedule
                    if not old_session_date:
                        print("Old session date is required to reschedule.")
                        return
                    # Check trainer availability for the new session date
                    cur.execute(
                        """
                        SELECT * FROM TrainerSchedules
                        WHERE TrainerID = %s AND AvailableFrom <= %s AND AvailableUntil >= %s
                        """,
                        (trainer_id, session_date, session_date)
                    )
                    if cur.fetchone():
                        cur.execute(
                            """
                            UPDATE PersonalTrainingSessions 
                            SET SessionDate = %s
                            WHERE MemberID = %s AND TrainerID = %s AND SessionDate = %s
                            """,
                            (session_date, member_id, trainer_id, old_session_date)
                        )
                        conn.commit()
                        print("Session rescheduled successfully.")
                    else:
                        print("Trainer not available on new date.")
                
                elif action == 'cancel':
                    # Logic for canceling a session
                    cur.execute(
                        """
                        DELETE FROM PersonalTrainingSessions 
                        WHERE MemberID = %s AND TrainerID = %s AND SessionDate = %s
                        """,
                        (member_id, trainer_id, session_date)
                    )
                    if cur.rowcount > 0:
                        conn.commit()
                        print("Session canceled successfully.")
                    else:
                        print("No session found to cancel on that date.")

        except psycopg2.Error as e:
            print("Error managing training session")
            print(e)
        finally:
            conn.close()
    else:
        print("Connection error")



def register_member_for_class(member_id, class_id):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                # Check for pending payments first
                cur.execute("""
                    SELECT COUNT(*) FROM BillingPayments 
                    WHERE MemberID = %s AND PaymentStatus = 'Pending'
                    """, (member_id,))
                if cur.fetchone()[0] > 0:
                    print("Payment pending. Cannot register for class.")
                    return

                # Check if the class exists in ClassSchedules
                cur.execute("""
                    SELECT ClassID FROM ClassSchedules 
                    WHERE ClassID = %s
                    """, (class_id,))
                if not cur.fetchone():
                    print("No such class found.")
                    return
                
                # Check for existing registration
                cur.execute("""
                    SELECT * FROM ClassRegistrations 
                    WHERE MemberID = %s AND ClassID = %s
                    """, (member_id, class_id))
                if cur.fetchone():
                    print("Member is already registered for this class.")
                    return

                # Register the member
                cur.execute("""
                    INSERT INTO ClassRegistrations (ClassID, MemberID, RegistrationDate) 
                    VALUES (%s, %s, CURRENT_DATE)
                    """, (class_id, member_id))
                conn.commit()
                print("Registration successful.")
        except psycopg2.Error as e:
            print("Database error:", e)
        finally:
            conn.close()
    else:
        print("Failed to connect to the database.")


def view_scheduled_classes(member_id):
    conn = get_db_connection()
    if conn is None:
        print("Failed to connect to the database.")
        return

    cursor = conn.cursor()
    try:
        query = """
            SELECT cs.ClassID, cs.StartTime, cs.EndTime, 'Group', t.FirstName, t.LastName
            FROM ClassSchedules cs
            JOIN RoomBookings r ON cs.RoomID = r.BookingID
            JOIN Trainers t ON cs.TrainerID = t.TrainerID
            JOIN ClassRegistrations cr ON cs.ClassID = cr.ClassID
            WHERE cr.MemberID = %s
            
            UNION
            
            SELECT ps.SessionID, ps.SessionDate, ps.SessionDate, 'Personal Training', t.FirstName, t.LastName
            FROM PersonalTrainingSessions ps
            JOIN Trainers t ON ps.TrainerID = t.TrainerID
            WHERE ps.MemberID = %s
        """
        cursor.execute(query, (member_id, member_id))
        scheduled_classes = cursor.fetchall()
        
        if scheduled_classes:
            print("Scheduled Classes:")
            for class_info in scheduled_classes:
                schedule_id, start_time, end_time, description, trainer_first_name, trainer_last_name = class_info
                print(f"ID: {schedule_id}, Description: {description}, Start Time: {start_time}, End Date: {end_time}, Trainer: {trainer_first_name} {trainer_last_name}")
        else:
            print("No scheduled classes found for this member.")
    except psycopg2.Error as e:
        print("Database Error:", e)
    finally:
        cursor.close()
        conn.close()

def manage_payment(member_id):
    conn = get_db_connection()
    if conn is not None:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT TransactionID, PaymentStatus FROM BillingPayments WHERE MemberID = %s AND PaymentStatus = 'Pending'",
                    (member_id,)
                )
                transaction = cur.fetchone()
                if transaction is None:
                    return "No pending transaction found."
                transaction_id, status = transaction
                payment_date = datetime.now()
                cur.execute(
                    "UPDATE BillingPayments SET PaymentStatus = %s, TransactionDate = %s WHERE TransactionID = %s",
                    ('Paid', payment_date, transaction_id)
                )
                conn.commit()
                return "Payment processed successfully."
        except psycopg2.Error as e:
            conn.rollback()  
            return f"Error processing payment: {e}"
        finally:
            conn.close()
    else:
        return "Connection error"

def main_menu(member_id):
    while True:
        print(f"\nMember Management System for Member ID {member_id}")
        print("1. Update My Profile")
        print("2. View My Details")
        print("3. Manage Fitness Goal")
        print("4. Manage Health Metric")
        print("5. Manage Personal Training Sessions")
        print("6. Register for Group Class")
        print("7. Display My Dashboard")
        print("8. View My Scheduled Classes")
        print("9. Manage Payment")
        print("10. Exit")

        choice = input("Enter your choice: ")

        if choice == '1':
            first_name = input("Enter new first name (press enter to skip): ")
            last_name = input("Enter new last name (press enter to skip): ")
            email = input("Enter new email (press enter to skip): ")
            contact_number = input("Enter new contact number (press enter to skip): ")
            update_member_profile(member_id, first_name or None, last_name or None, email or None, contact_number or None)

        elif choice == '2':
            get_member_details(member_id)

        elif choice == '3':
            weight_goal_kg = input("Enter weight goal in kg (leave blank if no update): ")
            time_goal_months = input("Enter time goal in months (leave blank if no update): ")
            weight_goal_kg = None if weight_goal_kg.strip() == "" else float(weight_goal_kg)
            time_goal_months = None if time_goal_months.strip() == "" else int(time_goal_months)
            manage_fitness_goal(member_id, weight_goal_kg, time_goal_months)

        elif choice == '4':
            weight_kg = float(input("Enter weight in kg: "))
            height_cm = int(input("Enter height in cm: "))
            recorded_date = input("Enter the date recorded (YYYY-MM-DD): ")
            manage_health_metric(member_id, weight_kg, height_cm, recorded_date)

        elif choice == '5':
            action = input("Enter action (schedule/reschedule/cancel): ")
            if action in ['schedule', 'reschedule', 'cancel']:
                trainer_id = input("Enter Trainer ID: ")
                session_date = input("Enter the session date (YYYY-MM-DD): ")
                manage_personal_training_schedule(member_id, trainer_id, session_date, action)
            else:
                print("Invalid selection.")
        
        elif choice == '6':
            class_id = input("Enter the Class ID you wish to register for: ")
            try:
                register_member_for_class(member_id, int(class_id))
            except ValueError:
                print("Invalid Class ID. Please enter a valid number.")

        elif choice == '7':
            display_member_dashboard(member_id)

        elif choice == '8':
            view_scheduled_classes(member_id)

        elif choice == '9':
            manage_payment(member_id)

        elif choice == '10':
            print("Exiting...")
            sys.exit(0)

        else:
            print("Invalid choice. Please enter a number between 1 and 10.")

