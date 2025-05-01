# Updated TextBank app with admin account creation and control
import mysql.connector
import getpass
from decimal import Decimal

# Connect to MySQL database
def connect_db():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Huynh08k!',
        database='example'
    )

# Create a new user or admin account
def create_account():
    print("\n--- Create Account ---")
    account_type = input("Register as 'user' or 'admin': ").strip().lower()
    if account_type not in ["user", "admin"]:
        print("❌ Invalid account type.")
        return

    first_name = input("First Name: ")
    last_name = input("Last Name: ")
    email = input("Email: ")
    password = input("Password: ")
    pin_2fa = int(input("Set 4-digit PIN for 2FA: "))

    if account_type == "admin":
        bank_pin = input("Enter official bank admin pin: ")
        if bank_pin != "1234":
            print("❌ Incorrect admin pin. Cannot register as admin.")
            return

    try:
        db = connect_db()
        cursor = db.cursor()

        query = """
        INSERT INTO users (first_name, last_name, email, password, pin_2fa, is_admin)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (first_name, last_name, email, password, pin_2fa, int(account_type == "admin")))
        db.commit()

        user_id = cursor.lastrowid
        account_num = 100000 + user_id

        update_query = "UPDATE users SET account_num = %s WHERE idusers = %s"
        cursor.execute(update_query, (account_num, user_id))
        db.commit()

        print(f"✅ {account_type.capitalize()} account created successfully! Your account number is: {account_num}\n")
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        cursor.close()
        db.close()

# Check user balance
def check_balance(user_id):
    try:
        db = connect_db()
        cursor = db.cursor()
        query = "SELECT balance FROM users WHERE idusers = %s"
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        if result:
            balance = result[0]
            print(f"\n💰 Current Balance: ${balance:.2f}")
        else:
            print("❌ User not found.")
    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        cursor.close()
        db.close()


# Deposit funds
def deposit(user_id):
    try:
        amount = Decimal(input("Enter amount to deposit: $"))
        if amount <= 0:
            print("❌ Amount must be positive.")
            return

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT balance FROM users WHERE idusers = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            new_balance = result[0] + amount
            cursor.execute("UPDATE users SET balance = %s WHERE idusers = %s", (new_balance, user_id))
            db.commit()
            print(f"✅ Deposited ${amount:.2f}. New balance: ${new_balance:.2f}")
        else:
            print("❌ User not found.")
    except Exception as err:
        print(f"❌ Error: {err}")
    finally:
        cursor.close()
        db.close()

# Withdraw funds
def withdraw(user_id):
    try:
        amount = Decimal(input("Enter amount to withdraw: $"))
        if amount <= 0:
            print("❌ Amount must be positive.")
            return

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT balance FROM users WHERE idusers = %s", (user_id,))
        result = cursor.fetchone()

        if result:
            current_balance = result[0]
            if amount > current_balance:
                print("❌ Insufficient funds.")
            else:
                new_balance = current_balance - amount
                cursor.execute("UPDATE users SET balance = %s WHERE idusers = %s", (new_balance, user_id))
                db.commit()
                print(f"✅ Withdrew ${amount:.2f}. New balance: ${new_balance:.2f}")
        else:
            print("❌ User not found.")
    except Exception as err:
        print(f"❌ Error: {err}")
    finally:
        cursor.close()
        db.close()



# Admin options: View, update, or delete user accounts
def admin_panel():
    db = connect_db()
    cursor = db.cursor()
    while True:
        print("\n--- Admin Panel ---")
        print("1. View User Accounts")
        print("2. Update User Balance")
        print("3. Delete User Account")
        print("4. Exit Admin Panel")
        choice = input("Choose an option: ")

        if choice == "1":
            cursor.execute("SELECT idusers, first_name, last_name, email, balance FROM users WHERE is_admin = 0")
            for user in cursor.fetchall():
                print(f"ID: {user[0]}, Name: {user[1]} {user[2]}, Email: {user[3]}, Balance: ${user[4]:.2f}")

        elif choice == "2":
            user_id = int(input("Enter User ID to update balance: "))
            new_balance = float(input("Enter new balance: $"))
            cursor.execute("UPDATE users SET balance = %s WHERE idusers = %s", (new_balance, user_id))
            db.commit()
            print("✅ Balance updated.")

        elif choice == "3":
            user_id = int(input("Enter User ID to delete: "))
            cursor.execute("DELETE FROM users WHERE idusers = %s AND is_admin = 0", (user_id,))
            db.commit()
            print("✅ User account deleted.")

        elif choice == "4":
            break
        else:
            print("❌ Invalid choice.")
    cursor.close()
    db.close()

# Log in user and return their user ID and admin status
def login():
    print("\n--- Login ---")
    email = input("Email: ")
    pin_2fa = input("2FA PIN: ")

    try:
        db = connect_db()
        cursor = db.cursor()
        query = "SELECT idusers, first_name, is_admin FROM users WHERE email = %s AND pin_2fa = %s"
        cursor.execute(query, (email, pin_2fa))
        result = cursor.fetchone()
        if result:
            print(f"✅ Welcome back, {result[1]}!")
            return result[0], bool(result[2])
        else:
            print("❌ Login failed. Check email or 2FA PIN.")
            return None, False
    finally:
        cursor.close()
        db.close()

# Menu loop after login
def user_menu(user_id):
    while True:
        print("\n--- Menu ---")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Log Out")
        choice = input("Choose an option: ")

        if choice == "1":
            check_balance(user_id)
        elif choice == "2":
            deposit(user_id)
        elif choice == "3":
            withdraw(user_id)
        elif choice == "4":
            print("🔓 Logged out.\n")
            break
        else:
            print("❌ Invalid option.")

# Main app loop
def main():
    print("=== Welcome to TextBank 💸 ===")
    while True:
        print("\n1. Create Account")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ")

        if choice == "1":
            create_account()
        elif choice == "2":
            user_id, is_admin = login()
            if user_id:
                if is_admin:
                    admin_panel()
                else:
                    user_menu(user_id)
        elif choice == "3":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice.")

if __name__ == "__main__":
    main()
