import sqlite3
import bcrypt
import json
from datetime import datetime, timedelta

class LibrarySystem:
    def __init__(self, db_name="mydatabase.db"):
        self.db_name = db_name

    def get_connection(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("DROP TABLE IF EXISTS users")  # remove old tables for fresh start
            cursor.execute("DROP TABLE IF EXISTS books")
            cursor.execute("DROP TABLE IF EXISTS borrowed_books")

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password BLOB NOT NULL,
                    dob TEXT,
                    email TEXT,
                    role TEXT CHECK(role IN ('admin', 'student')) NOT NULL
                );
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    author TEXT,
                    year INTEGER
                );
            ''')
#many to many relationship __#3NF form
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS borrowed_books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    borrow_date TEXT,
                    return_date TEXT,
                    issued_by_id INTEGER NOT NULL,
                    fine REAL DEFAULT 0,
                    is_paid INTEGER DEFAULT 0,
                    FOREIGN KEY (book_id) REFERENCES books(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (issued_by_id) REFERENCES users(id)
                );
            ''')

            # Check if admin user exists
            cursor.execute("SELECT * FROM users WHERE role = 'admin' LIMIT 1")
            admin_exists = cursor.fetchone()

            if not admin_exists:
                try:
                    with open("credential.json", "r") as f:
                        data = json.load(f)
                except FileNotFoundError:
                    print("credential.json file not found. Please create an admin user manually.")
                    return
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON in credential.json: {e}")
                    return

                username = data.get("username")
                password = data.get("password")
                dob = data.get("dob")
                email = data.get("email")
                role = "admin"

                if not all([username, password, dob, email]):
                    print("Incomplete admin credentials in credential.json.")
                    return

                hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

                cursor.execute('''
                    INSERT INTO users (username, password, dob, email, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, hashed_password, dob, email, role))

                print("Admin account created successfully.")
            else:
                print("Admin already exists.")

            conn.commit()
            print("Tables created/verified.")

if __name__ == "__main__":
    system = LibrarySystem()
    system.create_tables()
